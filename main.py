import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TYPESAFE_API_KEY = os.getenv("TYPESAFE_API_KEY", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Jev Bot Relay is running!"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    
    # Discordへの通知処理
    msg = f"【TFMA Signal Alert】\n銘柄: {payload.get('ticker')}\n時間足: {payload.get('timeframe')}\n終値: {payload.get('close')}"
    
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})
        
    return {"status": "success"}
