from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime
import json
import httpx
import asyncio
from dotenv import load_dotenv
import os
from fastapi import HTTPException
import sys
import re
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

load_dotenv()

key = os.getenv("OPENROUTER_KEY")

app = FastAPI(title="Note Creating Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],       # needed for POST
    allow_headers=["*"],       # needed for JSON
)

class Vars(BaseModel):
    id: str
    lang: Literal["fr", "en"]


system_prompt = open("system_prompt.txt", "r").read()

@app.get("/")
def read_root():
    return {"message": "API alive"}


@app.post("/generate_summary")
async def generate_transcript(vars: Vars):

    raw = vars.id 
    m = re.search(r"v=([A-Za-z0-9_-]{11})", raw)
    vid = m.group(1) if m else raw
    logger.info(f"Video ID extract as {vid}")

    try:
        
        ytt_api = YouTubeTranscriptApi()

        transcript = await asyncio.to_thread(
            ytt_api.fetch,
            vid,
            languages=[vars.lang, "en", "en-US", "a.en", "fr", "fr-FR", "a.fr"])

        transcript = "\n".join(item.text for item in transcript)


    except Exception as e:
        logger.exception(f"Transcript fetch failed, error is reported as {e}")
        return {"error": "Could not be generated, verify video ID and language are correct."}


    async with httpx.AsyncClient(timeout=10) as client:

        try:
    
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
            "Authorization": f"Bearer {key}",
        
            },
            json ={
                "model": "openai/gpt-4o", 
                "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"{transcript}"
                }
                ]
            }
                )

            response_data = response.json()
            response_data = response_data["choices"][0]["message"]["content"]

            return {"summary":response_data}

        except Exception as e:
            logger.exception(f"Summary generation failed, error is reported as {e}")
            return {"error": "Summary could not be generated, verify video ID and language are correct."}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

