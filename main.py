from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import ChatRequest, ChatResponse
from llm_service import process_chat_request
import os

app = FastAPI(title="Inventory Chat API")

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    result = await process_chat_request(request.message, request.context)
    
    return ChatResponse(
        natural_language_answer=result["natural_language_answer"],
        sql_query=result["sql_query"],
        token_usage=result["token_usage"],
        latency_ms=result["latency_ms"],
        provider=result["provider"],
        model=result["model"],
        status=result["status"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
