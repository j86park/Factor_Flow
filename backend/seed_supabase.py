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

# Mock data (same as in main.py)
DEFINITIONS_DATA = [
    {
        "term": "Factor",
        "description": "A simple grouping mechanism for stocks that share similar attributes. Think of it like a \"style\" (cheap, fast-growing, steady, etc.) that tend to explain historical returns.",
        "example": "The Value factor looks for stocks that are cheap compared to their earnings or assets."
    },
    {
        "term": "Z-Score",
        "description": "A way to see how unusual today's number is versus its own history. It tells you how far above or below average something is.",
        "example": "A Z-Score of 2.0 means it's unusually high."
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
    """Insert definitions into the 'definitions' table."""
    try:
        # Delete existing data (optional - comment out if you want to keep existing data)
        # supabase.table("definitions").delete().neq("id", 0).execute()
        
        # Insert new data
        result = supabase.table("definitions").insert(definitions).execute()
        print(f"✅ Successfully inserted {len(definitions)} definitions")
        return result
    except Exception as e:
        print(f"❌ Error inserting definitions: {e}")
        raise


def insert_factors(factors: List[Dict]):
    """Insert factors into the 'factors' table."""
    try:
        # Delete existing data (optional - comment out if you want to keep existing data)
        # supabase.table("factors").delete().neq("id", 0).execute()
        
        # Insert new data
        result = supabase.table("factors").insert(factors).execute()
        print(f"✅ Successfully inserted {len(factors)} factors")
        return result
    except Exception as e:
        print(f"❌ Error inserting factors: {e}")
        raise


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
        
        # Insert factors
        print("\n📊 Inserting factors...")
        insert_factors(FACTORS_DATA)
        
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




