from pydantic import BaseModel

class ProductRequest(BaseModel):
    product_name: str
