from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
from core.database import get_db
from core.dependencies import get_current_active_user, RoleChecker
from core.constants import (
    ROLE_FINANCE_MANAGER,
    ROLE_PROJECT_MANAGER,
    ROLE_CS_MANAGER,
    ROLE_HR_MANAGER,
)
from . import schemas, service

router = APIRouter()


# /project-governances Endpoints
@router.get(
    "/project-governances",
    response_model=schemas.ProjectGovernanceListWithKPIs,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [
                    ROLE_FINANCE_MANAGER,
                    ROLE_PROJECT_MANAGER,
                    ROLE_CS_MANAGER,
                    ROLE_HR_MANAGER,
                ]
            )
        ),
    ],
)
async def list_projectgovernances(db: AsyncSession = Depends(get_db)):
    records = await service.projectgovernance_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_projects,
            COUNT(CASE WHEN LOWER(COALESCE(project_status, '')) IN ('on track', 'inprogress', 'in progress', 'active', 'healthy', 'completed', 'good') OR (LOWER(COALESCE(project_status, '')) NOT IN ('at risk', 'critical', 'delayed', 'on hold', 'off track', 'warning', 'high risk') AND COALESCE(risks, 0) = 0) THEN 1 END) AS on_track_projects,
            COUNT(CASE WHEN LOWER(COALESCE(project_status, '')) IN ('at risk', 'critical', 'delayed', 'on hold', 'off track', 'warning', 'high risk') OR COALESCE(risks, 0) > 0 THEN 1 END) AS projects_at_risk,
            COALESCE(AVG(utilization_pct), 0) AS budget_utilized_pct,
            COALESCE(SUM(budget), 0) AS total_budget
        FROM project_governances
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    total_proj = row[0] if row is not None else 0
    on_track = row[1] if row is not None else 0
    at_risk = row[2] if row is not None else 0
    util_pct = round(row[3], 2) if row is not None else 0.0
    tot_bud = row[4] if row is not None else 0.0

    if tot_bud >= 100000:
        bud_fmt = f"₹{round(tot_bud / 100000, 2)} L Total Budget"
    else:
        bud_fmt = f"₹{round(tot_bud, 2)} Total Budget"

    return {
        "kpis": {
            "total_projects": total_proj,
            "on_track_projects": on_track,
            "projects_at_risk": at_risk,
            "budget_utilized_pct": util_pct,
            "total_budget": tot_bud,
            "total_budget_formatted": bud_fmt,
        },
        "data": records,
    }



@router.get(
    "/project-governances/{item_id}",
    response_model=schemas.ProjectGovernanceOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def get_projectgovernance(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.projectgovernance_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ProjectGovernance not found")
    return obj


@router.post(
    "/project-governances",
    response_model=schemas.ProjectGovernanceOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def create_projectgovernance(
    payload: schemas.ProjectGovernanceCreate, db: AsyncSession = Depends(get_db)
):
    return await service.projectgovernance_service.create(db, payload)


@router.put(
    "/project-governances/{item_id}",
    response_model=schemas.ProjectGovernanceOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def update_projectgovernance(
    item_id: int,
    payload: schemas.ProjectGovernanceUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.projectgovernance_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ProjectGovernance not found")
    return await service.projectgovernance_service.update(db, db_obj, payload)


@router.delete(
    "/project-governances/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def delete_projectgovernance(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.projectgovernance_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ProjectGovernance not found")
    return None


# /deliverable-trackers Endpoints
@router.get(
    "/deliverable-trackers",
    response_model=schemas.DeliverableTrackerListWithKPIs,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER, ROLE_FINANCE_MANAGER]
            )
        ),
    ],
)
async def list_deliverabletrackers(db: AsyncSession = Depends(get_db)):
    records = await service.deliverabletracker_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_deliverables,
            COUNT(CASE WHEN LOWER(COALESCE(status, '')) IN ('completed', 'done', 'delivered', 'closed', 'signed off') THEN 1 END) AS completed_deliverables,
            COUNT(CASE WHEN LOWER(COALESCE(status, '')) IN ('delayed', 'at risk', 'overdue', 'blocked', 'pending') OR (delay_reason IS NOT NULL AND delay_reason != '') THEN 1 END) AS delayed_milestones,
            COUNT(CASE WHEN customer_signoff IS TRUE THEN 1 END) AS client_signoffs
        FROM deliverable_trackers
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_deliverables": row[0] if row is not None else 0,
            "completed_deliverables": row[1] if row is not None else 0,
            "delayed_milestones": row[2] if row is not None else 0,
            "client_signoffs": row[3] if row is not None else 0,
        },
        "data": records,
    }



@router.get(
    "/deliverable-trackers/{item_id}",
    response_model=schemas.DeliverableTrackerOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def get_deliverabletracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.deliverabletracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="DeliverableTracker not found")
    return obj


@router.post(
    "/deliverable-trackers",
    response_model=schemas.DeliverableTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def create_deliverabletracker(
    payload: schemas.DeliverableTrackerCreate, db: AsyncSession = Depends(get_db)
):
    return await service.deliverabletracker_service.create(db, payload)


@router.put(
    "/deliverable-trackers/{item_id}",
    response_model=schemas.DeliverableTrackerOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def update_deliverabletracker(
    item_id: int,
    payload: schemas.DeliverableTrackerUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.deliverabletracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="DeliverableTracker not found")
    return await service.deliverabletracker_service.update(db, db_obj, payload)


@router.delete(
    "/deliverable-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def delete_deliverabletracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.deliverabletracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="DeliverableTracker not found")
    return None


# /customer-satisfactions Endpoints
@router.get(
    "/customer-satisfactions",
    response_model=schemas.CustomerSatisfactionListWithKPIs,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def list_customersatisfactions(db: AsyncSession = Depends(get_db)):
    records = await service.customersatisfaction_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COALESCE(AVG(csat_score), 0) AS avg_csat_score,
            COALESCE(AVG(nps_score), 0) AS avg_nps_score,
            COUNT(CASE WHEN LOWER(current_status) IN ('open', 'in progress', 'pending') THEN 1 END) AS open_action_items
        FROM customer_satisfactions
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "avg_csat_score": round(row[0], 2) if row is not None else 0.0,
            "avg_nps_score": round(row[1], 2) if row is not None else 0.0,
            "open_action_items": row[2] if row is not None else 0,
        },
        "data": records,
    }


@router.get(
    "/customer-satisfactions/{item_id}",
    response_model=schemas.CustomerSatisfactionOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def get_customersatisfaction(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.customersatisfaction_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="CustomerSatisfaction not found")
    return obj


@router.post(
    "/customer-satisfactions",
    response_model=schemas.CustomerSatisfactionOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def create_customersatisfaction(
    payload: schemas.CustomerSatisfactionCreate, db: AsyncSession = Depends(get_db)
):
    return await service.customersatisfaction_service.create(db, payload)


@router.put(
    "/customer-satisfactions/{item_id}",
    response_model=schemas.CustomerSatisfactionOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def update_customersatisfaction(
    item_id: int,
    payload: schemas.CustomerSatisfactionUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.customersatisfaction_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="CustomerSatisfaction not found")
    return await service.customersatisfaction_service.update(db, db_obj, payload)


@router.delete(
    "/customer-satisfactions/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER])),
    ],
)
async def delete_customersatisfaction(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.customersatisfaction_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="CustomerSatisfaction not found")
    return None


# /qa-trackers Endpoints
@router.get(
    "/qa-trackers",
    response_model=schemas.QATrackerListWithKPIs,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER, ROLE_FINANCE_MANAGER]
            )
        ),
    ],
)
async def list_qatrackers(db: AsyncSession = Depends(get_db)):
    records = await service.qatracker_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS tracked_projects,
            COALESCE(SUM(defect_count), 0) AS total_defects,
            COALESCE(SUM(critical_defects), 0) AS critical_defects,
            COUNT(CASE WHEN LOWER(COALESCE(golive_readiness, '')) IN ('ready', 'ready to go-live', 'go-live ready', 'passed', 'signed off', 'yes') OR LOWER(COALESCE(quality_status, '')) IN ('ready', 'passed', 'completed', 'good', 'healthy') THEN 1 END) AS ready_to_golive
        FROM qa_trackers
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "tracked_projects": row[0] if row is not None else 0,
            "total_defects": row[1] if row is not None else 0,
            "critical_defects": row[2] if row is not None else 0,
            "ready_to_golive": row[3] if row is not None else 0,
        },
        "data": records,
    }



@router.get(
    "/qa-trackers/{item_id}",
    response_model=schemas.QATrackerOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def get_qatracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.qatracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="QATracker not found")
    return obj


@router.post(
    "/qa-trackers",
    response_model=schemas.QATrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def create_qatracker(
    payload: schemas.QATrackerCreate, db: AsyncSession = Depends(get_db)
):
    return await service.qatracker_service.create(db, payload)


@router.put(
    "/qa-trackers/{item_id}",
    response_model=schemas.QATrackerOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def update_qatracker(
    item_id: int, payload: schemas.QATrackerUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await service.qatracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="QATracker not found")
    return await service.qatracker_service.update(db, db_obj, payload)


@router.delete(
    "/qa-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def delete_qatracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.qatracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="QATracker not found")
    return None


# /change-requests Endpoints
@router.get(
    "/change-requests",
    response_model=schemas.ChangeRequestListWithKPIs,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER, ROLE_FINANCE_MANAGER]
            )
        ),
    ],
)
async def list_changerequests(db: AsyncSession = Depends(get_db)):
    records = await service.changerequest_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_change_requests,
            COUNT(CASE WHEN LOWER(COALESCE(approval_status, '')) IN ('approved', 'cleared', 'implemented', 'completed', 'done') THEN 1 END) AS approved_crs,
            COUNT(CASE WHEN LOWER(COALESCE(approval_status, '')) IN ('pending', 'in review', 'submitted', 'awaiting sign-off', 'pending approval', 'under review', 'open') OR COALESCE(approval_status, '') = '' THEN 1 END) AS pending_approval,
            COALESCE(SUM(cost_impact), 0) AS total_cost_impact
        FROM change_requests
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    total_crs = row[0] if row is not None else 0
    approved = row[1] if row is not None else 0
    pending = row[2] if row is not None else 0
    tot_cost = row[3] if row is not None else 0.0

    if tot_cost >= 100000:
        cost_fmt = f"₹{round(tot_cost / 100000, 2)} L Total Cost Impact"
    else:
        cost_fmt = f"₹{round(tot_cost, 2)} Total Cost Impact"

    return {
        "kpis": {
            "total_change_requests": total_crs,
            "approved_crs": approved,
            "pending_approval": pending,
            "total_cost_impact": tot_cost,
            "total_cost_impact_formatted": cost_fmt,
        },
        "data": records,
    }



@router.get(
    "/change-requests/{item_id}",
    response_model=schemas.ChangeRequestOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def get_changerequest(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.changerequest_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ChangeRequest not found")
    return obj


@router.post(
    "/change-requests",
    response_model=schemas.ChangeRequestOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def create_changerequest(
    payload: schemas.ChangeRequestCreate, db: AsyncSession = Depends(get_db)
):
    return await service.changerequest_service.create(db, payload)


@router.put(
    "/change-requests/{item_id}",
    response_model=schemas.ChangeRequestOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def update_changerequest(
    item_id: int,
    payload: schemas.ChangeRequestUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.changerequest_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ChangeRequest not found")
    return await service.changerequest_service.update(db, db_obj, payload)


@router.delete(
    "/change-requests/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def delete_changerequest(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.changerequest_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ChangeRequest not found")
    return None


# /resource-utilizations Endpoints
@router.get(
    "/resource-utilizations",
    response_model=schemas.ResourceUtilizationListWithKPIs,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker([ROLE_HR_MANAGER, ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])
        ),
    ],
)
async def list_resourceutilizations(db: AsyncSession = Depends(get_db)):
    records = await service.resourceutilization_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_resources,
            COALESCE(AVG(billable_pct), 0) AS avg_billable_pct,
            COALESCE(AVG(utilization_pct), 0) AS avg_utilization_pct,
            COUNT(CASE WHEN LOWER(COALESCE(bench_status, '')) LIKE '%bench%' OR LOWER(COALESCE(bench_status, '')) LIKE '%available%' OR COALESCE(billable_pct, 0) = 0 THEN 1 END) AS bench_resources,
            COUNT(CASE WHEN LOWER(COALESCE(allocation_status, '')) IN ('active', 'assigned') THEN 1 END) AS active_allocations
        FROM resource_utilizations
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_resources": row[0] if row is not None else 0,
            "avg_billable_pct": round(row[1], 2) if row is not None else 0.0,
            "avg_utilization_pct": round(row[2], 2) if row is not None else 0.0,
            "bench_resources": row[3] if row is not None else 0,
            "active_allocations": row[4] if row is not None else 0,
        },
        "data": records,
    }



@router.get(
    "/resource-utilizations/{item_id}",
    response_model=schemas.ResourceUtilizationOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker([ROLE_HR_MANAGER, ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])
        ),
    ],
)
async def get_resourceutilization(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.resourceutilization_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ResourceUtilization not found")
    return obj


@router.post(
    "/resource-utilizations",
    response_model=schemas.ResourceUtilizationOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker([ROLE_HR_MANAGER, ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])
        ),
    ],
)
async def create_resourceutilization(
    payload: schemas.ResourceUtilizationCreate, db: AsyncSession = Depends(get_db)
):
    return await service.resourceutilization_service.create(db, payload)


@router.put(
    "/resource-utilizations/{item_id}",
    response_model=schemas.ResourceUtilizationOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker([ROLE_HR_MANAGER, ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])
        ),
    ],
)
async def update_resourceutilization(
    item_id: int,
    payload: schemas.ResourceUtilizationUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.resourceutilization_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ResourceUtilization not found")
    return await service.resourceutilization_service.update(db, db_obj, payload)


@router.delete(
    "/resource-utilizations/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker([ROLE_HR_MANAGER, ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])
        ),
    ],
)
async def delete_resourceutilization(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.resourceutilization_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ResourceUtilization not found")
    return None


# /raids Endpoints
@router.get(
    "/raids",
    response_model=schemas.RAIDListWithKPIs,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER, ROLE_FINANCE_MANAGER]
            )
        ),
    ],
)
async def list_raids(db: AsyncSession = Depends(get_db)):
    records = await service.raid_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_raid_mapped,
            COUNT(CASE WHEN LOWER(COALESCE(status, '')) NOT IN ('resolved', 'closed', 'completed', 'done', 'mitigated') THEN 1 END) AS active_risks_issues,
            COUNT(CASE WHEN LOWER(COALESCE(impact, '')) IN ('critical', 'high', 'severe') THEN 1 END) AS critical_impact_items,
            COUNT(CASE WHEN LOWER(COALESCE(status, '')) IN ('resolved', 'closed', 'completed', 'done', 'mitigated') THEN 1 END) AS resolved_closed
        FROM raids
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_raid_mapped": row[0] if row is not None else 0,
            "active_risks_issues": row[1] if row is not None else 0,
            "critical_impact_items": row[2] if row is not None else 0,
            "resolved_closed": row[3] if row is not None else 0,
        },
        "data": records,
    }



@router.get(
    "/raids/{item_id}",
    response_model=schemas.RAIDOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def get_raid(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.raid_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="RAID not found")
    return obj


@router.post(
    "/raids",
    response_model=schemas.RAIDOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def create_raid(payload: schemas.RAIDCreate, db: AsyncSession = Depends(get_db)):
    return await service.raid_service.create(db, payload)


@router.put(
    "/raids/{item_id}",
    response_model=schemas.RAIDOut,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def update_raid(
    item_id: int, payload: schemas.RAIDUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await service.raid_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="RAID not found")
    return await service.raid_service.update(db, db_obj, payload)


@router.delete(
    "/raids/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Project Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def delete_raid(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.raid_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="RAID not found")
    return None


# /vendor-subcontractor-governances Endpoints
@router.get(
    "/vendor-subcontractor-governances",
    response_model=schemas.VendorSubcontractorGovernanceListWithKPIs,
    tags=["Vendor & Subcontractor Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def list_vendorsubcontractorgovernances(db: AsyncSession = Depends(get_db)):
    records = await service.vendorsubcontractorgovernance_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_contracts,
            COUNT(CASE WHEN LOWER(contract_status) IN ('active', 'in progress', 'live') THEN 1 END) AS active_subcontractors,
            COALESCE(SUM(allocated_budget), 0) AS total_allocated_budget
        FROM vendor_subcontractor_governances
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_contracts": row[0] if row is not None else 0,
            "active_subcontractors": row[1] if row is not None else 0,
            "total_allocated_budget": row[2] if row is not None else 0.0,
        },
        "data": records,
    }


@router.get(
    "/vendor-subcontractor-governances/{item_id}",
    response_model=schemas.VendorSubcontractorGovernanceOut,
    tags=["Vendor & Subcontractor Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def get_vendorsubcontractorgovernance(
    item_id: int, db: AsyncSession = Depends(get_db)
):
    obj = await service.vendorsubcontractorgovernance_service.get(db, item_id)
    if not obj:
        raise HTTPException(
            status_code=404, detail="VendorSubcontractorGovernance not found"
        )
    return obj


@router.post(
    "/vendor-subcontractor-governances",
    response_model=schemas.VendorSubcontractorGovernanceOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Vendor & Subcontractor Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def create_vendorsubcontractorgovernance(
    payload: schemas.VendorSubcontractorGovernanceCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.vendorsubcontractorgovernance_service.create(db, payload)


@router.put(
    "/vendor-subcontractor-governances/{item_id}",
    response_model=schemas.VendorSubcontractorGovernanceOut,
    tags=["Vendor & Subcontractor Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def update_vendorsubcontractorgovernance(
    item_id: int,
    payload: schemas.VendorSubcontractorGovernanceUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.vendorsubcontractorgovernance_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(
            status_code=404, detail="VendorSubcontractorGovernance not found"
        )
    return await service.vendorsubcontractorgovernance_service.update(
        db, db_obj, payload
    )


@router.delete(
    "/vendor-subcontractor-governances/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Vendor & Subcontractor Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER])),
    ],
)
async def delete_vendorsubcontractorgovernance(
    item_id: int, db: AsyncSession = Depends(get_db)
):
    obj = await service.vendorsubcontractorgovernance_service.delete(db, item_id)
    if not obj:
        raise HTTPException(
            status_code=404, detail="VendorSubcontractorGovernance not found"
        )
    return None


# /milestone-billings Endpoints
@router.get(
    "/milestone-billings",
    response_model=schemas.MilestoneBillingListWithKPIs,
    tags=["Milestone Billing & Financial Realization"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def list_milestonebillings(db: AsyncSession = Depends(get_db)):
    records = await service.milestonebilling_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_milestones,
            COALESCE(SUM(amount), 0) AS total_milestone_value,
            COALESCE(SUM(CASE WHEN LOWER(invoice_status) IN ('paid', 'realized', 'received', 'completed') THEN amount ELSE 0 END), 0) AS realized_paid_invoices
        FROM milestone_billings
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_milestones": row[0] if row is not None else 0,
            "total_milestone_value": row[1] if row is not None else 0.0,
            "realized_paid_invoices": row[2] if row is not None else 0.0,
        },
        "data": records,
    }


@router.get(
    "/milestone-billings/{item_id}",
    response_model=schemas.MilestoneBillingOut,
    tags=["Milestone Billing & Financial Realization"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def get_milestonebilling(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.milestonebilling_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="MilestoneBilling not found")
    return obj


@router.post(
    "/milestone-billings",
    response_model=schemas.MilestoneBillingOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Milestone Billing & Financial Realization"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def create_milestonebilling(
    payload: schemas.MilestoneBillingCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.milestonebilling_service.create(db, payload)


@router.put(
    "/milestone-billings/{item_id}",
    response_model=schemas.MilestoneBillingOut,
    tags=["Milestone Billing & Financial Realization"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def update_milestonebilling(
    item_id: int,
    payload: schemas.MilestoneBillingUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.milestonebilling_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="MilestoneBilling not found")
    return await service.milestonebilling_service.update(db, db_obj, payload)


@router.delete(
    "/milestone-billings/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Milestone Billing & Financial Realization"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def delete_milestonebilling(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.milestonebilling_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="MilestoneBilling not found")
    return None


# /project-closures Endpoints
@router.get(
    "/project-closures",
    response_model=schemas.ProjectClosureListWithKPIs,
    tags=["Project Closure & Lessons Learned"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [
                    ROLE_PROJECT_MANAGER,
                    ROLE_CS_MANAGER,
                    ROLE_FINANCE_MANAGER,
                ]
            )
        ),
    ],
)
async def list_projectclosures(db: AsyncSession = Depends(get_db)):
    records = await service.projectclosure_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS closures_initiated,
            COUNT(CASE WHEN LOWER(closure_status) IN ('closed', 'completed', 'signoff completed', 'approved', 'done') THEN 1 END) AS projects_closed,
            COALESCE(AVG(CASE WHEN csat_rating > 0 THEN csat_rating END), 0) AS avg_csat_rating
        FROM project_closures
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "closures_initiated": row[0] if row is not None else 0,
            "projects_closed": row[1] if row is not None else 0,
            "avg_csat_rating": round(row[2], 2) if row is not None else 0.0,
        },
        "data": records,
    }


@router.get(
    "/project-closures/{item_id}",
    response_model=schemas.ProjectClosureOut,
    tags=["Project Closure & Lessons Learned"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [
                    ROLE_PROJECT_MANAGER,
                    ROLE_CS_MANAGER,
                    ROLE_FINANCE_MANAGER,
                ]
            )
        ),
    ],
)
async def get_projectclosure(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.projectclosure_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ProjectClosure not found")
    return obj


@router.post(
    "/project-closures",
    response_model=schemas.ProjectClosureOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Project Closure & Lessons Learned"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER]
            )
        ),
    ],
)
async def create_projectclosure(
    payload: schemas.ProjectClosureCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.projectclosure_service.create(db, payload)


@router.put(
    "/project-closures/{item_id}",
    response_model=schemas.ProjectClosureOut,
    tags=["Project Closure & Lessons Learned"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER]
            )
        ),
    ],
)
async def update_projectclosure(
    item_id: int,
    payload: schemas.ProjectClosureUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.projectclosure_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ProjectClosure not found")
    return await service.projectclosure_service.update(db, db_obj, payload)


@router.delete(
    "/project-closures/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Project Closure & Lessons Learned"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_PROJECT_MANAGER, ROLE_CS_MANAGER]
            )
        ),
    ],
)
async def delete_projectclosure(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.projectclosure_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ProjectClosure not found")
    return None




