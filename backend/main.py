from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class Definition(BaseModel):
    term: str
    description: str
    example: str

class Factor(BaseModel):
    name: str
    description: str
    category: str

# Mock Data (In a real app, this would come from a DB)
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
    return DEFINITIONS_DATA

@app.get("/api/factors", response_model=List[Factor])
def get_factors():
    return FACTORS_DATA
