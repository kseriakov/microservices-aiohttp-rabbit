from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DB_INVENTORY: str
    POSTGRES_USER_INVENTORY: str
    POSTGRES_PASSWORD_INVENTORY: str
    POSTGRES_HOST_INVENTORY: str
    POSTGRES_PORT_INVENTORY: int
    PORT_INVENTORY: int
    HOST_INVENTORY: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_HOST: str


settings = Settings()
