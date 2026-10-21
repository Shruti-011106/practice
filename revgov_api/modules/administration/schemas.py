# pyrefly: ignore [missing-import]
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from core.schemas import CommonOut


class OrgSettingBase(BaseModel):
    organization_name: str
    legal_name: Optional[str] = None
    alias_name: Optional[str] = None
    primary_domain: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    country: Optional[str] = None
    company_logo: Optional[str] = None

    admin_email: EmailStr
    support_email: Optional[EmailStr] = None
    billing_contact_email: Optional[EmailStr] = None


class OrgSettingCreate(OrgSettingBase):
    pass


class OrgSettingUpdate(BaseModel):
    organization_name: Optional[str] = None
    legal_name: Optional[str] = None
    alias_name: Optional[str] = None
    primary_domain: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    country: Optional[str] = None
    company_logo: Optional[str] = None

    admin_email: Optional[EmailStr] = None
    support_email: Optional[EmailStr] = None
    billing_contact_email: Optional[EmailStr] = None


class OrgSettingOut(CommonOut, OrgSettingBase):
    pass


# ── Microsoft Entra ID / Teams Configuration Schemas ───────────────────────────

class MicrosoftEntraConfigBase(BaseModel):
    tenant_id: str = Field(..., description="Microsoft Entra ID / Azure Tenant ID")
    client_id: str = Field(..., description="Application / Client ID")
    organization_id: Optional[int] = Field(None, description="Optional organization setting ID reference")
    is_active: Optional[bool] = Field(True, description="Whether this configuration is currently active")


class MicrosoftEntraConfigCreate(MicrosoftEntraConfigBase):
    client_secret: str = Field(..., description="Microsoft Entra ID Client Secret value")
    verify_connection: Optional[bool] = Field(
        True, description="Whether to test credentials against Microsoft OAuth before saving"
    )


class MicrosoftEntraConfigUpdate(BaseModel):
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    organization_id: Optional[int] = None
    is_active: Optional[bool] = None
    verify_connection: Optional[bool] = False


class MicrosoftEntraConfigOut(CommonOut, MicrosoftEntraConfigBase):
    client_secret_masked: str
    connection_status: str
    last_tested_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None
    synced_users_count: Optional[int] = 0


class MicrosoftEntraTestRequest(BaseModel):
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


class MicrosoftEntraTestResponse(BaseModel):
    status: str
    message: str
    token_type: Optional[str] = None
    expires_in: Optional[int] = None


class MicrosoftEntraManagerItem(BaseModel):
    id: Optional[str] = Field(None, description="Manager Microsoft Object ID")
    display_name: Optional[str] = Field(None, description="Manager Full Name")
    mail: Optional[str] = Field(None, description="Manager Email")
    user_principal_name: Optional[str] = Field(None, description="Manager UPN")


class MicrosoftEntraUserItem(BaseModel):
    id: str = Field(..., description="Microsoft 365 / Entra ID User Object ID")
    display_name: Optional[str] = Field(None, description="Full display name")
    given_name: Optional[str] = Field(None, description="First name")
    surname: Optional[str] = Field(None, description="Last name")
    user_principal_name: str = Field(..., description="Username / User Principal Name (UPN)")
    mail: Optional[str] = Field(None, description="Email address")
    job_title: Optional[str] = Field(None, description="Job title / Designation")
    department: Optional[str] = Field(None, description="Department")
    mobile_phone: Optional[str] = Field(None, description="Mobile phone number")
    business_phones: List[str] = Field(default=[], description="Business phone numbers")
    account_enabled: Optional[bool] = Field(True, description="Whether the account is enabled")
    employee_id: Optional[str] = Field(None, description="Employee ID from organization")
    employee_type: Optional[str] = Field(None, description="Employee type (Full-time, Contract, Intern)")
    date_of_joining: Optional[str] = Field(None, description="Date of joining / hire date")
    office_location: Optional[str] = Field(None, description="Office location / Branch")
    manager: Optional[MicrosoftEntraManagerItem] = Field(None, description="Reporting Manager details")
    inferred_role: Optional[str] = Field(None, description="Inferred system role")


class MicrosoftEntraUsersResponse(BaseModel):
    total: int = Field(..., description="Number of users returned in current batch")
    next_link: Optional[str] = Field(None, description="OData URL for next page of users if more exist")
    users: List[MicrosoftEntraUserItem] = Field(default=[], description="List of organization users")


class MicrosoftEntraSyncResponse(BaseModel):
    status: str
    message: str
    total_fetched: int
    created_users: int
    updated_users: int
    created_employees: int
    synced_at: datetime
