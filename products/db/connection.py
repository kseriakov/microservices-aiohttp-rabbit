from aiohttp.web_app import Application
import asyncpg

from ..settings import settings


async def db_pool() -> asyncpg.Pool:
    pool = await asyncpg.create_pool(
        host=settings.POSTGRES_HOST_PRODUCTS,
        port=settings.POSTGRES_PORT_PRODUCTS,
        user=settings.POSTGRES_USER_PRODUCTS,
        database=settings.POSTGRES_DB_PRODUCTS,
        password=settings.POSTGRES_PASSWORD_PRODUCTS,
    )
    return pool


async def db_connect(app: Application):
    pool = await db_pool()
    app["db_pool"] = pool


async def db_disconnect(app: Application):
    await app["db_pool"].close()
