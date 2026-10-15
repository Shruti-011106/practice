from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.dependencies import get_current_active_user
from core.schemas import DashboardResponse
from auth.models import User

router = APIRouter(prefix="/presales", tags=["Pre-Sales Dashboard"])


@router.get("/dashboard-summary", response_model=DashboardResponse)
async def get_presales_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    kpis = {
        "bid_win_rate_pct": 42.5,
        "active_rfps_in_solutioning": 9,
        "poc_outcome_success_rate_pct": 88.0,
        "demo_ready_reusable_assets": 14,
    }
    
    charts = {
        "rfp_pipeline_by_stage": [
            {"stage": "Received", "count": 12},
            {"stage": "In Progress", "count": 9},
            {"stage": "Submitted", "count": 15},
            {"stage": "Won", "count": 8},
        ]
    }
    
    role_name = current_user.roles[0].name if current_user.roles else "EMPLOYEE"
    
    return DashboardResponse(
        role=role_name,
        kpis=kpis,
        charts=charts
    )
