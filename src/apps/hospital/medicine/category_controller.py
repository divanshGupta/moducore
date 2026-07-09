import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.apps.hospital.medicine.category_dependencies import get_category_service
from src.apps.hospital.medicine.category_schemas import CategoryCreate, CategoryUpdate, CategoryRead
from src.apps.hospital.medicine.category_service import (
    CategoryService,
    CategoryNotFoundError,
    DuplicateCategoryNameError,
    CategoryInUseError,
)
from src.modules.user.dependencies import require_permission

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post(
    "", response_model=CategoryRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("category.create"))],
)
async def create_category(
    data: CategoryCreate,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryRead:
    try:
        category = await service.create_category(name=data.name, description=data.description)
    except DuplicateCategoryNameError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return CategoryRead.model_validate(category)


@router.get(
    "", response_model=list[CategoryRead],
    dependencies=[Depends(require_permission("category.read"))],
)
async def list_categories(
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[CategoryRead]:
    categories = await service.list_all()
    return [CategoryRead.model_validate(c) for c in categories]


@router.get(
    "/{category_id}", response_model=CategoryRead,
    dependencies=[Depends(require_permission("category.read"))],
)
async def get_category(
    category_id: uuid.UUID,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryRead:
    category = await service.get_by_id(category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return CategoryRead.model_validate(category)


@router.patch(
    "/{category_id}", response_model=CategoryRead,
    dependencies=[Depends(require_permission("category.update"))],
)
async def update_category(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryRead:
    try:
        category = await service.update_category(
            category_id, name=data.name, description=data.description
        )
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateCategoryNameError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return CategoryRead.model_validate(category)


@router.delete(
    "/{category_id}", status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("category.delete"))],
)
async def delete_category(
    category_id: uuid.UUID,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> None:
    try:
        await service.delete_category(category_id)
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CategoryInUseError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))