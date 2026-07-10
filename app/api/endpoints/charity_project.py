from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_can_delete_charity_project,
    check_charity_project_exists,
    check_full_amount_not_less_than_invested,
    check_name_duplicate,
    check_project_not_closed,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment import close_charity_obj, invest

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: SessionDep,
):
    """Create a charity project.

    Superuser-only.
    """
    await check_name_duplicate(charity_project.name, session)
    new_project = await charity_project_crud.create(
        charity_project,
        session,
        commit=False,
    )
    open_donations = await donation_crud.get_not_invested(session)
    invest(new_project, open_donations)
    await session.commit()
    await session.refresh(new_project)
    return new_project


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(session: SessionDep):
    """Show the list of all charity projects."""
    return await charity_project_crud.get_multi(session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: SessionDep,
):
    """Edit a charity project.

    Superuser-only.

    Cannot edit a closed project;
    cannot set the goal price to less than an already invested amount.
    """
    project = await check_charity_project_exists(project_id, session)
    check_project_not_closed(project)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    if obj_in.full_amount is not None:
        check_full_amount_not_less_than_invested(project, obj_in.full_amount)
    project = await charity_project_crud.update(
        project, obj_in, session, commit=False
    )
    if project.invested_amount >= project.full_amount:
        close_charity_obj(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
    project_id: int,
    session: SessionDep,
):
    """Delete a charity project.

    Superuser-only.

    Cannot delete a project with funds already invested.
    """
    project = await check_charity_project_exists(project_id, session)
    check_project_not_closed(project)
    check_can_delete_charity_project(project)
    return await charity_project_crud.remove(project, session)
