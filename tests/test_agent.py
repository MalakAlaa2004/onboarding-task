from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_agent_chat_endpoint(async_client: httpx.AsyncClient):
    payload = {
        "message": "What skills and backend projects does the developer have?",
        "thread_id": "test_session_101",
    }
    res = await async_client.post("/api/v1/agent/chat", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert "reply" in data
    assert len(data["reply"]) > 0
    assert data["thread_id"] == "test_session_101"
