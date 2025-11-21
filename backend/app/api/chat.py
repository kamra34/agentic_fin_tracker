from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, AsyncGenerator
from pydantic import BaseModel
import json
import asyncio
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.chat_data_service import ChatDataService
from app.services.conversation_manager import conversation_manager
from app.agents.orchestrator import OrchestratorAgent

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    """Request for chat interaction"""
    message: str


class ChatResponse(BaseModel):
    """Response from chat interaction"""
    response: str
    agents_consulted: List[str]
    iterations: int


@router.post("/stream")
async def stream_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stream chat response with real-time agent updates using Server-Sent Events.
    Returns events for agent activity and final response.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Create data service for this user
            data_service = ChatDataService(db, current_user.id)

            # Create orchestrator agent
            orchestrator = OrchestratorAgent(data_service)

            # Load conversation history from manager
            history = conversation_manager.get_history(current_user.id)
            orchestrator.conversation_history = history

            # Create a queue for events
            import queue
            event_queue = queue.Queue()

            # Event callback for agent activity - adds to queue immediately
            def on_agent_event(event_type: str, agent_name: str, data: dict = None):
                event_data = {
                    "type": event_type,
                    "agent": agent_name,
                    "data": data or {}
                }
                event_queue.put(event_data)

            # Attach event callback to orchestrator
            orchestrator.on_agent_event = on_agent_event

            # Send initial event
            yield f"data: {json.dumps({'type': 'start', 'agent': 'Orchestrator'})}\n\n"
            await asyncio.sleep(0.1)

            # Run the chat in a thread pool to not block async
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(orchestrator.chat, request.message)

                # While processing, send events as they arrive
                while not future.done():
                    try:
                        # Check for events with a short timeout
                        event = event_queue.get(timeout=0.1)
                        yield f"data: {json.dumps(event)}\n\n"
                        await asyncio.sleep(0.05)
                    except queue.Empty:
                        # No events yet, continue waiting
                        await asyncio.sleep(0.05)

                # Get the result
                result = future.result()

                # Send any remaining events
                while not event_queue.empty():
                    event = event_queue.get()
                    yield f"data: {json.dumps(event)}\n\n"
                    await asyncio.sleep(0.05)

            # Save the conversation to manager
            conversation_manager.add_message(current_user.id, "user", request.message)
            conversation_manager.add_message(current_user.id, "assistant", result["response"])

            # Send final response
            final_event = {
                "type": "response",
                "response": result["response"],
                "agents_consulted": result.get("agents_consulted", []),
                "iterations": result.get("iterations", 1)
            }
            yield f"data: {json.dumps(final_event)}\n\n"

            # Send completion event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            error_event = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI financial assistant.
    The orchestrator will route it to appropriate specialized agents.
    Maintains conversation history per user.
    """
    try:
        # Create data service for this user
        data_service = ChatDataService(db, current_user.id)

        # Create orchestrator agent
        orchestrator = OrchestratorAgent(data_service)

        # Load conversation history from manager
        history = conversation_manager.get_history(current_user.id)
        orchestrator.conversation_history = history

        # Process the message
        result = orchestrator.chat(request.message)

        # Save the conversation to manager
        conversation_manager.add_message(current_user.id, "user", request.message)
        conversation_manager.add_message(current_user.id, "assistant", result["response"])

        return ChatResponse(
            response=result["response"],
            agents_consulted=result.get("agents_consulted", []),
            iterations=result.get("iterations", 1)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.post("/clear")
async def clear_conversation(
    current_user: User = Depends(get_current_user)
):
    """Clear conversation history for current user"""
    conversation_manager.clear_history(current_user.id)
    return {"message": "Conversation history cleared successfully"}


@router.get("/health")
async def chat_health_check():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "service": "Multi-Agent Financial Chat",
        "agents": ["Orchestrator", "SQL Analyst", "Financial Advisor", "Market Data", "Financial Information"],
        "features": ["Conversation Memory", "User Context Awareness", "Real-time Market Data", "Web Search"]
    }
