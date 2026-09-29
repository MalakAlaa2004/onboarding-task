from __future__ import annotations

import httpx
import pytest

from app.services.job_service import JobMatchingService


@pytest.mark.asyncio
async def test_job_match_live_returns_matches(
    async_client: httpx.AsyncClient,
):
    res = await async_client.post("/api/v1/jobs/match", json={"max_results": 2})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "matches" in data["data"]


@pytest.mark.asyncio
async def test_job_match_invalid_key_returns_graceful_error(
    monkeypatch: pytest.MonkeyPatch,
    async_client: httpx.AsyncClient,
):
    # Verify graceful 502 handling when external service key is rejected
    def fake_init(self, *args, **kwargs):
        self.api_key = "invalid-key"
        self.endpoint = "https://api.tavily.com/search"

    monkeypatch.setattr(JobMatchingService, "__init__", fake_init)
    res = await async_client.post("/api/v1/jobs/match", json={"max_results": 2})
    assert res.status_code == 502
    data = res.json()
    assert data["code"] == "EXTERNAL_SERVICE_ERROR"
    assert "Tavily" in data["detail"]
