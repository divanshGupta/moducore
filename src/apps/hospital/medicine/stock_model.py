import uuid
from datetime import date

from sqlalchemy import ForeignKey, Date, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database.base import HospitalBase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.apps.hospital.medicine.medicine_model import Medicine


class Stock(HospitalBase):
    __tablename__ = "stocks"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_stocks_quantity_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    medicine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hospital.medicines.id", ondelete="RESTRICT"),
        nullable=False,
    )
    medicine: Mapped["Medicine"] = relationship(lazy="selectin")

    batch_number: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)