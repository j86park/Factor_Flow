"""
Script to seed data into Supabase database.
Run this script after setting up your .env file with Supabase credentials.

Usage:
    python seed_supabase.py
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List, Dict

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY "
        "in your .env file. See env_example.txt for reference."
    )

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Mock data for definitions table
# Note: Your table uses 'definition_name', 'definition_desc', and 'definition_example' columns
DEFINITIONS_DATA = [
    {
        "definition_name": "Factor",
        "definition_desc": "A simple grouping mechanism for stocks that share similar attributes. Think of it like a \"style\" (cheap, fast-growing, steady, etc.) that tend to explain historical returns.",
        "definition_example": "The Value factor looks for stocks that are cheap compared to their earnings or assets. Growth Rates, Subsectors, Regimes like WORK FROM HOME can all be factors."
    },
    {
        "definition_name": "Z-Score",
        "definition_desc": "A way to see how unusual today's number is versus its own history. It tells you how far above or below average something is. A Z-Score of 2.0 means it's unusually high.",
        "definition_example": "If a factor's Z-Score is +2.5, it's much higher than usual (stretched). A Z-Score of -2.0 means it's much lower than usual (beaten down)."
    },
    {
        "definition_name": "Momentum",
        "definition_desc": "A factor that measures the tendency of assets that have performed well in the recent past to continue performing well, and assets that have performed poorly to continue performing poorly.",
        "definition_example": "A stock that has gained 20% over the past 3 months is showing positive momentum. If it continues to rise, the momentum factor would capture this trend."
    },
    {
        "definition_name": "Value",
        "definition_desc": "A factor that identifies stocks trading at lower prices relative to their fundamental value, such as earnings, book value, or cash flow.",
        "definition_example": "A company with a P/E ratio of 8 when the market average is 20 would be considered a value stock, as it's trading at a discount relative to its earnings."
    },
    {
        "definition_name": "Spread Trade",
        "definition_desc": "A trading strategy that involves taking offsetting positions in two or more related securities to profit from the price difference (spread) between them. Common examples include pairs trading and calendar spreads.",
        "definition_example": "Buying Stock A at $100 and simultaneously shorting Stock B at $50, betting that the price difference will widen. If A rises to $110 and B falls to $45, you profit from both positions."
    },
    {
        "definition_name": "Cumulative Returns",
        "definition_desc": "The total return of an investment over a period, calculated by compounding all period returns together. It shows the overall performance from the start of the investment period to the end.",
        "definition_example": "If an investment returns +5% in month 1, +3% in month 2, and -2% in month 3, the cumulative return after 3 months is approximately +5.9% (calculated as (1.05 × 1.03 × 0.98) - 1)."
    },
    {
        "definition_name": "Period Returns",
        "definition_desc": "The return of an investment over a specific time period (daily, weekly, monthly, quarterly, or yearly), typically expressed as a percentage. Calculated as (ending value - beginning value) / beginning value.",
        "definition_example": "If a stock closes at $100 on Monday and $105 on Friday, the weekly period return is +5% ((105 - 100) / 100 = 0.05 or 5%)."
    },
    {
        "definition_name": "Volatility",
        "definition_desc": "A measure of the dispersion of returns for a given security or market index, typically measured by the standard deviation of returns. Higher volatility indicates greater price swings and risk.",
        "definition_example": "A stock with daily returns of +2%, -1%, +3%, -2%, +1% has higher volatility than a stock with returns of +0.5%, -0.3%, +0.4%, -0.2%, +0.3%. The first stock is more unpredictable."
    },
    {
        "definition_name": "Sharpe Ratio",
        "definition_desc": "A risk-adjusted return measure calculated as (portfolio return - risk-free rate) / volatility. It indicates how much excess return you receive for the extra volatility endured. Higher values indicate better risk-adjusted performance.",
        "definition_example": "A portfolio with 12% annual return, 3% risk-free rate, and 15% volatility has a Sharpe Ratio of 0.6 ((12% - 3%) / 15% = 0.6). A Sharpe above 1.0 is considered good, above 2.0 is excellent."
    },
    {
        "definition_name": "Profit Factor",
        "definition_desc": "A ratio of gross profit to gross loss, calculated as total winning trades / total losing trades. A profit factor above 1.0 indicates profitable trading, with higher values indicating stronger performance.",
        "definition_example": "If you have 20 winning trades totaling $10,000 profit and 15 losing trades totaling $4,000 loss, your profit factor is 2.5 ($10,000 / $4,000). This means you make $2.50 for every $1.00 lost."
    },
    {
        "definition_name": "Downside Deviation",
        "definition_desc": "A measure of volatility that only considers returns below a certain threshold (usually zero or a target return). Unlike standard deviation, it focuses solely on negative volatility, providing a better measure of downside risk.",
        "definition_example": "If monthly returns are +5%, -3%, +2%, -4%, +1%, -2%, downside deviation only considers the negative returns (-3%, -4%, -2%), ignoring the positive ones, giving a clearer picture of downside risk."
    },
    {
        "definition_name": "Sortino Ratio",
        "definition_desc": "A risk-adjusted return measure similar to the Sharpe ratio, but uses downside deviation instead of total volatility. It focuses only on harmful volatility (returns below a target), making it more relevant for investors concerned about downside risk.",
        "definition_example": "A portfolio with 10% return, 2% risk-free rate, and 8% downside deviation has a Sortino Ratio of 1.0 ((10% - 2%) / 8%). This is often higher than the Sharpe ratio because it ignores upside volatility."
    },
    {
        "definition_name": "Correlation",
        "definition_desc": "A statistical measure of how two assets move in relation to each other, ranging from -1 to +1. A correlation of +1 means they move perfectly together, -1 means they move in opposite directions, and 0 means no relationship.",
        "definition_example": "Tech stocks and the NASDAQ index typically have a correlation around +0.8, meaning they move together most of the time. Gold and the stock market often have negative correlation around -0.3, moving in opposite directions."
    },
    {
        "definition_name": "Spread Z Score",
        "definition_desc": "A standardized measure indicating how many standard deviations a spread is from its historical mean. Used to identify mean reversion opportunities - extreme values suggest the spread may revert to its average.",
        "definition_example": "If the price spread between two correlated stocks averages $5 with a standard deviation of $2, and the current spread is $11, the Z-Score is 3.0 ((11-5)/2). This suggests the spread is unusually wide and may revert to the mean."
    },
    {
        "definition_name": "Alpha",
        "definition_desc": "A measure of excess return relative to a benchmark, representing the value added by active management. Positive alpha indicates outperformance, while negative alpha indicates underperformance after adjusting for market risk (beta).",
        "definition_example": "If your portfolio returns 15% while the S&P 500 returns 10%, and your beta is 1.0, your alpha is +5%. This means you outperformed the market by 5% after accounting for market risk."
    },
    {
        "definition_name": "Beta",
        "definition_desc": "A measure of an investment's sensitivity to market movements. A beta of 1.0 means the investment moves with the market, greater than 1.0 means more volatile than the market, and less than 1.0 means less volatile.",
        "definition_example": "A stock with beta of 1.5 will typically move 15% when the market moves 10%. A utility stock with beta of 0.6 will only move 6% when the market moves 10%, making it less volatile."
    }
]

FACTORS_DATA = [
    {
        "name": "Agg",
        "description": "Agricultural commodities and farming equipment. Food security and weather-dependent.",
        "category": "Sector"
    },
    {
        "name": "AI Adopters Early",
        "description": "Companies deploying AI to improve margins and productivity. Efficiency gains from AI tools.",
        "category": "Theme"
    },
    {
        "name": "AI Theme Winners",
        "description": "Direct beneficiaries of AI adoption across sectors. Includes infrastructure, chips, and applications.",
        "category": "Theme"
    },
    {
        "name": "AI Private Credit",
        "description": "Private credit funds focused on AI-related investments. Exposure to private debt financing in the AI sector.",
        "category": "Theme"
    },
    {
        "name": "OAI Ecosystem",
        "description": "Companies in the OpenAI ecosystem and related AI infrastructure.",
        "category": "AI & Momentum"
    },
    {
        "name": "Team TPU",
        "description": "Companies leveraging Google's Tensor Processing Units and related AI hardware.",
        "category": "AI & Momentum"
    },
    {
        "name": "Momentum Long",
        "description": "Stocks with strong positive momentum trends.",
        "category": "AI & Momentum"
    },
    {
        "name": "Momentum Short",
        "description": "Stocks with strong negative momentum trends.",
        "category": "AI & Momentum"
    }
]


def insert_definitions(definitions: List[Dict]):
    """Insert definitions into the 'definitions' table. Uses upsert to avoid duplicates."""
    try:
        # Upsert: Insert new records or update existing ones based on definition_name
        # This prevents errors if the data already exists
        inserted_count = 0
        updated_count = 0
        
        for definition in definitions:
            # Check if definition already exists
            existing = supabase.table("definitions").select("id").eq("definition_name", definition["definition_name"]).execute()
            
            if existing.data:
                # Update existing record
                update_data = {
                    "definition_desc": definition["definition_desc"]
                }
                # Include definition_example if it exists
                if "definition_example" in definition:
                    update_data["definition_example"] = definition["definition_example"]
                supabase.table("definitions").update(update_data).eq("definition_name", definition["definition_name"]).execute()
                updated_count += 1
            else:
                # Insert new record
                supabase.table("definitions").insert(definition).execute()
                inserted_count += 1
        
        print(f"✅ Successfully processed {len(definitions)} definitions:")
        print(f"   - Inserted: {inserted_count} new definitions")
        print(f"   - Updated: {updated_count} existing definitions")
        return {"inserted": inserted_count, "updated": updated_count}
    except Exception as e:
        print(f"❌ Error inserting definitions: {e}")
        raise


# def insert_factors(factors: List[Dict]):
#     """Insert factors into the 'factors' table."""
#     try:
#         # Delete existing data (optional - comment out if you want to keep existing data)
#         # supabase.table("factors").delete().neq("id", 0).execute()
#         
#         # Insert new data
#         result = supabase.table("factors").insert(factors).execute()
#         print(f"✅ Successfully inserted {len(factors)} factors")
#         return result
#     except Exception as e:
#         print(f"❌ Error inserting factors: {e}")
#         raise


def main():
    """Main function to seed the database."""
    print("🚀 Starting Supabase data seeding...")
    print(f"📡 Connecting to: {SUPABASE_URL}")
    
    try:
        # Test connection
        print("🔍 Testing Supabase connection...")
        # You can add a simple query here to test connection
        
        # Insert definitions
        print("\n📚 Inserting definitions...")
        insert_definitions(DEFINITIONS_DATA)
        
        # Insert factors (commented out for now)
        # print("\n📊 Inserting factors...")
        # insert_factors(FACTORS_DATA)
        
        print("\n✅ Data seeding completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        print("\n💡 Make sure:")
        print("   1. Your .env file exists and has correct credentials")
        print("   2. Your Supabase tables are created (see SQL schema below)")
        print("   3. Your API key has the correct permissions")
        raise


if __name__ == "__main__":
    main()



