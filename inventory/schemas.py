from pydantic import BaseModel


class InventoryBase(BaseModel):
    product_id: int
    count: int

    class Config:
        orm_mode = True


class ProductInventoryCreate(InventoryBase):
    ...
    
    
class ProductInventoryUpdate(InventoryBase):
    ...


class ProductInventoryResponse(InventoryBase):
    ...


class AllProductsInventoryResponse(BaseModel):
    inventory: list[ProductInventoryResponse]

    class Config:
        orm_mode = True
