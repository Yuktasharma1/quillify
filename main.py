from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests, json, os
import time
import dotenv
import openai

from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    content: str

api_calls = {}

@app.get("/")
def hello():
    return "Hello, World!"


@app.post("/chat")
async def chat(request: Request, chat_request: ChatRequest):
    client_ip = request.client.host
    current_time = time.time()

    if client_ip not in api_calls:
        api_calls[client_ip] = [current_time]
    else:
        api_calls[client_ip].append(current_time)
        api_calls[client_ip] = [t for t in api_calls[client_ip] if t > current_time - 60]

    if len(api_calls[client_ip]) > 5:
        raise HTTPException(status_code=429, detail="Too many requests")

    prompt = chat_request.content

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """You're a Linkedin Copywriter""",
            },
            {
                "role": "user",
                "content": f"{prompt}",
            },
        ],
        temperature=0.2,
    )

    return response["choices"][0]["message"]["content"]
