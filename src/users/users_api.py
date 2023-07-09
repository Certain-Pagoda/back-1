from fastapi import APIRouter, Depends, HTTPException

from src.auth.auth_functions import get_current_user
from src.users.user_types import UserOUT

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/")
async def GET_user(
        user: dict = Depends(get_current_user)
        ) -> UserOUT:
    return user.to_pydantic()

@router.put("/")
async def PUT_user(
        user: dict = Depends(get_current_user)
    ) -> UserOUT:
    return user.to_pydantic()
