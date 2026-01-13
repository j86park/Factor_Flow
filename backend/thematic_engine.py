#!/usr/bin/env python3
"""
Thematic Engine - Intelligence Layer for Thematic Investing Engine

This script acts as the "Search & Verify" layer that:
1. Fetches thematic factor definitions from the factors table
2. Performs semantic search against company_documents using pgvector
3. Uses an LLM Agent (via OpenRouter) to verify if matches truly fit the theme
4. Saves validated matches to factor_results_thematic

Usage:
    python thematic_engine.py

Dependencies:
    pip install supabase fastembed openai python-dotenv
"""

import os
import sys
import json
import time
import logging
import re
from typing import List, Dict, Optional, Any
from datetime import date

from dotenv import load_dotenv
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
OPENROUTER_MODEL = "openai/gpt-4.1-mini"  # OpenRouter model ID
SIMILARITY_THRESHOLD = 0.42  # Loose threshold for initial candidates
ANALYST_APPROVAL_THRESHOLD = 65  # LLM score threshold for approval
MAX_CANDIDATES = 15  # Max vector matches to retrieve per factor


# =============================================================================
# Initialization Functions
# =============================================================================

def initialize_supabase() -> Optional[Client]:
    """Initialize and return Supabase client."""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        return None
    
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")
        return None


def initialize_embedding_model():
    """Initialize FastEmbed model for vector generation."""
    try:
        from fastembed import TextEmbedding
        model = TextEmbedding(model_name=EMBEDDING_MODEL)
        logger.info(f"Loaded FastEmbed Model: {EMBEDDING_MODEL}")
        return model
    except ImportError:
        logger.error("fastembed not installed. Run: pip install fastembed")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}")
        return None


def get_openrouter_client():
    """Initialize OpenAI client configured for OpenRouter."""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            logger.error("OPENROUTER_API_KEY not set in environment")
            return None
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        logger.info("Initialized OpenRouter client")
        return client
    except ImportError:
        logger.error("openai not installed. Run: pip install openai")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize OpenRouter client: {e}")
        return None


# =============================================================================
# Data Fetching Functions
# =============================================================================

def fetch_thematic_factors(supabase: Client) -> List[Dict]:
    """Fetch all active thematic factors from the factors table."""
    try:
        response = supabase.table("factors").select(
            "id, name, description, logic_config"
        ).eq("type", "THEMATIC").execute()
        
        factors = []
        for row in response.data:
            # Extract prompt_text from logic_config if available
            logic_config = row.get("logic_config") or {}
            prompt_text = logic_config.get("prompt_text", row.get("description", ""))
            
            factors.append({
                "id": row["id"],
                "name": row["name"],
                "description": row.get("description", ""),
                "prompt_text": prompt_text
            })
        
        logger.info(f"Found {len(factors)} thematic factors to analyze")
        return factors
    except Exception as e:
        logger.error(f"Failed to fetch factors: {e}")
        return []


def search_vector_matches(
    supabase: Client,
    embedding: List[float],
    threshold: float = SIMILARITY_THRESHOLD,
    limit: int = MAX_CANDIDATES
) -> List[Dict]:
    """
    Search for semantically similar company documents using pgvector.
    Uses the match_documents RPC function.
    """
    try:
        response = supabase.rpc("match_documents", {
            "query_embedding": embedding,
            "match_threshold": threshold,
            "match_count": limit
        }).execute()
        
        return response.data or []
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []


# =============================================================================
# AI Analyst Agent
# =============================================================================

def build_analyst_prompt(
    ticker: str,
    company_description: str,
    factor_name: str,
    factor_definition: str
) -> str:
    """Build the analyst verification prompt."""
    return f"""You are a Senior Equity Research Analyst with expertise in thematic investing.

Your task is to evaluate whether a company truly fits a specific investment theme. Be STRICT in your evaluation - we want quality matches, not quantity.

## Investment Theme
**Theme Name:** {factor_name}
**Theme Definition:** {factor_definition}

## Company to Evaluate
**Ticker:** {ticker}
**Business Description:** {company_description}

## Your Task
Analyze whether this company is a STRONG fit for the theme. Consider:
1. Is this company's PRIMARY business directly related to the theme?
2. Would an investor looking for exposure to "{factor_name}" be satisfied owning this stock?
3. Is this a direct play on the theme, or just tangentially related?

## Response Format
Return ONLY a valid JSON object (no markdown, no explanation outside JSON):
{{"score": <0-100>, "reasoning": "<1-2 sentence explanation>"}}

- Score 90-100: Core/pure-play exposure to the theme
- Score 70-89: Strong exposure, but not pure-play
- Score 50-69: Moderate/indirect exposure
- Score 0-49: Weak or no meaningful exposure

Be strict. Only companies with direct, material exposure should score above 80."""


def call_analyst_agent(
    client,
    ticker: str,
    company_description: str,
    factor_name: str,
    factor_definition: str,
    max_retries: int = 3
) -> Optional[Dict]:
    """
    Call the LLM analyst to verify a match.
    Returns dict with 'score' and 'reasoning', or None on failure.
    """
    prompt = build_analyst_prompt(
        ticker, company_description, factor_name, factor_definition
    )
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3,
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response (handle potential markdown wrapping)
            json_match = re.search(r'\{[^{}]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
                if "score" in result and "reasoning" in result:
                    return result
            
            logger.warning(f"Invalid JSON from LLM for {ticker}: {content[:100]}")
            return None
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error for {ticker}: {e}")
            return None
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str:
                wait_time = 2 ** attempt
                logger.warning(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            logger.error(f"LLM call failed for {ticker}: {e}")
            return None
    
    return None


# =============================================================================
# Database Operations
# =============================================================================

def save_validated_match(
    supabase: Client,
    factor_id: int,
    ticker: str,
    confidence_score: int,
    reasoning: str,
    run_date: str
) -> bool:
    """Save a validated thematic match to factor_results_thematic."""
    try:
        # Delete existing record for this factor/ticker/date combination
        supabase.table("factor_results_thematic").delete().eq(
            "factor_id", factor_id
        ).eq("ticker", ticker).eq("run_date", run_date).execute()
        
        # Insert new record
        payload = {
            "factor_id": factor_id,
            "ticker": ticker,
            "run_date": run_date,
            "confidence_score": confidence_score,
            "reasoning": reasoning
        }
        
        supabase.table("factor_results_thematic").insert(payload).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to save match for {ticker}: {e}")
        return False


# =============================================================================
# Main Pipeline
# =============================================================================

def process_factor(
    supabase: Client,
    embed_model,
    llm_client,
    factor: Dict,
    run_date: str
) -> int:
    """
    Process a single thematic factor:
    1. Embed the factor definition
    2. Search for vector matches
    3. Verify each match with LLM
    4. Save validated matches
    
    Returns count of validated matches.
    """
    factor_id = factor["id"]
    factor_name = factor["name"]
    factor_definition = factor["prompt_text"] or factor["description"]
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Analyzing Factor: '{factor_name}'")
    logger.info(f"{'='*60}")
    
    if not factor_definition:
        logger.warning(f"No definition found for factor '{factor_name}'. Skipping.")
        return 0
    
    # Step 1: Generate embedding for factor definition
    try:
        embeddings = list(embed_model.embed([factor_definition]))
        query_vector = embeddings[0].tolist()
    except Exception as e:
        logger.error(f"Failed to embed factor definition: {e}")
        return 0
    
    # Step 2: Search for vector matches
    candidates = search_vector_matches(supabase, query_vector)
    
    if not candidates:
        logger.info(f"[SEARCH] No vector candidates found.")
        return 0
    
    # Extract unique tickers with their content
    ticker_map = {}
    for doc in candidates:
        ticker = doc.get("ticker")
        if ticker and ticker not in ticker_map:
            ticker_map[ticker] = {
                "content": doc.get("content", ""),
                "similarity": doc.get("similarity", 0)
            }
    
    logger.info(f"[SEARCH] Found {len(ticker_map)} unique vector candidates")
    
    # Step 3: Verify each candidate with LLM
    validated_count = 0
    
    for ticker, doc_data in ticker_map.items():
        company_desc = doc_data["content"]
        similarity = doc_data["similarity"]
        
        logger.info(f"[AGENT] Reviewing '{ticker}' (similarity: {similarity:.3f})...")
        
        verdict = call_analyst_agent(
            client=llm_client,
            ticker=ticker,
            company_description=company_desc,
            factor_name=factor_name,
            factor_definition=factor_definition
        )
        
        if not verdict:
            logger.warning(f"   -> Could not get AI verdict. Skipping.")
            continue
        
        score = verdict.get("score", 0)
        reasoning = verdict.get("reasoning", "")
        
        if score >= ANALYST_APPROVAL_THRESHOLD:
            logger.info(f"   -> ✅ AI Verdict: {score}/100. \"{reasoning[:80]}...\"")
            
            # Save to database
            success = save_validated_match(
                supabase=supabase,
                factor_id=factor_id,
                ticker=ticker,
                confidence_score=score,
                reasoning=reasoning,
                run_date=run_date
            )
            
            if success:
                validated_count += 1
        else:
            logger.info(f"   -> ❌ AI Verdict: {score}/100. \"{reasoning[:80]}...\"")
        
        # Small delay to avoid rate limits
        time.sleep(0.5)
    
    logger.info(f"[DB] Uploaded {validated_count} valid matches for '{factor_name}'")
    return validated_count


def run_thematic_engine():
    """Main entry point for the thematic engine pipeline."""
    logger.info("=" * 70)
    logger.info("Thematic Engine - Intelligence Layer")
    logger.info("=" * 70)
    
    # Initialize clients
    supabase = initialize_supabase()
    if not supabase:
        logger.error("Failed to initialize Supabase. Exiting.")
        sys.exit(1)
    
    embed_model = initialize_embedding_model()
    if not embed_model:
        logger.error("Failed to initialize embedding model. Exiting.")
        sys.exit(1)
    
    llm_client = get_openrouter_client()
    if not llm_client:
        logger.error("Failed to initialize OpenRouter client. Exiting.")
        sys.exit(1)
    
    # Fetch thematic factors
    factors = fetch_thematic_factors(supabase)
    if not factors:
        logger.warning("No thematic factors found. Exiting.")
        sys.exit(0)
    
    # Process each factor
    run_date = date.today().isoformat()
    total_matches = 0
    
    for factor in factors:
        matches = process_factor(
            supabase=supabase,
            embed_model=embed_model,
            llm_client=llm_client,
            factor=factor,
            run_date=run_date
        )
        total_matches += matches
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("Thematic Engine Complete")
    logger.info("=" * 70)
    logger.info(f"Processed {len(factors)} thematic factors")
    logger.info(f"Total validated matches: {total_matches}")
    
    return total_matches


if __name__ == "__main__":
    run_thematic_engine()
