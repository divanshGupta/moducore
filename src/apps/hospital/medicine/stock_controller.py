import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.apps.hospital.medicine.stock_dependencies import get_stock_service
from src.apps.hospital.medicine.stock_schemas import (
    StockCreate, StockAdjust, StockBatchUpdate, StockRead,
)
from src.apps.hospital.medicine.stock_service import (
    StockService,
    StockNotFoundError,
    InvalidMedicineError,
    InsufficientStockError,
)
from src.modules.user.dependencies import require_permission

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.post(
    "", response_model=StockRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("stock.create"))],
)
async def create_stock(
    data: StockCreate,
    service: Annotated[StockService, Depends(get_stock_service)],
) -> StockRead:
    try:
        stock = await service.create_stock(
            medicine_id=data.medicine_id,
            batch_number=data.batch_number,
            quantity=data.quantity,
            expiry_date=data.expiry_date,
        )
    except InvalidMedicineError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InsufficientStockError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return StockRead.model_validate(stock)


@router.get(
    "", response_model=list[StockRead],
    dependencies=[Depends(require_permission("stock.read"))],
)
async def list_stocks(
    service: Annotated[StockService, Depends(get_stock_service)],
) -> list[StockRead]:
    stocks = await service.list_all()
    return [StockRead.model_validate(s) for s in stocks]


# Must stay ABOVE /{stock_id} — static path segments before dynamic ones.
@router.get(
    "/by-medicine/{medicine_id}", response_model=list[StockRead],
    dependencies=[Depends(require_permission("stock.read"))],
)
async def list_stocks_by_medicine(
    medicine_id: uuid.UUID,
    service: Annotated[StockService, Depends(get_stock_service)],
) -> list[StockRead]:
    stocks = await service.list_by_medicine(medicine_id)
    return [StockRead.model_validate(s) for s in stocks]


@router.get(
    "/{stock_id}", response_model=StockRead,
    dependencies=[Depends(require_permission("stock.read"))],
)
async def get_stock(
    stock_id: uuid.UUID,
    service: Annotated[StockService, Depends(get_stock_service)],
) -> StockRead:
    stock = await service.get_by_id(stock_id)
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")
    return StockRead.model_validate(stock)


@router.post(
    "/{stock_id}/adjust", response_model=StockRead,
    dependencies=[Depends(require_permission("stock.adjust"))],
)
async def adjust_stock(
    stock_id: uuid.UUID,
    data: StockAdjust,
    service: Annotated[StockService, Depends(get_stock_service)],
) -> StockRead:
    try:
        stock = await service.adjust_stock(stock_id, delta=data.delta, reason=data.reason)
    except StockNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InsufficientStockError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return StockRead.model_validate(stock)


@router.patch(
    "/{stock_id}", response_model=StockRead,
    dependencies=[Depends(require_permission("stock.update"))],
)
async def update_stock_batch(
    stock_id: uuid.UUID,
    data: StockBatchUpdate,
    service: Annotated[StockService, Depends(get_stock_service)],
) -> StockRead:
    try:
        stock = await service.update_batch_details(
            stock_id, batch_number=data.batch_number, expiry_date=data.expiry_date
        )
    except StockNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return StockRead.model_validate(stock)


@router.delete(
    "/{stock_id}", status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("stock.delete"))],
)
async def delete_stock(
    stock_id: uuid.UUID,
    service: Annotated[StockService, Depends(get_stock_service)],
) -> None:
    try:
        await service.delete_stock(stock_id)
    except StockNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))