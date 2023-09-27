from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, NonNegativeInt, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]


class DonationCreate(DonationBase):
    class Config:
        extra = Extra.forbid


class DonationDB(DonationBase):
    id: int
    create_date: datetime
    user_id: int
    invested_amount: NonNegativeInt
    fully_invested: bool
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
