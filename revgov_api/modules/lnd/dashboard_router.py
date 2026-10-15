from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.dependencies import get_current_active_user
from core.schemas import DashboardResponse
from auth.models import User

router = APIRouter(prefix="/lnd", tags=["L&D Dashboard"])


@router.get("/dashboard-summary", response_model=DashboardResponse)
async def get_lnd_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    kpis = {
        "certified_tech_resources": 95,
        "practice_readiness_score": 8.4,
        "alliance_revenue": 1450000.00,
        "asset_reuse_velocity": 42,
    }
    
    charts = {
        "training_hours_completed_by_dept": [
            {"department": "Engineering", "hours": 450},
            {"department": "Operations", "hours": 320},
            {"department": "Sales", "hours": 150},
        ]
    }
    
    role_name = current_user.roles[0].name if current_user.roles else "EMPLOYEE"
    
    return DashboardResponse(
        role=role_name,
        kpis=kpis,
        charts=charts
    )
