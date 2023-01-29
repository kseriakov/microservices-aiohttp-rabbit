import asyncio
import logging
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from .settings import settings
from .service import get_products_with_inventory, proxy_request_on_service
from .handlers import get_aiohttp_session, close_aiohttp_session


logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get("/users/{id}/products")
async def get_user_products(request: Request) -> Response:
    session = app["client_session"]

    user_id = int(request.match_info["id"])

    products = asyncio.create_task(session.get(f"{settings.PRODUCTS_API_BASE}/products"))
    favorites = asyncio.create_task(
        session.get(f"{settings.FAVORITE_API_BASE}/users/{user_id}/favorites")
    )
    cart = asyncio.create_task(session.get(f"{settings.CART_API_BASE}/users/{user_id}/cart"))

    requests = [products, favorites, cart]
    done, pending = await asyncio.wait(requests, timeout=1)

    if products in pending:
        [r.cancel() for r in requests]
        return web.json_response(
            data={"error": "Timeout is over for the connect to the service inventory"},
            status=504,
        )
    elif products in done and products.exception() is not None:
        [r.cancel() for r in requests]
        logger.exception(
            msg="Error to the connection in service inventory", exc_info=products.exception()
        )
        return web.json_response(
            data={"error": "Error to the connection in service inventory"}, status=500
        )
    else:
        products_response = await products.result().json()
        products_response_with_stocks = await get_products_with_inventory(
            products_response, session
        )

        if favorites in pending:
            favorites.cancel()
            favorites_response = None
        elif favorites.exception() is not None:
            favorites.cancel()
            logger.exception(
                msg="Error to the connection in service favorite",
                exc_info=favorites.exception(),
            )
            favorites_response = None
        else:
            favorites_response = await favorites.result().json()

        if cart in pending:
            cart.cancel()
            cart_response = None
        elif cart.exception() is not None:
            cart.cancel()
            logger.exception(
                msg="Error to the connection in service cart", exc_info=cart.exception()
            )
            cart_response = None
        else:
            cart_response = await cart.result().json()

    return web.json_response(
        data={
            "products": products_response_with_stocks,
            "favorite_products": favorites_response,
            "cart_products": cart_response,
        },
    )


@routes.post("/users/cart")
async def add_product_in_cart(request: Request) -> Request:
    session = app["client_session"]
    return await proxy_request_on_service(request, session, f"{settings.CART_API_BASE}/users/cart")


@routes.post("/products")
async def add_new_product(request: Request) -> Response:
    session = app["client_session"]
    return await proxy_request_on_service(
        request, session, f"{settings.PRODUCTS_API_BASE}/products"
    )


@routes.patch("/products/inventory")
async def update_product_count_in_inventory(request: Request) -> Response:
    session = app["client_session"]
    return await proxy_request_on_service(
        request, session, f"{settings.INVENTORY_API_BASE}/products/inventory"
    )


@routes.post("/products/inventory")
async def create_product_in_inventory(request: Request) -> Response:
    session = app["client_session"]
    return await proxy_request_on_service(
        request, session, f"{settings.INVENTORY_API_BASE}/products/inventory"
    )


app = web.Application()
app.on_startup.append(get_aiohttp_session)
app._on_cleanup.append(close_aiohttp_session)

app.add_routes(routes)


web.run_app(app, host=settings.HOST_BASE, port=settings.PORT_BASE)
