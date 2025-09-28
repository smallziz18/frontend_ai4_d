from fastapi import FastAPI
from src.users.router import user_router

from src.profile.router import router



version = "v1"
app = FastAPI(
    version = version,
    title = "Backend du projet AI4D",
    description="A faire",
)
# Montage des routes avec les bons préfixes
app.include_router(user_router, prefix=f"/auth/{version}", tags=["users"])
app.include_router(router, prefix=f"/profile/{version}", tags=["profile"])
