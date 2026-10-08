import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from app.telegram import process_update
from app.instagram import send_instagram_text
from app.store import products, create_order

app = FastAPI(title="Instagram Digital Store")

@app.get("/")
def root():
    return {"ok": True, "service": "Instagram Digital Store"}

@app.get("/api/instagram/webhook")
def verify_instagram(request: Request):
    q=request.query_params
    if q.get("hub.verify_token") != os.environ.get("INSTAGRAM_VERIFY_TOKEN"):
        raise HTTPException(403, "Invalid verify token")
    return PlainTextResponse(q.get("hub.challenge", ""))

@app.post("/api/instagram/webhook")
async def instagram_webhook(request: Request):
    body=await request.json()
    # Meta sends entry -> messaging. We only auto-reply to actual inbound text.
    for entry in body.get("entry", []):
        for event in entry.get("messaging", []):
            sender=(event.get("sender") or {}).get("id")
            msg=event.get("message") or {}
            text=(msg.get("text") or "").strip()
            if not sender or not text: continue
            if text.lower() in {"hi","hello","start","products","shop"}:
                ps=products(True)[:10]
                if not ps:
                    reply="👋 Welcome! Our store is currently updating."
                else:
                    reply="🛍️ Available products:\n\n" + "\n".join([f"• {p['name']} — ₹{p['price']}\n  Buy: {os.environ.get('PUBLIC_BASE_URL','')}/buy/{p['_id']}" for p in ps])
                await send_instagram_text(sender, reply)
            elif text.lower().startswith("buy "):
                pid=text.split(maxsplit=1)[1]
                oid=create_order(sender, pid)
                await send_instagram_text(sender, "❌ Product not found." if not oid else f"🧾 Order created: {oid}\nPlease complete payment using the payment link provided by the store.")
    return {"ok": True}

@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    await process_update(await request.json())
    return {"ok": True}
