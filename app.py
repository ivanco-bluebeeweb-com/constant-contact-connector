"""Extension declaration, capabilities, health check for Constant Contact Connector."""
from __future__ import annotations
import json
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "constant-contact-connector",
    version="0.1.0",
    display_name="Constant Contact",
    icon="icon.svg",
    capabilities=["constant_contact:manage"],
    description="Official Imperal connector for Constant Contact (C30. Email Marketing & Newsletter). Manage operations securely."
)

chat = ChatExtension(ext)

@ext.health_check
async def health_check(ctx) -> dict:
    raw = await ctx.secrets.get("constant_contact_connections")
    try:
        count = len(json.loads(raw)) if raw else 0
    except Exception:
        count = 0
    return {
        "healthy": True,
        "detail": f"{count} Constant Contact connection(s) configured." if count else "Not connected yet."
    }
