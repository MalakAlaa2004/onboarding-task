from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.router import api_router
from app.core import cache as cache_module
from app.core.cache import CacheService
from app.core.config import get_settings
from app.core.db_init import DatabaseManager
from app.core.exceptions import register_exception_handlers

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("PortfolioAPI")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Initializing services for: %s", settings.PROJECT_NAME)

    # 1. Initialize MongoDB with Beanie ODM
    await DatabaseManager.connect_and_init(
        uri=settings.MONGODB_URI,
        db_name=settings.MONGODB_DB_NAME,
    )

    # 2. Initialize Redis Caching Layer
    cache_module.cache_service = CacheService(
        redis_url=settings.REDIS_URL,
        default_ttl=settings.CACHE_DEFAULT_TTL,
    )
    await cache_module.cache_service.connect()

    logger.info("Startup complete. API is ready to serve requests.")
    yield

    # Shutdown sequence
    logger.info("Commencing application shutdown...")
    if cache_module.cache_service:
        await cache_module.cache_service.close()
    await DatabaseManager.close()
    logger.info("Application shutdown completed.")


def create_application() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "Production-grade Backend & AI Developer Portfolio service powered by "
            "FastAPI, Beanie ODM (MongoDB), Redis Cache, Tavily Job Search, and Ollama Cloud."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    register_exception_handlers(app)

    # Routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/", include_in_schema=False)
    async def root_redirect():
        return RedirectResponse(url="/docs")

    return app


app = create_application()
