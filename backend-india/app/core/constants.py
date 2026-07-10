"""
QuantView Indian Market Backend — Core Constants

Nifty 500 company universe, sector mappings, index definitions,
and other application-wide constants.
"""

# ── NSE Sector Mappings ──────────────────────────────────────────
SECTORS = [
    "Automobiles",
    "Banking",
    "Capital Goods",
    "Cement & Construction",
    "Chemicals",
    "Consumer Durables",
    "Energy",
    "Financial Services",
    "FMCG",
    "Healthcare",
    "Information Technology",
    "Insurance",
    "Media & Entertainment",
    "Metals & Mining",
    "Oil & Gas",
    "Pharmaceuticals",
    "Power",
    "Real Estate",
    "Telecom",
    "Textiles",
    "Utilities",
    "Diversified",
]

# ── Major Indices ────────────────────────────────────────────────
INDICES = {
    "NIFTY50": {"name": "NIFTY 50", "exchange": "NSE", "yahoo_symbol": "^NSEI"},
    "SENSEX": {"name": "SENSEX", "exchange": "BSE", "yahoo_symbol": "^BSESN"},
    "BANKNIFTY": {"name": "BANK NIFTY", "exchange": "NSE", "yahoo_symbol": "^NSEBANK"},
    "NIFTYIT": {"name": "NIFTY IT", "exchange": "NSE", "yahoo_symbol": "^CNXIT"},
    "NIFTYPHARMA": {"name": "NIFTY PHARMA", "exchange": "NSE", "yahoo_symbol": "^CNXPHARMA"},
    "NIFTYAUTO": {"name": "NIFTY AUTO", "exchange": "NSE", "yahoo_symbol": "^CNXAUTO"},
    "NIFTYFMCG": {"name": "NIFTY FMCG", "exchange": "NSE", "yahoo_symbol": "^CNXFMCG"},
    "NIFTYMETAL": {"name": "NIFTY METAL", "exchange": "NSE", "yahoo_symbol": "^CNXMETAL"},
    "NIFTYREALTY": {"name": "NIFTY REALTY", "exchange": "NSE", "yahoo_symbol": "^CNXREALTY"},
    "NIFTYENERGY": {"name": "NIFTY ENERGY", "exchange": "NSE", "yahoo_symbol": "^CNXENERGY"},
    "NIFTYPSUBANK": {"name": "NIFTY PSU BANK", "exchange": "NSE", "yahoo_symbol": "^CNXPSUBANK"},
    "NIFTYFINSERV": {"name": "NIFTY FIN SERVICE", "exchange": "NSE", "yahoo_symbol": "^CNXFINANCE"},
    "NIFTYMIDCAP150": {"name": "NIFTY MIDCAP 150", "exchange": "NSE", "yahoo_symbol": "NIFTY_MIDCAP_150.NS"},
    "NIFTYSMLCAP250": {"name": "NIFTY SMALLCAP 250", "exchange": "NSE", "yahoo_symbol": "NIFTY_SMLCAP_250.NS"},
    "NIFTY500": {"name": "NIFTY 500", "exchange": "NSE", "yahoo_symbol": "^CRSLDX"},
    "NIFTYNEXT50": {"name": "NIFTY NEXT 50", "exchange": "NSE", "yahoo_symbol": "^NSMIDCP"},
}

# ── AI Score Categories ──────────────────────────────────────────
AI_SCORE_CATEGORIES = [
    "financial_health",
    "earnings_quality",
    "governance",
    "growth",
    "valuation",
    "momentum",
    "quality",
    "risk",
    "management_confidence",
    "competitive_moat",
]

# ── Financial Ratio Definitions ──────────────────────────────────
RATIO_DEFINITIONS = {
    # Valuation
    "pe_ratio": {"name": "P/E Ratio", "category": "Valuation", "description": "Price to Earnings"},
    "pb_ratio": {"name": "P/B Ratio", "category": "Valuation", "description": "Price to Book Value"},
    "ev_ebitda": {"name": "EV/EBITDA", "category": "Valuation", "description": "Enterprise Value to EBITDA"},
    "price_to_sales": {"name": "P/S Ratio", "category": "Valuation", "description": "Price to Sales"},
    "dividend_yield": {"name": "Dividend Yield", "category": "Valuation", "description": "Annual dividend / Price"},
    # Profitability
    "roe": {"name": "ROE", "category": "Profitability", "description": "Return on Equity"},
    "roce": {"name": "ROCE", "category": "Profitability", "description": "Return on Capital Employed"},
    "roa": {"name": "ROA", "category": "Profitability", "description": "Return on Assets"},
    "operating_margin": {"name": "OPM", "category": "Profitability", "description": "Operating Profit Margin"},
    "net_margin": {"name": "NPM", "category": "Profitability", "description": "Net Profit Margin"},
    "ebitda_margin": {"name": "EBITDA Margin", "category": "Profitability", "description": "EBITDA / Revenue"},
    # Growth
    "revenue_growth_yoy": {"name": "Revenue Growth", "category": "Growth", "description": "YoY Revenue Growth"},
    "profit_growth_yoy": {"name": "Profit Growth", "category": "Growth", "description": "YoY Net Profit Growth"},
    "eps_growth_yoy": {"name": "EPS Growth", "category": "Growth", "description": "YoY EPS Growth"},
    # Leverage
    "debt_to_equity": {"name": "Debt/Equity", "category": "Leverage", "description": "Total Debt to Equity"},
    "interest_coverage": {"name": "Interest Coverage", "category": "Leverage", "description": "EBIT / Interest Expense"},
    "current_ratio": {"name": "Current Ratio", "category": "Leverage", "description": "Current Assets / Current Liabilities"},
    # Efficiency
    "asset_turnover": {"name": "Asset Turnover", "category": "Efficiency", "description": "Revenue / Total Assets"},
    "inventory_turnover": {"name": "Inventory Turnover", "category": "Efficiency", "description": "COGS / Average Inventory"},
}

# ── Document Types ───────────────────────────────────────────────
DOCUMENT_TYPES = [
    "annual_report",
    "quarterly_result",
    "earnings_call_transcript",
    "investor_presentation",
    "corporate_announcement",
    "credit_rating",
    "shareholding_pattern",
]

# ── News Sources ─────────────────────────────────────────────────
NEWS_RSS_FEEDS = {
    "economic_times_markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "economic_times_companies": "https://economictimes.indiatimes.com/news/company/rssfeeds/2143429.cms",
    "moneycontrol_news": "https://www.moneycontrol.com/rss/marketreports.xml",
    "livemint_markets": "https://www.livemint.com/rss/markets",
    "business_standard": "https://www.business-standard.com/rss/markets-106.rss",
}

# ── Market Cap Categories (in Crores) ───────────────────────────
MARKET_CAP_CATEGORIES = {
    "Large Cap": {"min": 20000, "max": float("inf")},
    "Mid Cap": {"min": 5000, "max": 20000},
    "Small Cap": {"min": 0, "max": 5000},
}

# ── BSE/NSE Configuration ───────────────────────────────────────
BSE_BASE_URL = "https://api.bseindia.com/BseIndiaAPI/api"
NSE_BASE_URL = "https://www.nseindia.com/api"
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

# ── Yahoo Finance suffix for Indian stocks ───────────────────────
YAHOO_NSE_SUFFIX = ".NS"
YAHOO_BSE_SUFFIX = ".BO"

# ── Celery Task Schedule (all times in IST = UTC+5:30) ───────────
CELERY_SCHEDULE = {
    "ingest-daily-prices": {"hour": 16, "minute": 30},        # 4:30 PM IST
    "ingest-index-data": {"hour": 17, "minute": 0},           # 5:00 PM IST
    "ingest-fii-dii": {"hour": 18, "minute": 0},              # 6:00 PM IST
    "ingest-insider-trades": {"hour": 19, "minute": 0},       # 7:00 PM IST
    "ingest-corporate-actions": {"hour": 20, "minute": 0},    # 8:00 PM IST
    "run-knowledge-extraction": {"hour": 23, "minute": 0},    # 11:00 PM IST
    "update-ai-scores": {"hour": 0, "minute": 0},             # 12:00 AM IST
    "generate-daily-intelligence": {"hour": 1, "minute": 0},  # 1:00 AM IST
    "neo4j-keep-alive": {"hour": 6, "minute": 0},             # 6:00 AM IST
}
