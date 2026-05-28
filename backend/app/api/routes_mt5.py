from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
import json
import time
from app.services.mt5_service import MT5Service

router = APIRouter()
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mt5_config.json")
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mt5_logs.json")

class MT5Credentials(BaseModel):
    accountId: str
    token: str
    volume: float = 0.01

class AutoTradingToggle(BaseModel):
    active: bool

class TradeRequest(BaseModel):
    symbol: str
    action: str  # BUY or SELL
    volume: float = 0.01
    stopLoss: float = None
    takeProfit: float = None

class CloseRequest(BaseModel):
    positionId: str

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"accountId": "", "token": "", "volume": 0.01, "isAutoTradingActive": False}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Failed to save MT5 config: {e}")

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
        "message": message,
        "symbol": symbol,
        "profit": profit
    })
    
    # Keep only the last 100 execution logs
    logs = logs[:100]
    try:
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)
    except Exception as e:
        print(f"Failed to write MT5 log: {e}")

@router.post("/mt5/connect")
def connect_mt5(creds: MT5Credentials):
    """
    Tests and saves the MetaAPI MT5 credentials.
    """
    res = MT5Service.get_account_information(creds.accountId, creds.token)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    
    config = load_config()
    config.update({
        "accountId": creds.accountId,
        "token": creds.token,
        "volume": creds.volume
    })
    save_config(config)
    
    add_log(f"Autobot successfully linked to MT5 Account: {res['name']} ({res['broker']})")
    return {
        "success": True,
        "account": res
    }

@router.get("/mt5/account")
def get_mt5_account():
    """
    Fetches active account balance/equity/margin.
    """
    config = load_config()
    if not config["accountId"] or not config["token"]:
        return {"success": False, "connected": False, "message": "No account connected"}
        
    res = MT5Service.get_account_information(config["accountId"], config["token"])
    if "error" in res:
        return {"success": False, "connected": True, "error": res["error"]}
        
    return {
        "success": True,
        "connected": True,
        "autoTradingActive": config.get("isAutoTradingActive", False),
        "volume": config.get("volume", 0.01),
        "accountId": config["accountId"],
        "account": res
    }

@router.get("/mt5/positions")
def get_mt5_positions():
    """
    Fetches all active positions directly from MT5.
    """
    config = load_config()
    if not config["accountId"] or not config["token"]:
        return []
        
    return MT5Service.get_active_positions(config["accountId"], config["token"])

@router.post("/mt5/trade")
def submit_trade(req: TradeRequest):
    """
    Manually submits a market trade.
    """
    config = load_config()
    if not config["accountId"] or not config["token"]:
        raise HTTPException(status_code=400, detail="Account not configured")
        
    res = MT5Service.execute_trade_order(
        config["accountId"],
        config["token"],
        req.symbol,
        req.action,
        req.volume,
        req.stopLoss,
        req.takeProfit
    )
    
    if not res.get("success", False):
        raise HTTPException(status_code=400, detail=res.get("error", "Execution failed"))
        
    add_log(f"Manual {req.action} order executed for {req.symbol} ({req.volume} Lots)", req.symbol)
    return res

@router.post("/mt5/close")
def close_trade(req: CloseRequest):
    """
    Closes a specific position by ID.
    """
    config = load_config()
    if not config["accountId"] or not config["token"]:
        raise HTTPException(status_code=400, detail="Account not configured")
        
    # Get active positions to find symbol and profit for logging
    positions = MT5Service.get_active_positions(config["accountId"], config["token"])
    symbol = "UNKNOWN"
    profit = 0.0
    for p in positions:
        if p["id"] == req.positionId:
            symbol = p["symbol"]
            profit = p["profit"]
            break
            
    res = MT5Service.close_trade_position(
        config["accountId"],
        config["token"],
        req.positionId
    )
    
    if not res.get("success", False):
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to close position"))
        
    add_log(f"Position #{req.positionId} closed. PnL: ${profit:+.2f}", symbol, profit)
    return res

@router.post("/mt5/toggle-auto")
def toggle_auto(req: AutoTradingToggle):
    """
    Enables/disables the Auto Trading engine.
    """
    config = load_config()
    config["isAutoTradingActive"] = req.active
    save_config(config)
    
    status = "STARTED" if req.active else "STOPPED"
    add_log(f"AI Auto Trading Bot has been {status}")
    return {"success": True, "active": req.active}

class ProvisionRequest(BaseModel):
    token: str
    login: str
    password: str
    server: str
    name: str = "QuantView Terminal"

@router.post("/mt5/provision")
def provision_mt5(req: ProvisionRequest):
    """
    Programmatically registers a raw MT5 broker account on MetaAPI cloud,
    gets the Account ID, and automatically links it in our backend!
    """
    res = MT5Service.provision_mt5_account(
        token=req.token,
        login=req.login,
        password=req.password,
        server=req.server,
        name=req.name
    )
    if not res.get("success", False):
        raise HTTPException(status_code=400, detail=res.get("error", "Provisioning failed"))
        
    accountId = res["accountId"]
    
    config = load_config()
    config.update({
        "accountId": accountId,
        "token": req.token,
        "volume": config.get("volume", 0.01)
    })
    save_config(config)
    
    add_log(f"Programmatic Cloud Bridge successfully established! Linked MT5 Account: {req.login} on {req.server}")
    
    return {
        "success": True,
        "accountId": accountId,
        "message": "MetaAPI Cloud bridge provisioned and linked successfully!"
    }

@router.get("/mt5/logs")
def get_logs():
    """
    Returns the execution logs of the MT5 Bot.
    """
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []
