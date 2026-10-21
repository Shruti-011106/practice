from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.dependencies import get_current_active_user
from core.schemas import DashboardResponse
from auth.models import User
from modules.hr import models

router = APIRouter(prefix="/hr", tags=["HR Dashboard"])


@router.get("/dashboard-summary", response_model=DashboardResponse)
async def get_hr_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Dummy structure for now. Will be populated with real queries based on roles later.
    
    # 1. Active Headcount
    # query = select(func.count(models.Employee.id)).where(models.Employee.status.in_(["Active", "Confirmed", "Probation"]))
    
    kpis = {
        "active_headcount": 142,
        "open_requisitions": 14,
        "high_priority_open": 5,
        "offer_acceptance_rate_pct": 80.0,
        "avg_time_to_hire_days": 24.0,
    }
    
    charts = {
        "recruitment_funnel": [
            {"stage": "Applied", "count": 450},
            {"stage": "Shortlisted", "count": 120},
            {"stage": "Interviewed", "count": 80},
            {"stage": "Selected", "count": 40},
            {"stage": "Offered", "count": 35},
            {"stage": "Joined", "count": 28},
        ]
    }
    
    role_name = current_user.roles[0].name if current_user.roles else "EMPLOYEE"
    
    return DashboardResponse(
        role=role_name,
        kpis=kpis,
        charts=charts
    )
