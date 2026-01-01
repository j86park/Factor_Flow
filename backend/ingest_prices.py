import os
import pandas as pd
import yfinance as yf
from supabase import create_client, Client
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List
import requests

# 1. SETUP
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Supabase credentials missing. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")

print(f"🚀 Connecting to Supabase at {SUPABASE_URL}")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

USER_AGENT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_sp500_tickers() -> List[str]:
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    try:
        resp = requests.get(url, headers=USER_AGENT_HEADERS, timeout=15)
        resp.raise_for_status()
        df = pd.read_html(resp.text, header=0)[0]
        symbols = df["Symbol"].astype(str).str.replace(".", "-", regex=False).tolist()
        print(f"✔️ Retrieved {len(symbols)} S&P 500 tickers")
        return symbols
    except Exception as exc:
        print(f"⚠️ Could not fetch S&P 500 tickers: {exc}")
        return []


def fetch_nasdaq100_tickers() -> List[str]:
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    try:
        resp = requests.get(url, headers=USER_AGENT_HEADERS, timeout=15)
        resp.raise_for_status()
        tables = pd.read_html(resp.text, header=0)
        for table in tables:
            if "Ticker" in table.columns:
                symbols = table["Ticker"].astype(str).str.replace(".", "-", regex=False).tolist()
                print(f"✔️ Retrieved {len(symbols)} Nasdaq-100 tickers")
                return symbols
        raise ValueError("Ticker column not found on Nasdaq-100 page")
    except Exception as exc:
        print(f"⚠️ Could not fetch Nasdaq-100 tickers: {exc}")
        return []


def gather_index_tickers() -> List[str]:
    sp500 = fetch_sp500_tickers()
    nasdaq100 = fetch_nasdaq100_tickers()
    if not sp500 and not nasdaq100:
        fallback = ["NVDA", "AAPL", "TSLA", "AMD", "MSFT", "GOOGL", "AMZN"]
        print("⚠️ Falling back to a small manual ticker list")
        return fallback
    combined = sorted({*sp500, *nasdaq100})
    print(f"🔍 Combined unique tickers count: {len(combined)}")
    return combined


def get_date_ranges_from_db(tickers):
    """
    Queries the DB to find the min and max recorded date for every ticker.
    Returns a dict: {'NVDA': {'min_date': '2024-01-02', 'max_date': '2025-12-31'}, ...}
    """
    try:
        # Try the view first for max dates
        response = supabase.table("view_latest_stock_dates").select("*").execute()
        max_dates = {row['ticker']: row['max_date'] for row in response.data}
    except Exception as e:
        print(f"Error fetching max dates from view: {e}")
        max_dates = {}
    
    # Get min dates by querying stock_prices directly
    min_dates = {}
    tickers_with_data = [t for t in tickers if t in max_dates]
    if tickers_with_data:
        print(f"Fetching earliest dates for {len(tickers_with_data)} tickers...")
        for i, ticker in enumerate(tickers_with_data):
            if (i + 1) % 50 == 0:
                print(f"   ... checked {i + 1}/{len(tickers_with_data)} tickers")
            try:
                response = supabase.table("stock_prices").select("date").eq("ticker", ticker).order("date", desc=False).limit(1).execute()
                if response.data:
                    min_dates[ticker] = response.data[0]['date']
            except Exception as e:
                print(f"Error fetching min date for {ticker}: {e}")
    
    # Combine into single dict
    result = {}
    for ticker in set(list(max_dates.keys()) + list(min_dates.keys())):
        result[ticker] = {
            'min_date': min_dates.get(ticker),
            'max_date': max_dates.get(ticker)
        }
    
    return result

def ingest_daily_data():
    # 1. Define your Universe
    tickers = gather_index_tickers()
    
    print("Checking database for existing data...")
    date_ranges = get_date_ranges_from_db(tickers)
    print(f"Found date ranges for {len(date_ranges)} tickers in database")
    
    # 2. Group tickers by "Start Date" to batch requests
    today_str = datetime.now().strftime('%Y-%m-%d')
    two_years_ago = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    batch_downloads = {}  # Format: {'start_date': {'end_date': 'YYYY-MM-DD', 'tickers': [...]}}
    
    for t in tickers:
        ticker_range = date_ranges.get(t)
        
        if not ticker_range or not ticker_range.get('max_date'):
            # Case A: New Stock -> Download full 2-year history
            start_date = two_years_ago
            end_date = today_str
        else:
            min_date = ticker_range.get('min_date')
            max_date = ticker_range.get('max_date')
            
            # Case B: Check for BACKFILL (historical data before earliest date)
            if min_date and min_date > two_years_ago:
                backfill_start = two_years_ago
                # End date for backfill is the day before the earliest existing date
                min_dt_obj = datetime.strptime(min_date, '%Y-%m-%d')
                backfill_end = (min_dt_obj - timedelta(days=1)).strftime('%Y-%m-%d')
                
                if backfill_start <= backfill_end:
                    key = f"{backfill_start}_to_{backfill_end}"
                    if key not in batch_downloads:
                        batch_downloads[key] = {'start': backfill_start, 'end': backfill_end, 'tickers': []}
                    batch_downloads[key]['tickers'].append(t)
            
            # Case C: Check for FORWARD fill (new data after latest date)
            if max_date:
                max_dt_obj = datetime.strptime(max_date, '%Y-%m-%d')
                forward_start = (max_dt_obj + timedelta(days=1)).strftime('%Y-%m-%d')
                
                if forward_start <= today_str:
                    key = f"{forward_start}_to_{today_str}"
                    if key not in batch_downloads:
                        batch_downloads[key] = {'start': forward_start, 'end': today_str, 'tickers': []}
                    batch_downloads[key]['tickers'].append(t)
            
            continue  # Already handled above
        
        # For new tickers (Case A)
        key = f"{start_date}_to_{end_date}"
        if key not in batch_downloads:
            batch_downloads[key] = {'start': start_date, 'end': end_date, 'tickers': []}
        batch_downloads[key]['tickers'].append(t)

    # 3. Execution Loop
    if not batch_downloads:
        print("✔️ No new batches to download.")
        return
    
    # Summary of what will be downloaded
    print(f"\n📊 Download plan: {len(batch_downloads)} batch(es)")
    for batch_key, batch_info in batch_downloads.items():
        print(f"   • {batch_info['start']} → {batch_info['end']}: {len(batch_info['tickers'])} tickers")
    print()

    for batch_key, batch_info in batch_downloads.items():
        start_date = batch_info['start']
        end_date = batch_info['end']
        batch_tickers = batch_info['tickers']
        
        print(f"📥 Fetching data from {start_date} to {end_date} for {len(batch_tickers)} stocks...")
        
        # yfinance can download multiple tickers at once (Efficient)
        try:
            # auto_adjust=True handles splits/dividends for the NEW data
            # Note: yfinance 'end' is exclusive, so add 1 day
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            end_date_yf = end_dt.strftime('%Y-%m-%d')
            
            data = yf.download(batch_tickers, start=start_date, end=end_date_yf, group_by='ticker', progress=False, auto_adjust=True)
            
            if data.empty:
                print(f"⚠️ No data returned for batch starting {start_date}")
                continue
            
            # Debug: print column structure
            print(f"📊 Data columns type: {type(data.columns)}")
            print(f"📊 Data columns: {list(data.columns)[:10]}...")  # First 10 columns
            
            records_to_insert = []
            
            # 4. Parse and Format for SQL
            # yfinance returns a MultiIndex if multiple tickers, or simple DF if single
            # Flatten MultiIndex columns if present
            if isinstance(data.columns, pd.MultiIndex):
                print(f"📊 MultiIndex detected with {data.columns.nlevels} levels")
                if len(batch_tickers) == 1:
                    # Single ticker with MultiIndex: columns are (Ticker, Metric)
                    # We need level 1 (metric names like Open, High, etc.)
                    data.columns = data.columns.get_level_values(1)
                    print(f"📊 Flattened columns: {list(data.columns)}")
                    t = batch_tickers[0]
                    for date, row in data.dropna().iterrows():
                        records_to_insert.append(format_row(t, date, row))
                else:
                    # Multiple tickers with MultiIndex: columns are (Ticker, Metric)
                    # Use level 0 to get ticker data
                    for t in batch_tickers:
                        try:
                            df_ticker = data.xs(t, level=0, axis=1).dropna()
                            for date, row in df_ticker.iterrows():
                                records_to_insert.append(format_row(t, date, row))
                        except KeyError:
                            print(f"⚠️ No data for {t}")
            else:
                print(f"📊 Simple columns detected")
                # Simple columns (older yfinance or single ticker without MultiIndex)
                if len(batch_tickers) == 1:
                    t = batch_tickers[0]
                    for date, row in data.dropna().iterrows():
                        records_to_insert.append(format_row(t, date, row))
                else:
                    for t in batch_tickers:
                        df_ticker = data[t].dropna()
                        for date, row in df_ticker.iterrows():
                            records_to_insert.append(format_row(t, date, row))
            
            # 5. Bulk Upsert to Supabase
            if records_to_insert:
                print(f"Uploading {len(records_to_insert)} rows...")
                response = supabase.table("stock_prices").upsert(records_to_insert).execute()
                print(f"✅ Supabase upsert wrote {len(response.data)} rows")
            else:
                print("⚠️ No records extracted for this batch.")
                
        except Exception as e:
            print(f"Error processing batch {start_date}: {e}")

def format_row(ticker, date, row):
    return {
        "ticker": ticker,
        "date": date.strftime('%Y-%m-%d'),
        "open": float(row['Open']),
        "high": float(row['High']),
        "low": float(row['Low']),
        "close": float(row['Close']),
        "volume": int(row['Volume']),
        "adjusted_close": float(row['Close']) 
    }

if __name__ == "__main__":
    ingest_daily_data()