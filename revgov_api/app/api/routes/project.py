from app.api.crud_factory import make_router
from app.db import models as m, schemas as s
from core.constants import (
    ROLE_HR_MANAGER,
    ROLE_FINANCE_MANAGER,
    ROLE_PROJECT_MANAGER,
    ROLE_CS_MANAGER,
)

project_gov = make_router(
    m.ProjectGovernance,
    s.ProjectGovernanceCreate,
    s.ProjectGovernanceUpdate,
    s.ProjectGovernanceOut,
    "/project-governances",
    ["Project Governance"],
    allowed_roles=[ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER],
)
deliverables = make_router(
    m.DeliverableTracker,
    s.DeliverableTrackerCreate,
    s.DeliverableTrackerUpdate,
    s.DeliverableTrackerOut,
    "/deliverable-trackers",
    ["Project Governance"],
    allowed_roles=[ROLE_PROJECT_MANAGER],
)
csat = make_router(
    m.CustomerSatisfaction,
    s.CustomerSatisfactionCreate,
    s.CustomerSatisfactionUpdate,
    s.CustomerSatisfactionOut,
    "/customer-satisfactions",
    ["Project Governance"],
    allowed_roles=[ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER],
)
qa = make_router(
    m.QATracker,
    s.QATrackerCreate,
    s.QATrackerUpdate,
    s.QATrackerOut,
    "/qa-trackers",
    ["Project Governance"],
    allowed_roles=[ROLE_PROJECT_MANAGER],
)
change_requests = make_router(
    m.ChangeRequest,
    s.ChangeRequestCreate,
    s.ChangeRequestUpdate,
    s.ChangeRequestOut,
    "/change-requests",
    ["Project Governance"],
    allowed_roles=[ROLE_PROJECT_MANAGER],
)
resource_util = make_router(
    m.ResourceUtilization,
    s.ResourceUtilizationCreate,
    s.ResourceUtilizationUpdate,
    s.ResourceUtilizationOut,
    "/resource-utilizations",
    ["Project Governance"],
    allowed_roles=[ROLE_HR_MANAGER, ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER],
)
raid = make_router(
    m.RAID,
    s.RAIDCreate,
    s.RAIDUpdate,
    s.RAIDOut,
    "/raids",
    ["Project Governance"],
    allowed_roles=[ROLE_PROJECT_MANAGER],
)
