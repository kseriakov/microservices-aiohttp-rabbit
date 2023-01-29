import asyncio
import json
from aio_pika import DeliveryMode, ExchangeType, Message, RobustChannel, connect, connect_robust
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool

from ..settings import settings
from .enums import RabbitExchange, RabbitRoutingKey


class CartSender:
    def __init__(self):
        self.rabbit_url = f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@{settings.RABBITMQ_HOST}/"

        self.loop = asyncio.get_event_loop()
        self.connection_pool = Pool(self.get_connection, max_size=2, loop=self.loop)
        self.channel_pool = Pool(self.get_channel, max_size=5, loop=self.loop)

    async def get_connection(self) -> AbstractRobustConnection:
        return await connect_robust(self.rabbit_url)

    async def get_channel(self) -> RobustChannel:
        async with self.connection_pool.acquire() as connection:
            return await connection.channel()

    async def _send_message(self, exchange_name: str, routing_key: str, body: dict) -> None:
        async with self.channel_pool.acquire() as channel:
            # Creating exchange
            exchange = await channel.declare_exchange(
                exchange_name,
                ExchangeType.DIRECT,
            )

            data = json.dumps(body, indent=2).encode("UTF-8")

            # Sending the message
            await exchange.publish(
                Message(data, delivery_mode=DeliveryMode.PERSISTENT),
                routing_key=routing_key,
            )

    async def get_product_from_inventory(self, body: dict) -> None:
        return await self._send_message(
            RabbitExchange.INVENTORY.value, RabbitRoutingKey.DELETE_PRODUCT.value, body
        )

    async def return_product_to_inventory(self, body: dict) -> None:
        return await self._send_message(
            RabbitExchange.INVENTORY.value, RabbitRoutingKey.ADD_PRODUCT.value, body
        )
