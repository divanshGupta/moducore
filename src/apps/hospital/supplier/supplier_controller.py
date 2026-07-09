import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.apps.hospital.supplier.supplier_dependencies import get_supplier_service
from src.apps.hospital.supplier.supplier_schemas import SupplierCreate, SupplierUpdate, SupplierRead
from src.apps.hospital.supplier.supplier_service import (
    SupplierService,
    SupplierNotFoundError,
    SupplierInUseError,
)
from src.modules.user.dependencies import require_permission

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.post(
    "", response_model=SupplierRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("supplier.create"))],
)
async def create_supplier(
    data: SupplierCreate,
    service: Annotated[SupplierService, Depends(get_supplier_service)],
) -> SupplierRead:
    supplier = await service.create_supplier(
        name=data.name, contact_email=data.contact_email, contact_phone=data.contact_phone
    )
    return SupplierRead.model_validate(supplier)


@router.get(
    "", response_model=list[SupplierRead],
    dependencies=[Depends(require_permission("supplier.read"))],
)
async def list_suppliers(
    service: Annotated[SupplierService, Depends(get_supplier_service)],
) -> list[SupplierRead]:
    suppliers = await service.list_all()
    return [SupplierRead.model_validate(s) for s in suppliers]


@router.get(
    "/{supplier_id}", response_model=SupplierRead,
    dependencies=[Depends(require_permission("supplier.read"))],
)
async def get_supplier(
    supplier_id: uuid.UUID,
    service: Annotated[SupplierService, Depends(get_supplier_service)],
) -> SupplierRead:
    supplier = await service.get_by_id(supplier_id)
    if supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return SupplierRead.model_validate(supplier)


@router.patch(
    "/{supplier_id}", response_model=SupplierRead,
    dependencies=[Depends(require_permission("supplier.update"))],
)
async def update_supplier(
    supplier_id: uuid.UUID,
    data: SupplierUpdate,
    service: Annotated[SupplierService, Depends(get_supplier_service)],
) -> SupplierRead:
    try:
        supplier = await service.update_supplier(
            supplier_id,
            name=data.name,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
        )
    except SupplierNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return SupplierRead.model_validate(supplier)


@router.delete(
    "/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("supplier.delete"))],
)
async def delete_supplier(
    supplier_id: uuid.UUID,
    service: Annotated[SupplierService, Depends(get_supplier_service)],
) -> None:
    try:
        await service.delete_supplier(supplier_id)
    except SupplierNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SupplierInUseError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))