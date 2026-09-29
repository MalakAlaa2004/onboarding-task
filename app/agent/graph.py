from __future__ import annotations

import logging
from typing import Any, cast

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.llm_factory import get_agent_llm
from app.agent.tools import PORTFOLIO_TOOLS

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the NovaGates Autonomous Portfolio AI Agent.
Your role is to represent the developer, answering questions accurately and professionally about their skills, featured projects, and career background.
Always use the provided tools to lookup actual facts from the database before answering. Do not fabricate skills or projects.
Be concise, articulate, and technical."""


def build_portfolio_graph():
    llm = get_agent_llm()
    llm_with_tools = llm.bind_tools(PORTFOLIO_TOOLS)

    async def agent_node(state: MessagesState) -> dict[str, Any]:
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        try:
            response = await llm_with_tools.ainvoke(messages)
        except Exception as e:
            logger.warning(
                "LLM invocation failed (%s). Generating fallback response.", e
            )
            response = AIMessage(
                content=(
                    "I am the NovaGates Portfolio AI Agent. The developer specializes in "
                    "Python, FastAPI, MongoDB, Redis, Celery, and LangGraph."
                )
            )
        return {"messages": [response]}

    tool_node = ToolNode(PORTFOLIO_TOOLS)

    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


# Singleton compiled graph instance
portfolio_agent_graph = build_portfolio_graph()


async def run_portfolio_agent(
    message: str, thread_id: str = "default"
) -> dict[str, Any]:
    """Executes a multi-turn conversation with memory using LangGraph."""
    config: RunnableConfig = cast(RunnableConfig, {"configurable": {"thread_id": thread_id}})
    input_message = HumanMessage(content=message)

    result = await portfolio_agent_graph.ainvoke(
        {"messages": [input_message]},
        config=config,
    )

    messages = result.get("messages", [])
    last_message = (
        messages[-1] if messages else AIMessage(content="No response generated.")
    )

    tools_called = []
    for m in messages:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                tools_called.append(tc.get("name", "unknown_tool"))

    return {
        "reply": last_message.content,
        "thread_id": thread_id,
        "tools_called": list(set(tools_called)),
    }
