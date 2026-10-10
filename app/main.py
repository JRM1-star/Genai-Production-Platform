import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("application_starting", version=settings.app_version)
    yield
    log.info("application_stopping")


app = FastAPI(
    title="GenAI Production Platform",
    version=settings.app_version,
    description="Multi-tenant Agentic RAG API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        log.exception("unhandled_request_error")
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id

    log.info(
        "request_completed",
        status_code=response.status_code,
        duration_ms=duration_ms,
    )

    structlog.contextvars.clear_contextvars()
    return response


app.include_router(router)
