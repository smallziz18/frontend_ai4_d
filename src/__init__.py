from fastapi import FastAPI
from src.users.router import user_router
from contextlib import asynccontextmanager
from src.db.main import init_db

@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting... by smallziz")
    await init_db()
    yield
    print("server is shutting down...")


version = "v1"
app = FastAPI(
    version = version,
    title = "Backend du projet AI4D",
    description="A faire",
    lifespan=life_span,
)
app.include_router(user_router,prefix=f"/users/{version}",tags=["users"])
