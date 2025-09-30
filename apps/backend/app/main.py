"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import create_tables
from app.routes import (
    import_chesscom,
    analyze,
    games,
    puzzles,
    human,
    sparring,
    websocket,
    pgn_upload,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    create_tables()
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title="Chess Coach API",
    description="Chess analysis and coaching platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(import_chesscom.router, prefix="/api/import", tags=["import"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(puzzles.router, prefix="/api/puzzles", tags=["puzzles"])
app.include_router(human.router, prefix="/api/human", tags=["human"])
app.include_router(sparring.router, prefix="/api/spar", tags=["sparring"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(pgn_upload.router, prefix="/api/pgn", tags=["pgn"])


@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint."""
    return JSONResponse({
        "message": "Chess Coach API",
        "version": "0.1.0",
        "docs": "/docs"
    })


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )

