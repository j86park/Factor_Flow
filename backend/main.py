from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import httpx
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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Simple in-memory cache for theme titles
_theme_title_cache: dict[str, str] = {}

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


class FactorWithPerformance(BaseModel):
    id: int
    name: str
    description: str
    type: Optional[str] = None
    perf_1d: Optional[float] = None
    perf_5d: Optional[float] = None
    perf_1m: Optional[float] = None
    perf_3m: Optional[float] = None
    perf_6m: Optional[float] = None
    perf_1y: Optional[float] = None
    num_holdings: Optional[int] = None


class TopFactor(BaseModel):
    id: int
    name: str
    description: str
    perf_1d: Optional[float] = None
    perf_5d: Optional[float] = None
    perf_1m: Optional[float] = None


class ThemeTitleRequest(BaseModel):
    factor_names: List[str]


class ThemeTitleResponse(BaseModel):
    title: str


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


@app.get("/api/factors-with-performance", response_model=List[FactorWithPerformance])
def get_factors_with_performance():
    """Fetch factors joined with their latest performance data from Supabase."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    
    try:
        # Fetch all factors
        factors_response = supabase.table("factors").select("id, name, description, type").execute()
        factors = {row["id"]: row for row in factors_response.data}
        
        # Fetch latest performance for each factor (ordered by run_date desc)
        perf_response = supabase.table("factor_performance").select(
            "factor_id, run_date, perf_1d, perf_5d, perf_1m, perf_3m, perf_6m, perf_1y, num_holdings"
        ).order("run_date", desc=True).execute()
        
        # Build a map of factor_id -> latest performance (first occurrence due to desc order)
        latest_perf = {}
        for row in perf_response.data:
            fid = row["factor_id"]
            if fid not in latest_perf:
                latest_perf[fid] = row
        
        # Combine factors with their performance data
        result = []
        for factor_id, factor in factors.items():
            perf = latest_perf.get(factor_id, {})
            result.append({
                "id": factor_id,
                "name": factor["name"],
                "description": factor.get("description") or "",
                "type": factor.get("type"),
                "perf_1d": perf.get("perf_1d"),
                "perf_5d": perf.get("perf_5d"),
                "perf_1m": perf.get("perf_1m"),
                "perf_3m": perf.get("perf_3m"),
                "perf_6m": perf.get("perf_6m"),
                "perf_1y": perf.get("perf_1y"),
                "num_holdings": perf.get("num_holdings"),
            })
        
        # Sort by name for consistent ordering
        result.sort(key=lambda x: x["name"])
        return result
        
    except Exception as e:
        print(f"Error fetching factors with performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/top-factors", response_model=List[TopFactor])
def get_top_factors(limit: int = 5):
    """Fetch top N factors by weekly (5D) performance from the latest run_date."""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    
    try:
        # First, find the latest run_date in factor_performance
        latest_date_response = supabase.table("factor_performance").select(
            "run_date"
        ).order("run_date", desc=True).limit(1).execute()
        
        if not latest_date_response.data:
            return []
        
        latest_run_date = latest_date_response.data[0]["run_date"]
        
        # Fetch performance data for the latest run_date, sorted by perf_5d descending
        perf_response = supabase.table("factor_performance").select(
            "factor_id, perf_1d, perf_5d, perf_1m"
        ).eq("run_date", latest_run_date).order("perf_5d", desc=True).limit(limit).execute()
        
        if not perf_response.data:
            return []
        
        # Get the factor IDs
        factor_ids = [row["factor_id"] for row in perf_response.data]
        
        # Fetch factor details
        factors_response = supabase.table("factors").select(
            "id, name, description"
        ).in_("id", factor_ids).execute()
        
        factors_map = {row["id"]: row for row in factors_response.data}
        
        # Combine and maintain the performance-sorted order
        result = []
        for perf_row in perf_response.data:
            factor_id = perf_row["factor_id"]
            factor = factors_map.get(factor_id, {})
            if factor:
                result.append({
                    "id": factor_id,
                    "name": factor.get("name", "Unknown"),
                    "description": factor.get("description", ""),
                    "perf_1d": perf_row.get("perf_1d"),
                    "perf_5d": perf_row.get("perf_5d"),
                    "perf_1m": perf_row.get("perf_1m"),
                })
        
        return result
        
    except Exception as e:
        print(f"Error fetching top factors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-theme-title", response_model=ThemeTitleResponse)
async def generate_theme_title(request: ThemeTitleRequest):
    """Generate a 2-4 word theme title for a list of factor names using OpenRouter LLM."""
    if not request.factor_names:
        return {"title": "Top Factors"}
    
    # Create a cache key from sorted factor names
    cache_key = "|".join(sorted(request.factor_names))
    
    # Check cache first
    if cache_key in _theme_title_cache:
        return {"title": _theme_title_cache[cache_key]}
    
    # If no API key, return a generic title
    if not OPENROUTER_API_KEY:
        print("Warning: OPENROUTER_API_KEY not set. Using fallback title.")
        return {"title": "Top Performers"}
    
    try:
        factors_list = ", ".join(request.factor_names)
        prompt = f"""Given these investment factor names: {factors_list}

Generate a short, catchy 2-4 word title that captures the common theme or category these factors belong to. 
Just respond with the title, nothing else. No quotes, no explanation.

Examples of good titles: "AI & Tech", "Value Plays", "Growth Momentum", "Defensive Assets", "Energy & Materials"
"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "mistralai/mistral-7b-instruct",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 20,
                    "temperature": 0.7,
                },
                timeout=10.0,
            )
            
            if response.status_code != 200:
                print(f"OpenRouter API error: {response.status_code} - {response.text}")
                return {"title": "Top Performers"}
            
            data = response.json()
            title = data["choices"][0]["message"]["content"].strip()
            
            # Clean up the title (remove quotes if present)
            title = title.strip('"\'')
            
            # Cache the result
            _theme_title_cache[cache_key] = title
            
            return {"title": title}
            
    except Exception as e:
        print(f"Error generating theme title: {e}")
        return {"title": "Top Performers"}
