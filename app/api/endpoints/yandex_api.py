from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.core.yandex_client import YandexDiskClient, get_yandex_client
from app.crud.charity_project import charity_project_crud
from app.services.yandex_api import create_simple_report

router = APIRouter()


@router.post(
    '/',
    response_model=str,
    dependencies=(Depends(current_superuser),),
    summary='Создать Excel-отчёт на Яндекс Диске',
    description=(
        'Создаёт Excel-файл с отчётом по закрытым целевым проектам,'
        'отсортированным по скорости сбора средств. Файл сохраняется на'
        'Яндекс Диске в папке "QRKot Reports" и становится доступен по'
        'публичной ссылке. \n\n'
        'Требуются права суперпользователя.'
    ),
)
async def get_report(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    yandex_client: Annotated[YandexDiskClient, Depends(get_yandex_client)],
) -> str:
    """Create an Excel report of closed projects and upload it to Disk."""
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )
    if not projects:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Нет закрытых проектов для формирования отчёта',
        )
    try:
        public_url = await create_simple_report(projects, yandex_client)
    except Exception as error:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при создании отчёта: {error}',
        ) from error
    return public_url
