#!/usr/bin/env python3
"""
Thematic Ingestion Script - Ingestion Layer for Thematic Investing Engine

This script populates a Vector Database (Supabase with pgvector) with semantic 
representations of company business models. It enables downstream AI agents to 
perform semantic search (e.g., finding "Uranium" stocks).

Usage:
    python thematic_ingestion.py

Dependencies:
    pip install supabase yfinance fastembed python-dotenv
"""

import os
import sys
import logging
from typing import List, Optional

from dotenv import load_dotenv
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_supabase() -> Optional[Client]:
    """Initialize and return Supabase client."""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment")
        return None
    
    try:
        client = create_client(supabase_url, supabase_key)
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None


def initialize_embedding_model():
    """Initialize and return the FastEmbed model."""
    try:
        from fastembed import TextEmbedding
        model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        logger.info("Loaded FastEmbed Model: BAAI/bge-small-en-v1.5")
        return model
    except ImportError:
        logger.error("fastembed not installed. Run: pip install fastembed")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {e}")
        return None


def fetch_active_tickers(supabase: Client) -> List[str]:
    """Fetch distinct active tickers from stock_prices table."""
    try:
        # Fetch distinct tickers from stock_prices table
        response = supabase.table("stock_prices").select("ticker").execute()
        
        # Extract unique tickers
        tickers = list(set(row["ticker"] for row in response.data if row.get("ticker")))
        tickers.sort()  # Sort for consistent processing order
        
        logger.info(f"Found {len(tickers)} active tickers in database.")
        return tickers
    except Exception as e:
        logger.error(f"Failed to fetch tickers from database: {e}")
        return []


def fetch_business_summary(ticker: str) -> Optional[str]:
    """Fetch longBusinessSummary from Yahoo Finance for a given ticker."""
    try:
        import yfinance as yf
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get the long business summary
        summary = info.get("longBusinessSummary")
        
        if not summary or len(summary.strip()) == 0:
            return None
        
        return summary.strip()
    except Exception as e:
        logger.debug(f"Error fetching data for {ticker}: {e}")
        return None


def generate_embedding(model, text: str) -> Optional[List[float]]:
    """Generate embedding vector for the given text."""
    try:
        # fastembed returns a generator, convert to list
        embeddings = list(model.embed([text]))
        
        if not embeddings:
            return None
        
        # Convert numpy array to Python list for JSON serialization
        vector = embeddings[0].tolist()
        
        # Verify dimensionality (BAAI/bge-small-en-v1.5 outputs 384 dimensions)
        if len(vector) != 384:
            logger.warning(f"Unexpected embedding dimension: {len(vector)} (expected 384)")
        
        return vector
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return None


def upsert_document(
    supabase: Client,
    ticker: str,
    doc_type: str,
    content: str,
    embedding: List[float]
) -> bool:
    """
    Upsert a document to company_documents table.
    If a record with same ticker and doc_type exists, it will be updated.
    """
    try:
        # First, delete any existing record for this ticker and doc_type
        # This ensures no duplicates when re-running the script
        supabase.table("company_documents").delete().eq(
            "ticker", ticker
        ).eq(
            "doc_type", doc_type
        ).execute()
        
        # Insert new record
        payload = {
            "ticker": ticker,
            "doc_type": doc_type,
            "content": content,
            "embedding": embedding
        }
        
        supabase.table("company_documents").insert(payload).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to upsert document for {ticker}: {e}")
        return False


def run_ingestion():
    """Main ingestion pipeline."""
    logger.info("=" * 60)
    logger.info("Thematic Ingestion Pipeline - Starting")
    logger.info("=" * 60)
    
    # Step 0: Initialize clients
    supabase = initialize_supabase()
    if not supabase:
        logger.error("Failed to initialize Supabase. Exiting.")
        sys.exit(1)
    
    model = initialize_embedding_model()
    if not model:
        logger.error("Failed to initialize embedding model. Exiting.")
        sys.exit(1)
    
    # Step 1: Fetch active tickers from database
    tickers = fetch_active_tickers(supabase)
    if not tickers:
        logger.error("No tickers found in database. Exiting.")
        sys.exit(1)
    
    # Step 2-4: Process each ticker
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for i, ticker in enumerate(tickers, 1):
        logger.info(f"[{i}/{len(tickers)}] Processing {ticker}...")
        
        # Fetch business summary from Yahoo Finance
        summary = fetch_business_summary(ticker)
        
        if not summary:
            logger.warning(f"Processing {ticker}... No summary found. Skipping.")
            skip_count += 1
            continue
        
        # Generate embedding
        embedding = generate_embedding(model, summary)
        
        if not embedding:
            logger.error(f"Processing {ticker}... Failed to generate embedding. Skipping.")
            error_count += 1
            continue
        
        # Upsert to database
        success = upsert_document(
            supabase=supabase,
            ticker=ticker,
            doc_type="business_desc",
            content=summary,
            embedding=embedding
        )
        
        if success:
            logger.info(f"Processing {ticker}... Success.")
            success_count += 1
        else:
            logger.error(f"Processing {ticker}... Failed to save to database.")
            error_count += 1
    
    # Summary
    logger.info("=" * 60)
    logger.info("Ingestion Complete")
    logger.info("=" * 60)
    logger.info(f"[SUCCESS] {success_count} documents indexed.")
    logger.info(f"[SKIPPED] {skip_count} tickers had no summary available.")
    logger.info(f"[ERRORS]  {error_count} tickers failed processing.")
    
    return success_count, skip_count, error_count


if __name__ == "__main__":
    run_ingestion()
