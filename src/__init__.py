from fastapi import FastAPI
from src.users.router import user_router




version = "v1"
app = FastAPI(
    version = version,
    title = "Backend du projet AI4D",
    description="A faire",
)
app.include_router(user_router,prefix=f"/auth/{version}",tags=["users"])


