import json
import logging
from typing import Any

from sqlalchemy import delete, insert, select, update

from redis.exceptions import ConnectionError as RedisError
from src.auth.exceptions import InvalidCredentials
from src.auth.schemas import AuthUser, UserResponse
from src.auth.security import check_password, hash_password
from src.database import User, execute, fetch_all, fetch_one
from src.rabbitmq import rabbit_connection
from src.redis import RedisData, delete_by_key, get_by_key, set_redis_key


async def create_user(user: AuthUser) -> dict[str, Any] | None:
    insert_query = (
        insert(User)
        .values(
            {
                "email": user.email,
                "password": hash_password(user.password)
            }
        )
        .returning(User)
    )

    result = await fetch_one(insert_query)
    try:
        await delete_by_key(key='ALL_USERS')
        message = {
            'type': 'NEW_USER',
            'message': f'New user has registered with an email: {user.email}'
        }
        await rabbit_connection.send_messages(
            messages=message
        )
    except RuntimeError as e:
        logging.exception(e)
    except RedisError:
        logging.exception('Redis connection is failed')
    return result # noqa


async def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    select_query = select(User).where(User.id == user_id)

    return await fetch_one(select_query)


async def delete_user_by_id(user_id: int) -> None:
    delete_query = delete(User).where(User.id == user_id)

    await execute(delete_query)

    try:
        await delete_by_key(key='ALL_USERS')
    except RuntimeError as e:
        logging.exception(e)
    except RedisError:
        logging.exception('Redis connection is failed')


async def get_all_users() -> list[dict[str, Any]] | None:
    try:
        if result := await get_by_key('ALL_USERS'):
            return json.loads(result)
        select_query = select(User)
        result = [UserResponse(**elem).model_dump() for elem in await fetch_all(select_query)]
        await set_redis_key(RedisData(key='ALL_USERS', value=json.dumps(result)))
    except RuntimeError as e:
        logging.exception(e)
    except RedisError:
        logging.exception('Redis connection is failed')
    finally:
        select_query = select(User)
        result = [UserResponse(**elem).model_dump() for elem in await fetch_all(select_query)]
    return result


async def update_user(id, params_to_change) -> dict[str, Any] | None:
    update_query = (
        update(User)
        .where(User.id == id)
        .values(**{k: v for k, v in params_to_change.model_dump().items() if v is not None})
        .returning(User)
    )
    result = await fetch_one(update_query)
    try:
        await delete_by_key(key='ALL_USERS')
    except RuntimeError as e:
        logging.exception(e)
    except RedisError:
        logging.exception('Redis connection is failed')
    return result # noqa


async def get_user_by_email(email: str) -> dict[str, Any] | None:
    select_query = select(User).where(User.email == email)

    return await fetch_one(select_query)


async def authenticate_user(auth_data: AuthUser) -> dict[str, Any]:
    user = await get_user_by_email(auth_data.email)
    if not user:
        raise InvalidCredentials()

    if not check_password(auth_data.password, user["password"]):
        raise InvalidCredentials()

    return user
