from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
import shutil
import os
from datetime import date
from core.database import get_db
from core.dependencies import get_current_active_user, RoleChecker
from core.constants import (
    ROLE_EMPLOYEE,
    ROLE_HR_MANAGER,
    ROLE_LND_MANAGER,
    ROLE_PROJECT_MANAGER,
    ROLE_SUPER_ADMIN,
    ROLE_CEO,
)
from . import schemas, service
from modules.hr.service import employee_service
from auth.models import User

router = APIRouter()


# /reusable-assets Endpoints
@router.get(
    "/reusable-assets",
    response_model=List[schemas.ReusableAssetOut],
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_LND_MANAGER])),
    ],
)
async def list_reusableassets(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await service.reusableasset_service.get_all_by_user(db, current_user)


@router.get(
    "/reusable-assets/{item_id}",
    response_model=schemas.ReusableAssetOut,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_LND_MANAGER])),
    ],
)
async def get_reusableasset(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.reusableasset_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ReusableAsset not found")
    return obj


@router.post(
    "/reusable-assets",
    response_model=schemas.ReusableAssetOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_LND_MANAGER])),
    ],
)
async def create_reusableasset(
    asset_name: str = Form(...),
    category: str = Form(...),
    owner_id: int = Form(...),
    technology: str = Form(...),
    version: Optional[str] = Form(None),
    document_name: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    repository_link: Optional[str] = Form(None),
    maturity_level: Optional[str] = Form(None),
    approval_status: Optional[str] = Form(None),
    last_review_date: Optional[date] = Form(None),
    tag: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    upload: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Validate that the employee exists
    employee = await employee_service.get(db, owner_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    file_path = None
    if upload is not None and upload.filename:
        # Validate file extension
        allowed_extensions = {
            ".pdf",
            ".docx",
            ".doc",
            ".pptx",
            ".ppt",
            ".xlsx",
            ".xls",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
        }
        _, ext = os.path.splitext(upload.filename.lower())
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '{ext}' is not allowed. Supported formats: PDF, Word, PowerPoint, Excel, and standard images.",
            )

        # Ensure uploads directory exists
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename to avoid collision
        unique_filename = f"{uuid.uuid4()}_{upload.filename}"
        file_path = f"{upload_dir}/{unique_filename}"

        # Save the file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)

    payload = schemas.ReusableAssetCreate(
        asset_name=asset_name,
        category=category,
        technology=technology,
        owner_id=owner_id,
        version=version,
        document_name=document_name,
        document_type=document_type,
        upload=file_path,
        repository_link=repository_link,
        maturity_level=maturity_level,
        approval_status=approval_status,
        last_review_date=last_review_date,
        tag=tag,
        description=description,
    )
    return await service.reusableasset_service.create_by_user(db, payload, current_user)


@router.put(
    "/reusable-assets/{item_id}",
    response_model=schemas.ReusableAssetOut,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_LND_MANAGER])),
    ],
)
async def update_reusableasset(
    item_id: int,
    asset_name: str = Form(...),
    category: str = Form(...),
    owner_id: int = Form(...),
    technology: str = Form(...),
    version: Optional[str] = Form(None),
    document_name: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    repository_link: Optional[str] = Form(None),
    maturity_level: Optional[str] = Form(None),
    approval_status: Optional[str] = Form(None),
    last_review_date: Optional[date] = Form(None),
    tag: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    upload: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.reusableasset_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ReusableAsset not found")

    # Validate that the employee exists
    employee = await employee_service.get(db, owner_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    file_path = db_obj.upload
    if upload is not None and upload.filename:
        # Validate file extension
        allowed_extensions = {
            ".pdf",
            ".docx",
            ".doc",
            ".pptx",
            ".ppt",
            ".xlsx",
            ".xls",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",
        }
        _, ext = os.path.splitext(upload.filename.lower())
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '{ext}' is not allowed. Supported formats: PDF, Word, PowerPoint, Excel, and standard images.",
            )

        # Ensure uploads directory exists
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename to avoid collision
        unique_filename = f"{uuid.uuid4()}_{upload.filename}"
        new_file_path = f"{upload_dir}/{unique_filename}"

        # Save the new file to disk
        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)

        # Clean up the old file if it exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        file_path = new_file_path

    payload = schemas.ReusableAssetUpdate(
        asset_name=asset_name,
        category=category,
        technology=technology,
        owner_id=owner_id,
        version=version,
        document_name=document_name,
        document_type=document_type,
        upload=file_path,
        repository_link=repository_link,
        maturity_level=maturity_level,
        approval_status=approval_status,
        last_review_date=last_review_date,
        tag=tag,
        description=description,
    )
    return await service.reusableasset_service.update(db, db_obj, payload)


@router.delete(
    "/reusable-assets/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_LND_MANAGER])),
    ],
)
async def delete_reusableasset(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.reusableasset_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="ReusableAsset not found")

    # Clean up the associated file if it exists
    if obj.upload and os.path.exists(obj.upload):
        try:
            os.remove(obj.upload)
        except Exception:
            pass
    return None


# Knowledge Repository - Merged into Reusable Asset (Temporarily Disabled)
# # /knowledge-repos Endpoints
# @router.get(
#     "/knowledge-repos",
#     response_model=List[schemas.KnowledgeRepoOut],
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_EMPLOYEE, ROLE_LND_MANAGER])),
#     ],
# )
# async def list_knowledgerepos(db: AsyncSession = Depends(get_db)):
#     return await service.knowledgerepo_service.get_all(db)
#
#
# @router.get(
#     "/knowledge-repos/{item_id}",
#     response_model=schemas.KnowledgeRepoOut,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_EMPLOYEE, ROLE_LND_MANAGER])),
#     ],
# )
# async def get_knowledgerepo(item_id: int, db: AsyncSession = Depends(get_db)):
#     obj = await service.knowledgerepo_service.get(db, item_id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="KnowledgeRepo not found")
#     return obj
#
#
# @router.post(
#     "/knowledge-repos",
#     response_model=schemas.KnowledgeRepoOut,
#     status_code=status.HTTP_201_CREATED,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_EMPLOYEE, ROLE_LND_MANAGER])),
#     ],
# )
# async def create_knowledgerepo(
#     payload: schemas.KnowledgeRepoCreate, db: AsyncSession = Depends(get_db)
# ):
#     return await service.knowledgerepo_service.create(db, payload)
#
#
# @router.put(
#     "/knowledge-repos/{item_id}",
#     response_model=schemas.KnowledgeRepoOut,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_EMPLOYEE, ROLE_LND_MANAGER])),
#     ],
# )
# async def update_knowledgerepo(
#     item_id: int,
#     payload: schemas.KnowledgeRepoUpdate,
#     db: AsyncSession = Depends(get_db),
# ):
#     db_obj = await service.knowledgerepo_service.get(db, item_id)
#     if not db_obj:
#         raise HTTPException(status_code=404, detail="KnowledgeRepo not found")
#     return await service.knowledgerepo_service.update(db, db_obj, payload)
#
#
# @router.delete(
#     "/knowledge-repos/{item_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_EMPLOYEE, ROLE_LND_MANAGER])),
#     ],
# )
# async def delete_knowledgerepo(item_id: int, db: AsyncSession = Depends(get_db)):
#     obj = await service.knowledgerepo_service.delete(db, item_id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="KnowledgeRepo not found")
#     return None


# /capability-buildings Endpoints
@router.get(
    "/capability-buildings",
    response_model=schemas.CapabilityBuildingListWithKPIs,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
            )
        ),
    ],
)
async def list_capabilitybuildings(
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_active_user),
    view: Optional[str] = Query(None, description="Set to 'employee' or 'manager' to filter data.")
):
    records = await service.capabilitybuilding_service.get_all_by_user(db, current_user, view)

    role_names = [role.name for role in current_user.roles] if current_user.roles else []
    is_employee_only = ROLE_EMPLOYEE in role_names and not any(r in role_names for r in [ROLE_SUPER_ADMIN, ROLE_CEO, ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_LND_MANAGER])

    kpis = {}

    if is_employee_only or (view and view.lower() == "employee"):
        # Employee KPIs
        total_trainings = 0
        completed_courses = 0
        certifications_completed = 0
        total_pct = 0.0
        pct_count = 0

        for rec in records:
            # Check training_details array
            if rec.training_details and isinstance(rec.training_details, list):
                for t in rec.training_details:
                    total_trainings += 1
                    if t.get("completion_pct") is not None:
                        total_pct += float(t.get("completion_pct"))
                        pct_count += 1
                    if t.get("completion_status") and str(t.get("completion_status")).strip().lower() in ["completed", "done"]:
                        completed_courses += 1
                    if t.get("certification_status") and str(t.get("certification_status")).strip().lower() in ["pass", "passed", "completed", "achieved"]:
                        certifications_completed += 1

        kpis = {
            "total_trainings": total_trainings,
            "completed_courses": completed_courses,
            "certifications_completed": certifications_completed,
            "learning_progress_pct": round(total_pct / pct_count, 2) if pct_count > 0 else 0.0,
        }
    else:
        # Admin KPIs
        total_employees_tracked = len(records)
        certifications_completed = 0
        active_training_tracks = 0
        intermediate_advance = 0

        for rec in records:
            # Additional check from training details
            if rec.training_details and isinstance(rec.training_details, list):
                for t in rec.training_details:
                    if t.get("certification_status") and str(t.get("certification_status")).strip().lower() in ["pass", "passed", "completed", "achieved"]:
                        certifications_completed += 1

            # Active Training Tracks
            if rec.training_details and isinstance(rec.training_details, list):
                for t in rec.training_details:
                    if t.get("completion_status") and str(t.get("completion_status")).strip().lower() in ["open", "in progress"]:
                        active_training_tracks += 1

            # Intermediate & Advance
            if rec.skill_level and rec.skill_level.strip().lower() in ["intermediate", "advance", "advanced"]:
                intermediate_advance += 1

        kpis = {
            "total_employees_tracked": total_employees_tracked,
            "certifications_completed": certifications_completed,
            "active_training_tracks": active_training_tracks,
            "intermediate_advance": intermediate_advance,
        }

    return {
        "kpis": kpis,
        "data": records,
    }


@router.get(
    "/capability-buildings/{item_id}",
    response_model=schemas.CapabilityBuildingOut,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
            )
        ),
    ],
)
async def get_capabilitybuilding(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.capabilitybuilding_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="CapabilityBuilding not found")
    return obj


@router.post(
    "/capability-buildings",
    response_model=schemas.CapabilityBuildingOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
            )
        ),
    ],
)
async def create_capabilitybuilding(
    payload: schemas.CapabilityBuildingCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return await service.capabilitybuilding_service.create_by_user(db, payload, current_user)


@router.put(
    "/capability-buildings/{item_id}",
    response_model=schemas.CapabilityBuildingOut,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
            )
        ),
    ],
)
async def update_capabilitybuilding(
    item_id: int,
    payload: schemas.CapabilityBuildingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_obj = await service.capabilitybuilding_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="CapabilityBuilding not found")
    return await service.capabilitybuilding_service.update_by_user(db, db_obj, payload, current_user)


@router.delete(
    "/capability-buildings/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(
            RoleChecker(
                [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
            )
        ),
    ],
)
async def delete_capabilitybuilding(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.capabilitybuilding_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="CapabilityBuilding not found")
    return None


# /partnership-alliances Endpoints
# @router.get(
#     "/partnership-alliances",
#     response_model=List[schemas.PartnershipAllianceOut],
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_LND_MANAGER])),
#     ],
# )
# async def list_partnershipalliances(db: AsyncSession = Depends(get_db)):
#     return await service.partnershipalliance_service.get_all(db)
#
#
# @router.get(
#     "/partnership-alliances/{item_id}",
#     response_model=schemas.PartnershipAllianceOut,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_LND_MANAGER])),
#     ],
# )
# async def get_partnershipalliance(item_id: int, db: AsyncSession = Depends(get_db)):
#     obj = await service.partnershipalliance_service.get(db, item_id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="PartnershipAlliance not found")
#     return obj
#
#
# @router.post(
#     "/partnership-alliances",
#     response_model=schemas.PartnershipAllianceOut,
#     status_code=status.HTTP_201_CREATED,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_LND_MANAGER])),
#     ],
# )
# async def create_partnershipalliance(
#     payload: schemas.PartnershipAllianceCreate, db: AsyncSession = Depends(get_db)
# ):
#     return await service.partnershipalliance_service.create(db, payload)
#
#
# @router.put(
#     "/partnership-alliances/{item_id}",
#     response_model=schemas.PartnershipAllianceOut,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_LND_MANAGER])),
#     ],
# )
# async def update_partnershipalliance(
#     item_id: int,
#     payload: schemas.PartnershipAllianceUpdate,
#     db: AsyncSession = Depends(get_db),
# ):
#     db_obj = await service.partnershipalliance_service.get(db, item_id)
#     if not db_obj:
#         raise HTTPException(status_code=404, detail="PartnershipAlliance not found")
#     return await service.partnershipalliance_service.update(db, db_obj, payload)
#
#
# @router.delete(
#     "/partnership-alliances/{item_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_LND_MANAGER])),
#     ],
# )
# async def delete_partnershipalliance(item_id: int, db: AsyncSession = Depends(get_db)):
#     obj = await service.partnershipalliance_service.delete(db, item_id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="PartnershipAlliance not found")
#     return None


# /tech-capabilities Endpoints
# @router.get(
#     "/tech-capabilities",
#     response_model=List[schemas.TechCapabilityOut],
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_LND_MANAGER])),
#     ],
# )
# async def list_techcapabilitys(db: AsyncSession = Depends(get_db)):
#     return await service.techcapability_service.get_all(db)
#
#
# @router.get(
#     "/tech-capabilities/{item_id}",
#     response_model=schemas.TechCapabilityOut,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_LND_MANAGER])),
#     ],
# )
# async def get_techcapability(item_id: int, db: AsyncSession = Depends(get_db)):
#     obj = await service.techcapability_service.get(db, item_id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="TechCapability not found")
#     return obj
#
#
# @router.post(
#     "/tech-capabilities",
#     response_model=schemas.TechCapabilityOut,
#     status_code=status.HTTP_201_CREATED,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_LND_MANAGER])),
#     ],
# )
# async def create_techcapability(
#     payload: schemas.TechCapabilityCreate, db: AsyncSession = Depends(get_db)
# ):
#     return await service.techcapability_service.create(db, payload)
#
#
# @router.put(
#     "/tech-capabilities/{item_id}",
#     response_model=schemas.TechCapabilityOut,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_LND_MANAGER])),
#     ],
# )
# async def update_techcapability(
#     item_id: int,
#     payload: schemas.TechCapabilityUpdate,
#     db: AsyncSession = Depends(get_db),
# ):
#     db_obj = await service.techcapability_service.get(db, item_id)
#     if not db_obj:
#         raise HTTPException(status_code=404, detail="TechCapability not found")
#     return await service.techcapability_service.update(db, db_obj, payload)
#
#
# @router.delete(
#     "/tech-capabilities/{item_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(RoleChecker([ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_LND_MANAGER])),
#     ],
# )
# async def delete_techcapability(item_id: int, db: AsyncSession = Depends(get_db)):
#     obj = await service.techcapability_service.delete(db, item_id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="TechCapability not found")
#     return None


# /innovation-automations Endpoints
@router.get(
    "/innovation-automations",
    response_model=schemas.InnovationAutomationListWithKPIs,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER])),
    ],
)
async def list_innovationautomations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    innovations = await service.innovationautomation_service.get_all_by_user(db, current_user)

    total_innovations = len(innovations)
    ai_automations = 0
    high_efficiency_gain = 0
    active_implementations = 0

    for inv in innovations:
        # Check AI automations
        if inv.automation_type and "AI" in inv.automation_type.upper():
            ai_automations += 1

        # Check high efficiency gain (>= 30)
        if inv.productivity_gain:
            import re

            numbers = re.findall(r"\d+", inv.productivity_gain)
            if numbers:
                # Find first number in string
                val = int(numbers[0])
                if val >= 30:
                    high_efficiency_gain += 1

        # Check active implementations
        if inv.status and inv.status.strip().lower() in ["implemented", "scaled"]:
            active_implementations += 1

    return {
        "kpis": {
            "total_innovations": total_innovations,
            "ai_automations": ai_automations,
            "high_efficiency_gain": high_efficiency_gain,
            "active_implementations": active_implementations,
        },
        "data": innovations,
    }


@router.get(
    "/innovation-automations/{item_id}",
    response_model=schemas.InnovationAutomationOut,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER])),
    ],
)
async def get_innovationautomation(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.innovationautomation_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="InnovationAutomation not found")
    return obj


@router.post(
    "/innovation-automations",
    response_model=schemas.InnovationAutomationOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER])),
    ],
)
async def create_innovationautomation(
    payload: schemas.InnovationAutomationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return await service.innovationautomation_service.create_by_user(db, payload, current_user)


@router.put(
    "/innovation-automations/{item_id}",
    response_model=schemas.InnovationAutomationOut,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER])),
    ],
)
async def update_innovationautomation(
    item_id: int,
    payload: schemas.InnovationAutomationUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.innovationautomation_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="InnovationAutomation not found")
    return await service.innovationautomation_service.update(db, db_obj, payload)


@router.delete(
    "/innovation-automations/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Learning & Development"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER])),
    ],
)
async def delete_innovationautomation(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.innovationautomation_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="InnovationAutomation not found")
    return None


# /training-trackers Endpoints (Commented out to keep only 3 L&D trackers active)
# @router.get(
#     "/training-trackers",
#     response_model=List[schemas.TrainingTrackerOut],
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(
#             RoleChecker(
#                 [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
#             )
#         ),
#     ],
# )
# async def list_trainingtrackers(db: AsyncSession = Depends(get_db)):
#     return await service.trainingtracker_service.get_all(db)
# 
# 
# @router.get(
#     "/training-trackers/{item_id}",
#     response_model=schemas.TrainingTrackerOut,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(
#             RoleChecker(
#                 [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
#             )
#         ),
#     ],
# )
# async def get_trainingtracker(item_id: int, db: AsyncSession = Depends(get_db)):
#     obj = await service.trainingtracker_service.get(db, item_id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="TrainingTracker not found")
#     return obj
# 
# 
# @router.post(
#     "/training-trackers",
#     response_model=schemas.TrainingTrackerOut,
#     status_code=status.HTTP_201_CREATED,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(
#             RoleChecker(
#                 [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
#             )
#         ),
#     ],
# )
# async def create_trainingtracker(
#     payload: schemas.TrainingTrackerCreate, db: AsyncSession = Depends(get_db)
# ):
#     return await service.trainingtracker_service.create(db, payload)
# 
# 
# @router.put(
#     "/training-trackers/{item_id}",
#     response_model=schemas.TrainingTrackerOut,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(
#             RoleChecker(
#                 [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
#             )
#         ),
#     ],
# )
# async def update_trainingtracker(
#     item_id: int,
#     payload: schemas.TrainingTrackerUpdate,
#     db: AsyncSession = Depends(get_db),
# ):
#     db_obj = await service.trainingtracker_service.get(db, item_id)
#     if not db_obj:
#         raise HTTPException(status_code=404, detail="TrainingTracker not found")
#     return await service.trainingtracker_service.update(db, db_obj, payload)
# 
# 
# @router.delete(
#     "/training-trackers/{item_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     tags=["Learning & Development"],
#     dependencies=[
#         Depends(get_current_active_user),
#         Depends(
#             RoleChecker(
#                 [ROLE_HR_MANAGER, ROLE_PROJECT_MANAGER, ROLE_EMPLOYEE, ROLE_LND_MANAGER]
#             )
#         ),
#     ],
# )
# async def delete_trainingtracker(item_id: int, db: AsyncSession = Depends(get_db)):
#     obj = await service.trainingtracker_service.delete(db, item_id)
#     if not obj:
#         raise HTTPException(status_code=404, detail="TrainingTracker not found")
#     return None
