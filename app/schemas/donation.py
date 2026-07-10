from datetime import datetime

from pydantic import BaseModel, ConfigDict, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt
    comment: str | None = None

    model_config = ConfigDict(extra='forbid')


class DonationCreate(DonationBase):
    pass


class DonationDB(DonationCreate):
    """Shown to the donor: on creation, and in their own donation list."""

    id: int
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationDB):
    """Shown to superusers: full donation info, including distribution."""

    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: datetime | None = None
