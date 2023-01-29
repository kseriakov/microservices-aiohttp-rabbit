from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DB_PRODUCTS: str
    POSTGRES_USER_PRODUCTS: str
    POSTGRES_PASSWORD_PRODUCTS: str
    POSTGRES_HOST_PRODUCTS: str
    POSTGRES_PORT_PRODUCTS: int
    PORT_PRODUCTS: int
    HOST_PRODUCTS: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_HOST: str
    


settings = Settings()
