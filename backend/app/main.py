# app/main.py
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from app.config import CORS_ORIGINS
from app.database import engine
from app.routes import root, health, documents, users, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev convenience: creates tables from SQLModel metadata on startup.
    # Swap for Alembic migrations once the schema needs to evolve in production.
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


app = FastAPI(title="Paper Trail API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes live under /api so they can share an origin with the frontend
# build (see the "static" dir below) without colliding with SPA client routes.
app.include_router(root.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

# Populated by the Docker image (frontend build output copied to ./static).
# Not present in local dev, where the Vite dev server runs separately.
STATIC_DIR = Path(__file__).parent.parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa(full_path: str):
        """Serve the SPA shell for any non-API route (client-side routing)."""
        return FileResponse(STATIC_DIR / "index.html")
