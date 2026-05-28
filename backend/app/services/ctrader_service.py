"""
cTrader Open API Service
========================
Uses cTrader's OAuth2 + REST HTTP endpoints to:
  - Exchange auth code for access token
  - Fetch account balance/equity/margin
  - Get open positions
  - Place market orders (BUY/SELL)
  - Close positions

cTrader Open API docs: https://help.ctrader.com/open-api/
OAuth endpoint:        https://id.ctrader.com/
Trading REST endpoint: https://api.spotware.com/  (v2 HTTP)

The user needs to:
  1. Register a free app at https://openapi.ctrader.com/apps
     → gets client_id + client_secret
  2. Complete OAuth2 login flow to get access_token
  3. Paste access_token + account_id into QuantView
"""

import requests
import json
import os
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

CTRADER_AUTH_BASE   = "https://connect.spotware.com"
CTRADER_API_BASE    = "https://api.spotware.com"


class CTraderService:

    # ──────────────────────────────────────────────
    # OAuth2 helpers
    # ──────────────────────────────────────────────

    @staticmethod
    def build_auth_url(client_id: str, redirect_uri: str) -> str:
        """
        Returns the URL the user must visit in their browser to authorise the app.
        Scope 'trading' allows placing and closing orders.
        """
        return (
            f"{CTRADER_AUTH_BASE}/apps/auth"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=trading"
            f"&response_type=code"
        )

    @staticmethod
    def exchange_code_for_token(
        client_id: str,
        client_secret: str,
        code: str,
        redirect_uri: str
    ) -> dict:
        """
        Exchanges an authorization code for an access_token + refresh_token.
        POST https://id.ctrader.com/connect/token
        """
        url = f"{CTRADER_AUTH_BASE}/apps/token"
        data = {
            "grant_type":    "authorization_code",
            "code":          code,
            "redirect_uri":  redirect_uri,
            "client_id":     client_id,
            "client_secret": client_secret,
        }
        try:
            res = requests.post(url, data=data, timeout=15, verify=False)
            if res.status_code == 200:
                return {"success": True, **res.json()}
            else:
                return {"success": False, "error": res.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def refresh_access_token(
        client_id: str,
        client_secret: str,
        refresh_token: str
    ) -> dict:
        """
        Uses refresh_token to get a new access_token without user interaction.
        """
        url = f"{CTRADER_AUTH_BASE}/apps/token"
        data = {
            "grant_type":    "refresh_token",
            "refresh_token": refresh_token,
            "client_id":     client_id,
            "client_secret": client_secret,
        }
        try:
            res = requests.post(url, data=data, timeout=15, verify=False)
            if res.status_code == 200:
                return {"success": True, **res.json()}
            else:
                return {"success": False, "error": res.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ──────────────────────────────────────────────
    # Account information
    # ──────────────────────────────────────────────

    @staticmethod
    def get_accounts(access_token: str) -> dict:
        """
        Lists all cTrader accounts linked to this access token.
        GET /v2/webserv/accounts
        Returns list of {accountId, balance, currency, brokerName, ...}
        """
        url = f"{CTRADER_API_BASE}/v2/webserv/accounts"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            res = requests.get(url, headers=headers, timeout=15, verify=False)
            if res.status_code == 200:
                data = res.json()
                accounts = data.get("data", data) if isinstance(data, dict) else data
                return {"success": True, "accounts": accounts}
            else:
                return {"success": False, "error": res.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_account_summary(access_token: str, account_id: str) -> dict:
        """
        Fetches live account balance, equity, margin for a specific account.
        GET /v2/webserv/accounts/{account_id}
        """
        url = f"{CTRADER_API_BASE}/v2/webserv/accounts/{account_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            res = requests.get(url, headers=headers, timeout=15, verify=False)
            if res.status_code == 200:
                data = res.json()
                # cTrader returns monetary values in cents (divide by 100)
                divisor = 100.0
                acc = data.get("data", data) if isinstance(data, dict) else data
                return {
                    "balance":     acc.get("balance",     0) / divisor,
                    "equity":      acc.get("equity",      0) / divisor,
                    "margin":      acc.get("usedMargin",  0) / divisor,
                    "freeMargin":  acc.get("freeMargin",  0) / divisor,
                    "currency":    acc.get("depositCurrency", "USD"),
                    "leverage":    acc.get("leverage",    1),
                    "broker":      acc.get("brokerName",  "cTrader Broker"),
                    "name":        acc.get("name",        f"Account {account_id}"),
                }
            else:
                return {"error": f"cTrader API error {res.status_code}: {res.text[:200]}"}
        except Exception as e:
            return {"error": str(e)}

    # ──────────────────────────────────────────────
    # Positions
    # ──────────────────────────────────────────────

    @staticmethod
    def get_positions(access_token: str, account_id: str) -> list:
        """
        Fetches all open positions for the account.
        GET /v2/webserv/accounts/{account_id}/positions
        """
        url = f"{CTRADER_API_BASE}/v2/webserv/accounts/{account_id}/positions"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            res = requests.get(url, headers=headers, timeout=15, verify=False)
            if res.status_code == 200:
                data = res.json()
                raw = data.get("data", data) if isinstance(data, dict) else data
                positions = []
                for p in (raw if isinstance(raw, list) else []):
                    divisor = 100.0
                    positions.append({
                        "id":           str(p.get("positionId", p.get("id", ""))),
                        "symbol":       p.get("symbolName", p.get("symbol", "")),
                        "type":         "BUY" if p.get("tradeType") == "BUY" else "SELL",
                        "volume":       p.get("volume", 0) / 100,  # centilots → lots
                        "openPrice":    p.get("entryPrice", 0),
                        "currentPrice": p.get("currentPrice", 0),
                        "stopLoss":     p.get("stopLoss"),
                        "takeProfit":   p.get("takeProfit"),
                        "profit":       p.get("netProfit", p.get("grossProfit", 0)) / divisor,
                        "time":         p.get("tradeData", {}).get("openTime", ""),
                    })
                return positions
            else:
                logger.error(f"cTrader positions error {res.status_code}: {res.text}")
                return []
        except Exception as e:
            logger.error(f"cTrader get_positions exception: {e}")
            return []

    # ──────────────────────────────────────────────
    # Trade execution
    # ──────────────────────────────────────────────

    @staticmethod
    def place_order(
        access_token: str,
        account_id: str,
        symbol: str,
        trade_type: str,      # "BUY" or "SELL"
        volume_lots: float,
        stop_loss: float = None,
        take_profit: float = None
    ) -> dict:
        """
        Places a market order via cTrader REST API.
        POST /v2/webserv/accounts/{account_id}/orders
        volume is in centilots (lots * 100).
        """
        url = f"{CTRADER_API_BASE}/v2/webserv/accounts/{account_id}/orders"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/json"
        }
        payload = {
            "symbolName": symbol.upper().replace("/", "").replace("_", ""),
            "orderType":  "MARKET",
            "tradeType":  trade_type.upper(),
            "volume":     int(volume_lots * 100),   # centilots
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
                try:
                    err = res.json()
                    msg = err.get("description", err.get("message", res.text))
                except Exception:
                    msg = res.text
                return {"success": False, "error": msg}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def close_position(
        access_token: str,
        account_id: str,
        position_id: str,
        volume_lots: float = None
    ) -> dict:
        """
        Closes an open position.
        DELETE /v2/webserv/accounts/{account_id}/positions/{position_id}
        """
        url = f"{CTRADER_API_BASE}/v2/webserv/accounts/{account_id}/positions/{position_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {}
        if volume_lots:
            params["volume"] = int(volume_lots * 100)
        try:
            res = requests.delete(url, headers=headers, params=params, timeout=30, verify=False)
            if res.status_code in [200, 201, 204]:
                return {"success": True}
            else:
                try:
                    err = res.json()
                    msg = err.get("description", err.get("message", res.text))
                except Exception:
                    msg = res.text
                return {"success": False, "error": msg}
        except Exception as e:
            return {"success": False, "error": str(e)}
