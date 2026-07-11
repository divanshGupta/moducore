from decimal import Decimal
from pydantic import BaseModel

class DashboardSummary(BaseModel):
    total_medicines: int
    low_stock_count: int
    expiring_soon_count: int
    out_of_stock_count: int
    today_purchases_count: int
    today_purchases_total: Decimal