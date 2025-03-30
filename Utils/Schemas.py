from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
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


if __name__ == "__main__":
    print(
        VAL_UPSERT(name="Test Item", category="Electronics", price="99.99").model_dump()
    )
