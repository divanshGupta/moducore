import uuid
from datetime import date
from pydantic import BaseModel, Field, ConfigDict

from src.apps.hospital.medicine.medicine_schemas import MedicineRead


class StockCreate(BaseModel):
    medicine_id: uuid.UUID
    batch_number: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=0)
    expiry_date: date


class StockAdjust(BaseModel):
    delta: int  # positive to add, negative to deduct
    reason: str = Field(min_length=1, max_length=255)


class StockBatchUpdate(BaseModel):
    batch_number: str | None = Field(default=None, min_length=1, max_length=100)
    expiry_date: date | None = None


class StockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    medicine: MedicineRead
    batch_number: str
    quantity: int
    expiry_date: date