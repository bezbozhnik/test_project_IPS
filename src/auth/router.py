from fastapi import APIRouter, Depends, status

from src.auth import service
from src.auth.dependencies import valid_user_create, valid_user_update
from src.auth.schemas import AuthUser, UserResponse, UserUpdateSchema

router = APIRouter()


@router.post("/users/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(auth_data: AuthUser = Depends(valid_user_create)) -> UserResponse:
    return await service.create_user(auth_data)


@router.get("/users/", status_code=status.HTTP_200_OK, response_model=list[UserResponse])
async def get_user_by_params() -> list[UserResponse]:
    return await service.get_all_users()


@router.patch("/users/{id}/", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user(id: int, params_to_change: UserUpdateSchema = Depends(valid_user_update)) -> UserResponse:
    return await service.update_user(id, params_to_change)


@router.delete("/users/{id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int) -> None:
    return await service.delete_user_by_id(id)
