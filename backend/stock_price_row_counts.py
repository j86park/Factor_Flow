"""
Generate a CSV showing how many rows exist per ticker and how many unique dates
are present, mirroring the dataset used in calculate_features.py.
"""

import os
import csv

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

CSV_PATH = "stock_prices_row_counts.csv"


def fetch_price_matrix() -> pd.DataFrame:
    """Fetch raw price data and pivot it exactly like calculate_features.py."""
    response = supabase.table("stock_prices").select("ticker, date").execute()
    df = pd.DataFrame(response.data)
    if df.empty:
        return pd.DataFrame()
    df["date"] = pd.to_datetime(df["date"])
    matrix = df.pivot(index="date", columns="ticker", values="date")
    return matrix.sort_index()


def write_csv(rows: list[tuple[str, int]], unique_dates: int) -> None:
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["ticker", "row_count"])
        writer.writerows(rows)
        writer.writerow([])
        writer.writerow(["unique_dates", unique_dates])


def main() -> None:
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY/KEY before running.")

    global supabase
    supabase = create_client(supabase_url, supabase_key)

    print("📊 Fetching stock_prices data...")
    price_matrix = fetch_price_matrix()
    if price_matrix.empty:
        print("⚠️ No data found.")
        return

    rows = [(ticker, int(price_matrix[ticker].count())) for ticker in price_matrix.columns]
    unique_dates = len(price_matrix.index)
    write_csv(rows, unique_dates)
    print(f"✅ Wrote {len(rows)} tickers / {unique_dates} unique dates to {CSV_PATH}")


if __name__ == "__main__":
    main()

