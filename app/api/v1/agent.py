from __future__ import annotations

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.agent.graph import run_portfolio_agent
from app.schemas.common import APIResponse

router = APIRouter(prefix="/agent", tags=["LangGraph Autonomous Agent"])


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question or prompt")
    thread_id: str = Field(
        default="default_thread",
        description="Unique conversation thread ID for session memory",
    )


class AgentChatResponse(BaseModel):
    reply: str
    thread_id: str
    tools_called: list[str]


@router.post(
    "/chat",
    response_model=APIResponse[AgentChatResponse],
    status_code=status.HTTP_200_OK,
    summary="Chat with stateful LangGraph Portfolio Bot",
)
async def chat_with_agent(request: AgentChatRequest):
    result = await run_portfolio_agent(
        message=request.message, thread_id=request.thread_id
    )
    return APIResponse(
        data=AgentChatResponse(**result),
        message="Agent response generated successfully.",
    )
