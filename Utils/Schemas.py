from pydantic import BaseModel


class VAL_UPSERT(BaseModel):
    name: str
    category: str
    price: float
