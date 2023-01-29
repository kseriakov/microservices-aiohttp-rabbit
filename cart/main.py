import json
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from asyncpg import Pool, UniqueViolationError

from .rabbit.sender import CartSender

from .db.connection import db_connect, db_disconnect
from .schemas import CreateCartProduct, ShowCartProducts, DeleteCartProduct
from .settings import settings


routes = web.RouteTableDef()

cart_rabbit_sender = CartSender()


@routes.get("/users/{id}/cart")
async def get_cart_products_id(request: Request) -> Response:
    user_id = int(request.match_info["id"])
    pool: Pool = app["db_pool"]

    async with pool.acquire() as conn:
        query = """SELECT product_id FROM cart WHERE user_id = $1"""
        rows = await conn.fetch(query, user_id)

    favorites = [dict(row)["product_id"] for row in rows]
    return Response(
        body=ShowCartProducts(user_id=user_id, cart_products=favorites).json(),
        content_type="application/json",
    )


@routes.post("/users/cart")
async def add_product_in_cart(request: Request) -> Response:
    body = await request.json()
    data = CreateCartProduct(**body)
    pool: Pool = app["db_pool"]

    try:
        async with pool.acquire() as conn:
            query = """INSERT INTO cart (user_id, product_id) VALUES ($1, $2)"""
            await conn.execute(query, data.user_id, data.product_id)
    except UniqueViolationError:
        raise web.HTTPBadRequest(
            body=json.dumps({"error": "This product already in cart"}),
            content_type="application/json",
        )

    await cart_rabbit_sender.get_product_from_inventory(data.dict())

    return Response(
        body=json.dumps({"success": "created"}), status=201, content_type="application/json"
    )


@routes.delete("/users/{id}/cart/{product_id}")
async def delete_cart_product(request: Request) -> Response:
    data = DeleteCartProduct(
        user_id=request.match_info["id"], product_id=request.match_info["product_id"]
    )

    pool: Pool = app["db_pool"]

    async with pool.acquire() as conn:
        query = """DELETE FROM cart WHERE user_id = $1 AND product_id = $2"""
        deleted = await conn.execute(query, data.user_id, data.product_id)

    if deleted[-1] == "0":
        raise web.HTTPNotFound(
            text=f"Product with id = {data.product_id} does not in user's ({data.user_id}) cart"
        )

    await cart_rabbit_sender.return_product_to_inventory(data.dict())

    return Response(content_type="application/json", status=204)


app = web.Application()
app.add_routes(routes)

app.on_startup.append(db_connect)
app.on_shutdown.append(db_disconnect)

web.run_app(app, host=settings.HOST_CART, port=settings.PORT_CART)
