import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database import get_db
from modules.hr.models import JobOpening, Candidate

router = APIRouter()

# Directory for storing resumes locally
UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/forms/{uuid}", tags=["Public APIs"])
async def get_public_form(uuid: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(JobOpening).where(JobOpening.public_form_uuid == uuid)
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

    # Dynamic form fields configuration could be constructed here
    form_fields = [
        {
            "name": "candidate_name",
            "type": "text",
            "required": True,
            "label": "Full Name",
        },
        {"name": "email", "type": "email", "required": True, "label": "Email Address"},
        {
            "name": "contact_number",
            "type": "text",
            "required": True,
            "label": "Contact Number",
        },
        {"name": "experience", "type": "text", "required": True, "label": "Experience"},
        {"name": "skills", "type": "text", "required": True, "label": "Skills"},
        {
            "name": "current_company",
            "type": "text",
            "required": False,
            "label": "Current Company",
        },
        {
            "name": "expected_ctc",
            "type": "text",
            "required": False,
            "label": "Expected CTC",
        },
        {
            "name": "resume_file",
            "type": "file",
            "required": True,
            "label": "Upload Resume (PDF/DOC)",
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
    "/forms/{uuid}/submit", tags=["Public APIs"], status_code=status.HTTP_201_CREATED
)
async def submit_public_form(
    uuid: str,
    candidate_name: str = Form(..., min_length=2, max_length=100),
    email: EmailStr = Form(...),
    contact_number: str = Form(
        ..., min_length=10, max_length=15, pattern=r"^\+?[0-9\-\s]+$"
    ),
    experience: str = Form(..., max_length=50),
    skills: str = Form(..., max_length=500),
    current_company: str = Form(None, max_length=100),
    expected_ctc: str = Form(None, max_length=50),
    resume_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Verify job opening exists and is open
    result = await db.execute(
        select(JobOpening).where(JobOpening.public_form_uuid == uuid)
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

    # Save the uploaded file
    file_path = os.path.join(
        UPLOAD_DIR,
        f"{job.id}_{candidate_name.replace(' ', '_')}_{resume_file.filename}",
    )
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume_file.file, buffer)

    resume_url = f"/{file_path}"  # Ideally this would be an S3 URL or similar

    # Create the candidate
    new_candidate = Candidate(
        job_opening_id=job.id,
        candidate_name=candidate_name,
        email=email,
        contact_number=contact_number,
        experience=experience,
        skills=skills,
        current_company=current_company,
        expected_ctc=expected_ctc,
        resume_url=resume_url,
        source="Career Site",
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
