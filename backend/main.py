from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
# IMPORTANT: Service role key is required for write operations
# The anon key lacks write permissions and will cause permission errors
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client | None = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    except Exception as e:
        print(f"Warning: Could not initialize Supabase client: {e}")
        print("Note: Service role key is required for database operations.")
else:
    if not SUPABASE_URL:
        print("Warning: SUPABASE_URL not set. Supabase features will be disabled.")
    if not SUPABASE_SERVICE_ROLE_KEY:
        print("Warning: SUPABASE_SERVICE_ROLE_KEY not set. Supabase features will be disabled.")
        print("Note: Service role key is required for write operations. Anon key will not work.")

# Data Models
class Definition(BaseModel):
    term: str
    description: str
    example: str

class Factor(BaseModel):
    name: str
    description: str
    type: str | None = None


# Fallback mock data (used if Supabase is not configured)
FALLBACK_DEFINITIONS_DATA = [
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
        "type": "THEMATIC",
    },
    {
        "name": "AI Adopters Early",
        "description": "Companies deploying AI to improve margins and productivity. Efficiency gains from AI tools.",
        "type": "THEMATIC",
    },
    {
        "name": "AI Theme Winners",
        "description": "Direct beneficiaries of AI adoption across sectors. Includes infrastructure, chips, and applications.",
        "type": "THEMATIC",
    }
]

@app.get("/")
def read_root():
    return {"message": "Factor Flow API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/definitions", response_model=List[Definition])
def get_definitions():
    """Fetch definitions from Supabase database."""
    if supabase:
        try:
            # Fetch definitions from Supabase
            response = supabase.table("definitions").select("definition_name, definition_desc, definition_example").execute()
            
            # Map Supabase fields to API response format
            definitions = []
            for row in response.data:
                definitions.append({
                    "term": row["definition_name"],
                    "description": row["definition_desc"] or "",
                    "example": row.get("definition_example") or ""  # Use definition_example field from database
                })
            
            return definitions
        except Exception as e:
            print(f"Error fetching definitions from Supabase: {e}")
            # Fall back to mock data if Supabase fails
            return FALLBACK_DEFINITIONS_DATA
    else:
        # Return fallback data if Supabase is not configured
        return FALLBACK_DEFINITIONS_DATA

@app.get("/api/factors", response_model=List[Factor])
def get_factors():
    """Fetch factors from Supabase"""
    if supabase:
        try:
            response = supabase.table("factors").select("name, description, type").execute()
            factors = []
            for row in response.data:
                factors.append({
                    "name": row["name"],
                    "description": row.get("description") or "",
                    "type": row.get("type") or ""
                })
            return factors
        except Exception as e:
            print(f"Error fetching factors from Supabase: {e}")
            return FACTORS_DATA
    return FACTORS_DATA
