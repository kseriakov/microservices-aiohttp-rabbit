from pydantic import HttpUrl, BaseSettings


class Settings(BaseSettings):
    HOST_BASE: str
    PORT_BASE: int
    HOST_CART: str
    PORT_CART: int
    HOST_INVENTORY: str
    PORT_INVENTORY: int
    HOST_FAVORITE: str
    PORT_FAVORITE: int
    HOST_PRODUCTS: str
    PORT_PRODUCTS: int
    CART_API_BASE: HttpUrl | None
    INVENTORY_API_BASE: HttpUrl | None
    FAVORITE_API_BASE: HttpUrl | None
    PRODUCTS_API_BASE: HttpUrl | None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.CART_API_BASE = f"http://{self.HOST_CART}:{self.PORT_CART}"
        self.INVENTORY_API_BASE = f"http://{self.HOST_INVENTORY}:{self.PORT_INVENTORY}"
        self.PRODUCTS_API_BASE = f"http://{self.HOST_PRODUCTS}:{self.PORT_PRODUCTS}"
        self.FAVORITE_API_BASE = f"http://{self.HOST_FAVORITE}:{self.PORT_FAVORITE}"


settings = Settings()
