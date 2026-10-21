from app.api.crud_factory import make_router
from app.db import models as m, schemas as s
from core.constants import ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER

qbr = make_router(
    m.QBRTracker,
    s.QBRTrackerCreate,
    s.QBRTrackerUpdate,
    s.QBRTrackerOut,
    "/qbr-trackers",
    ["Customer Success"],
    allowed_roles=[ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER],
)
escalations = make_router(
    m.EscalationTracker,
    s.EscalationTrackerCreate,
    s.EscalationTrackerUpdate,
    s.EscalationTrackerOut,
    "/escalation-trackers",
    ["Customer Success"],
    allowed_roles=[ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER],
)
revenue = make_router(
    m.RevenueTracker,
    s.RevenueTrackerCreate,
    s.RevenueTrackerUpdate,
    s.RevenueTrackerOut,
    "/revenue-trackers",
    ["Customer Success"],
    allowed_roles=[ROLE_FINANCE_MANAGER, ROLE_CS_MANAGER],
)
executive_connect = make_router(
    m.ExecutiveContentTracker,
    s.ExecutiveContentTrackerCreate,
    s.ExecutiveContentTrackerUpdate,
    s.ExecutiveContentTrackerOut,
    "/executive-connect-trackers",
    ["Customer Success"],
    allowed_roles=[ROLE_CS_MANAGER],
)
