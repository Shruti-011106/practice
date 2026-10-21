from app.api.crud_factory import make_router
from app.db import models as m, schemas as s
from core.constants import ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER

proposal_tracker = make_router(
    m.ProposalTracker,
    s.ProposalTrackerCreate,
    s.ProposalTrackerUpdate,
    s.ProposalTrackerOut,
    "/proposal-trackers",
    ["Presales"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER],
)
rfp_tracker = make_router(
    m.RFPTracker,
    s.RFPTrackerCreate,
    s.RFPTrackerUpdate,
    s.RFPTrackerOut,
    "/rfp-trackers",
    ["Presales"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER],
)
poc_tracker = make_router(
    m.POCTracker,
    s.POCTrackerCreate,
    s.POCTrackerUpdate,
    s.POCTrackerOut,
    "/poc-trackers",
    ["Presales"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER],
)
presales_bid = make_router(
    m.PresalesBID,
    s.PresalesBIDCreate,
    s.PresalesBIDUpdate,
    s.PresalesBIDOut,
    "/presales-bids",
    ["Presales"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER],
)
presales_demo = make_router(
    m.PresalesDemo,
    s.PresalesDemoCreate,
    s.PresalesDemoUpdate,
    s.PresalesDemoOut,
    "/presales-demos",
    ["Presales"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER],
)
presales_gov = make_router(
    m.PresalesGovernance,
    s.PresalesGovernanceCreate,
    s.PresalesGovernanceUpdate,
    s.PresalesGovernanceOut,
    "/presales-governances",
    ["Presales"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER],
)
