from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.dependencies import get_current_active_user
from core.schemas import DashboardResponse
from auth.models import User

router = APIRouter(prefix="/dashboard", tags=["Centralized Dashboards"])


@router.get("/hr/dashboard-summary", response_model=DashboardResponse)
async def get_hr_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
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
    return DashboardResponse(role=role_name, kpis=kpis, charts=charts)


@router.get("/finance/dashboard-summary", response_model=DashboardResponse)
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
    return DashboardResponse(role=role_name, kpis=kpis, charts=charts)


@router.get("/project/dashboard-summary", response_model=DashboardResponse)
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
    return DashboardResponse(role=role_name, kpis=kpis, charts=charts)


@router.get("/sales/dashboard-summary", response_model=DashboardResponse)
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
    return DashboardResponse(role=role_name, kpis=kpis, charts=charts)


@router.get("/customer-success/dashboard-summary", response_model=DashboardResponse)
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
    return DashboardResponse(role=role_name, kpis=kpis, charts=charts)


@router.get("/presales/dashboard-summary", response_model=DashboardResponse)
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
    return DashboardResponse(role=role_name, kpis=kpis, charts=charts)


@router.get("/marketing/dashboard-summary", response_model=DashboardResponse)
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
    return DashboardResponse(role=role_name, kpis=kpis, charts=charts)


@router.get("/lnd/dashboard-summary", response_model=DashboardResponse)
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
    return DashboardResponse(role=role_name, kpis=kpis, charts=charts)
