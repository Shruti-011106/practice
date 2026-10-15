import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from core.database import get_db
from core.dependencies import get_current_active_user, RoleChecker
from core.constants import (
    ROLE_CEO,
    ROLE_EMPLOYEE,
    ROLE_HR_MANAGER,
    ROLE_LND_MANAGER,
    ROLE_PROJECT_MANAGER,
    ROLE_RECRUITER,
    ROLE_SUPER_ADMIN,
)
from . import schemas, service, models
from auth.models import User, Role

router = APIRouter()

# /employees Endpoints
@router.get(
    "/employees/by-role",
    response_model=List[schemas.EmployeeOut],
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
    ],
)
async def get_employees_by_role(
    role_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Fetch all employees who have a specific role (Useful for UI Dropdowns)."""
    from sqlalchemy.orm import selectinload
    
    # Using ilike for case-insensitive and partial match to handle 'sales' vs 'Sales Manager'
    query = (
        select(models.Employee)
        .join(User, models.Employee.user_id == User.id)
        .where(User.roles.any(Role.name.ilike(f"%{role_name}%")))
        .options(
            selectinload(models.Employee.manager),
            selectinload(models.Employee.department_details)
        )
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get(
    "/employees/me",
    response_model=schemas.EmployeeOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
    ],
)
async def get_my_profile(
    current_user=Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
):
    obj = await service.employee_service.get_my_employee_profile(db, current_user.id)
    if not obj:
        raise HTTPException(status_code=404, detail="Your HR Employee profile is not linked or does not exist.")
    return obj

@router.put(
    "/employees/me",
    response_model=schemas.EmployeeOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
    ],
)
async def update_my_profile(
    payload: schemas.EmployeeProfileUpdate,
    current_user=Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
):
    db_obj = await service.employee_service.get_my_employee_profile(db, current_user.id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Your HR Employee profile is not linked or does not exist.")
    return await service.employee_service.update(db, db_obj, payload)

UPLOAD_DIR = "uploads/employee_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post(
    "/employees/me/upload",
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
    ],
)
async def upload_employee_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_active_user)
):
    """
    Upload a document or profile image.
    Returns the local URL to the file, which can then be passed to PUT /employees/me.
    """
    # Create a safe, unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{current_user.id}_{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": f"/{file_path}"}

@router.get(
    "/employees/unlinked",
    response_model=List[schemas.EmployeeOut],
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_SUPER_ADMIN, ROLE_CEO, ROLE_HR_MANAGER])),
    ],
)
async def get_unlinked_employees(db: AsyncSession = Depends(get_db)):
    return await service.employee_service.get_unlinked_employees(db)

@router.get(
    "/employees",
    response_model=schemas.EmployeeListWithKPIs,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE])),
    ],
)
async def list_employees(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from core.security_scopes import is_admin_ceo_or_hr, get_employee_id_for_user
    is_hr = is_admin_ceo_or_hr(current_user)
    
    try:
        if is_hr:
            employees = await service.employee_service.get_all(db, skip=skip, limit=limit)
            kpi_query = text("""
                SELECT 
                    COUNT(*) FILTER (WHERE LOWER(status::text) = 'active') AS total_active,
                    COUNT(*) FILTER (WHERE extract(month from doj) = extract(month from CURRENT_DATE) AND extract(year from doj) = extract(year from CURRENT_DATE)) AS new_joiners,
                    COUNT(*) FILTER (WHERE LOWER(employment_type::text) = 'probation') AS probation_count,
                    COUNT(*) FILTER (WHERE LOWER(employment_type::text) = 'exited') AS resigned_count
                FROM employees
            """)
            result = await db.execute(kpi_query)
        else:
            emp_id = await get_employee_id_for_user(db, current_user)
            employees = await service.employee_service.get_all(db, skip=skip, limit=limit, manager_id=emp_id)
            kpi_query = text("""
                SELECT 
                    COUNT(*) FILTER (WHERE LOWER(status::text) = 'active') AS total_active,
                    COUNT(*) FILTER (WHERE extract(month from doj) = extract(month from CURRENT_DATE) AND extract(year from doj) = extract(year from CURRENT_DATE)) AS new_joiners,
                    COUNT(*) FILTER (WHERE LOWER(employment_type::text) = 'probation') AS probation_count,
                    COUNT(*) FILTER (WHERE LOWER(employment_type::text) = 'exited') AS resigned_count
                FROM employees
                WHERE manager_id = :emp_id OR id = :emp_id
            """)
            result = await db.execute(kpi_query, {"emp_id": emp_id})
        row = result.fetchone()

        response_data = {
            "kpis": {
                "total_active": row[0] if row is not None else 0,
                "new_joiners_this_month": row[1] if row is not None else 0,
                "probation_count": row[2] if row is not None else 0,
                "resigned_count": row[3] if row is not None else 0,
            },
            "data": employees,
        }
        # Manually validate to catch Pydantic errors inside the block
        return schemas.EmployeeListWithKPIs.model_validate(response_data)
    except Exception as e:
        import traceback

        return {
            "kpis": {
                "total_active": 0,
                "new_joiners_this_month": 0,
                "probation_count": 0,
                "resigned_count": 0,
            },
            "data": [],
            "debug_error": str(e),
            "traceback": traceback.format_exc(),
        }


@router.get(
    "/employees/{item_id}",
    response_model=schemas.EmployeeOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE])),
    ],
)
async def get_employee(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.employee_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee not found")
    return obj


@router.post(
    "/employees",
    response_model=schemas.EmployeeOut,
    status_code=status.HTTP_201_CREATED,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE])),
    ],
)
async def create_employee(
    payload: schemas.EmployeeCreate, db: AsyncSession = Depends(get_db)
):
    return await service.employee_service.create(db, payload)


@router.put(
    "/employees/{item_id}",
    response_model=schemas.EmployeeOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE])),
    ],
)
async def update_employee(
    item_id: int, payload: schemas.EmployeeUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await service.employee_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Employee not found")
    return await service.employee_service.update(db, db_obj, payload)


@router.delete(
    "/employees/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE])),
    ],
)
async def delete_employee(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.employee_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Employee not found")
    return None


# /learning-trackers Endpoints
@router.get(
    "/learning-trackers",
    response_model=schemas.LearningTrackerListWithKPIs,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
            )
        ),
    ],
)
async def list_learningtrackers(
    current_user=Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
):
    learning_trackers = await service.learningtracker_service.get_all_by_user(db, current_user)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_learning,
            COUNT(*) FILTER (WHERE LOWER(completion_status::text) = 'inprogress') AS total_inprogress,
            COUNT(*) FILTER (WHERE LOWER(completion_status::text) IN ('pass', 'completed')) AS total_pass_completed,
            COUNT(*) FILTER (WHERE LOWER(completion_status::text) IN ('failed', 'not started')) AS total_failed_not_started
        FROM learning_trackers
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_learning": row[0] if row is not None else 0,
            "total_inprogress": row[1] if row is not None else 0,
            "total_pass_completed": row[2] if row is not None else 0,
            "total_failed_not_started": row[3] if row is not None else 0,
        },
        "data": learning_trackers,
    }


@router.get(
    "/learning-trackers/{item_id}",
    response_model=schemas.LearningTrackerOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
            )
        ),
    ],
)
async def get_learningtracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.learningtracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="LearningTracker not found")
    return obj


@router.post(
    "/learning-trackers",
    response_model=schemas.LearningTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
            )
        ),
    ],
)
async def create_learningtracker(
    payload: schemas.LearningTrackerCreate, 
    current_user=Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
):
    return await service.learningtracker_service.create_by_user(db, payload, current_user)


@router.put(
    "/learning-trackers/{item_id}",
    response_model=schemas.LearningTrackerOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
            )
        ),
    ],
)
async def update_learningtracker(
    item_id: int,
    payload: schemas.LearningTrackerUpdate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.learningtracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="LearningTracker not found")
    return await service.learningtracker_service.update_by_user(db, db_obj, payload, current_user)


@router.delete(
    "/learning-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
            )
        ),
    ],
)
async def delete_learningtracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.learningtracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="LearningTracker not found")
    return None


# /linkedin-trackers Endpoints
@router.get(
    "/linkedin-trackers",
    response_model=schemas.LinkedInTrackerListWithKPIs,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_RECRUITER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE]
            )
        ),
    ],
)
async def list_linkedintrackers(db: AsyncSession = Depends(get_db)):
    linkedin_trackers = await service.linkedintracker_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_posting,
            COUNT(*) FILTER (WHERE LOWER(status::text) = 'active') AS total_active_posting,
            COALESCE(SUM(no_of_applicants), 0) AS total_applicant_count,
            COALESCE(SUM(engagement_count), 0) AS total_engagement_count
        FROM linkedin_trackers
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_posting": row[0] if row is not None else 0,
            "total_active_posting": row[1] if row is not None else 0,
            "total_applicant_count": row[2] if row is not None else 0,
            "total_engagement_count": row[3] if row is not None else 0,
        },
        "data": linkedin_trackers,
    }


@router.get(
    "/linkedin-trackers/{item_id}",
    response_model=schemas.LinkedInTrackerOut,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_RECRUITER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE]
            )
        ),
    ],
)
async def get_linkedintracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.linkedintracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="LinkedInTracker not found")
    return obj


@router.post(
    "/linkedin-trackers",
    response_model=schemas.LinkedInTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_RECRUITER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE]
            )
        ),
    ],
)
async def create_linkedintracker(
    payload: schemas.LinkedInTrackerCreate, db: AsyncSession = Depends(get_db)
):
    # Note: before_create logic 'set_linkedin_posting_id' should ideally be moved to service.
    # For now, we will assume standard creation.
    return await service.linkedintracker_service.create(db, payload)


@router.put(
    "/linkedin-trackers/{item_id}",
    response_model=schemas.LinkedInTrackerOut,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_RECRUITER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE]
            )
        ),
    ],
)
async def update_linkedintracker(
    item_id: int,
    payload: schemas.LinkedInTrackerUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.linkedintracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="LinkedInTracker not found")
    return await service.linkedintracker_service.update(db, db_obj, payload)


@router.delete(
    "/linkedin-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_RECRUITER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE]
            )
        ),
    ],
)
async def delete_linkedintracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.linkedintracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="LinkedInTracker not found")
    return None


# /job-openings Endpoints
@router.get(
    "/job-openings",
    response_model=schemas.JobOpeningListWithKPIs,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
    ],
)
async def list_jobopenings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from core.security_scopes import is_admin_ceo_or_hr, get_employee_id_for_user
    is_hr = is_admin_ceo_or_hr(current_user)
    
    if is_hr:
        job_openings = await service.jobopening_service.get_all(db)
    
        kpi_query = text("""
            SELECT 
                COUNT(*) FILTER (WHERE LOWER(current_status::text) = 'open') AS total_open,
                COUNT(*) FILTER (WHERE LOWER(priority::text) = 'critical') AS critical_positions,
                COUNT(*) FILTER (WHERE LOWER(current_status::text) != 'closed' AND LOWER(current_status::text) != 'cancelled' AND target_closure_date >= CURRENT_DATE AND target_closure_date <= CURRENT_DATE + 15) AS closing_soon,
                (SELECT COUNT(*) FROM candidates) AS total_applications
            FROM job_openings
        """)
        result = await db.execute(kpi_query)
    else:
        emp_id = await get_employee_id_for_user(db, current_user)
        if not emp_id:
            return {
                "kpis": {
                    "total_open": 0,
                    "critical_positions": 0,
                    "closing_soon": 0,
                    "total_applications": 0,
                },
                "data": [],
            }
            
        from sqlalchemy import select, or_
        from .models import JobOpening, InterviewGovernance, InterviewFeedback
        
        query = (
            select(JobOpening)
            .outerjoin(InterviewGovernance, InterviewGovernance.job_opening_id == JobOpening.id)
            .outerjoin(InterviewFeedback, InterviewFeedback.interview_id == InterviewGovernance.id)
            .where(
                or_(
                    JobOpening.hiring_manager_id == emp_id,
                    InterviewFeedback.interviewer_id == emp_id
                )
            ).distinct()
        )
        res = await db.execute(query)
        job_openings = res.scalars().all()
        
        kpi_query = text("""
            SELECT 
                COUNT(DISTINCT jo.id) FILTER (WHERE LOWER(jo.current_status::text) = 'open') AS total_open,
                COUNT(DISTINCT jo.id) FILTER (WHERE LOWER(jo.priority::text) = 'critical') AS critical_positions,
                COUNT(DISTINCT jo.id) FILTER (WHERE LOWER(jo.current_status::text) != 'closed' AND LOWER(jo.current_status::text) != 'cancelled' AND jo.target_closure_date >= CURRENT_DATE AND jo.target_closure_date <= CURRENT_DATE + 15) AS closing_soon,
                COUNT(DISTINCT c.id) AS total_applications
            FROM job_openings jo
            LEFT JOIN interview_governance ig ON ig.job_opening_id = jo.id
            LEFT JOIN interview_feedbacks fb ON fb.interview_id = ig.id
            LEFT JOIN candidates c ON c.job_opening_id = jo.id
            WHERE jo.hiring_manager_id = :emp_id OR fb.interviewer_id = :emp_id
        """)
        result = await db.execute(kpi_query, {"emp_id": emp_id})
    row = result.fetchone()

    return {
        "kpis": {
            "total_open": row[0] if row is not None else 0,
            "critical_positions": row[1] if row is not None else 0,
            "closing_soon": row[2] if row is not None else 0,
            "total_applications": row[3] if row is not None else 0,
        },
        "data": job_openings,
    }


@router.get(
    "/job-openings/{item_id}",
    response_model=schemas.JobOpeningOut,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def get_jobopening(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.jobopening_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="JobOpening not found")
        
    metrics_query = text("""
        SELECT 
            COUNT(DISTINCT c.id) AS total_applicants,
            COUNT(DISTINCT c.id) FILTER (WHERE LOWER(c.status::text) IN ('interviewing', 'shortlisted', 'screening')) AS in_progress,
            COUNT(DISTINCT c.id) FILTER (WHERE LOWER(c.status::text) = 'offer released') AS offers_released,
            COUNT(DISTINCT c.id) FILTER (WHERE LOWER(c.status::text) = 'joined') AS hired,
            COUNT(DISTINCT c.id) FILTER (WHERE LOWER(c.status::text) IN ('rejected', 'not selected')) AS rejected_candidates
        FROM candidates c
        WHERE c.job_opening_id = :job_id
    """)
    result = await db.execute(metrics_query, {"job_id": item_id})
    row = result.fetchone()
    
    total_positions = obj.vacancies if hasattr(obj, 'vacancies') and obj.vacancies else 0
    hired = row[3] if row is not None else 0
    
    pydantic_obj = schemas.JobOpeningOut.model_validate(obj)
    pydantic_obj.recruitment_metrics = schemas.JobOpeningRecruitmentMetrics(
        total_applicants=row[0] if row is not None else 0,
        in_progress=row[1] if row is not None else 0,
        offers_released=row[2] if row is not None else 0,
        positions_filled=f"{hired}/{total_positions}",
        rejected_candidates=row[4] if row is not None else 0,
    )
    return pydantic_obj


@router.get(
    "/job-openings/{item_id}/candidates",
    response_model=list[schemas.CandidateOut],
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def get_jobopening_candidates(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Candidate)
        .where(models.Candidate.job_opening_id == item_id)
        .order_by(models.Candidate.created_at.desc())
    )
    candidates = result.scalars().all()
    return candidates


@router.put(
    "/job-openings/{job_id}/candidates/{candidate_id}",
    response_model=schemas.CandidateOut,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def update_jobopening_candidate(
    job_id: int,
    candidate_id: int,
    payload: schemas.CandidateUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Candidate).where(
            models.Candidate.id == candidate_id,
            models.Candidate.job_opening_id == job_id,
        )
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(
            status_code=404, detail="Candidate not found for this Job Opening"
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)

    await db.commit()
    await db.refresh(candidate)
    return candidate


@router.post(
    "/job-openings",
    response_model=schemas.JobOpeningOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def create_jobopening(
    payload: schemas.JobOpeningCreate, db: AsyncSession = Depends(get_db)
):
    # Note: before_create logic 'set_job_opening_defaults' should ideally be moved to service.
    # For now, we will assume standard creation.
    return await service.jobopening_service.create(db, payload)


@router.put(
    "/job-openings/{item_id}",
    response_model=schemas.JobOpeningOut,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def update_jobopening(
    item_id: int, payload: schemas.JobOpeningUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await service.jobopening_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="JobOpening not found")
    return await service.jobopening_service.update(db, db_obj, payload)


@router.delete(
    "/job-openings/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def delete_jobopening(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.jobopening_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="JobOpening not found")
    return None


@router.post(
    "/job-openings/{item_id}/generate-link",
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def generate_jobopening_link(item_id: int, db: AsyncSession = Depends(get_db)):
    db_obj = await service.jobopening_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="JobOpening not found")

    if not db_obj.public_form_uuid:
        db_obj.public_form_uuid = str(uuid.uuid4())
        await db.commit()
        await db.refresh(db_obj)

    # Return the dynamic link info
    return {
        "apply_link": f"/apply/{db_obj.public_form_uuid}",
        "public_form_uuid": db_obj.public_form_uuid,
    }


# /interview-governance Endpoints
@router.get(
    "/interview-governance",
    response_model=schemas.InterviewGovernanceListWithKPIs,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
    ],
)
async def list_interviewgovernances(
    candidate_id: Optional[int] = Query(None, description="Filter by candidate ID for the timeline"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from core.security_scopes import is_admin_ceo_or_hr, get_employee_id_for_user
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from .models import InterviewGovernance, InterviewFeedback
    
    is_hr = is_admin_ceo_or_hr(current_user)
    
    # Custom query to allow filtering by candidate_id
    query = select(InterviewGovernance).options(
        selectinload(InterviewGovernance.job_opening),
        selectinload(InterviewGovernance.candidate),
        selectinload(InterviewGovernance.feedbacks).selectinload(InterviewFeedback.interviewer),
    )
    if candidate_id:
        query = query.where(InterviewGovernance.candidate_id == candidate_id)
        
    result = await db.execute(query)
    interview_governances = result.scalars().all()
    
    if not is_hr:
        emp_id = await get_employee_id_for_user(db, current_user)
        if not emp_id:
            return {
                "kpis": {
                    "total_pipeline": 0,
                    "todays": 0,
                    "upcoming": 0,
                    "completed": 0,
                    "pending_feedback": 0,
                },
                "data": [],
            }
            
        filtered = []
        for ig in interview_governances:
            is_interviewer = any(fb.interviewer_id == emp_id for fb in ig.feedbacks)
            is_hiring_manager = ig.job_opening and ig.job_opening.hiring_manager_id == emp_id
            
            if is_interviewer or is_hiring_manager:
                pydantic_ig = schemas.InterviewGovernanceOutWithFeedback.model_validate(ig)
                # If they are only an interviewer (not HM), optionally filter to show only their feedback.
                # But typically they should see all feedbacks if they are part of the panel. 
                # Keeping the original logic but extending it for HM.
                if not is_hiring_manager:
                    pydantic_ig.feedbacks = [fb for fb in pydantic_ig.feedbacks if fb.interviewer_id == emp_id]
                filtered.append(pydantic_ig)
        interview_governances = filtered

        kpi_query = text("""
            SELECT 
                COUNT(DISTINCT ig.id) AS total_pipeline,
                COUNT(DISTINCT ig.id) FILTER (WHERE ig.interview_date = CURRENT_DATE) AS todays,
                COUNT(DISTINCT ig.id) FILTER (WHERE ig.interview_date > CURRENT_DATE) AS upcoming,
                COUNT(DISTINCT ig.id) FILTER (WHERE LOWER(ig.status::text) = 'completed') AS completed,
                COUNT(DISTINCT ig.id) FILTER (WHERE LOWER(fb.feedback_status::text) = 'pending') AS pending_feedback
            FROM interview_governance ig
            JOIN interview_feedbacks fb ON ig.id = fb.interview_id
            WHERE fb.interviewer_id = :emp_id
        """)
        result = await db.execute(kpi_query, {"emp_id": emp_id})
    else:
        kpi_query = text("""
            SELECT 
                COUNT(DISTINCT ig.id) AS total_pipeline,
                COUNT(DISTINCT ig.id) FILTER (WHERE ig.interview_date = CURRENT_DATE) AS todays,
                COUNT(DISTINCT ig.id) FILTER (WHERE ig.interview_date > CURRENT_DATE) AS upcoming,
                COUNT(DISTINCT ig.id) FILTER (WHERE LOWER(ig.status::text) = 'completed') AS completed,
                COUNT(DISTINCT ig.id) FILTER (WHERE LOWER(fb.feedback_status::text) = 'pending') AS pending_feedback
            FROM interview_governance ig
            LEFT JOIN interview_feedbacks fb ON ig.id = fb.interview_id
        """)
        result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_pipeline": row[0] if row is not None else 0,
            "todays": row[1] if row is not None else 0,
            "upcoming": row[2] if row is not None else 0,
            "completed": row[3] if row is not None else 0,
            "pending_feedback": row[4] if row is not None else 0,
        },
        "data": interview_governances,
    }


@router.get(
    "/interview-governance/{item_id}",
    response_model=schemas.InterviewGovernanceOutWithFeedback,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
    ],
)
async def get_interviewgovernance(
    item_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from core.security_scopes import is_admin_ceo_or_hr, get_employee_id_for_user
    obj = await service.interviewgovernance_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="InterviewGovernance not found")
        
    is_hr = is_admin_ceo_or_hr(current_user)
    if not is_hr:
        emp_id = await get_employee_id_for_user(db, current_user)
        if not emp_id:
            raise HTTPException(status_code=403, detail="Your HR Employee profile is not linked or does not exist.")
            
        is_interviewer = any(fb.interviewer_id == emp_id for fb in obj.feedbacks)
        is_hiring_manager = obj.job_opening and obj.job_opening.hiring_manager_id == emp_id
        
        if not (is_interviewer or is_hiring_manager):
            raise HTTPException(status_code=403, detail="Not authorized to view this interview")
            
        pydantic_obj = schemas.InterviewGovernanceOutWithFeedback.model_validate(obj)
        if not is_hiring_manager:
            pydantic_obj.feedbacks = [fb for fb in pydantic_obj.feedbacks if fb.interviewer_id == emp_id]
        return pydantic_obj

    return obj


@router.post(
    "/interview-governance",
    response_model=schemas.InterviewGovernanceOutWithFeedback,
    status_code=status.HTTP_201_CREATED,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def create_interviewgovernance(
    payload: schemas.InterviewGovernanceCreate, db: AsyncSession = Depends(get_db)
):
    return await service.interviewgovernance_service.create(db, payload)


@router.put(
    "/interview-governance/{item_id}",
    response_model=schemas.InterviewGovernanceOutWithFeedback,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def update_interviewgovernance(
    item_id: int,
    payload: schemas.InterviewGovernanceUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.interviewgovernance_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="InterviewGovernance not found")
    return await service.interviewgovernance_service.update(db, db_obj, payload)


@router.put(
    "/interview-feedback/{feedback_id}",
    response_model=schemas.InterviewFeedbackOut,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
    ],
)
async def update_interviewfeedback(
    feedback_id: int, 
    payload: schemas.InterviewFeedbackUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from .models import InterviewFeedback
    from core.security_scopes import is_admin_ceo_or_hr, get_employee_id_for_user
    fb = await db.get(InterviewFeedback, feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Interview Feedback not found")
        
    if not is_admin_ceo_or_hr(current_user):
        emp_id = await get_employee_id_for_user(db, current_user)
        if fb.interviewer_id != emp_id:
            raise HTTPException(status_code=403, detail="You can only update your own feedback")
        
    obj_data = payload.model_dump(exclude_unset=True)
    for field, value in obj_data.items():
        setattr(fb, field, value)
    
    db.add(fb)
    await db.commit()
    await db.refresh(fb)
    
    # Trigger aggregation to check if interview status needs updating
    await service.aggregate_interview_feedback(db, fb.interview_id)
    
    # We must return it with the interviewer eagerly loaded if the schema uses it
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(InterviewFeedback)
        .options(selectinload(InterviewFeedback.interviewer))
        .filter(InterviewFeedback.id == feedback_id)
    )
    return result.scalar_one()


@router.delete(
    "/interview-governance/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def delete_interviewgovernance(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.interviewgovernance_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="InterviewGovernance not found")
    return None


# /offer-trackers Endpoints
@router.get(
    "/offer-trackers",
    response_model=schemas.OfferTrackerListWithKPIs,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def list_offertrackers(db: AsyncSession = Depends(get_db)):
    offer_trackers = await service.offertracker_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_offers,
            COUNT(*) FILTER (WHERE LOWER(status::text) = 'pending' OR LOWER(status::text) = 'offer released') AS pending_offers,
            COUNT(*) FILTER (WHERE LOWER(status::text) = 'accepted' OR LOWER(status::text) = 'offer accepted') AS offers_accepted,
            COUNT(*) FILTER (WHERE LOWER(status::text) = 'rejected' OR LOWER(status::text) = 'dropped' OR LOWER(status::text) = 'offer dropped' OR LOWER(status::text) = 'declined') AS offers_dropped
        FROM offer_trackers
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_offers": row[0] if row is not None else 0,
            "pending_offers": row[1] if row is not None else 0,
            "offers_accepted": row[2] if row is not None else 0,
            "offers_dropped": row[3] if row is not None else 0,
        },
        "data": offer_trackers,
    }


@router.get(
    "/offer-trackers/{item_id}",
    response_model=schemas.OfferTrackerOut,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def get_offertracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.offertracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="OfferTracker not found")
    return obj


@router.post(
    "/offer-trackers",
    response_model=schemas.OfferTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def create_offertracker(
    payload: schemas.OfferTrackerCreate, db: AsyncSession = Depends(get_db)
):
    return await service.offertracker_service.create(db, payload)


@router.put(
    "/offer-trackers/{item_id}",
    response_model=schemas.OfferTrackerOut,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def update_offertracker(
    item_id: int,
    payload: schemas.OfferTrackerUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.offertracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="OfferTracker not found")
    return await service.offertracker_service.update(db, db_obj, payload)


@router.delete(
    "/offer-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def delete_offertracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.offertracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="OfferTracker not found")
    return None


# /partner-trackers Endpoints
@router.get(
    "/partner-trackers",
    response_model=schemas.PartnerTrackerListWithKPIs,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def list_partnertrackers(db: AsyncSession = Depends(get_db)):
    partner_trackers = await service.partnertracker_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_partners,
            COUNT(*) FILTER (WHERE LOWER(current_status::text) = 'active') AS total_active_partners
        FROM partner_trackers
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_partners": row[0] if row is not None else 0,
            "total_active_partners": row[1] if row is not None else 0,
        },
        "data": partner_trackers,
    }


@router.get(
    "/partner-trackers/{item_id}",
    response_model=schemas.PartnerTrackerOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def get_partnertracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.partnertracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="PartnerTracker not found")
    return obj


@router.post(
    "/partner-trackers",
    response_model=schemas.PartnerTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def create_partnertracker(
    payload: schemas.PartnerTrackerCreate, db: AsyncSession = Depends(get_db)
):
    return await service.partnertracker_service.create(db, payload)


@router.put(
    "/partner-trackers/{item_id}",
    response_model=schemas.PartnerTrackerOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def update_partnertracker(
    item_id: int,
    payload: schemas.PartnerTrackerUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.partnertracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PartnerTracker not found")
    return await service.partnertracker_service.update(db, db_obj, payload)


@router.delete(
    "/partner-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def delete_partnertracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.partnertracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="PartnerTracker not found")
    return None


# /vendor-partner-hiring Endpoints
@router.get(
    "/vendor-partner-hiring",
    response_model=schemas.VendorPartnerHiringListWithKPIs,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def list_vendorpartnerhirings(db: AsyncSession = Depends(get_db)):
    vendorpartnerhirings = await service.vendorpartnerhiring_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_vendors,
            COALESCE(SUM(annual_contract_value), 0) AS total_contract_value,
            COUNT(req_id) AS total_requests,
            COUNT(CASE WHEN LOWER(priority) = 'high' THEN 1 END) AS high_priority,
            COUNT(CASE WHEN LOWER(current_status) IN ('closed / joined', 'closed', 'joined') THEN 1 END) AS closed_joined,
            COALESCE(SUM(no_of_positions), 0) AS total_positions
        FROM vendor_partner_hirings
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_vendors": row[0] if row is not None else 0,
            "total_contract_value": row[1] if row is not None else 0,
            "total_requests": row[2] if row is not None else 0,
            "high_priority": row[3] if row is not None else 0,
            "closed_joined": row[4] if row is not None else 0,
            "total_positions": row[5] if row is not None else 0,
        },
        "data": vendorpartnerhirings,
    }


@router.get(
    "/vendor-partner-hiring/{item_id}",
    response_model=schemas.VendorPartnerHiringOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def get_vendorpartnerhiring(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.vendorpartnerhiring_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="VendorPartnerHiring not found")
    return obj


@router.post(
    "/vendor-partner-hiring",
    response_model=schemas.VendorPartnerHiringOut,
    status_code=status.HTTP_201_CREATED,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def create_vendorpartnerhiring(
    payload: schemas.VendorPartnerHiringCreate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.vendorpartnerhiring_service.create(db, payload)
    return db_obj


@router.put(
    "/vendor-partner-hiring/{item_id}",
    response_model=schemas.VendorPartnerHiringOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def update_vendorpartnerhiring(
    item_id: int,
    payload: schemas.VendorPartnerHiringUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.vendorpartnerhiring_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="VendorPartnerHiring not found")

    db_obj = await service.vendorpartnerhiring_service.update(db, db_obj, payload)
    return db_obj


@router.delete(
    "/vendor-partner-hiring/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def delete_vendorpartnerhiring(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.vendorpartnerhiring_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="VendorPartnerHiring not found")
    return None


# /internship-statuses Endpoints
@router.get(
    "/internship-statuses",
    response_model=schemas.InternshipStatusListWithKPIs,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def list_internshipstatuss(db: AsyncSession = Depends(get_db)):
    internship_statuses = await service.internshipstatus_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_interns,
            COUNT(*) FILTER (WHERE LOWER(evaluation_status::text) = 'not started') AS total_not_started,
            COUNT(*) FILTER (WHERE LOWER(evaluation_status::text) = 'internship completed') AS total_internship_completed,
            COUNT(*) FILTER (WHERE LOWER(evaluation_status::text) = 'under observation') AS total_under_observation
        FROM internship_statuses
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_interns": row[0] if row is not None else 0,
            "total_not_started": row[1] if row is not None else 0,
            "total_internship_completed": row[2] if row is not None else 0,
            "total_under_observation": row[3] if row is not None else 0,
        },
        "data": internship_statuses,
    }


@router.get(
    "/internship-statuses/{item_id}",
    response_model=schemas.InternshipStatusOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def get_internshipstatus(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.internshipstatus_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="InternshipStatus not found")
    return obj


@router.post(
    "/internship-statuses",
    response_model=schemas.InternshipStatusOut,
    status_code=status.HTTP_201_CREATED,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def create_internshipstatus(
    payload: schemas.InternshipStatusCreate, db: AsyncSession = Depends(get_db)
):
    return await service.internshipstatus_service.create(db, payload)


@router.put(
    "/internship-statuses/{item_id}",
    response_model=schemas.InternshipStatusOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def update_internshipstatus(
    item_id: int,
    payload: schemas.InternshipStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.internshipstatus_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="InternshipStatus not found")
    return await service.internshipstatus_service.update(db, db_obj, payload)


@router.delete(
    "/internship-statuses/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def delete_internshipstatus(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.internshipstatus_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="InternshipStatus not found")
    return None


# /buddy-engagements Endpoints
@router.get(
    "/buddy-engagements",
    response_model=schemas.BuddyEngagementListWithKPIs,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def list_buddyengagements(db: AsyncSession = Depends(get_db)):
    buddyengagements = await service.buddyengagement_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_engagements,
            COUNT(*) FILTER (
                WHERE TRIM(onboarding_progress) IN ('100%', '100', '100.0', '100.0%')
                   OR CAST(NULLIF(REGEXP_REPLACE(onboarding_progress, '[^0-9.]', '', 'g'), '') AS FLOAT) >= 100
            ) AS onboarding_completed,
            COUNT(*) FILTER (
                WHERE TRIM(onboarding_progress) IN ('25%', '50%', '75%', '25', '50', '75', '25.0%', '50.0%', '75.0%')
                   OR (
                       CAST(NULLIF(REGEXP_REPLACE(onboarding_progress, '[^0-9.]', '', 'g'), '') AS FLOAT) > 0
                       AND CAST(NULLIF(REGEXP_REPLACE(onboarding_progress, '[^0-9.]', '', 'g'), '') AS FLOAT) < 100
                   )
            ) AS in_progress,
            ROUND(CAST(COALESCE(AVG(engagement_score), 0) AS NUMERIC), 1) AS average_engagement
        FROM buddy_engagements
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_engagements": int(row[0]) if row is not None and row[0] is not None else 0,
            "onboarding_completed": int(row[1]) if row is not None and row[1] is not None else 0,
            "in_progress": int(row[2]) if row is not None and row[2] is not None else 0,
            "average_engagement": float(row[3]) if row is not None and row[3] is not None else 0.0,
        },
        "data": buddyengagements,
    }


@router.get(
    "/buddy-engagements/{item_id}",
    response_model=schemas.BuddyEngagementOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def get_buddyengagement(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.buddyengagement_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="BuddyEngagement not found")
    return obj


@router.post(
    "/buddy-engagements",
    response_model=schemas.BuddyEngagementOut,
    status_code=status.HTTP_201_CREATED,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def create_buddyengagement(
    payload: schemas.BuddyEngagementCreate, db: AsyncSession = Depends(get_db)
):
    return await service.buddyengagement_service.create(db, payload)


@router.put(
    "/buddy-engagements/{item_id}",
    response_model=schemas.BuddyEngagementOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def update_buddyengagement(
    item_id: int,
    payload: schemas.BuddyEngagementUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.buddyengagement_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="BuddyEngagement not found")
    return await service.buddyengagement_service.update(db, db_obj, payload)


@router.delete(
    "/buddy-engagements/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def delete_buddyengagement(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.buddyengagement_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="BuddyEngagement not found")
    return None


# /employee-performances Endpoints
@router.get(
    "/employee-performances",
    response_model=schemas.EmployeePerformanceListWithKPIs,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def list_employeeperformances(db: AsyncSession = Depends(get_db)):
    employee_performances = await service.employeeperformance_service.get_all(db)

    kpi_query = text("""
        SELECT COUNT(*) AS total_reviewed
        FROM employee_performances
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_reviewed": row[0] if row is not None else 0,
        },
        "data": employee_performances,
    }


@router.get(
    "/employee-performances/{item_id}",
    response_model=schemas.EmployeePerformanceOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def get_employeeperformance(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.employeeperformance_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EmployeePerformance not found")
    return obj


@router.post(
    "/employee-performances",
    response_model=schemas.EmployeePerformanceOut,
    status_code=status.HTTP_201_CREATED,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def create_employeeperformance(
    payload: schemas.EmployeePerformanceCreate, db: AsyncSession = Depends(get_db)
):
    return await service.employeeperformance_service.create(db, payload)


@router.put(
    "/employee-performances/{item_id}",
    response_model=schemas.EmployeePerformanceOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def update_employeeperformance(
    item_id: int,
    payload: schemas.EmployeePerformanceUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.employeeperformance_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="EmployeePerformance not found")
    return await service.employeeperformance_service.update(db, db_obj, payload)


@router.delete(
    "/employee-performances/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def delete_employeeperformance(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.employeeperformance_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EmployeePerformance not found")
    return None


# /department-masters Endpoints
@router.get(
    "/department-masters",
    response_model=schemas.DepartmentListWithKPIs,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def list_departmentmasters(db: AsyncSession = Depends(get_db)):
    department_masters = await service.departmentmaster_service.get_all(db)

    kpi_query = text("""
        SELECT 
            COUNT(*) AS total_departments,
            COUNT(*) FILTER (WHERE LOWER(status::text) = 'active') AS active_departments,
            COUNT(*) FILTER (WHERE LOWER(status::text) = 'inactive') AS inactive_departments
        FROM department_masters
    """)
    result = await db.execute(kpi_query)
    row = result.fetchone()

    return {
        "kpis": {
            "total_departments": row[0] if row is not None else 0,
            "active_departments": row[1] if row is not None else 0,
            "inactive_departments": row[2] if row is not None else 0,
        },
        "data": department_masters,
    }


@router.get(
    "/department-masters/{item_id}",
    response_model=schemas.DepartmentMasterOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def get_departmentmaster(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.departmentmaster_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="DepartmentMaster not found")
    return obj


@router.post(
    "/department-masters",
    response_model=schemas.DepartmentMasterOut,
    status_code=status.HTTP_201_CREATED,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def create_departmentmaster(
    payload: schemas.DepartmentMasterCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return await service.departmentmaster_service.create(
        db, payload, user_email=current_user.email
    )


@router.put(
    "/department-masters/{item_id}",
    response_model=schemas.DepartmentMasterOut,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def update_departmentmaster(
    item_id: int,
    payload: schemas.DepartmentMasterUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.departmentmaster_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="DepartmentMaster not found")
    return await service.departmentmaster_service.update(db, db_obj, payload)


@router.delete(
    "/department-masters/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["HR"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_SUPER_ADMIN, ROLE_CEO])),
    ],
)
async def delete_departmentmaster(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.departmentmaster_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="DepartmentMaster not found")
    return None


@router.post(
    "/candidates",
    tags=["Social Media Governance"],
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def create_candidate_manually(
    job_id: int = Form(...),
    candidate_name: str = Form(...),
    email: str = Form(...),
    contact_number: str = Form(...),
    experience: str = Form(...),
    skills: str = Form(...),
    current_company: str = Form(None),
    notice_period: str = Form(None),
    current_ctc: str = Form(None),
    expected_ctc: str = Form(None),
    source: str = Form(None),
    remarks_notes: str = Form(None),
    resume_file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    # Verify job opening exists
    result = await db.execute(
        select(models.JobOpening).where(models.JobOpening.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job opening not found.")

    resume_url = None
    if resume_file:
        file_path = os.path.join(
            UPLOAD_DIR,
            f"{job.id}_{candidate_name.replace(' ', '_')}_{resume_file.filename}",
        )
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)
        resume_url = f"/{file_path}"

    new_candidate = models.Candidate(
        job_opening_id=job.id,
        candidate_name=candidate_name,
        email=email,
        contact_number=contact_number,
        experience=experience,
        skills=skills,
        current_company=current_company,
        notice_period=notice_period,
        current_ctc=current_ctc,
        expected_ctc=expected_ctc,
        source=source if source else "Manual Entry",
        remarks_notes=remarks_notes,
        resume_url=resume_url,
        status="Applied",
    )

    db.add(new_candidate)
    await db.commit()
    await db.refresh(new_candidate)

    return {
        "status": "success",
        "message": "Candidate added successfully.",
        "candidate_id": new_candidate.id,
    }


@router.get(
    "/candidates",
    response_model=list[schemas.CandidateOut],
    tags=["Social Media Governance"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_RECRUITER])),
    ],
)
async def get_all_candidates(
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(models.Candidate)
    if status_filter:
        query = query.where(models.Candidate.status.ilike(f"%{status_filter}%"))
    
    query = query.order_by(models.Candidate.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


# Directory for storing resumes locally
UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/public/forms/{uuid}", tags=["Public APIs"])
async def get_public_form(uuid: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.JobOpening).where(models.JobOpening.public_form_uuid == uuid)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=404, detail="Job opening not found or link has expired."
        )

    if job.current_status and job.current_status.lower() != "open":
        raise HTTPException(
            status_code=400, detail="This position is no longer accepting applications."
        )

    form_fields = [
        {
            "name": "candidate_name",
            "type": "text",
            "required": True,
            "label": "Candidate Name",
        },
        {"name": "email", "type": "email", "required": True, "label": "Email ID"},
        {
            "name": "contact_number",
            "type": "text",
            "required": True,
            "label": "Contact Number",
        },
        {"name": "experience", "type": "text", "required": True, "label": "Experience"},
        {"name": "skills", "type": "text", "required": True, "label": "Skills"},
        {
            "name": "resume_file",
            "type": "file",
            "required": True,
            "label": "Resume Upload (pdf,doc,docx up to 10 mb)",
        },
        {
            "name": "current_company",
            "type": "text",
            "required": False,
            "label": "Current Company",
        },
        {
            "name": "notice_period",
            "type": "text",
            "required": False,
            "label": "Notice Period",
        },
        {
            "name": "current_ctc",
            "type": "text",
            "required": False,
            "label": "Current CTC",
        },
        {
            "name": "expected_ctc",
            "type": "text",
            "required": False,
            "label": "Expected CTC",
        },
        {"name": "source", "type": "text", "required": False, "label": "Source"},
        {
            "name": "remarks_notes",
            "type": "text",
            "required": False,
            "label": "Remarks / Notes",
        },
    ]

    return {
        "job_id": job.id,
        "job_title": job.job_title,
        "experience_required": job.experience_required,
        "skills_required": job.skills_required,
        "status": job.current_status,
        "form_fields": form_fields,
    }


@router.post(
    "/public/forms/{uuid}/submit",
    tags=["Public APIs"],
    status_code=status.HTTP_201_CREATED,
)
async def submit_public_form(
    uuid: str,
    candidate_name: str = Form(...),
    email: str = Form(...),
    contact_number: str = Form(...),
    experience: str = Form(...),
    skills: str = Form(...),
    current_company: str = Form(None),
    notice_period: str = Form(None),
    current_ctc: str = Form(None),
    expected_ctc: str = Form(None),
    source: str = Form(None),
    remarks_notes: str = Form(None),
    resume_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.JobOpening).where(models.JobOpening.public_form_uuid == uuid)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=404, detail="Job opening not found or link has expired."
        )

    if job.current_status and job.current_status.lower() != "open":
        raise HTTPException(
            status_code=400, detail="This position is no longer accepting applications."
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        f"{job.id}_{candidate_name.replace(' ', '_')}_{resume_file.filename}",
    )
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume_file.file, buffer)

    resume_url = f"/{file_path}"

    new_candidate = models.Candidate(
        job_opening_id=job.id,
        candidate_name=candidate_name,
        email=email,
        contact_number=contact_number,
        experience=experience,
        skills=skills,
        current_company=current_company,
        notice_period=notice_period,
        current_ctc=current_ctc,
        expected_ctc=expected_ctc,
        source=source if source else "Career Site",
        remarks_notes=remarks_notes,
        resume_url=resume_url,
        status="Applied",
    )

    db.add(new_candidate)

    await db.commit()
    await db.refresh(new_candidate)

    return {
        "status": "success",
        "message": "Application submitted successfully.",
        "candidate_id": new_candidate.id,
    }
