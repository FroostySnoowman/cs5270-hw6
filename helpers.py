import json
from datetime import datetime, timezone

def owner_slug(owner: str) -> str:
    return owner.strip().lower().replace(" ", "-")

def s3_key_for(owner: str, widget_id: str, prefix: str = "widgets/") -> str:
    p = prefix.rstrip("/") + "/"
    return f"{p}{owner_slug(owner)}/{widget_id}"

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_request(raw: str) -> dict:
    d = json.loads(raw)
    # keep fields as in the request schema
    return {
        "type": d.get("type"),
        "requestId": d.get("requestId"),
        "widgetId": d.get("widgetId"),
        "owner": d.get("owner"),
        "label": d.get("label"),
        "description": d.get("description"),
        "otherAttributes": d.get("otherAttributes", []),
    }

def build_widget_for_s3(req: dict) -> dict:
    w = {
        "widgetId": req["widgetId"],
        "owner": req["owner"],
    }
    if req.get("label") is not None:
        w["label"] = req["label"]
    if req.get("description") is not None:
        w["description"] = req["description"]
    oa = req.get("otherAttributes") or []
    if oa:
        w["otherAttributes"] = [{"name": x["name"], "value": x["value"]} for x in oa]
    return w

def build_ddb_item(req: dict) -> dict:
    item = {
        "widgetId": req["widgetId"],
        "owner": req["owner"],
    }
    if req.get("label") is not None:
        item["label"] = req["label"]
    if req.get("description") is not None:
        item["description"] = req["description"]
    for x in req.get("otherAttributes") or []:
        item[x["name"]] = x["value"]
    item["createdAt"] = now_iso()
    return item