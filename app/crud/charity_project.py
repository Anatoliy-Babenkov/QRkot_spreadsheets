from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDProject(CRUDBase):
    async def get_project_id_by_name(
        self, project_name: str, session: AsyncSession
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(CharityProject.name == project_name)
        )
        return db_project_id.scalars().first()

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession,
    ) -> List[Dict[str, str]]:
        charity_projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested == 1
            )
        )
        charity_projects = charity_projects.scalars().all()
        projects_list = []
        for project in charity_projects:
            fund_time = str(project.close_date - project.create_date)
            projects_list.append({
                'name': project.name,
                'fund_time': fund_time,
                'description': project.description
            })
        projects_list = sorted(projects_list, key=lambda x: x['fund_time'])
        return projects_list


project_crud = CRUDProject(CharityProject)
