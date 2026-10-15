from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from core.schemas import OrmBase


class POTrackerBase(BaseModel):
    po_number: Optional[str] = None
    request_order_id: Optional[int] = None
    vendor_id: Optional[int] = None
    po_date: Optional[date] = None
    expiry_date: Optional[date] = None
    delivery_date: Optional[date] = None
    amount: Optional[float] = 0
    department_id: Optional[int] = None
    approval_status: Optional[str] = "Pending Approval"
    po_status: Optional[str] = "Open"
    remarks: Optional[str] = None
    finance_owner_id: Optional[int] = None


class POTrackerCreate(POTrackerBase):
    pass


class POTrackerUpdate(POTrackerBase):
    pass


class POTrackerOut(OrmBase, POTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    vendor_name: Optional[str] = None
    department_name: Optional[str] = None
    project_name: Optional[str] = None


class POTrackerKPIs(BaseModel):
    total_pos: int = 0
    pending_approval: int = 0
    completed: int = 0
    total_amount: float = 0


class POTrackerListWithKPIs(BaseModel):
    kpis: POTrackerKPIs
    data: List[POTrackerOut]


class InvoiceTrackerBase(BaseModel):
    invoice_number: Optional[str] = None
    po_id: Optional[int] = None
    vendor_id: Optional[int] = None
    invoice_date: Optional[date] = None
    invoice_amount: Optional[float] = 0
    tax: Optional[float] = 0
    due_date: Optional[date] = None
    payment_status: Optional[str] = "Open"
    remarks: Optional[str] = None
    finance_owner_id: Optional[int] = None


class InvoiceTrackerCreate(InvoiceTrackerBase):
    pass


class InvoiceTrackerUpdate(InvoiceTrackerBase):
    pass


class InvoiceTrackerOut(OrmBase, InvoiceTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    vendor_name: Optional[str] = None
    po_number: Optional[str] = None


class InvoiceTrackerKPIs(BaseModel):
    total_invoices: int = 0
    pending_approval: int = 0
    completed: int = 0
    total_amount: float = 0


class InvoiceTrackerListWithKPIs(BaseModel):
    kpis: InvoiceTrackerKPIs
    data: List[InvoiceTrackerOut]


class BudgetTrackerBase(BaseModel):
    project_id: Optional[int] = None
    budget: Optional[float] = 0
    consumed: Optional[float] = 0
    remaining: Optional[float] = 0
    forecast: Optional[float] = 0
    variance: Optional[float] = 0
    approval_status: Optional[str] = "Pending Approval"
    remarks: Optional[str] = None
    finance_owner_id: Optional[int] = None


class BudgetTrackerCreate(BudgetTrackerBase):
    project_id: int


class BudgetTrackerUpdate(BudgetTrackerBase):
    pass


class BudgetTrackerOut(OrmBase, BudgetTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project_name: Optional[str] = None


class BudgetTrackerKPIs(BaseModel):
    total_projects: int = 0
    pending_approval: int = 0
    total_budget: float = 0
    total_remaining_budget: float = 0


class BudgetTrackerListWithKPIs(BaseModel):
    kpis: BudgetTrackerKPIs
    data: List[BudgetTrackerOut]


class RequestOrderTrackerBase(BaseModel):
    department_id: Optional[int] = None
    project_id: Optional[int] = None
    vendor_id: Optional[int] = None
    item: Optional[str] = None
    cost: Optional[float] = 0
    approval_status: Optional[str] = "Pending Approval"
    reason: Optional[str] = None
    finance_owner_id: Optional[int] = None

class RequestOrderTrackerCreate(RequestOrderTrackerBase):
    project_id: int


class RequestOrderTrackerUpdate(RequestOrderTrackerBase):
    pass


class RequestOrderTrackerOut(OrmBase, RequestOrderTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    department_name: Optional[str] = None
    project_name: Optional[str] = None
    vendor_name: Optional[str] = None


class RequestOrderTrackerKPIs(BaseModel):
    total_requests: int = 0
    pending_approval: int = 0
    approved_requests: int = 0
    total_cost: float = 0


class RequestOrderTrackerListWithKPIs(BaseModel):
    kpis: RequestOrderTrackerKPIs
    data: List[RequestOrderTrackerOut]


class PaymentTrackerBase(BaseModel):
    payment_id: Optional[str] = None
    invoice_id: Optional[int] = None
    vendor_id: Optional[int] = None
    amount: Optional[float] = 0
    method: Optional[str] = "Bank Transfer"
    reference: Optional[str] = None
    status: Optional[str] = "Pending"
    remarks: Optional[str] = None
    finance_owner_id: Optional[int] = None


class PaymentTrackerCreate(PaymentTrackerBase):
    invoice_id: int


class PaymentTrackerUpdate(PaymentTrackerBase):
    pass


class PaymentTrackerOut(OrmBase, PaymentTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None


class PaymentTrackerKPIs(BaseModel):
    total_payments: int = 0
    completed_payments: int = 0
    pending_payments: int = 0
    total_amount: float = 0


class PaymentTrackerListWithKPIs(BaseModel):
    kpis: PaymentTrackerKPIs
    data: List[PaymentTrackerOut]


class RevenueTrackerBase(BaseModel):
    revenue_id: Optional[str] = None
    month: Optional[str] = None
    sales_owner_id: Optional[int] = None
    payment_id: Optional[int] = None
    target_revenue: Optional[float] = 0
    achieved_revenue: Optional[float] = 0
    region: Optional[str] = None
    status: Optional[str] = "Open"
    remarks: Optional[str] = None


class RevenueTrackerCreate(RevenueTrackerBase):
    pass


class RevenueTrackerUpdate(RevenueTrackerBase):
    pass


class RevenueTrackerOut(OrmBase, RevenueTrackerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    sales_owner_name: Optional[str] = None
    payment_reference: Optional[str] = None


class RevenueTrackerKPIs(BaseModel):
    total_records: int = 0
    completed_records: int = 0
    total_target_revenue: float = 0
    total_achieved_revenue: float = 0


class RevenueTrackerListWithKPIs(BaseModel):
    kpis: RevenueTrackerKPIs
    data: List[RevenueTrackerOut]

