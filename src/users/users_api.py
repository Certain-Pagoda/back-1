from fastapi import APIRouter, Depends, HTTPException

from src.auth.auth_functions import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/")
async def GET_user(
        user: dict = Depends(get_current_user)
    ):
    return {"message": user}
