from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.dependencies import get_current_active_user
from core.schemas import DashboardResponse
from auth.models import User

router = APIRouter(prefix="/project", tags=["Project Dashboard"])


@router.get("/dashboard-summary", response_model=DashboardResponse)
async def get_project_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    kpis = {
        "active_delivery_projects": 34,
        "milestone_on_time_delivery_pct": 87.5,
        "qa_execution_pass_rate_pct": 92.4,
        "open_raid_exposure": 14,
    }
    
    charts = {
        "portfolio_rag_health": [
            {"status": "Green", "count": 22},
            {"status": "Amber", "count": 8},
            {"status": "Red", "count": 4},
        ]
    }
    
    role_name = current_user.roles[0].name if current_user.roles else "EMPLOYEE"
    
    return DashboardResponse(
        role=role_name,
        kpis=kpis,
        charts=charts
    )

