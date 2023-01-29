from aiohttp.web_app import Application
import asyncpg

from ..settings import settings


async def db_pool() -> asyncpg.Pool:
    pool = await asyncpg.create_pool(
        host=settings.POSTGRES_HOST_INVENTORY,
        port=settings.POSTGRES_PORT_INVENTORY,
        user=settings.POSTGRES_USER_INVENTORY,
        database=settings.POSTGRES_DB_INVENTORY,
        password=settings.POSTGRES_PASSWORD_INVENTORY,
    )
    return pool


async def db_connect(app: Application):
    pool = await db_pool()
    app["db_pool"] = pool


async def db_disconnect(app: Application):
    await app["db_pool"].close()
