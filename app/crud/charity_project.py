from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    """CRUD operations for the CharityProject model."""

    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> int | None:
        """Get a project's ID by its provided name."""
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return db_project_id.scalars().first()

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> list[CharityProject]:
        """Get closed projects, fastest-gathered first."""
        db_objs = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(True)
            )
        )
        projects = db_objs.scalars().all()
        return sorted(
            projects,
            key=lambda project: project.close_date - project.create_date,
        )


charity_project_crud = CRUDCharityProject(CharityProject)
