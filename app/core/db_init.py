from __future__ import annotations

import logging

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings
from app.models.experience import Experience
from app.models.project import Project
from app.models.skill import Skill

# Compatibility patch: Motor delegates to PyMongo client for append_metadata
if not hasattr(AsyncIOMotorClient, "append_metadata"):
    AsyncIOMotorClient.append_metadata = lambda self, *args, **kwargs: getattr(
        self.delegate, "append_metadata", lambda *a, **k: None
    )(*args, **kwargs)

logger = logging.getLogger(__name__)


class DatabaseManager:
    client: AsyncIOMotorClient | None = None

    @classmethod
    async def connect_and_init(
        cls, uri: str | None = None, db_name: str | None = None
    ) -> None:
        settings = get_settings()
        mongo_uri = uri or settings.MONGODB_URI
        target_db = db_name or settings.MONGODB_DB_NAME

        logger.info("Connecting to MongoDB at: %s (database: %s)", mongo_uri, target_db)
        cls.client = AsyncIOMotorClient(mongo_uri)
        db = cls.client[target_db]

        await init_beanie(
            database=db,
            document_models=[
                Project,
                Skill,
                Experience,
            ],
        )
        logger.info("Beanie ODM successfully initialized with Document models.")

    @classmethod
    async def close(cls) -> None:
        if cls.client:
            cls.client.close()
            logger.info("MongoDB client connection closed.")
