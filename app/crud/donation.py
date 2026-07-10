from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.donation import Donation
from app.models.user import User


class CRUDDonation(CRUDBase):
    """CRUD operations for the Donation model."""

    async def get_by_user(
        self,
        user: User,
        session: AsyncSession,
    ):
        """Get all donations made by the requested user."""
        user_donation_objs = await session.execute(
            select(Donation).where(Donation.user_id == user.id)
        )
        return user_donation_objs.scalars().all()


donation_crud = CRUDDonation(Donation)
