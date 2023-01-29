from asyncio import Task
import asyncio
import logging
from aiohttp import ClientSession, web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from .settings import settings


logger = logging.getLogger(__name__)


def get_product_stocks(product_id: int, session: ClientSession) -> Task:
    return asyncio.create_task(
        session.get(
            f"{settings.INVENTORY_API_BASE}/products/{product_id}/inventory",
        )
    )


async def get_products_with_inventory(products: dict, session: ClientSession) -> dict:
    products_tasks_inventory = {
        get_product_stocks(product["id"], session): product for product in products["products"]
    }

    products_response = []

    products_done, products_pending = await asyncio.wait(products_tasks_inventory.keys(), timeout=1)

    for done in products_done:
        if done.exception() is None:
            stocks = await done.result().json()
        else:
            stocks = None
            product_id = products_tasks_inventory[done]["product_id"]
            logger.exception(
                msg=f"Do not get information about product with id  = {product_id} in inventory",
                exc_info=done.exception(),
            )

        product_data = products_tasks_inventory[done]
        product_data.update({"stocks": stocks})
        products_response.append(product_data)

    for pending in products_pending:
        pending.cancel()
        product_id = products_tasks_inventory[pending]["product_id"]
        logger.info(
            msg=f"Server do not response on get information about product with {product_id} in inventory"
        )

        product_data = products_tasks_inventory[pending]
        product_data.update({"stocks": None})
        products_response.append(product_data)

    return products_response


async def proxy_request_on_service(request: Request, session: ClientSession, url: str) -> Response:
    data = await request.json()

    match request.method:
        case "POST":
            response = await session.post(url=url, json=data)
        case "PATCH":
            response = await session.patch(url=url, json=data)

    response_body = await response.json()
    return web.json_response(data=response_body, status=response.status)


