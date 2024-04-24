from src.auth import service
from src.auth.exceptions import EmailTaken
from src.auth.schemas import AuthUser, UserUpdateSchema
from src.auth.security import hash_password


async def valid_user_create(user: AuthUser) -> AuthUser:
    if await service.get_user_by_email(user.email):
        raise EmailTaken()

    return user


async def valid_user_update(user: UserUpdateSchema) -> UserUpdateSchema:
    if user.email and await service.get_user_by_email(user.email):
        raise EmailTaken()
    if user.password:
        AuthUser.valid_password(user.password)
        user.password = hash_password(user.password)
    return user
