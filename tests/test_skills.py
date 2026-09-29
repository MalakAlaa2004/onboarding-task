from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_skill_lifecycle_and_caching(async_client: httpx.AsyncClient):
    # 1. Create Skill (Happy Path)
    payload = {
        "name": "AsyncIO",
        "category": "Backend",
        "proficiency": 92,
        "years_experience": 3.5,
        "tags": ["python", "concurrency"],
    }
    create_res = await async_client.post("/api/v1/skills", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()["data"]
    skill_id = created["id"]
    assert created["name"] == "AsyncIO"

    # 2. List Skills (Verifies retrieval & cache warming)
    list_res = await async_client.get("/api/v1/skills")
    assert list_res.status_code == 200
    skills = list_res.json()["data"]
    assert any(s["id"] == skill_id for s in skills)

    # 3. Get by ID
    get_res = await async_client.get(f"/api/v1/skills/{skill_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["name"] == "AsyncIO"

    # 4. Duplicate Name Error (409 Conflict)
    dup_res = await async_client.post("/api/v1/skills", json=payload)
    assert dup_res.status_code == 409
    assert dup_res.json()["code"] == "ENTITY_ALREADY_EXISTS"

    # 5. Non-existent ID Error (404 Not Found)
    non_existent = "660000000000000000000999"
    not_found_res = await async_client.get(f"/api/v1/skills/{non_existent}")
    assert not_found_res.status_code == 404
    assert not_found_res.json()["code"] == "ENTITY_NOT_FOUND"
