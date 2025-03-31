from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List, Literal
from datetime import datetime


class VAL_UPSERT(BaseModel):
    name: str
    category: str
    price: float


class VAL_QUERY(BaseModel):
    dt_from: Optional[datetime] = None
    dt_to: Optional[datetime] = None
    category: Optional[str] = None

    @field_validator("category")
    def check_empty_str(cls, v):
        if v == "":
            raise ValueError(
                "Category cannot be an empty string. Kindly indicate null or omit the key entirely."
            )
        return v

    @model_validator(mode="after")
    def check_date_pair(self):
        # dt_from must be before dt_to
        if (self.dt_from and self.dt_to) and (self.dt_from > self.dt_to):
            raise ValueError("dt_from must be before dt_to")

        return self


class Filters(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price_range: List[float]

    @model_validator(mode="after")
    def check_price_range(self):
        # index 0 must be lesser than index 1
        if self.price_range[0] > self.price_range[1]:
            raise ValueError("Price at index 0 must be lesser than price at index 1.")

        return self


class Pagination(BaseModel):
    page: int
    limit: int


class Sort(BaseModel):
    field: Literal["name", "category", "price"]
    order: Literal["asc", "desc"]


class VAL_ADVANCE_QUERY(BaseModel):
    filters: Filters
    pagination: Pagination
    sort: Sort
