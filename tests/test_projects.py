from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_project_lifecycle_and_joins(async_client: httpx.AsyncClient):
    # 1. Create a prerequisite skill
    skill_payload = {
        "name": "FastAPI Testing",
        "category": "Backend",
        "proficiency": 88,
        "years_experience": 2.0,
        "tags": ["fastapi", "testing"],
    }
    skill_res = await async_client.post("/api/v1/skills", json=skill_payload)
    skill_id = skill_res.json()["data"]["id"]

    # 2. Create Project referencing the skill
    project_payload = {
        "title": "Automated Quality Gate",
        "slug": "automated-quality-gate",
        "summary": "Enterprise CI quality gate checking code health and test coverage.",
        "description": "Full end-to-end integration test harness for FastAPI and Beanie.",
        "featured": True,
        "status": "completed",
        "stars": 25,
        "skill_ids": [skill_id],
    }
    create_res = await async_client.post("/api/v1/projects", json=project_payload)
    assert create_res.status_code == 201
    created = create_res.json()["data"]
    project_id = created["id"]
    assert created["slug"] == "automated-quality-gate"

    # 3. Retrieve Project by Slug
    slug_res = await async_client.get("/api/v1/projects/automated-quality-gate")
    assert slug_res.status_code == 200
    assert slug_res.json()["data"]["id"] == project_id

    # 4. Retrieve Detail with Relational Joined Skills
    detail_res = await async_client.get(f"/api/v1/projects/{project_id}/detail")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()["data"]
    assert len(detail_data["skills"]) == 1
    assert detail_data["skills"][0]["name"] == "FastAPI Testing"

    # 5. Duplicate Slug Error (409 Conflict)
    dup_res = await async_client.post("/api/v1/projects", json=project_payload)
    assert dup_res.status_code == 409
    assert dup_res.json()["code"] == "ENTITY_ALREADY_EXISTS"

    # 6. Not Found Error (404 Not Found)
    missing_res = await async_client.get("/api/v1/projects/non-existent-slug-xyz")
    assert missing_res.status_code == 404
    assert missing_res.json()["code"] == "ENTITY_NOT_FOUND"
