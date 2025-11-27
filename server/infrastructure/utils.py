import json
from datetime import datetime

def sanitize_name(name):
    return "".join(c for c in name.strip() if c.isalnum() or c in "-_ ").strip()

def timestamp_now():
    return datetime.now().strftime("%H:%M:%S")

async def broadcast_json(users, obj):
    msg = json.dumps(obj)
    for u in users:
        try:
            await u.websocket.send(msg)
        except:
            pass
