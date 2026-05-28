import requests
import logging
import json
import os
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from app.services.live_cache import LIVE_CACHE

logger = logging.getLogger(__name__)

SIM_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mt5_simulated_db.json")

def load_sim_db():
    if os.path.exists(SIM_DB_FILE):
        try:
            with open(SIM_DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "balance": 10000.00,
        "currency": "USD",
        "broker": "QuantView Demo Simulator",
        "name": "Local Simulation Desk",
        "positions": []
    }

def save_sim_db(db):
    try:
        with open(SIM_DB_FILE, "w") as f:
            json.dump(db, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save simulated DB: {e}")

class MT5Service:
    @staticmethod
    def get_account_information(account_id: str, token: str):
        """
        Fetches live account information from MetaAPI, fallback to local simulator if DEMO credentials used
        """
        if not account_id or not token:
            return {"error": "Missing MetaAPI Account ID or Token"}
            
        # Demo Simulator Check
        if "DEMO" in account_id.upper() or "DEMO" in token.upper():
            db = load_sim_db()
            positions = db.get("positions", [])
            net_pnl = 0.0
            
            # calculate ticking PnL from backend live cache
            for p in positions:
                sym = p.get("symbol")
                current_price = p.get("openPrice", 1.0)
                
                # Fetch price from active WebSocket stream
                if sym in LIVE_CACHE:
                    current_price = LIVE_CACHE[sym].get("price", current_price)
                elif f"{sym}/USD" in LIVE_CACHE:
                    current_price = LIVE_CACHE[f"{sym}/USD"].get("price", current_price)
                
                coef = 1000.0 if "XAU" in sym or "/" in sym else 10.0
                if p["type"] == "BUY":
                    profit = (current_price - p["openPrice"]) * p["volume"] * coef
                else:
                    profit = (p["openPrice"] - current_price) * p["volume"] * coef
                net_pnl += profit
                
            return {
                "balance": db["balance"],
                "equity": db["balance"] + net_pnl,
                "margin": 0.0,
                "freeMargin": db["balance"] + net_pnl,
                "marginLevel": 100.0,
                "leverage": 100,
                "currency": "USD",
                "broker": "QuantView Simulator",
                "name": "Local Demo Desk"
            }
        
        # MetaAPI Live connection
        url = f"https://mt-client-api.new-york.metaapi.cloud/users/current/accounts/{account_id}/account-information"
        headers = {"auth-token": token}
        
        try:
            res = requests.get(url, headers=headers, timeout=10, verify=False)
            if res.status_code == 200:
                data = res.json()
                return {
                    "balance": data.get("balance", 0.0),
                    "equity": data.get("equity", 0.0),
                    "margin": data.get("margin", 0.0),
                    "freeMargin": data.get("freeMargin", 0.0),
                    "marginLevel": data.get("marginLevel", 0.0),
                    "leverage": data.get("leverage", 1),
                    "currency": data.get("currency", "USD"),
                    "broker": data.get("broker", "Unknown"),
                    "name": data.get("name", "Demo Account")
                }
            else:
                logger.error(f"MetaAPI Error: Status {res.status_code} - {res.text}")
                return {"error": f"MetaAPI returned status code {res.status_code}: {res.text[:100]}"}
        except Exception as e:
            logger.error(f"Failed to fetch MetaAPI account details: {str(e)}")
            return {"error": f"Connection failed: {str(e)}"}

    @staticmethod
    def get_active_positions(account_id: str, token: str):
        """
        Retrieves all currently active open positions (MetaAPI or Demo Simulator)
        """
        if not account_id or not token:
            return []
            
        # Demo Simulator Check
        if "DEMO" in account_id.upper() or "DEMO" in token.upper():
            db = load_sim_db()
            positions = db.get("positions", [])
            for p in positions:
                sym = p.get("symbol")
                current_price = p.get("openPrice", 1.0)
                
                if sym in LIVE_CACHE:
                    current_price = LIVE_CACHE[sym].get("price", current_price)
                elif f"{sym}/USD" in LIVE_CACHE:
                    current_price = LIVE_CACHE[f"{sym}/USD"].get("price", current_price)
                
                p["currentPrice"] = current_price
                coef = 1000.0 if "XAU" in sym or "/" in sym else 10.0
                if p["type"] == "BUY":
                    p["profit"] = (current_price - p["openPrice"]) * p["volume"] * coef
                else:
                    p["profit"] = (p["openPrice"] - current_price) * p["volume"] * coef
            return positions
            
        # MetaAPI Live connection
        url = f"https://mt-client-api.new-york.metaapi.cloud/users/current/accounts/{account_id}/positions"
        headers = {"auth-token": token}
        
        try:
            res = requests.get(url, headers=headers, timeout=10, verify=False)
            if res.status_code == 200:
                positions = res.json()
                formatted_positions = []
                for p in positions:
                    formatted_positions.append({
                        "id": p.get("id"),
                        "symbol": p.get("symbol"),
                        "type": "BUY" if p.get("type") == "POSITION_TYPE_BUY" else "SELL",
                        "volume": p.get("volume", 0.01),
                        "openPrice": p.get("openPrice"),
                        "currentPrice": p.get("currentPrice"),
                        "stopLoss": p.get("stopLoss"),
                        "takeProfit": p.get("takeProfit"),
                        "profit": p.get("profit", 0.0),
                        "time": p.get("time")
                    })
                return formatted_positions
            else:
                logger.error(f"MetaAPI active positions retrieval failed: {res.text}")
                return []
        except Exception as e:
            logger.error(f"Exception retrieving active positions: {str(e)}")
            return []

    @staticmethod
    def execute_trade_order(account_id: str, token: str, symbol: str, action: str, volume: float = 0.01, stop_loss: float = None, take_profit: float = None):
        """
        Submits a market trade (MetaAPI or Demo Simulator)
        """
        if not account_id or not token:
            return {"error": "Missing MetaAPI Account ID or Token"}
            
        # Demo Simulator Check
        if "DEMO" in account_id.upper() or "DEMO" in token.upper():
            db = load_sim_db()
            
            # Fetch active market spot price
            open_price = 1.0
            if symbol in LIVE_CACHE:
                open_price = LIVE_CACHE[symbol].get("price", 1.0)
            elif f"{symbol}/USD" in LIVE_CACHE:
                open_price = LIVE_CACHE[f"{symbol}/USD"].get("price", 1.0)
                
            new_pos = {
                "id": str(int(time.time() * 1000)),
                "symbol": symbol,
                "type": action.upper(),
                "volume": float(volume),
                "openPrice": open_price,
                "currentPrice": open_price,
                "stopLoss": stop_loss,
                "takeProfit": take_profit,
                "profit": 0.0,
                "time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            db["positions"].append(new_pos)
            save_sim_db(db)
            return {"success": True, "data": {"positionId": new_pos["id"]}}
            
        # MetaAPI Live connection
        url = f"https://mt-client-api.new-york.metaapi.cloud/users/current/accounts/{account_id}/trade"
        headers = {"auth-token": token, "Content-Type": "application/json"}
        
        clean_symbol = symbol.replace("/", "").replace("_", "")
        
        payload = {
            "symbol": clean_symbol,
            "actionType": "ORDER_TYPE_BUY" if action.upper() == "BUY" else "ORDER_TYPE_SELL",
            "volume": float(volume),
        }
        
        if stop_loss:
            payload["stopLoss"] = float(stop_loss)
        if take_profit:
            payload["takeProfit"] = float(take_profit)
            
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)
            if res.status_code in [200, 201]:
                return {"success": True, "data": res.json()}
            else:
                logger.error(f"MetaAPI order execution failed: {res.text}")
                return {"success": False, "error": res.json().get("message", res.text)}
        except Exception as e:
            logger.error(f"Exception executing MetaAPI trade: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def close_trade_position(account_id: str, token: str, position_id: str):
        """
        Closes a specific active position (MetaAPI or Demo Simulator)
        """
        if not account_id or not token or not position_id:
            return {"error": "Missing credentials or position ID"}
            
        # Demo Simulator Check
        if "DEMO" in account_id.upper() or "DEMO" in token.upper():
            db = load_sim_db()
            positions = db.get("positions", [])
            target = None
            for p in positions:
                if p["id"] == position_id:
                    target = p
                    break
                    
            if not target:
                return {"success": False, "error": "Simulated position not found"}
                
            # Calculate closed trade PnL
            sym = target.get("symbol")
            current_price = target.get("openPrice", 1.0)
            if sym in LIVE_CACHE:
                current_price = LIVE_CACHE[sym].get("price", current_price)
            elif f"{sym}/USD" in LIVE_CACHE:
                current_price = LIVE_CACHE[f"{sym}/USD"].get("price", current_price)
                
            coef = 1000.0 if "XAU" in sym or "/" in sym else 10.0
            if target["type"] == "BUY":
                profit = (current_price - target["openPrice"]) * target["volume"] * coef
            else:
                profit = (target["openPrice"] - current_price) * target["volume"] * coef
                
            db["balance"] = db["balance"] + profit
            db["positions"] = [p for p in positions if p["id"] != position_id]
            save_sim_db(db)
            return {"success": True}
            
        # MetaAPI Live connection
        url = f"https://mt-client-api.new-york.metaapi.cloud/users/current/accounts/{account_id}/trade"
        headers = {"auth-token": token, "Content-Type": "application/json"}
        
        payload = {
            "actionType": "ORDER_TYPE_CLOSE_BY_POSITION",
            "positionId": position_id
        }
        
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)
            if res.status_code in [200, 201]:
                return {"success": True, "data": res.json()}
            else:
                return {"success": False, "error": res.json().get("message", res.text)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def provision_mt5_account(token: str, login: str, password: str, server: str, name: str = "QuantView Terminal"):
        """
        Programmatically registers a raw MT5 broker account on MetaAPI cloud provisioning.
        """
        url = "https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai/users/current/accounts"
        headers = {
            "auth-token": token,
            "Content-Type": "application/json"
        }
        payload = {
            "name": name,
            "type": "cloud",
            "login": str(login),
            "password": password,
            "server": server,
            "platform": "mt5",
            "magic": 123456,
            "quoteStreamingIntervalInSeconds": 2.5
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=60, verify=False)
            if res.status_code in [200, 201, 202]:
                data = res.json()
                return {"success": True, "accountId": str(data.get("id"))}
            else:
                try:
                    data = res.json()
                    err_msg = data.get("message", res.text)
                    if "details" in data and isinstance(data["details"], list):
                        details_list = []
                        for item in data["details"]:
                            param = item.get("parameter", "")
                            msg = item.get("message", "")
                            if param and msg:
                                details_list.append(f"{param}: {msg}")
                        if details_list:
                            err_msg = f"{err_msg} ({', '.join(details_list)})"
                except Exception:
                    err_msg = res.text
                return {"success": False, "error": err_msg}
        except Exception as e:
            return {"success": False, "error": str(e)}
