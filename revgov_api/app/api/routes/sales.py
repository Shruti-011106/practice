from app.api.crud_factory import make_router
from app.db import models as m, schemas as s
from core.constants import (
    ROLE_SALES_MANAGER,
    ROLE_PRESALES_MANAGER,
    ROLE_MARKETING_MANAGER,
)

lead_tracker = make_router(
    m.LeadTracker,
    s.LeadTrackerCreate,
    s.LeadTrackerUpdate,
    s.LeadTrackerOut,
    "/lead-trackers",
    ["Sales"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER],
)
sales_revenue_tracker = make_router(
    m.SalesRevenueTracker,
    s.SalesRevenueTrackerCreate,
    s.SalesRevenueTrackerUpdate,
    s.SalesRevenueTrackerOut,
    "/sales-revenue-trackers",
    ["Sales"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER],
)
sales_pipeline = make_router(
    m.SalesPipeline,
    s.SalesPipelineCreate,
    s.SalesPipelineUpdate,
    s.SalesPipelineOut,
    "/sales-pipelines",
    ["Sales"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER],
)
