from app.api.crud_factory import make_router
from app.db import models as m, schemas as s
from core.constants import (
    ROLE_HR_MANAGER,
    ROLE_PROJECT_MANAGER,
    ROLE_EMPLOYEE,
    ROLE_LND_MANAGER,
)

reusable_assets = make_router(
    m.ReusableAsset,
    s.ReusableAssetCreate,
    s.ReusableAssetUpdate,
    s.ReusableAssetOut,
    "/reusable-assets",
    ["Learning & Development"],
    allowed_roles=[ROLE_LND_MANAGER],
)
# Knowledge Repository - Merged into Reusable Asset (Temporarily Disabled)
# knowledge_repo = make_router(
#     m.KnowledgeRepo,
#     s.KnowledgeRepoCreate,
#     s.KnowledgeRepoUpdate,
#     s.KnowledgeRepoOut,
#     "/knowledge-repos",
#     ["Learning & Development"],
#     allowed_roles=[ROLE_EMPLOYEE, ROLE_LND_MANAGER],
# )
capability_building = make_router(
    m.CapabilityBuilding,
    s.CapabilityBuildingCreate,
    s.CapabilityBuildingUpdate,
    s.CapabilityBuildingOut,
    "/capability-buildings",
    ["Learning & Development"],
    allowed_roles=[
        ROLE_HR_MANAGER,
        ROLE_PROJECT_MANAGER,
        ROLE_EMPLOYEE,
        ROLE_LND_MANAGER,
    ],
)
partnership_alliance = make_router(
    m.PartnershipAlliance,
    s.PartnershipAllianceCreate,
    s.PartnershipAllianceUpdate,
    s.PartnershipAllianceOut,
    "/partnership-alliances",
    ["Learning & Development"],
    allowed_roles=[ROLE_HR_MANAGER, ROLE_LND_MANAGER],
)
tech_capability = make_router(
    m.TechCapability,
    s.TechCapabilityCreate,
    s.TechCapabilityUpdate,
    s.TechCapabilityOut,
    "/tech-capabilities",
    ["Learning & Development"],
    allowed_roles=[ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_LND_MANAGER],
)
innovation = make_router(
    m.InnovationAutomation,
    s.InnovationAutomationCreate,
    s.InnovationAutomationUpdate,
    s.InnovationAutomationOut,
    "/innovation-automations",
    ["Learning & Development"],
    allowed_roles=[ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER],
)
training_tracker = make_router(
    m.TrainingTracker,
    s.TrainingTrackerCreate,
    s.TrainingTrackerUpdate,
    s.TrainingTrackerOut,
    "/training-trackers",
    ["Learning & Development"],
    allowed_roles=[
        ROLE_HR_MANAGER,
        ROLE_PROJECT_MANAGER,
        ROLE_EMPLOYEE,
        ROLE_LND_MANAGER,
    ],
)
