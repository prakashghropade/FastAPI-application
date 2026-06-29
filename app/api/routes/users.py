from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse, tags=["users"])
async def read_user_me(
    current_user: User = Depends(get_current_user)
):
    """
    Returns the authenticated user details for the active JWT session.
    """
    return current_user
