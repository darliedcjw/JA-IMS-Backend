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

    @model_validator(mode="after")
    def check_date_pair(self):
        # Both must be empty or present
        if (self.dt_from is None) != (self.dt_to is None):
            raise ValueError(
                "Both dt_from and dt_to must be provided or omitted together"
            )

        # dt_from must be before dt_to
        elif self.dt_from > self.dt_to:
            raise ValueError("dt_from must be before dt_to")

        return self
