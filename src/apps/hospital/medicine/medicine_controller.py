import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.apps.hospital.medicine.medicine_dependencies import get_medicine_service
from src.apps.hospital.medicine.medicine_schemas import MedicineCreate, MedicineUpdate, MedicineRead
from src.apps.hospital.medicine.medicine_service import (
    MedicineService,
    MedicineNotFoundError,
    InvalidCategoryError,
    InvalidSupplierError,
)
from src.modules.user.dependencies import require_permission

router = APIRouter(prefix="/medicines", tags=["medicines"])


@router.post(
    "", response_model=MedicineRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("medicine.create"))],
)
async def create_medicine(
    data: MedicineCreate,
    service: Annotated[MedicineService, Depends(get_medicine_service)],
) -> MedicineRead:
    try:
        medicine = await service.create_medicine(
            name=data.name, category_id=data.category_id, supplier_id=data.supplier_id
        )
    except InvalidCategoryError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InvalidSupplierError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return MedicineRead.model_validate(medicine)


@router.get(
    "", response_model=list[MedicineRead],
    dependencies=[Depends(require_permission("medicine.read"))],
)
async def list_medicines(
    service: Annotated[MedicineService, Depends(get_medicine_service)],
) -> list[MedicineRead]:
    medicines = await service.list_all()
    return [MedicineRead.model_validate(m) for m in medicines]


# Must stay ABOVE /{medicine_id} — see note above.
@router.get(
    "/search", response_model=list[MedicineRead],
    dependencies=[Depends(require_permission("medicine.read"))],
)
async def search_medicines(
    q: str,
    service: Annotated[MedicineService, Depends(get_medicine_service)],
) -> list[MedicineRead]:
    medicines = await service.search(q)
    return [MedicineRead.model_validate(m) for m in medicines]


@router.get(
    "/{medicine_id}", response_model=MedicineRead,
    dependencies=[Depends(require_permission("medicine.read"))],
)
async def get_medicine(
    medicine_id: uuid.UUID,
    service: Annotated[MedicineService, Depends(get_medicine_service)],
) -> MedicineRead:
    medicine = await service.get_by_id(medicine_id)
    if medicine is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    return MedicineRead.model_validate(medicine)


@router.patch(
    "/{medicine_id}", response_model=MedicineRead,
    dependencies=[Depends(require_permission("medicine.update"))],
)
async def update_medicine(
    medicine_id: uuid.UUID,
    data: MedicineUpdate,
    service: Annotated[MedicineService, Depends(get_medicine_service)],
) -> MedicineRead:
    try:
        medicine = await service.update_medicine(
            medicine_id,
            name=data.name,
            category_id=data.category_id,
            supplier_id=data.supplier_id,
        )
    except MedicineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidCategoryError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InvalidSupplierError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return MedicineRead.model_validate(medicine)


@router.delete(
    "/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("medicine.delete"))],
)
async def delete_medicine(
    medicine_id: uuid.UUID,
    service: Annotated[MedicineService, Depends(get_medicine_service)],
) -> None:
    try:
        await service.delete_medicine(medicine_id)
    except MedicineNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))