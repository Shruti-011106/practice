from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.dependencies import get_current_active_user
from core.schemas import DashboardResponse
from auth.models import User

router = APIRouter(prefix="/finance", tags=["Finance Dashboard"])


@router.get("/dashboard-summary", response_model=DashboardResponse)
async def get_finance_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    kpis = {
        "budget_allocated": 1500000.00,
        "budget_utilized": 1026000.00,
        "overall_utilization_pct": 68.4,
        "total_overdue_amount": 48000.00,
        "unapproved_po_exposure": 125000.00,
    }
    
    charts = {
        "departmental_budget_burn": [
            {"department": "Engineering", "allocated": 800000, "utilized": 600000},
            {"department": "Sales", "allocated": 400000, "utilized": 250000},
            {"department": "Marketing", "allocated": 300000, "utilized": 176000},
        ]
    }
    
    role_name = current_user.roles[0].name if current_user.roles else "EMPLOYEE"
    
    return DashboardResponse(
        role=role_name,
        kpis=kpis,
        charts=charts
    )
