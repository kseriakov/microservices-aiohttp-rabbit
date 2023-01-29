from pydantic import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DB_FAVORITE: str
    POSTGRES_USER_FAVORITE: str
    POSTGRES_PASSWORD_FAVORITE: str
    POSTGRES_HOST_FAVORITE: str
    POSTGRES_PORT_FAVORITE: int
    PORT_FAVORITE: int
    HOST_FAVORITE: str


settings = Settings()
