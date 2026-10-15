from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InventoryItemCreate(BaseModel):
    inventory_type: str
    category: str
    sub_category: Optional[str] = None

    asset_tag: str
    status: str

    vendor: Optional[str] = None
    module_number: Optional[str] = None
    serial_number: Optional[str] = None

    configuration: Optional[str] = None
    operating_system: Optional[str] = None
    antivirus: Optional[str] = None

    purchase_date: Optional[date] = None
    warranty_expiry: Optional[date] = None
    usage_year: Optional[int] = None
    retirement_date: Optional[date] = None


class InventoryItemUpdate(BaseModel):
    inventory_type: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None

    asset_tag: Optional[str] = None
    status: Optional[str] = None

    vendor: Optional[str] = None
    module_number: Optional[str] = None
    serial_number: Optional[str] = None

    configuration: Optional[str] = None
    operating_system: Optional[str] = None
    antivirus: Optional[str] = None

    purchase_date: Optional[date] = None
    warranty_expiry: Optional[date] = None
    usage_year: Optional[int] = None
    retirement_date: Optional[date] = None


class InventoryItemResponse(InventoryItemCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)