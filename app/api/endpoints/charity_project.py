from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.services import invest_new_project, patch_project_full_invested
from app.api.validators import (
    check_name_duplicate,
    check_project_delete_possibility,
    check_project_exists,
    check_project_update_possibility,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import project_crud
from app.models import CharityProject
from app.schemas.charity_project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.post(
    '/',
    response_model=ProjectResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_project(
    project: ProjectCreate, session: AsyncSession = Depends(get_async_session)
):
    '''Только для суперюзеров.'''

    await check_name_duplicate(project.name, session)

    new_project = await project_crud.create(project, session)

    await invest_new_project(new_project, session)
    return new_project


@router.get('/', response_model=list[ProjectResponse], response_model_exclude_none=True)
async def get_all_projects(session: AsyncSession = Depends(get_async_session)):
    return await project_crud.get_multi(session)


@router.patch(
    '/{project_id}',
    response_model=ProjectResponse,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_project(
    project_id: int,
    obj_in: ProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    '''Только для суперюзеров.'''

    project = await check_project_exists(project_id, session)

    await check_project_update_possibility(project, obj_in, session)
    project: CharityProject = await project_crud.update(project, obj_in, session)

    if obj_in.full_amount:
        await patch_project_full_invested(project, session)
    return project


@router.delete(
    '/{project_id}',
    response_model=ProjectResponse,
    dependencies=[Depends(current_superuser)],
)
async def remove_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    '''Только для суперюзеров.'''

    await check_project_exists(project_id, session)
    project = await check_project_delete_possibility(project_id, session)
    project = await project_crud.remove(project, session)
    return project
