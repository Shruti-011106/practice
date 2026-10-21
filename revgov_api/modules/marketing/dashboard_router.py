from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.dependencies import get_current_active_user
from core.schemas import DashboardResponse
from auth.models import User

router = APIRouter(prefix="/marketing", tags=["Marketing Dashboard"])


@router.get("/dashboard-summary", response_model=DashboardResponse)
async def get_marketing_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    kpis = {
        "marketing_spend_ytd": 120000.00,
        "total_inbound_leads": 480,
        "avg_campaign_roi_pct": 310.5,
        "webinar_participants": 1420,
    }
    
    charts = {
        "lead_source_and_channel_share": [
            {"channel": "Events", "leads": 200},
            {"channel": "Social", "leads": 120},
            {"channel": "Email", "leads": 90},
            {"channel": "SEO", "leads": 70},
        ]
    }
    
    role_name = current_user.roles[0].name if current_user.roles else "EMPLOYEE"
    
    return DashboardResponse(
        role=role_name,
        kpis=kpis,
        charts=charts
    )
