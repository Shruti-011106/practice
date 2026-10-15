from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.dependencies import get_current_active_user
from core.schemas import DashboardResponse
from auth.models import User

router = APIRouter(prefix="/sales", tags=["Sales Dashboard"])


@router.get("/dashboard-summary", response_model=DashboardResponse)
async def get_sales_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    kpis = {
        "unweighted_pipeline_value": 4200000.00,
        "weighted_forecast_value": 2450000.00,
        "target_revenue_achieved_pct": 78.5,
        "opportunity_win_rate_pct": 34.2,
    }
    
    charts = {
        "sales_pipeline_stage_funnel": [
            {"stage": "Prospecting", "value": 1500000},
            {"stage": "Qualification", "value": 1200000},
            {"stage": "Proposal", "value": 900000},
            {"stage": "Negotiation", "value": 600000},
        ],
        "lead_outcome_distribution": [
            {"outcome": "Won", "count": 45},
            {"outcome": "Lost", "count": 60},
            {"outcome": "In-Progress", "count": 80},
        ]
    }
    
    role_name = current_user.roles[0].name if current_user.roles else "EMPLOYEE"
    
    return DashboardResponse(
        role=role_name,
        kpis=kpis,
        charts=charts
    )
