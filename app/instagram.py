import os
import httpx

GRAPH = "https://graph.facebook.com/v24.0"

def _token():
    return os.environ.get("INSTAGRAM_ACCESS_TOKEN")

async def send_instagram_text(recipient_id: str, text: str):
    token = _token()
    if not token:
        raise RuntimeError("INSTAGRAM_ACCESS_TOKEN is missing")
    # Instagram Messaging API endpoint for professional accounts.
    url = f"{GRAPH}/{os.environ['INSTAGRAM_USER_ID']}/messages"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, params={"access_token": token}, json=payload)
        r.raise_for_status()
        return r.json()
