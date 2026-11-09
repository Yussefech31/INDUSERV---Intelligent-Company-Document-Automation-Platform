from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.session import engine, Base, SessionLocal
from app.database.seed import seed_database
from app.api.routes import health, prompts, providers, settings as settings_routes, workspace, dashboard, documents, calculations, generation, templates, history, workflows

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed default data
    logger.info("Initializing INDUSERV database and seeding default data...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    settings.ensure_storage_dirs()
    logger.info("INDUSERV backend successfully initialized.")
    yield
    # Shutdown actions if any
    logger.info("INDUSERV backend shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Company Document Automation Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
api_prefix = settings.API_V1_PREFIX
app.include_router(health.router, prefix=api_prefix)
app.include_router(prompts.router, prefix=api_prefix)
app.include_router(providers.router, prefix=api_prefix)
app.include_router(settings_routes.router, prefix=api_prefix)
app.include_router(workspace.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(documents.router, prefix=api_prefix)
app.include_router(calculations.router, prefix=api_prefix)
app.include_router(generation.router, prefix=api_prefix)
app.include_router(templates.router, prefix=api_prefix)
app.include_router(history.router, prefix=api_prefix)
app.include_router(workflows.router, prefix=api_prefix)

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": api_prefix
    }
