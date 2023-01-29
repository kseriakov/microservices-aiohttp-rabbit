import json
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from asyncpg import Pool, UniqueViolationError

from .db.connection import db_connect, db_disconnect
from .schemas import AllProductsResponse, ProductShow, ProductCreate
from .settings import settings


routes = web.RouteTableDef()


@routes.get("/products")
async def get_all_products(request: Request) -> Response:
    pool: Pool = request.app["db_pool"]

    async with pool.acquire() as conn:
        query = """SELECT * FROM products"""
        response = await conn.fetch(query)

    if len(response) > 0:
        products_data = [ProductShow(**dict(p)) for p in response]
        return Response(
            body=AllProductsResponse(products=products_data).json(), content_type="application/json"
        )
    else:
        raise web.HTTPNotFound(
            body=json.dumps({"error": "No products"}), content_type="application/json"
        )


@routes.get("/products/{id}")
async def get_product(request: Request) -> Response:
    id = request.match_info["id"]
    pool: Pool = request.app["db_pool"]

    async with pool.acquire() as conn:
        query = """SELECT * FROM products WHERE id = $1"""
        product_data = await conn.fetchrow(query, int(id))

    if product_data is None:
        raise web.HTTPNotFound(
            body=json.dumps({"error": f"Product with id = {id} does not exists"}),
            content_type="application/json",
        )

    product = ProductShow(**dict(product_data))
    return Response(body=product.json(), content_type="application/json")


@routes.delete("/products/{id}")
async def delete_product(request: Request) -> Response:
    id = request.match_info["id"]
    pool: Pool = request.app["db_pool"]

    async with pool.acquire() as conn:
        query = """DELETE FROM products WHERE id = $1"""
        deleted = await conn.execute(query, int(id))

    if deleted[-1] == "0":
        raise web.HTTPNotFound(
            body=json.dumps({"error": f"Product with id = {id} does not exists"}),
            content_type="application/json",
        )

    return Response(content_type="application/json", status=204)


@routes.post("/products")
async def create_product(request: Request) -> Response:
    pool: Pool = request.app["db_pool"]
    body = await request.json()
    product_data = ProductCreate(**body)
    try:
        async with pool.acquire() as conn:
            query = """
                    INSERT INTO products (name, price) VALUES ($1, $2)
                    """
            await conn.execute(query, product_data.name, product_data.price)
    except UniqueViolationError:
        raise web.HTTPBadRequest(
            body=json.dumps({"error": f"{product_data.name} already exists"}),
            content_type="application/json",
        )
    
    return Response(
        body=json.dumps({"success": "created"}), status=201, content_type="application/json"
    )


app = web.Application()
app.add_routes(routes)

app.on_startup.append(db_connect)
app.on_shutdown.append(db_disconnect)

web.run_app(app, host=settings.HOST_PRODUCTS, port=settings.PORT_PRODUCTS)
