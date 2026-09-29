from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_experience_crud_flow(async_client: httpx.AsyncClient):
    payload = {
        "company": "NovaGates AI",
        "role": "Senior Backend & AI Engineer",
        "start_date": "2026-03-01",
        "end_date": None,
        "is_current": True,
        "technologies": ["FastAPI", "MongoDB", "Redis", "Celery", "LangGraph"],
        "responsibilities": [
            "Lead backend architecture",
            "Design agentic AI workflows",
        ],
    }

    # 1. Create Experience
    res = await async_client.post("/api/v1/experiences", json=payload)
    assert res.status_code == 201
    created = res.json()["data"]
    exp_id = created["id"]
    assert created["company"] == "NovaGates AI"

    # 2. List Experiences
    list_res = await async_client.get("/api/v1/experiences?current_only=true")
    assert list_res.status_code == 200
    items = list_res.json()["data"]
    assert any(x["id"] == exp_id for x in items)

    # 3. Update Experience
    update_res = await async_client.put(
        f"/api/v1/experiences/{exp_id}",
        json={"role": "Lead AI Architect"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["role"] == "Lead AI Architect"

    # 4. Delete Experience
    del_res = await async_client.delete(f"/api/v1/experiences/{exp_id}")
    assert del_res.status_code == 204

    # 5. Verify 404 after deletion
    get_res = await async_client.get(f"/api/v1/experiences/{exp_id}")
    assert get_res.status_code == 404
    assert get_res.json()["code"] == "ENTITY_NOT_FOUND"
