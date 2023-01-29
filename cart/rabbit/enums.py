from enum import Enum


class RabbitExchange(Enum):
    INVENTORY = "inventory"


class RabbitRoutingKey(Enum):
    DELETE_PRODUCT = "delete"
    ADD_PRODUCT = "add"
