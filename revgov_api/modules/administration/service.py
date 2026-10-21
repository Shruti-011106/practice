import logging
from datetime import date, datetime, timezone
from typing import Optional, Any, List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.service import BaseService
from core.security import get_password_hash
from core.constants import (
    ROLE_SUPER_ADMIN,
    ROLE_CEO,
    ROLE_HR_MANAGER,
    ROLE_RECRUITER,
    ROLE_FINANCE_MANAGER,
    ROLE_PROJECT_MANAGER,
    ROLE_EMPLOYEE,
    ROLE_SALES_MANAGER,
    ROLE_PRESALES_MANAGER,
    ROLE_MARKETING_MANAGER,
    ROLE_LND_MANAGER,
    ROLE_CS_MANAGER,
)
from auth import models as auth_models
from modules.hr import models as hr_models
from . import models, schemas

logger = logging.getLogger(__name__)


class OrgSettingService(
    BaseService[
        models.OrgSetting, schemas.OrgSettingCreate, schemas.OrgSettingUpdate
    ]
):
    pass


org_setting_service = OrgSettingService(models.OrgSetting)


# ── Microsoft Entra ID Helpers & Services ──────────────────────────────────────

def mask_client_secret(secret: str) -> str:
    """Masks a client secret for safe display in API responses."""
    if not secret:
        return ""
    if len(secret) <= 8:
        return "********"
    return f"{secret[:4]}********{secret[-4:]}"


async def test_microsoft_entra_credentials(
    tenant_id: str, client_id: str, client_secret: str
) -> dict:
    """Tests Azure / Microsoft Entra ID credentials against the OAuth token endpoint."""
    import httpx

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(token_url, data=payload, headers=headers)
            try:
                data = resp.json()
            except Exception:
                data = {"error": resp.text}

            if resp.status_code == 200 and "access_token" in data:
                return {
                    "success": True,
                    "message": "Successfully authenticated with Microsoft Entra ID",
                    "token_type": data.get("token_type"),
                    "expires_in": data.get("expires_in"),
                }
            else:
                error_desc = data.get(
                    "error_description", data.get("error", "Authentication failed")
                )
                if isinstance(error_desc, str):
                    error_desc = error_desc.split("\r\n")[0]
                return {
                    "success": False,
                    "message": str(error_desc),
                }
    except Exception as exc:
        return {
            "success": False,
            "message": f"Connection error: {str(exc)}",
        }


async def get_microsoft_entra_access_token(
    tenant_id: str, client_id: str, client_secret: str
) -> str:
    """Acquires a valid OAuth2 Bearer token from Microsoft Entra ID."""
    import httpx

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(token_url, data=payload, headers=headers)
        data = resp.json()
        if resp.status_code == 200 and "access_token" in data:
            return data["access_token"]
        else:
            error_desc = data.get("error_description", data.get("error", "Authentication failed"))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Microsoft authentication failed: {error_desc}",
            )


def infer_role_from_ms_user(job_title: Optional[str], department: Optional[str]) -> str:
    """Infers the RevGov system role based on Microsoft 365 job title and department."""
    jt = (job_title or "").strip().lower()
    dept = (department or "").strip().lower()

    if any(k in jt for k in ["ceo", "chief executive", "managing director", "founder", "president"]):
        return ROLE_CEO
    if any(k in jt for k in ["recruiter", "talent acquisition", "sourcing"]):
        return ROLE_RECRUITER
    if "hr" in jt or "human resource" in jt or "talent" in jt or "hr" in dept or "human resource" in dept or "talent" in dept:
        return ROLE_HR_MANAGER
    if any(k in jt for k in ["finance", "account", "procurement", "controller", "billing", "cfo"]) or "finance" in dept:
        return ROLE_FINANCE_MANAGER
    if any(k in jt for k in ["project manager", "program manager", "delivery manager", "scrum master", "pmo", "project lead", "technical lead", "tech lead"]):
        return ROLE_PROJECT_MANAGER
    if any(k in jt for k in ["sales", "account executive", "business development", "bde", "bdm"]) or "sales" in dept:
        return ROLE_SALES_MANAGER
    if any(k in jt for k in ["presales", "pre-sales", "solution architect", "bid manager"]) or "presales" in dept:
        return ROLE_PRESALES_MANAGER
    if any(k in jt for k in ["marketing", "branding", "growth", "seo", "content writer"]) or "marketing" in dept or "growth" in dept:
        return ROLE_MARKETING_MANAGER
    if any(k in jt for k in ["learning", "l&d", "trainer", "training"]) or "learning" in dept or "l&d" in dept:
        return ROLE_LND_MANAGER
    if any(k in jt for k in ["customer success", "csm", "client partner"]) or "customer success" in dept:
        return ROLE_CS_MANAGER
    return ROLE_EMPLOYEE


def map_employment_type(emp_type_str: Optional[str]) -> Any:
    default_val = getattr(hr_models.EmploymentTypeEnum, "CONFIRMED", "Confirmed")
    if not emp_type_str:
        return default_val
    clean = emp_type_str.strip().lower()
    if "intern" in clean:
        return getattr(hr_models.EmploymentTypeEnum, "INTERN", "Intern")
    if "contract" in clean:
        return getattr(hr_models.EmploymentTypeEnum, "CONTRACT", "Contract")
    if "vendor" in clean:
        return getattr(hr_models.EmploymentTypeEnum, "VENDOR_RESOURCE", getattr(hr_models.EmploymentTypeEnum, "CONTRACT", "Contract"))
    if "probation" in clean:
        return getattr(hr_models.EmploymentTypeEnum, "PROBATION", getattr(hr_models.EmploymentTypeEnum, "FULL_TIME", "Full-Time"))
    if "notice" in clean:
        return getattr(hr_models.EmploymentTypeEnum, "NOTICE_PERIOD", getattr(hr_models.EmploymentTypeEnum, "FULL_TIME", "Full-Time"))
    return default_val


def parse_iso_date(date_str: Optional[str]) -> Optional[date]:
    if not date_str:
        return None
    try:
        clean = str(date_str).split("T")[0].strip()
        return datetime.strptime(clean, "%Y-%m-%d").date()
    except Exception:
        return None


async def fetch_microsoft_entra_users(
    db: AsyncSession,
    top: int = 100,
    search: Optional[str] = None,
    filter_str: Optional[str] = None,
    next_link: Optional[str] = None,
) -> dict:
    """Fetches all organization users from Microsoft Graph API using saved Entra ID credentials."""
    import httpx

    result = await db.execute(
        select(models.MicrosoftEntraConfig)
        .where(models.MicrosoftEntraConfig.is_active.is_(True))
        .order_by(models.MicrosoftEntraConfig.id.desc())
    )
    config = result.scalars().first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Microsoft Entra ID credentials are not configured or inactive. Please configure them via POST /api/v1/administration/microsoft-entra first.",
        )

    token = await get_microsoft_entra_access_token(
        config.tenant_id, config.client_id, config.client_secret
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "ConsistencyLevel": "eventual",
    }

    if next_link:
        url = next_link
        params = {}
    else:
        url = "https://graph.microsoft.com/v1.0/users"
        select_fields = (
            "id,displayName,givenName,surname,userPrincipalName,mail,jobTitle,"
            "department,mobilePhone,businessPhones,accountEnabled,"
            "employeeId,employeeType,employeeHireDate,officeLocation"
        )
        params = {
            "$top": min(max(top, 1), 999),
            "$select": select_fields,
            "$expand": "manager($select=id,displayName,mail,userPrincipalName)",
        }

        filters = []
        if filter_str:
            filters.append(filter_str)
        if search:
            escaped_search = search.replace("'", "''")
            filters.append(
                f"(startswith(displayName,'{escaped_search}') or "
                f"startswith(userPrincipalName,'{escaped_search}') or "
                f"startswith(mail,'{escaped_search}'))"
            )

        if filters:
            params["$filter"] = " and ".join(filters)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            try:
                data = resp.json()
            except Exception:
                data = {}

            if resp.status_code != 200:
                err_msg = data.get("error", {}).get("message", resp.text)
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Microsoft Graph API error: {err_msg}",
                )

            raw_users = data.get("value", [])
            users = []
            for u in raw_users:
                mgr_data = u.get("manager")
                mgr_item = None
                if mgr_data and isinstance(mgr_data, dict) and mgr_data.get("id"):
                    mgr_item = schemas.MicrosoftEntraManagerItem(
                        id=mgr_data.get("id"),
                        display_name=mgr_data.get("displayName"),
                        mail=mgr_data.get("mail"),
                        user_principal_name=mgr_data.get("userPrincipalName"),
                    )

                job_title = u.get("jobTitle")
                department = u.get("department")
                inferred = infer_role_from_ms_user(job_title, department)

                users.append(
                    schemas.MicrosoftEntraUserItem(
                        id=u.get("id"),
                        display_name=u.get("displayName"),
                        given_name=u.get("givenName"),
                        surname=u.get("surname"),
                        user_principal_name=u.get("userPrincipalName", ""),
                        mail=u.get("mail"),
                        job_title=job_title,
                        department=department,
                        mobile_phone=u.get("mobilePhone"),
                        business_phones=u.get("businessPhones") or [],
                        account_enabled=u.get("accountEnabled", True),
                        employee_id=u.get("employeeId"),
                        employee_type=u.get("employeeType"),
                        date_of_joining=u.get("employeeHireDate"),
                        office_location=u.get("officeLocation"),
                        manager=mgr_item,
                        inferred_role=inferred,
                    )
                )

            return {
                "total": len(users),
                "next_link": data.get("@odata.nextLink"),
                "users": users,
            }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users from Microsoft Entra: {str(exc)}",
        )


async def sync_microsoft_entra_users_to_db(db: AsyncSession) -> dict:
    """Fetches all users from Microsoft Graph API and synchronizes them into the database."""
    import httpx

    # 1. Fetch active credentials
    res_cfg = await db.execute(
        select(models.MicrosoftEntraConfig)
        .where(models.MicrosoftEntraConfig.is_active.is_(True))
        .order_by(models.MicrosoftEntraConfig.id.desc())
    )
    config = res_cfg.scalars().first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Microsoft Entra ID credentials are not configured or inactive. Please configure them via POST /api/v1/administration/microsoft-entra first.",
        )

    # 2. Get Access Token
    token = await get_microsoft_entra_access_token(
        config.tenant_id, config.client_id, config.client_secret
    )

    # 3. Fetch all users from Microsoft Graph
    headers = {
        "Authorization": f"Bearer {token}",
        "ConsistencyLevel": "eventual",
    }
    url = (
        "https://graph.microsoft.com/v1.0/users?$top=999"
        "&$select=id,displayName,givenName,surname,userPrincipalName,mail,jobTitle,"
        "department,mobilePhone,businessPhones,accountEnabled,"
        "employeeId,employeeType,employeeHireDate,officeLocation"
        "&$expand=manager($select=id,displayName,mail,userPrincipalName)"
    )

    all_ms_users = []
    async with httpx.AsyncClient(timeout=25.0) as client:
        current_url = url
        while current_url:
            resp = await client.get(current_url, headers=headers)
            if resp.status_code != 200:
                err_data = (
                    resp.json()
                    if resp.headers.get("content-type", "").startswith("application/json")
                    else {}
                )
                err_msg = err_data.get("error", {}).get("message", resp.text)
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Microsoft Graph API error: {err_msg}",
                )

            payload = resp.json()
            all_ms_users.extend(payload.get("value", []))
            current_url = payload.get("@odata.nextLink")

    # 4. Pre-fetch all System Roles
    roles_res = await db.execute(select(auth_models.Role))
    all_roles = {r.name: r for r in roles_res.scalars().all()}
    employee_role = all_roles.get(ROLE_EMPLOYEE)
    if not employee_role:
        employee_role = auth_models.Role(name=ROLE_EMPLOYEE, permissions={})
        db.add(employee_role)
        await db.flush()
        all_roles[ROLE_EMPLOYEE] = employee_role

    # 5. Pre-fetch existing Users, Employees, and Departments
    users_res = await db.execute(
        select(auth_models.User).options(selectinload(auth_models.User.roles))
    )
    existing_users = {u.email.lower(): u for u in users_res.scalars().all() if u.email}

    emp_res = await db.execute(select(hr_models.Employee))
    all_employees = emp_res.scalars().all()
    existing_employees = {e.email.lower(): e for e in all_employees if e.email}

    emp_code_field = "employee_id" if hasattr(hr_models.Employee, "employee_id") else "employee_code"
    existing_emp_codes = {
        getattr(e, emp_code_field).upper()
        for e in all_employees
        if getattr(e, emp_code_field, None)
    }
    assigned_user_ids = {e.user_id for e in all_employees if e.user_id}

    dept_res = await db.execute(select(hr_models.DepartmentMaster))
    all_depts = dept_res.scalars().all()
    departments = {
        d.department_name.lower(): d
        for d in all_depts
        if d.department_name
    }
    existing_dept_codes = {
        d.department_code.upper() for d in all_depts if d.department_code
    }

    created_users = 0
    updated_users = 0
    created_employees = 0

    # ── PASS 1: Create or Update Users, Departments, and Employees ──
    for ms_user in all_ms_users:
        raw_email = ms_user.get("mail") or ms_user.get("userPrincipalName")
        if not raw_email or "@" not in raw_email:
            continue
        email = raw_email.strip().lower()

        display_name = ms_user.get("displayName") or ""
        given_name = ms_user.get("givenName") or ""
        surname = ms_user.get("surname") or ""
        if not given_name and not surname and display_name:
            parts = display_name.strip().split(" ", 1)
            given_name = parts[0]
            surname = parts[1] if len(parts) > 1 else ""

        designation = ms_user.get("jobTitle") or "Employee"
        phones = ms_user.get("businessPhones") or []
        phone = ms_user.get("mobilePhone") or (phones[0] if phones else None)
        dept_name = ms_user.get("department")

        ms_emp_id = ms_user.get("employeeId")
        emp_type = map_employment_type(ms_user.get("employeeType"))
        doj = parse_iso_date(ms_user.get("employeeHireDate"))
        location = ms_user.get("officeLocation")

        # Inferred role
        inferred_role_name = infer_role_from_ms_user(designation, dept_name)
        user_target_role = all_roles.get(inferred_role_name)
        if not user_target_role:
            user_target_role = auth_models.Role(name=inferred_role_name, permissions={})
            db.add(user_target_role)
            await db.flush()
            all_roles[inferred_role_name] = user_target_role

        # Department resolution
        dept_id = None
        if dept_name and dept_name.strip():
            clean_dept = dept_name.strip()
            if clean_dept.lower() in departments:
                dept_id = departments[clean_dept.lower()].id
            else:
                base_code = "".join([w[0].upper() for w in clean_dept.split()[:4]]) or "GEN"
                code = base_code
                counter = 1
                while code.upper() in existing_dept_codes:
                    code = f"{base_code[:5]}_{counter}"
                    counter += 1
                new_dept = hr_models.DepartmentMaster(
                    department_name=clean_dept,
                    department_code=code,
                    status="Active",
                )
                db.add(new_dept)
                await db.flush()
                departments[clean_dept.lower()] = new_dept
                existing_dept_codes.add(code.upper())
                dept_id = new_dept.id

        # Upsert User
        target_user = existing_users.get(email)
        if not target_user:
            target_user = auth_models.User(
                email=email,
                first_name=given_name or display_name or "Team",
                last_name=surname or "Member",
                designation=designation,
                is_active=ms_user.get("accountEnabled", True),
                hashed_password=get_password_hash("TeamsAuth123!@#"),
                roles=[user_target_role],
            )
            db.add(target_user)
            await db.flush()
            existing_users[email] = target_user
            created_users += 1
        else:
            updated = False
            if designation and target_user.designation != designation:
                target_user.designation = designation
                updated = True
            if given_name and target_user.first_name != given_name:
                target_user.first_name = given_name
                updated = True
            if surname and target_user.last_name != surname:
                target_user.last_name = surname
                updated = True

            existing_role_names = [r.name for r in target_user.roles]
            if (
                ROLE_SUPER_ADMIN not in existing_role_names
                and ROLE_CEO not in existing_role_names
                and user_target_role not in target_user.roles
            ):
                target_user.roles = [user_target_role]
                updated = True

            if updated:
                updated_users += 1

        # Upsert Employee
        target_emp = existing_employees.get(email)
        if not target_emp:
            if ms_emp_id and str(ms_emp_id).strip() and str(ms_emp_id).strip().upper() not in existing_emp_codes:
                emp_code = str(ms_emp_id).strip()
            else:
                base_code = f"REV-{target_user.id:04d}"
                emp_code = base_code
                counter = 1
                while emp_code.upper() in existing_emp_codes:
                    emp_code = f"REV-{target_user.id:03d}_{counter}"
                    counter += 1
            existing_emp_codes.add(emp_code.upper())

            emp_user_id = target_user.id if target_user.id not in assigned_user_ids else None
            emp_kwargs = {
                emp_code_field: emp_code,
                "employee_name": f"{given_name} {surname}".strip() or display_name or email,
                "email": email,
                "user_id": emp_user_id,
                "department_id": dept_id,
                "designation": designation,
                "mobile_number": phone,
                "status": getattr(hr_models.StatusEnum, "ACTIVE", "Active"),
                "employment_type": emp_type,
                "doj": doj,
                "location": location,
            }
            target_emp = hr_models.Employee(**emp_kwargs)
            db.add(target_emp)
            await db.flush()
            existing_employees[email] = target_emp
            if emp_user_id:
                assigned_user_ids.add(emp_user_id)
            created_employees += 1
        else:
            if not target_emp.user_id and target_user.id not in assigned_user_ids:
                target_emp.user_id = target_user.id
                assigned_user_ids.add(target_user.id)
            if designation and target_emp.designation != designation:
                target_emp.designation = designation
            if dept_id and not target_emp.department_id:
                target_emp.department_id = dept_id
            if location and target_emp.location != location:
                target_emp.location = location
            if doj and target_emp.doj != doj:
                target_emp.doj = doj
            if emp_type and target_emp.employment_type != emp_type:
                target_emp.employment_type = emp_type
            if ms_emp_id and not getattr(target_emp, emp_code_field, None):
                setattr(target_emp, emp_code_field, str(ms_emp_id).strip())

    # ── PASS 2: Connect Reporting Managers ──
    for ms_user in all_ms_users:
        raw_email = ms_user.get("mail") or ms_user.get("userPrincipalName")
        if not raw_email:
            continue
        email = raw_email.strip().lower()
        emp = existing_employees.get(email)
        if not emp:
            continue

        mgr_data = ms_user.get("manager")
        if mgr_data and isinstance(mgr_data, dict):
            mgr_email = (
                mgr_data.get("mail") or mgr_data.get("userPrincipalName") or ""
            ).strip().lower()
            if mgr_email and mgr_email in existing_employees:
                mgr_emp = existing_employees[mgr_email]
                if mgr_emp and mgr_emp.id != emp.id and emp.manager_id != mgr_emp.id:
                    emp.manager_id = mgr_emp.id

    now = datetime.now(timezone.utc)
    config.last_synced_at = now
    config.synced_users_count = len(all_ms_users)

    await db.commit()

    return {
        "status": "success",
        "message": f"Successfully synchronized {len(all_ms_users)} organization users from Microsoft Teams.",
        "total_fetched": len(all_ms_users),
        "created_users": created_users,
        "updated_users": updated_users,
        "created_employees": created_employees,
        "synced_at": now,
    }
