"""
QuantView Financial Knowledge Platform — Whole Market Batch Ingestor

Automated CLI script to discover, download, parse, extract, chunk, and index
annual reports for top 1000 Indian companies (Nifty 500 / Nifty 1000) into Qdrant Vector DB.
"""

import sys
import os
import asyncio
import logging
import argparse
from typing import List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.knowledge.pipeline import KnowledgeIngestionPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("market_batch_ingestor")

# Master Ticker Universe: Top Indian Market Symbols (Nifty 500 + Core Liquid Universe)
TOP_INDIAN_STOCKS = [
    # Nifty 50 Core
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL", "LT", "ITC", "TATAMOTORS",
    "AXISBANK", "KOTAKBANK", "BAJFINANCE", "HINDUNILVR", "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "ASIANPAINT", "NESTLEIND",
    "ADANIENT", "ADANIPORTS", "TATASTEEL", "POWERGRID", "NTPC", "COALINDIA", "BAJAJFINSV", "ONGC", "M&M", "JSWSTEEL",
    "GRASIM", "HCLTECH", "TECHM", "WIPRO", "HDFCLIFE", "SBILIFE", "BPCL", "HEROMOTOCO", "EICHERMOT", "BRITANNIA",
    "CIPLA", "APOLLOHOSP", "DIVISLAB", "TATACONSUM", "BEL", "TRENT", "SHRIRAMFIN", "JIOFIN", "HINDALCO", "LTIM",

    # Nifty Next 50 & Heavyweight Universe
    "DABUR", "GODREJCP", "MARICO", "PIDILITIND", "BERGEPAINT", "DLF", "GODREJPROP", "OBEROIRLTY", "MACROTECH", "PHOENIXLTD",
    "INDIGO", "IRCTC", "CONCOR", "HAL", "BDL", "SOLARINDS", "MAZDOCK", "COCHINSHIP", "BHEL", "SIEMENS",
    "ABB", "CGPOWER", "HAVELLS", "POLYCAB", "KEI", "VOLTAS", "BLUESTARCO", "AMBUJACEM", "ACC", "DALBHARAT",
    "VEDL", "NMDC", "NATIONALUM", "JINDALSTEL", "SAIL", "JINDALSAW", "MUTHOOTFIN", "MANAPPURAM", "CHOLAFIN", "PFC",
    "RECLTD", "IREDA", "L&TFH", "BAJAJHLDNG", "SUNDARMFIN", "LICHSGFIN", "CANFINHOME", "AUBANK", "FEDERALBNK", "IDFCFIRSTB",
    "BANDHANBNK", "BANKBARODA", "PNB", "UNIONBANK", "CANBK", "INDIANB", "IOB", "UCOBANK", "CENTRALBK", "PSB",

    # MidCap 150 & Sectoral Champions
    "MAXHEALTH", "FORTIS", "LUPIN", "ALKEM", "TORNTPHARMA", "GLENMARK", "BIOCON", "LAURUSLABS", "ZYDUSLIFE", "AUROPHARMA",
    "TATACOMM", "INDUSTOWER", "IDEA", "ROUTE", "AFFLE", "TANLA", "PERSISTENT", "COFORGE", "MPHASIS", "KPITTECH",
    "LTTS", "TATAELXSI", "CYIENT", "ZENSARTECH", "SONACOMS", "BALKRISIND", "MRF", "APOLLOTYRE", "CEATLTD", "MOTHERSON",
    "BOSCHLTD", "UNOMINDA", "ENDURANCE", "CUMMINSIND", "THERMAX", "AISI", "TIMKEN", "SKFINDIA", "SCHAEFFLER", "RATNAMANI",
    "TATAINVEST", "CDSL", "BSE", "MCX", "CAMSLTD", "IEX", "KFINTECH", "SUZLON", "INOXWIND", "KPIGREEN"
]


async def run_batch_ingestion(symbols: List[str], max_concurrent: int = 2):
    pipeline = KnowledgeIngestionPipeline()
    logger.info(f"🚀 Starting Whole Market Ingestion Batch ({len(symbols)} stocks)...")

    success_count = 0
    failed_count = 0

    for idx, symbol in enumerate(symbols, 1):
        logger.info(f"[{idx}/{len(symbols)}] Ingesting filings for {symbol}...")
        try:
            res = await pipeline.ingest_company(symbol)
            if res.get("status") == "success":
                success_count += 1
                logger.info(f"  ✅ Completed {symbol}: {res.get('processed_count')} reports ingested")
            else:
                failed_count += 1
                logger.warning(f"  ⚠️ Skipped/Failed {symbol}: {res.get('message')}")
        except Exception as e:
            failed_count += 1
            logger.error(f"  ❌ Error ingesting {symbol}: {e}")

        # Rate limiting delay between company downloads
        await asyncio.sleep(1.5)

    logger.info(f"🏁 Batch Ingestion Complete! Success: {success_count}, Failed/Skipped: {failed_count}")


def main():
    parser = argparse.ArgumentParser(description="QuantView Whole Market Batch Report Ingestor")
    parser.add_argument("--symbols", type=str, help="Comma-separated stock symbols (e.g. INFY,TCS,TATAMOTORS)")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum number of stocks to ingest")
    args = parser.parse_args()

    if args.symbols:
        symbol_list = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    else:
        symbol_list = TOP_INDIAN_STOCKS[:args.limit]

    asyncio.run(run_batch_ingestion(symbol_list))


if __name__ == "__main__":
    main()
