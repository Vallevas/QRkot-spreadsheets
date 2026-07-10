from dataclasses import dataclass

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.models import User


@dataclass
class CRUDBase:
    """Base class for CRUD operations in app models."""

    model: type[Base]

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        """Get an object by its provided ID."""
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession):
        """Get all objects of the provided model."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def get_not_invested(self, session: AsyncSession):
        """Get all not-yet-fully-invested objects, oldest first."""
        db_objs = await session.execute(
            select(self.model)
            .where(self.model.fully_invested.is_(False))
            .order_by(self.model.create_date, self.model.id)
        )
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
        user: User | None = None,
        commit: bool = True,
    ):
        """Add a row to the DB.

        Set commit=False to defer the transaction.
        """
        obj_in_data = obj_in.model_dump()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        # Flush (without commit) so Python-side column defaults —
        # invested_amount, fully_invested, create_date — are populated
        # on the instance even when the caller wants to defer the commit
        # (e.g. to run investment logic in the same transaction).
        await session.flush()
        if commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
        commit: bool = True,
    ):
        """Update a row.

        Set commit=False to defer the transaction.
        """
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        if commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        """Remove the row."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj
