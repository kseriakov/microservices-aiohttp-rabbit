import logging
import asyncpg
import asyncio
import json
from typing import Callable
from aio_pika import ExchangeType, connect_robust, RobustChannel
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection
from aio_pika.pool import Pool

from ..logs.config import get_logger
from .enums import RabbitExchange, RabbitRoutingKey
from ..settings import settings
from ..db.connection import db_pool


logger = get_logger("inventory consumer")


class InventoryConsumer:
    def __init__(self, db_connect: Callable[[None], asyncpg.Pool], loop: asyncio.AbstractEventLoop):
        """Инициализируем пулы соединений и каналов RabbitMQ"""
        self.rabbit_url = f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@{settings.RABBITMQ_HOST}/"
        self.__db_connect = db_connect
        self.db_pool = None
        self.loop = loop

        self.connection_pool = Pool(self.get_connection, max_size=2, loop=self.loop)
        self.channel_pool = Pool(self.get_channel, max_size=5, loop=self.loop)

    async def set_db_pool(self):
        self.db_pool = await self.__db_connect()

    async def get_connection(self) -> AbstractRobustConnection:
        return await connect_robust(self.rabbit_url)

    async def get_channel(self) -> RobustChannel:
        async with self.connection_pool.acquire() as connection:
            return await connection.channel()

    async def _create_consumer(self, callback: Callable, exchange_name: str, routing_key: str):
        async with self.channel_pool.acquire() as channel:
            exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT)
            queue = await channel.declare_queue(durable=True)
            await queue.bind(exchange, routing_key=routing_key)
            await queue.consume(callback, no_ack=True)

            # Для того, чтобы consumer не завершал работу
            await asyncio.Future()

    @staticmethod
    def parse_message_data(message: AbstractIncomingMessage) -> dict:
        return json.loads(message.body)

    async def on_message_delete_product(self, message: AbstractIncomingMessage) -> None:
        body = self.parse_message_data(message)
        product_id = body["product_id"]

        async with self.db_pool.acquire() as conn:
            query = """UPDATE inventory SET count = count - 1 WHERE product_id = $1"""
            res = await conn.execute(query, product_id)

            if res[-1] == "1":
                logger.info(f"Successful deleted one product (id = {product_id}) from inventory")
            else:
                logger.info(
                    f"Product (id = {product_id}) does not exists in inventory. Operation deleting failed"
                )

    async def consumer_delete(self):
        await self._create_consumer(
            self.on_message_delete_product,
            RabbitExchange.INVENTORY.value,
            RabbitRoutingKey.DELETE_PRODUCT.value,
        )

    async def on_message_add_product(self, message: AbstractIncomingMessage) -> None:
        body = self.parse_message_data(message)
        product_id = body["product_id"]

        async with self.db_pool.acquire() as conn:
            query = """UPDATE inventory SET count = count + 1 WHERE product_id = $1"""
            res = await conn.execute(query, product_id)

            if res[-1] == "1":
                logger.info(f"Successful added one product (id = {product_id}) to inventory")
            else:
                logger.info(
                    f"Product (id = {product_id}) does not exists in inventory. Operation adding failed"
                )

    async def consumer_add(self):
        await self._create_consumer(
            self.on_message_add_product,
            RabbitExchange.INVENTORY.value,
            RabbitRoutingKey.ADD_PRODUCT.value,
        )

    async def run_consumers(self):
        await self.set_db_pool()

        tasks = [
            self.loop.create_task(self.consumer_delete()),
            self.loop.create_task(self.consumer_add()),
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        inventory_consumer = InventoryConsumer(db_pool, loop)
        loop.run_until_complete(inventory_consumer.run_consumers())
    except Exception as err:
        logger.error("Error with InventoryConsumer", exc_info=str(err))
        loop.close()
