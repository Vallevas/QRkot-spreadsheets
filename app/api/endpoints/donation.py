from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investment import invest

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
UserDep = Annotated[User, Depends(current_user)]


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
)
async def create_donation(
    donation: DonationCreate,
    session: SessionDep,
    user: UserDep,
):
    """Make a donation.

    Registered users-only.
    """
    new_donation = await donation_crud.create(
        donation,
        session,
        user=user,
        commit=False,
    )
    open_projects = await charity_project_crud.get_not_invested(session)
    invest(new_donation, open_projects)
    await session.commit()
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/',
    response_model=list[DonationFullInfoDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(session: SessionDep):
    """Show the list of all donations.

    Superuser-only.
    """
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
)
async def get_user_donations(
    user: UserDep,
    session: SessionDep,
):
    """Show the list of all donations made by the requesting user.

    Registered users-only.
    """
    return await donation_crud.get_by_user(user, session)
