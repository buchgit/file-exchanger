import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from auth import init_admin
from config import settings
from database import Base, SessionLocal, engine
from routes.auth import router as auth_router
from routes.files import cleanup_expired_files, router as files_router
from routes.users import router as users_router
from routes.ws import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    settings.STORAGE_PATH.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    try:
        init_admin(db)
    finally:
        db.close()

    cleanup_task = asyncio.create_task(cleanup_expired_files(SessionLocal))

    yield

    # Shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="File Exchanger", version="1.0.0", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(files_router)
app.include_router(ws_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
