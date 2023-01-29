from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DB_CART: str
    POSTGRES_USER_CART: str
    POSTGRES_PASSWORD_CART: str
    POSTGRES_HOST_CART: str
    POSTGRES_PORT_CART: int
    PORT_CART: int
    HOST_CART: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_HOST: str


settings = Settings()
