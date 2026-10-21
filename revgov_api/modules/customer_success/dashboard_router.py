from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.dependencies import get_current_active_user
from core.schemas import DashboardResponse
from auth.models import User

router = APIRouter(prefix="/customer-success", tags=["Customer Success Dashboard"])


@router.get("/dashboard-summary", response_model=DashboardResponse)
async def get_cs_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    kpis = {
        "avg_account_csat_score": 4.6,
        "sla_compliance_rate_pct": 94.2,
        "open_client_escalations": 3,
        "arr_exposure_at_risk": 250000.00,
    }
    
    charts = {
        "escalation_severity_breakdown": [
            {"severity": "Critical", "count": 1},
            {"severity": "High", "count": 2},
            {"severity": "Medium", "count": 5},
        ],
        "quarterly_qbr_cadence": [
            {"status": "Scheduled", "count": 12},
            {"status": "Delivered", "count": 28},
        ]
    }
    
    role_name = current_user.roles[0].name if current_user.roles else "EMPLOYEE"
    
    return DashboardResponse(
        role=role_name,
        kpis=kpis,
        charts=charts
    )
