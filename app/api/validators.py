from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import project_crud
from app.models import CharityProject
from app.schemas.charity_project import ProjectDB, ProjectUpdate


async def check_name_duplicate(project_name: str, session: AsyncSession) -> None:
    project_id = await project_crud.get_project_id_by_name(project_name, session)
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!',
        )


async def check_project_exists(
    project_id: int, session: AsyncSession
) -> CharityProject:
    project = await project_crud.get(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Проект не найден!'
        )
    return project


async def check_greater_than_invested(
    new_value: int, project: CharityProject
) -> CharityProject:
    if project.invested_amount > new_value:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Новая сумма инвестирования меньше чем внесенные средства',
        )
    return project


async def check_project_update_possibility(
    old_obj: ProjectDB, new_data: ProjectUpdate, session: AsyncSession
) -> None:
    if not any([new_data.name, new_data.description, new_data.full_amount]):
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Необходимо ввести новые данные',
        )
    if new_data.name:
        await check_name_duplicate(new_data.name, session)
    if new_data.description == '':
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Описание не должно быть пустым',
        )
    if new_data.full_amount:
        await check_greater_than_invested(new_data.full_amount, old_obj)
    if old_obj.fully_invested is True:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )


async def check_project_delete_possibility(
    project_id: int, session: AsyncSession
) -> CharityProject:
    project = await project_crud.get(obj_id=project_id, session=session)
    if project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!',
        )
    return project
