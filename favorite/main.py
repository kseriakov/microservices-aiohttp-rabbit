import json
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from asyncpg import Pool, UniqueViolationError

from .db.connection import db_connect, db_disconnect
from .schemas import CreateFavoriteProduct, DeleteFavoriteProduct, ShowFavoriteProducts
from .settings import settings


routes = web.RouteTableDef()


@routes.get("/users/{id}/favorites")
async def get_favorite_products_id(request: Request) -> Response:
    user_id = int(request.match_info["id"])
    pool: Pool = app["db_pool"]

    async with pool.acquire() as conn:
        query = """SELECT product_id FROM favorite WHERE user_id = $1"""
        rows = await conn.fetch(query, user_id)

    favorites = [dict(row)["product_id"] for row in rows]
    return Response(
        body=ShowFavoriteProducts(user_id=user_id, favorite_products=favorites).json(),
        content_type="application/json",
    )


@routes.post("/users/favorites")
async def add_product_in_favorite(request: Request) -> Response:
    body = await request.json()
    data = CreateFavoriteProduct(**body)
    pool: Pool = app["db_pool"]

    try:
        async with pool.acquire() as conn:
            query = """INSERT INTO favorite (user_id, product_id) VALUES ($1, $2)"""
            await conn.execute(query, data.user_id, data.product_id)
    except UniqueViolationError:
        raise web.HTTPBadRequest(
            body=json.dumps({"error": "This product already is favorite"}),
            content_type="application/json",
        )

    return Response(
        body=json.dumps({"success": "created"}), status=201, content_type="application/json"
    )


@routes.delete("/users/{id}/favorites/{product_id}")
async def delete_favorite_product(request: Request) -> Response:
    data = DeleteFavoriteProduct(
        user_id=request.match_info["id"], product_id=request.match_info["product_id"]
    )

    pool: Pool = app["db_pool"]

    async with pool.acquire() as conn:
        query = """DELETE FROM favorite WHERE user_id = $1 AND product_id = $2"""
        deleted = await conn.execute(query, data.user_id, data.product_id)

    if deleted[-1] == "0":
        raise web.HTTPNotFound(
            text=f"Product with id = {data.product_id} does not favorite for user_id = {data.user_id}"
        )

    return Response(content_type="application/json", status=204)


app = web.Application()
app.add_routes(routes)

app.on_startup.append(db_connect)
app.on_shutdown.append(db_disconnect)

web.run_app(app, host=settings.HOST_FAVORITE, port=settings.PORT_FAVORITE)
