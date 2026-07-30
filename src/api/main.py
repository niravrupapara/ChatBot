from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.db.schema import init_schema
from src.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    #startup: ensure SQLite atabase schema exists
    init_schema()
    logger.info("FastAPI ervice starting up - SQLite schema verified")

    yield
    #shutdown
    logger.info("FastAPI service shutting down")


app = FastAPI(
    title="LangGraph Chatbot API",
    description="Provide REST API for LangGraph AI Assistant with native tool calling and persistent SQLite memory",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register routes
app.include_router(router)

