from app.api.crud_factory import make_router
from app.db import models as m, schemas as s
from core.constants import (
    ROLE_SALES_MANAGER,
    ROLE_PRESALES_MANAGER,
    ROLE_MARKETING_MANAGER,
)

events = make_router(
    m.EventWebinar,
    s.EventWebinarCreate,
    s.EventWebinarUpdate,
    s.EventWebinarOut,
    "/event-webinars",
    ["Marketing"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER],
)
content = make_router(
    m.ContentBranding,
    s.ContentBrandingCreate,
    s.ContentBrandingUpdate,
    s.ContentBrandingOut,
    "/content-brandings",
    ["Marketing"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER],
)
campaigns = make_router(
    m.Campaign,
    s.CampaignCreate,
    s.CampaignUpdate,
    s.CampaignOut,
    "/campaigns",
    ["Marketing"],
    allowed_roles=[ROLE_SALES_MANAGER, ROLE_PRESALES_MANAGER, ROLE_MARKETING_MANAGER],
)
