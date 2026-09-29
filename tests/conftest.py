from __future__ import annotations

from collections.abc import AsyncGenerator

import httpx
import pytest_asyncio
from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.core import cache as cache_module
from app.core.cache import CacheService
from app.core.config import Settings
from app.main import create_application
from app.models.experience import Experience
from app.models.project import Project
from app.models.skill import Skill

TEST_DB_NAME = "portfolio_test_db"
TEST_MONGO_URI = "mongodb://localhost:27017/portfolio_test_db"
TEST_REDIS_URL = "redis://localhost:6379/15"  # Use dedicated DB 15 for tests


def get_test_settings() -> Settings:
    return Settings(
        ENVIRONMENT="testing",
        MONGODB_URI=TEST_MONGO_URI,
        MONGODB_DB_NAME=TEST_DB_NAME,
        REDIS_URL=TEST_REDIS_URL,
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    client = AsyncIOMotorClient(TEST_MONGO_URI)
    db = client[TEST_DB_NAME]

    await init_beanie(
        database=db,
        document_models=[Project, Skill, Experience],
    )

    # Initialize test cache
    cache_module.cache_service = CacheService(redis_url=TEST_REDIS_URL, default_ttl=60)
    await cache_module.cache_service.connect()

    yield

    # Clean up test DB after all tests
    await client.drop_database(TEST_DB_NAME)
    if cache_module.cache_service and cache_module.cache_service.client:
        await cache_module.cache_service.client.flushdb()
        await cache_module.cache_service.close()
    client.close()


@pytest_asyncio.fixture
async def app_instance() -> FastAPI:
    return create_application()


@pytest_asyncio.fixture
async def async_client(
    app_instance: FastAPI,
) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app_instance),
        base_url="http://test",
    ) as client:
        yield client
