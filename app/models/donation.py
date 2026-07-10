from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import CharityDonationBase


class Donation(CharityDonationBase):
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey('user.id', name='fk_donation_user_id_user'),
        nullable=True,
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f'Пожертвование на сумму {self.full_amount}.'
