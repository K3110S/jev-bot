import os
import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from pydantic_ai import Agent

app = FastAPI()

TYPESAFE_API_KEY = os.getenv("TYPESAFE_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

class TFMAAssessment(BaseModel):
    tfma_score: int = Field(description="TFMAエントリー条件としての質を0〜100でスコア化")
    is_valid_setup: bool = Field(description="騙しリスクが低く、エントリー推奨ならTrue")

agent = Agent('typesafe:jev-latest', output_type=TFMAAssessment)

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    
    state_prompt = f"""
    通貨ペア: {data.get('ticker')} ({data.get('timeframe')}分足)
    終値: {data.get('close')}
    20SMA: {data.get('ma20')}, 80SMA: {data.get('ma80')}
    MACDヒストグラム: {data.get('macd_hist')}
    ヒドゥンダイバージェンス発生: {data.get('hidden_div')}
    
    上記状態から、TFMA（Trend Following Moving Average）の戦略に基づいて、
    現在の押し目・戻りの綺麗さと勝率の期待値を評価してください。
    """
    
    result = agent.run_sync(state_prompt)
    assessment = result.output
    
    color = 0x00FF00 if assessment.is_valid_setup else 0xFF0000
    discord_payload = {
        "embeds": [{
            "title": f"📈 TFMA Signal: {data.get('ticker')} ({data.get('timeframe')}分足)",
            "color": color,
            "fields": [
                {"name": "Jev スコア", "value": f"**{assessment.tfma_score} / 100**", "inline": True},
                {"name": "エントリー推奨", "value": "✅ 推奨" if assessment.is_valid_setup else "❌ 見送り", "inline": True},
                {"name": "現在価格", "value": str(data.get('close')), "inline": False}
            ]
        }]
    }
    
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
        
    return {"status": "success", "score": assessment.tfma_score}
