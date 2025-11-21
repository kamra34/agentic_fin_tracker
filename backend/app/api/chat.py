from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
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
        "agents": ["Orchestrator", "SQL Analyst", "Financial Advisor"],
        "features": ["Conversation Memory", "User Context Awareness"]
    }
