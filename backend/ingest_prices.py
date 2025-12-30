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


def get_latest_dates_from_db(tickers):
    """
    Queries the DB to find the last recorded date for every ticker.
    Returns a dict: {'NVDA': '2024-10-25', 'AAPL': '2024-10-24'}
    """
    # We use a RPC (Stored Procedure) for speed, or a simple query for small lists.
    # For simplicity here, we query the 'view_latest_dates' (we will create this view below)
    try:
        response = supabase.table("view_latest_stock_dates").select("*").execute()
        return {row['ticker']: row['max_date'] for row in response.data}
    except Exception as e:
        print(f"Error fetching dates: {e}")
        return {}

def ingest_daily_data():
    # 1. Define your Universe
    tickers = gather_index_tickers()
    
    print("Checking database for existing data...")
    existing_dates = get_latest_dates_from_db(tickers)
    print(f"Existing dates fetched: {existing_dates}")
    
    # 2. Group tickers by "Start Date" to batch requests
    # (Most stocks will need 'Today', new ones need '1 Year ago')
    today_str = datetime.now().strftime('%Y-%m-%d')
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    batch_downloads = {} # Format: {'start_date': [list_of_tickers]}

    for t in tickers:
        last_date = existing_dates.get(t)
        
        if not last_date:
            # Case A: New Stock -> Download full history
            start_date = one_year_ago
        else:
            # Case B: Existing Stock -> Download only what's missing
            # Start from the next day
            last_dt_obj = datetime.strptime(last_date, '%Y-%m-%d')
            start_date = (last_dt_obj + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # If database is already up to date, skip
            if start_date > today_str:
                continue

        if start_date not in batch_downloads:
            batch_downloads[start_date] = []
        batch_downloads[start_date].append(t)

    # 3. Execution Loop
    if not batch_downloads:
        print("✔️ No new batches to download.")
        return

    for start_date, batch_tickers in batch_downloads.items():
        print(f"Fetching data starting {start_date} for {len(batch_tickers)} stocks...")
        
        # yfinance can download multiple tickers at once (Efficient)
        try:
            # auto_adjust=True handles splits/dividends for the NEW data
            data = yf.download(batch_tickers, start=start_date, group_by='ticker', progress=False, auto_adjust=True)
            
            records_to_insert = []
            
            # 4. Parse and Format for SQL
            # yfinance returns a MultiIndex if multiple tickers, or simple DF if single
            if len(batch_tickers) == 1:
                # Handle single ticker case manually to match structure
                t = batch_tickers[0]
                for date, row in data.iterrows():
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
        # yfinance 'Close' is already adjusted when auto_adjust=True
        "adjusted_close": float(row['Close']) 
    }

if __name__ == "__main__":
    ingest_daily_data()