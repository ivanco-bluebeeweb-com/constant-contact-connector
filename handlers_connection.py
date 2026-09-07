"""Connection management for Constant Contact Connector."""
from __future__ import annotations
import uuid, json
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from schemas import NoParams, ConnectParams, ConnectionIdParams, ConnectionRecord, ConnectionList, DeleteResult
from constant_contact_connector_client import ConstantContactClient

_SECRET = "constant_contact_connector_connections"

def _mask(v: str) -> str:
    return v[:4] + "…" + v[-4:] if len(v) > 8 else "***"

async def _load_conns(ctx) -> list[dict]:
    raw = await ctx.secrets.get(_SECRET)
    if not raw: return []
    try: data = json.loads(raw)
    except: return []
    return data if isinstance(data, list) else []

async def _save_conns(ctx, conns: list[dict]) -> None:
    await ctx.secrets.set(_SECRET, json.dumps(conns))

async def resolve_client(ctx, connection_id: str = "") -> ConstantContactClient:
    conns = await _load_conns(ctx)
    if not conns:
        raise ValueError("No Constant Contact connections configured. Use connect_constant_contact_connector first.")
    conn = conns[0]
    if connection_id:
        for c in conns:
            if c["id"] == connection_id:
                conn = c
                break
    return ConstantContactClient(access_token=conn["access_token"], base_url=conn.get("base_url", ""))

@chat.function("connect_constant_contact_connector", "Connect Constant Contact account via credentials.", action_type="write", chain_callable=True, event="constant-contact-connector.connect_constant_contact_connector", effects=["create:connection"], data_model=ConnectionRecord)
async def connect_constant_contact_connector(ctx, params: ConnectParams) -> ActionResult:
    client = ConstantContactClient(access_token=params.access_token, base_url=params.base_url)
    res = await client.verify_auth()
    if res.get("status") == "error":
        return ActionResult.error(f"Failed to connect to Constant Contact: {res.get('error')}")
    conns = await _load_conns(ctx)
    cid = f"conn_{uuid.uuid4().hex[:8]}"
    rec = {
        "id": cid,
        "label": params.label or "Primary Constant Contact",
        "access_token": params.access_token,
        "masked_key": _mask(params.access_token),
        "base_url": params.base_url,
        "is_active": True
    }
    for c in conns: c["is_active"] = False
    conns.append(rec)
    await _save_conns(ctx, conns)
    return ActionResult.success(rec, summary=f"Connected Constant Contact ({rec['label']}).")

@chat.function("list_connections", "List configured Constant Contact connections.", action_type="read", chain_callable=True, event="constant-contact-connector.list_connections", effects=["read:connections"], data_model=ConnectionList)
async def list_connections(ctx, params: NoParams) -> ActionResult:
    conns = await _load_conns(ctx)
    items = [{
        "id": c["id"],
        "label": c["label"],
        "masked_key": c.get("masked_key", "***"),
        "base_url": c.get("base_url", "https://api.cc.email/v3"),
        "is_active": c.get("is_active", False)
    } for c in conns]
    return ActionResult.success({"connections": items, "total": len(items)}, summary=f"Found {len(items)} connection(s).")

@chat.function("disconnect_constant_contact_connector", "Disconnect Constant Contact account and delete stored credentials.", action_type="destructive", chain_callable=True, event="constant-contact-connector.disconnect_constant_contact_connector", effects=["delete:connection"], data_model=DeleteResult)
async def disconnect_constant_contact_connector(ctx, params: ConnectionIdParams) -> ActionResult:
    conns = await _load_conns(ctx)
    if not conns:
        return ActionResult.error("No connections to disconnect.")
    if params.connection_id:
        conns = [c for c in conns if c["id"] != params.connection_id]
    else:
        conns.clear()
    await _save_conns(ctx, conns)
    return ActionResult.success({"success": True, "message": "Disconnected successfully."}, summary="Disconnected Constant Contact connection.")
