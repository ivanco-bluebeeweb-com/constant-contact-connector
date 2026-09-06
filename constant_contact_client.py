"""Official Constant Contact REST API v3 client aligned with api.cc.email/v3."""
from __future__ import annotations
import httpx
from typing import Any, Optional

DEFAULT_CC_BASE = "https://api.cc.email/v3"

class ConstantContactClient:
    def __init__(self, api_key: str, base_url: str = ""):
        self.api_key = api_key.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_CC_BASE).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Imperal-ConstantContact/0.1.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    def _sanitize_msg(self, msg: str) -> str:
        if not msg:
            return ""
        if self.api_key and len(self.api_key) > 6:
            msg = msg.replace(self.api_key, self.api_key[:3] + "..." + self.api_key[-3:])
        return msg

    def _classify_error(self, resp: httpx.Response, action_name: str) -> dict[str, Any]:
        status = resp.status_code
        err_msg = ""
        try:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and "error_message" in data[0]:
                err_msg = "; ".join(e.get("error_message", "") for e in data)
            elif isinstance(data, dict):
                if "error_message" in data:
                    err_msg = data["error_message"]
                elif "message" in data:
                    err_msg = data["message"]
                elif "error" in data:
                    err_msg = str(data["error"])
        except Exception:
            err_msg = resp.text[:200]
        err_msg = self._sanitize_msg(err_msg)

        if status == 429:
            retry_after = resp.headers.get("Retry-After", "60")
            return {
                "status": "error",
                "code": "RATE_LIMITED",
                "message": f"Constant Contact API rate limit exceeded in {action_name}. Retry after {retry_after}s.",
                "retry_after": int(retry_after) if retry_after.isdigit() else 60
            }
        elif status == 401:
            return {
                "status": "error",
                "code": "UNAUTHORIZED",
                "message": f"Constant Contact authentication failed in {action_name}: {err_msg or 'Invalid OAuth2/Bearer token'}"
            }
        elif status == 403:
            return {
                "status": "error",
                "code": "FORBIDDEN",
                "message": f"Constant Contact permission denied in {action_name}: {err_msg or 'Insufficient scopes/permissions'}"
            }
        return {
            "status": "error",
            "code": f"HTTP_{status}",
            "message": f"Constant Contact API error in {action_name} ({status}): {err_msg}"
        }

    async def verify(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            try:
                resp = await c.get(f"{self.base_url}/account/summary", headers=self.headers)
                if resp.status_code == 200:
                    return {"status": "ok", "data": resp.json()}
                return self._classify_error(resp, "verify")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_subscribers(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": min(limit, 500)}
        if cursor: params["cursor"] = cursor
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            try:
                resp = await c.get(f"{self.base_url}/contacts", headers=self.headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    return {"items": data.get("contacts", []), "total": data.get("contacts_count", len(data.get("contacts", []))), "next_cursor": data.get("_links", {}).get("next", {}).get("href", "")}
                return self._classify_error(resp, "list_subscribers")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_subscriber(self, subscriber_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            try:
                resp = await c.get(f"{self.base_url}/contacts/{subscriber_id}", headers=self.headers)
                if resp.status_code == 200: return resp.json()
                return self._classify_error(resp, "get_subscriber")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_campaigns(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": min(limit, 500)}
        if cursor: params["cursor"] = cursor
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            try:
                resp = await c.get(f"{self.base_url}/emails", headers=self.headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    return {"items": data.get("campaigns", []), "total": len(data.get("campaigns", []))}
                return self._classify_error(resp, "list_campaigns")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_lists(self, limit: int = 50) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": min(limit, 500)}
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            try:
                resp = await c.get(f"{self.base_url}/contact_lists", headers=self.headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    return {"items": data.get("lists", []), "total": len(data.get("lists", []))}
                return self._classify_error(resp, "list_lists")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_segments(self, limit: int = 50) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": min(limit, 500)}
        async with httpx.AsyncClient(timeout=self.timeout) as c:
            try:
                resp = await c.get(f"{self.base_url}/segments", headers=self.headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    return {"items": data.get("segments", []), "total": len(data.get("segments", []))}
                return self._classify_error(resp, "list_segments")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}
