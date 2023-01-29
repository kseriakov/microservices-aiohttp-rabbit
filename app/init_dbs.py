import asyncio

from cart.db.init import create_db as cart_init
from inventory.db.init import create_db as inventory_init
from favorite.db.init import create_db as favorite_init
from products.db.init import create_db as products_init


async def init_all_dbs():
    dbs = [
        asyncio.create_task(inventory_init()),
        asyncio.create_task(cart_init()),
        asyncio.create_task(favorite_init()),
        asyncio.create_task(products_init()),
    ]

    await asyncio.gather(*dbs)


if __name__ == "__main__":  
    asyncio.run(init_all_dbs())
