from app.api.crud_factory import make_router
from app.db import models as m, schemas as s
from core.constants import ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER

po_tracker = make_router(
    m.POTracker,
    s.POTrackerCreate,
    s.POTrackerUpdate,
    s.POTrackerOut,
    "/po-trackers",
    ["Finance & Procurement"],
    allowed_roles=[ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER],
)
invoice_tracker = make_router(
    m.InvoiceTracker,
    s.InvoiceTrackerCreate,
    s.InvoiceTrackerUpdate,
    s.InvoiceTrackerOut,
    "/invoice-trackers",
    ["Finance & Procurement"],
    allowed_roles=[ROLE_FINANCE_MANAGER],
)
budget_tracker = make_router(
    m.BudgetTracker,
    s.BudgetTrackerCreate,
    s.BudgetTrackerUpdate,
    s.BudgetTrackerOut,
    "/budget-trackers",
    ["Finance & Procurement"],
    allowed_roles=[ROLE_FINANCE_MANAGER],
)
