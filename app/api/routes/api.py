from fastapi import APIRouter
from app.api.routes import auth, health, root, users

api_router = APIRouter()

# Mount routes with appropriate path prefixes
api_router.include_router(root.router)
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(users.router, prefix="/users")
