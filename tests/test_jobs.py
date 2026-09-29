from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_job_match_unconfigured_key_returns_graceful_error(
    async_client: httpx.AsyncClient,
):
    # Without TAVILY_API_KEY in test environment, endpoint gracefully raises 502 ExternalServiceError
    res = await async_client.post("/api/v1/jobs/match", json={"max_results": 3})
    assert res.status_code == 502
    data = res.json()
    assert data["code"] == "EXTERNAL_SERVICE_ERROR"
    assert "Tavily" in data["detail"]
