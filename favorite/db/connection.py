from aiohttp.web_app import Application
import asyncpg

from ..settings import settings


async def db_pool() -> asyncpg.Pool:
    pool = await asyncpg.create_pool(
        host=settings.POSTGRES_HOST_FAVORITE,
        port=settings.POSTGRES_PORT_FAVORITE,
        user=settings.POSTGRES_USER_FAVORITE,
        database=settings.POSTGRES_DB_FAVORITE,
        password=settings.POSTGRES_PASSWORD_FAVORITE,
    )
    return pool


async def db_connect(app: Application):
    pool = await db_pool()
    app["db_pool"] = pool


async def db_disconnect(app: Application):
    await app["db_pool"].close()
