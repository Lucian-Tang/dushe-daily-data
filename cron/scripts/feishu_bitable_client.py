#!/usr/bin/env python3
"""
feishu_bitable_client.py - Simple Feishu Bitable API helper for record creation.
Used by the opportunity signals collector scripts.
"""
import json
import urllib.request
import urllib.error
import os

# Token is loaded from environment or config
FEISHU_APP_TOKEN = os.environ.get("FEISHU_APP_TOKEN", "")
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

def create_record(app_token, table_id, fields):
    """
    Create a single record in a Feishu Bitable table.
    
    Args:
        app_token: Bitable app token
        table_id: Table ID within the bitable
        fields: dict of field_name -> value
    
    Returns:
        record_id on success, None on failure
    """
    import time
    url = f"{FEISHU_API_BASE}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    
    # Build field values - handle special types
    formatted_fields = {}
    for key, value in fields.items():
        if isinstance(value, dict) and "text" in value and "link" in value:
            # URL type: {"text": "display", "link": "https://..."}
            formatted_fields[key] = value
        elif isinstance(value, list):
            # MultiSelect: [{"text": "AI", "value": "ai_option"}, ...] or plain list
            formatted_fields[key] = value
        elif isinstance(value, str):
            formatted_fields[key] = value
        elif isinstance(value, (int, float)):
            formatted_fields[key] = value
        elif value is None:
            pass
    
    payload = {"fields": formatted_fields}
    
    # Get access token from env
    access_token = os.environ.get("FEISHU_ACCESS_TOKEN", "")
    if not access_token:
        # Try to use tenant access token from file
        token_file = "/root/.openclaw/workspace/agents/engineering/feishu_token.json"
        if os.path.exists(token_file):
            with open(token_file) as f:
                token_data = json.load(f)
                access_token = token_data.get("tenant_access_token", "")
    
    if not access_token:
        print(f"WARNING: No FEISHU_ACCESS_TOKEN available, skipping write")
        return None
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            resp = json.loads(r.read().decode("utf-8"))
            if resp.get("code") == 0:
                return resp.get("data", {}).get("record", {}).get("record_id")
            else:
                print(f"Feishu API error: code={resp.get('code')}, msg={resp.get('msg')}")
                return None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        print(f"HTTPError {e.code}: {body[:200]}")
        return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 4:
        app_token = sys.argv[1]
        table_id = sys.argv[2]
        fields = json.loads(sys.argv[3])
        result = create_record(app_token, table_id, fields)
        print(result if result else "FAILED")
    else:
        print("Usage: python3 feishu_bitable_client.py <app_token> <table_id> <fields_json>")