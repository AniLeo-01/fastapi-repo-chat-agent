from fastapi import APIRouter, WebSocket
from app.schemas import ChatRequest
from app.services.orchestrator import call_orchestrator

router = APIRouter()

@router.post("/api/chat")
async def chat(req: ChatRequest):
    return await call_orchestrator(req.message, req.session_id)

@router.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    await ws.accept()
    while True:
        msg = await ws.receive_text()
        result = await call_orchestrator(msg, None)
        await ws.send_text(result["response"])
