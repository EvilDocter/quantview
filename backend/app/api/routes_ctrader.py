from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
import time
from app.services.ctrader_service import CTraderService

router = APIRouter()

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ctrader_config.json")
LOG_FILE    = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ctrader_logs.json")


# ── Models ─────────────────────────────────────────────────────────────────────

class CTraderConnect(BaseModel):
    access_token: str
    account_id:   str
    volume:       float = 0.01

class CTraderTokenExchange(BaseModel):
    client_id:     str
    client_secret: str
    code:          str
    redirect_uri:  str = "https://localhost"

class CTraderRefresh(BaseModel):
    client_id:     str
    client_secret: str
    refresh_token: str

class CTraderAuthUrl(BaseModel):
    client_id:    str
    redirect_uri: str = "https://localhost"

class CTraderTrade(BaseModel):
    symbol:     str
    action:     str       # BUY | SELL
    volume:     float = 0.01
    stopLoss:   float = None
    takeProfit: float = None

class CTraderClose(BaseModel):
    positionId: str

class CTraderAutoToggle(BaseModel):
    active: bool


# ── Config helpers ──────────────────────────────────────────────────────────────

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "access_token": "",
        "account_id":   "",
        "volume":       0.01,
        "isAutoTradingActive": False,
    }

def save_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"Failed to save cTrader config: {e}")

def add_log(message: str, symbol: str = "SYSTEM", profit: float = 0.0):
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except Exception:
            pass
    logs.insert(0, {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "message":   message,
        "symbol":    symbol,
        "profit":    profit,
    })
    logs = logs[:100]
    try:
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)
    except Exception as e:
        print(f"Failed to write cTrader log: {e}")


# ── OAuth2 routes ───────────────────────────────────────────────────────────────

@router.post("/ctrader/auth-url")
def get_auth_url(req: CTraderAuthUrl):
    """Returns the browser URL the user must visit to authorise QuantView."""
    url = CTraderService.build_auth_url(req.client_id, req.redirect_uri)
    return {"success": True, "url": url}


@router.post("/ctrader/exchange-token")
def exchange_token(req: CTraderTokenExchange):
    """
    After the user grants access in the browser they get an auth code.
    POST here to exchange that code for access_token + refresh_token.
    """
    res = CTraderService.exchange_code_for_token(
        req.client_id, req.client_secret, req.code, req.redirect_uri
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Token exchange failed"))
    return res


@router.post("/ctrader/refresh-token")
def refresh_token(req: CTraderRefresh):
    """Uses a refresh_token to silently obtain a new access_token."""
    res = CTraderService.refresh_access_token(
        req.client_id, req.client_secret, req.refresh_token
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Refresh failed"))
    return res


# ── Account listing ─────────────────────────────────────────────────────────────

@router.get("/ctrader/accounts")
def list_accounts():
    """Lists all cTrader accounts linked to the saved access token."""
    cfg = load_config()
    token = cfg.get("access_token", "")
    if not token:
        return {"success": False, "accounts": [], "message": "No access token saved"}
    res = CTraderService.get_accounts(token)
    return res


@router.get("/ctrader/accounts/by-token")
def list_accounts_by_token(access_token: str):
    """Lists all cTrader accounts for a given access token (before saving)."""
    res = CTraderService.get_accounts(access_token)
    return res


# ── Connect / status ────────────────────────────────────────────────────────────

@router.post("/ctrader/connect")
def connect_ctrader(req: CTraderConnect):
    """
    Saves the access_token + account_id and verifies the connection by
    fetching the account summary.
    """
    summary = CTraderService.get_account_summary(req.access_token, req.account_id)
    if "error" in summary:
        raise HTTPException(status_code=400, detail=summary["error"])

    cfg = load_config()
    cfg.update({
        "access_token": req.access_token,
        "account_id":   req.account_id,
        "volume":       req.volume,
    })
    save_config(cfg)

    broker = summary.get("broker", "cTrader Broker")
    name   = summary.get("name",   f"Account {req.account_id}")
    add_log(f"cTrader connected: {name} @ {broker}")

    return {"success": True, "account": summary}


@router.get("/ctrader/account")
def get_ctrader_account():
    """Returns live account balance/equity for the saved cTrader account."""
    cfg = load_config()
    token = cfg.get("access_token", "")
    acct  = cfg.get("account_id",   "")
    if not token or not acct:
        return {"success": False, "connected": False, "message": "No cTrader account linked"}

    summary = CTraderService.get_account_summary(token, acct)
    if "error" in summary:
        return {"success": False, "connected": True, "error": summary["error"]}

    return {
        "success":          True,
        "connected":        True,
        "autoTradingActive":cfg.get("isAutoTradingActive", False),
        "volume":           cfg.get("volume", 0.01),
        "accountId":        acct,
        "account":          summary,
    }


# ── Positions ───────────────────────────────────────────────────────────────────

@router.get("/ctrader/positions")
def get_positions():
    """Returns all open positions for the linked cTrader account."""
    cfg   = load_config()
    token = cfg.get("access_token", "")
    acct  = cfg.get("account_id",   "")
    if not token or not acct:
        return []
    return CTraderService.get_positions(token, acct)


# ── Trade execution ─────────────────────────────────────────────────────────────

@router.post("/ctrader/trade")
def place_trade(req: CTraderTrade):
    """Places a market BUY or SELL order."""
    cfg   = load_config()
    token = cfg.get("access_token", "")
    acct  = cfg.get("account_id",   "")
    if not token or not acct:
        raise HTTPException(status_code=400, detail="cTrader account not configured")

    res = CTraderService.place_order(
        token, acct, req.symbol, req.action,
        req.volume, req.stopLoss, req.takeProfit
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Order failed"))

    add_log(f"{req.action} {req.volume} lots {req.symbol}", req.symbol)
    return res


@router.post("/ctrader/close")
def close_position(req: CTraderClose):
    """Closes an open position by ID."""
    cfg   = load_config()
    token = cfg.get("access_token", "")
    acct  = cfg.get("account_id",   "")
    if not token or not acct:
        raise HTTPException(status_code=400, detail="cTrader account not configured")

    # Try to grab profit for the log
    positions = CTraderService.get_positions(token, acct)
    symbol, profit = "UNKNOWN", 0.0
    for p in positions:
        if p["id"] == req.positionId:
            symbol = p["symbol"]
            profit = p["profit"]
            break

    res = CTraderService.close_position(token, acct, req.positionId)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Close failed"))

    add_log(f"Closed #{req.positionId} PnL: ${profit:+.2f}", symbol, profit)
    return res


# ── Auto-trading toggle ─────────────────────────────────────────────────────────

@router.post("/ctrader/toggle-auto")
def toggle_auto(req: CTraderAutoToggle):
    """Enables / disables the cTrader auto-trading bot."""
    cfg = load_config()
    cfg["isAutoTradingActive"] = req.active
    save_config(cfg)
    status = "STARTED" if req.active else "STOPPED"
    add_log(f"cTrader Auto Trading Bot {status}")
    return {"success": True, "active": req.active}


# ── Logs ────────────────────────────────────────────────────────────────────────

@router.get("/ctrader/logs")
def get_logs():
    """Returns cTrader execution logs."""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []
