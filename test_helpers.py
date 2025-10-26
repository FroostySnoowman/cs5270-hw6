import json
from helpers import owner_slug, s3_key_for, build_widget_for_s3, build_ddb_item, parse_request

def test_owner_slug_basic():
    assert owner_slug("Jane Doe") == "jane-doe"
    assert owner_slug("  A B  ") == "a-b"

def test_s3_key_for():
    k = s3_key_for("Jane Doe", "w123")
    assert k == "widgets/jane-doe/w123"
    k2 = s3_key_for("X Y", "IDZ", prefix="widgets/")
    assert k2 == "widgets/x-y/IDZ"

def test_parse_and_build_s3():
    raw = json.dumps({
        "type": "create",
        "requestId": "r1",
        "widgetId": "w1",
        "owner": "Jane Doe",
        "label": "L",
        "description": "D",
        "otherAttributes": [{"name": "color", "value": "blue"}],
    })
    req = parse_request(raw)
    w = build_widget_for_s3(req)
    assert w["widgetId"] == "w1"
    assert w["owner"] == "Jane Doe"
    assert w["label"] == "L"
    assert w["description"] == "D"
    assert w["otherAttributes"][0]["name"] == "color"
    assert w["otherAttributes"][0]["value"] == "blue"

def test_build_ddb_item_flatten():
    req = {
        "widgetId": "w9",
        "owner": "Ann Lee",
        "label": "Z",
        "description": None,
        "otherAttributes": [{"name": "a", "value": "1"}, {"name": "b", "value": "2"}],
    }
    item = build_ddb_item(req)
    assert item["widgetId"] == "w9"
    assert item["owner"] == "Ann Lee"
    assert item["label"] == "Z"
    assert item["a"] == "1"
    assert item["b"] == "2"
    assert "description" not in item