"""HTTP client for Constant Contact API."""
from __future__ import annotations
import httpx
from typing import Any, Optional

DEFAULT_BASE = "https://api.cc.email/v3"

class ConstantContactClient:
    def __init__(self, access_token: str, base_url: str = ""):
        self.access_token = access_token.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_BASE).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}" if "Authorization" == "Authorization" else self.access_token,
            "Content-Type": "application/json",
            "User-Agent": "Imperal-ConstantContact-Connector/1.0.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def verify_auth(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/contacts?limit=1", headers=self.headers)
                if resp.status_code in (200, 201, 204):
                    return {"status": "ok", "data": resp.json() if resp.content else {}}
                return {"status": "error", "error": f"HTTP {resp.status_code}: {resp.text}"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    async def list_contacts(self, limit: int = 20) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/contacts", headers=self.headers, params={"limit": limit})
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list): return data
                for k in ["data", "contacts", "items", "results"]:
                    if k in data and isinstance(data[k], list): return data[k]
                return []
            return []

    async def get_contact(self, contact_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/contacts/{contact_id}", headers=self.headers)
            if resp.status_code == 200:
                return resp.json()
            raise ValueError(f"HTTP {resp.status_code}: {resp.text}")
