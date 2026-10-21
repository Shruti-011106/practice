from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.database import get_db
from core.dependencies import get_current_active_user
from auth.models import User
from modules.hr.models import Employee
from modules.project import schemas, models

router = APIRouter(prefix="/project", tags=["Project Dashboard"])

@router.get(
    "/dashboard/my-projects", 
    response_model=schemas.EmployeeProjectDashboardList,
    dependencies=[Depends(get_current_active_user)]
)
async def get_my_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query_emp = select(Employee).filter(Employee.user_id == current_user.id)
    res_emp = await db.execute(query_emp)
    emp = res_emp.scalar_one_or_none()
    
    if not emp:
        return schemas.EmployeeProjectDashboardList(
            kpis=schemas.EmployeeProjectKPIs(),
            data=[]
        )
        
    query = select(models.ResourceUtilization).options(
        selectinload(models.ResourceUtilization.project)
    ).filter(models.ResourceUtilization.employee_id == emp.id)
    
    result = await db.execute(query.order_by(models.ResourceUtilization.id.desc()))
    records = result.scalars().all()
    
    total_projects = 0
    total_active_projects = 0
    upcoming_projects = 0
    completed = 0
    
    data_list = []
    
    for rec in records:
        proj = rec.project
        if not proj:
            continue
            
        total_projects += 1
        
        status_lower = proj.project_status.lower() if proj.project_status else ""
        if status_lower == "completed":
            completed += 1
            
        alloc_status = rec.allocation_status.lower() if rec.allocation_status else ""
        if alloc_status == "active":
            total_active_projects += 1
        elif alloc_status == "assigned":
            upcoming_projects += 1
            
        data_list.append(schemas.EmployeeProjectDashboardOut(
            id=rec.id,
            project_id=proj.id,
            project_name=proj.project_name,
            start_date=proj.start_date,
            end_date=proj.end_date,
            project_status=proj.project_status,
            milestone=proj.milestone_status,
            pm_name=proj.pm_name,
            primary_skill=rec.skill,
            role=rec.role,
            utilization_pct=rec.utilization_pct,
            allocation_status=rec.allocation_status,
            assigned_on=rec.assigned_on,
            release_date=rec.release_date,
            bench_status=rec.bench_status,
            availability_date=rec.availability
        ))
        
    return schemas.EmployeeProjectDashboardList(
        kpis=schemas.EmployeeProjectKPIs(
            total_projects=total_projects,
            total_active_projects=total_active_projects,
            upcoming_projects=upcoming_projects,
            completed_projects=completed
        ),
        data=data_list
    )


@router.get(
    "/dashboard/my-projects/{assignment_id}",
    response_model=schemas.EmployeeProjectDetailsOut,
    dependencies=[Depends(get_current_active_user)]
)
async def get_my_project_details(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query_emp = select(Employee).filter(Employee.user_id == current_user.id)
    res_emp = await db.execute(query_emp)
    emp = res_emp.scalar_one_or_none()
    
    if not emp:
        raise HTTPException(status_code=403, detail="Not authorized. No employee record found.")
        
    check_query = select(models.ResourceUtilization).filter(
        models.ResourceUtilization.employee_id == emp.id,
        models.ResourceUtilization.id == assignment_id
    )
    check_res = await db.execute(check_query)
    assignment = check_res.scalars().first()
    
    if not assignment:
        raise HTTPException(
            status_code=403, 
            detail="Access Denied (IDOR Prevention). You are not assigned to this project."
        )
        
    proj_query = select(models.ProjectGovernance).options(
        selectinload(models.ProjectGovernance.pm),
        selectinload(models.ProjectGovernance.delivery_lead)
    ).filter(models.ProjectGovernance.id == assignment.project_id)
    
    proj_res = await db.execute(proj_query)
    proj = proj_res.scalar_one_or_none()
    
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")
        
    return schemas.EmployeeProjectDetailsOut(
        id=assignment.id,
        project_id=proj.id,
        project_name=proj.project_name,
        start_date=proj.start_date,
        end_date=proj.end_date,
        project_status=proj.project_status,
        milestone=proj.milestone_status,
        pm_name=proj.pm_name,
        delivery_lead_name=proj.delivery_lead_name,
        primary_skill=assignment.skill,
        utilization_pct=assignment.utilization_pct,
        bench_status=assignment.bench_status,
        availability_date=assignment.availability,
        risks=proj.risks,
        escalations=proj.escalations,
        dependencies=proj.dependencies,
        key_delivery_risks=proj.key_delivery_risks,
        active_escalations=proj.active_escalations,
        critical_dependencies=proj.critical_dependencies
    )
