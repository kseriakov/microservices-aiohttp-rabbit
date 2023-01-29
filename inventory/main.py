import json
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from asyncpg import Pool, UniqueViolationError

from .db.connection import db_connect, db_disconnect
from .schemas import (
    AllProductsInventoryResponse,
    ProductInventoryResponse,
    ProductInventoryCreate,
    ProductInventoryUpdate,
)
from .settings import settings
from .logs.config import get_logger


logger = get_logger(__name__)

routes = web.RouteTableDef()


@routes.get("/products/{id}/inventory")
async def get_inventory_product(request: Request) -> Response:
    product_id = int(request.match_info["id"])
    pool: Pool = request.app["db_pool"]

    async with pool.acquire() as conn:
        query = """SELECT * FROM inventory WHERE product_id = $1"""
        product_data = await conn.fetchrow(query, product_id)

    if product_data is None:
        count = 0
    else:
        count = product_data["count"]

    return Response(
        body=ProductInventoryResponse(product_id=product_id, count=count).json(),
        content_type="application/json",
    )


@routes.patch("/products/inventory")
async def change_product_count(request: Request) -> Response:
    pool: Pool = request.app["db_pool"]

    body = await request.json()
    updated_data = ProductInventoryUpdate(**body)

    async with pool.acquire() as conn:
        query = """UPDATE inventory SET count = $1 WHERE product_id = $2"""
        resp = await conn.execute(query, updated_data.count, updated_data.product_id)

        if resp[-1] == "1":
            return Response(
                body=json.dumps({"success": "updated"}),
                content_type="application/json",
            )
        else:
            logger.info(f"Not updated product count (id = {updated_data.product_id}) in inventory")
            raise web.HTTPNotFound(
                body=json.dumps(
                    {
                        "error": f"Product with id = {updated_data.product_id} does not exists in inventory"
                    }
                ),
                content_type="application/json",
            )


@routes.delete("/products/{id}/inventory")
async def delete_product(request: Request) -> Response:
    product_id = int(request.match_info["id"])
    pool: Pool = request.app["db_pool"]

    async with pool.acquire() as conn:
        query = """DELETE FROM inventory WHERE product_id = $1"""
        deleted = await conn.execute(query, product_id)

    if deleted[-1] == "0":
        raise web.HTTPNotFound(
            body=json.dumps(
                {"error": f"Product with id = {product_id} does not exists in inventory"}
            ),
            content_type="application/json",
        )

    return Response(content_type="application/json", status=204)


@routes.get("/products/inventory")
async def get_inventory(request: Request) -> Response:
    pool: Pool = request.app["db_pool"]

    async with pool.acquire() as conn:
        query = """SELECT * FROM inventory"""
        response = await conn.fetch(query)

    if len(response) > 0:
        products_data = [ProductInventoryResponse(**dict(p)) for p in response]
        return Response(
            body=AllProductsInventoryResponse(inventory=products_data).json(),
            content_type="application/json",
        )
    else:
        raise web.HTTPNotFound(
            body=json.dumps({"error": "Inventory is empty"}), content_type="application/json"
        )


@routes.post("/products/inventory")
async def add_product_in_inventory(request: Request) -> Response:
    pool: Pool = request.app["db_pool"]
    body = await request.json()
    product_data = ProductInventoryCreate(**body)
    try:
        async with pool.acquire() as conn:
            query = """
                    INSERT INTO inventory (product_id, count) VALUES ($1, $2)
                    """
            await conn.execute(query, product_data.product_id, product_data.count)
    except UniqueViolationError:

        raise web.HTTPBadRequest(
            body=json.dumps(
                {"error": f"Product with id = {product_data.product_id} is already in inventory"}
            ),
            content_type="application/json",
        )

    return Response(
        body=json.dumps({"success": "created"}), status=201, content_type="application/json"
    )


app = web.Application()
app.add_routes(routes)

app.on_startup.append(db_connect)
app.on_shutdown.append(db_disconnect)

web.run_app(app, host=settings.HOST_INVENTORY, port=settings.PORT_INVENTORY)
