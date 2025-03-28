from pydantic import BaseModel


class VAL_INSERT(BaseModel):
    name: str
    category: str
    price: float
