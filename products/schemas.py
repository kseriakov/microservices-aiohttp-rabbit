from pydantic import condecimal
from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    price: condecimal(max_digits=5, decimal_places=2)

    class Config:
        orm_mode = True


class ProductCreate(ProductBase):
    ...


class ProductShow(ProductBase):
    id: int


class AllProductsResponse(BaseModel):
    products: list[ProductShow]

    class Config:
        orm_mode = True
