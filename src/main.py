import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import redis.asyncio as aioredis
from src import redis
from src.auth.router import router as auth_router
from src.config import app_configs, settings
from src.rabbitmq import rabbit_connection


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    # Startup
    redis_connected = False
    redis_retry_count = 0
    while not redis_connected and redis_retry_count < settings.MAX_RETRIES:
        try:
            pool = aioredis.ConnectionPool.from_url(
                str(settings.REDIS_URL), max_connections=10, decode_responses=True
            )
            redis.redis_client = aioredis.Redis(connection_pool=pool)
            redis_connected = True
            logging.warn("Connected to Redis")
        except Exception as e:
            redis_retry_count += 1
            logging.warn(f"Failed to connect to Redis: {e}. Attempt #{redis_retry_count}. Retrying...")
            await asyncio.sleep(settings.RETRY_INTERVAL)

    rabbit_connected = False
    rabbit_retry_count = 0
    while not rabbit_connected and rabbit_retry_count < settings.MAX_RETRIES:
        try:
            await rabbit_connection.connect()
            asyncio.create_task(rabbit_connection.consume_rabbit_queue())
            rabbit_connected = True
            logging.warn("Connected to RabbitMQ")
        except Exception as e:
            rabbit_retry_count += 1
            logging.warn(f"Failed to connect to RabbitMQ: {e}. Attempt #{rabbit_retry_count}. Retrying...")
            await asyncio.sleep(settings.RETRY_INTERVAL)

    if not redis_connected:
        logging.exception("Failed to connect to Redis after multiple retries")
    if not rabbit_connected:
        logging.exception("Failed to connect to RabbitMQ after multiple retries")

    yield

    await rabbit_connection.disconnect()
    await pool.disconnect()


app = FastAPI(**app_configs, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
