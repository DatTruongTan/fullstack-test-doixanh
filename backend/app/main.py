from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.presentation.api import api_router
from app.config import settings
from app.infrastructure.services.elastic import setup_elasticsearch, es_client
from app.infrastructure.services.redis import redis_client
from app.infrastructure.db.session import engine, SessionLocal
from app.domain.models import user, task

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    user.Base.metadata.create_all(bind=engine)
    task.Base.metadata.create_all(bind=engine)
    
    setup_elasticsearch()
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to TodoList API"}

@app.get("/health")
async def health_check():
    """Health check endpoint for the API and its dependencies"""
    health_status = {
        "api": "ok",
        "database": "ok",
        "redis": "ok",
        "elasticsearch": "ok"
    }
    
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
    
    try:
        redis_client.ping()
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
    
    try:
        if not es_client.ping():
            health_status["elasticsearch"] = "error: failed to connect"
    except Exception as e:
        health_status["elasticsearch"] = f"error: {str(e)}"
    
    return health_status 