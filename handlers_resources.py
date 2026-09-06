"""Resource handlers for Constant Contact Connector."""
from __future__ import annotations
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from schemas import (
    ListContactParams, GetContactParams,
    ContactRecord, ContactList, AuditHealthReport, ConnectionIdParams
)
from handlers_connection import resolve_client

@chat.function("list_contacts", "List contacts in Constant Contact.", action_type="read", chain_callable=True, event="constant-contact-connector.list_contacts", effects=["read:contacts"], data_model=ContactList)
async def list_contacts(params: ListContactParams, ctx) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        raw_items = await client.list_contacts(limit=params.limit)
        items = []
        for r in raw_items:
            rid = str(r.get("id") or r.get("key") or r.get("uuid") or "unknown")
            rname = r.get("name") or r.get("title") or r.get("label") or rid
            items.append({"id": rid, "name": rname, "status": r.get("status"), "created_at": r.get("createdAt") or r.get("created_at"), "raw": r})
        return ActionResult.ok({"contacts": items, "total": len(items)}, summary=f"Found {len(items)} contacts.")
    except Exception as e:
        return ActionResult.error(f"Error listing contacts: {e}")

@chat.function("get_contact", "Get details of one Contact in Constant Contact.", action_type="read", chain_callable=True, event="constant-contact-connector.get_contact", effects=["read:contact"], data_model=ContactRecord)
async def get_contact(params: GetContactParams, ctx) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        r = await client.get_contact(params.contact_id)
        rid = str(r.get("id") or params.contact_id)
        rname = r.get("name") or r.get("title") or rid
        return ActionResult.ok({"id": rid, "name": rname, "status": r.get("status"), "created_at": r.get("createdAt") or r.get("created_at"), "raw": r}, summary=f"Retrieved Contact {rid}.")
    except Exception as e:
        return ActionResult.error(f"Error retrieving Contact: {e}")

@chat.function("audit_contact_health", "Audit health of Constant Contact contacts and connectivity.", action_type="read", chain_callable=True, event="constant-contact-connector.audit_contact_health", effects=["read:audit"], data_model=AuditHealthReport)
async def audit_contact_health(params: ConnectionIdParams, ctx) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        items = await client.list_contacts(limit=50)
        return ActionResult.ok({
            "healthy": True,
            "total_contacts": len(items),
            "details": {"sample_count": len(items)},
            "summary": f"Constant Contact healthy. Sampled {len(items)} contacts."
        }, summary=f"Constant Contact health check passed with {len(items)} contacts.")
    except Exception as e:
        return ActionResult.error(f"Error auditing Constant Contact health: {e}")
