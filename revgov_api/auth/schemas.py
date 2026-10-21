from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from core.schemas import CommonOut
from pydantic import computed_field




   
class RoleBase(BaseModel):
    name: str


class RoleResponse(CommonOut, RoleBase):
    permissions: Optional[dict] = {}


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    designation: Optional[str] = None
    
    mobile_number: Optional[str] = Field(
    None,
    min_length=10,
    max_length=10,
    pattern=r"^[0-9]{10}$"
    )




class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role_ids: List[int] = Field(..., min_length=1)
    employee_id: int


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    designation: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None


class UserResponse(CommonOut, UserBase):
    is_active: bool = Field(exclude=True)
    roles: List[RoleResponse] = []

    @computed_field
    @property
    def status(self) -> str:
        return "Active" if self.is_active else "Inactive"

class UserMeResponse(UserResponse):
    accessible_modules: List[str] = []


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    message: str
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str


class MessageResponse(BaseModel):
    message: str


class TeamsSSORequest(BaseModel):
    code: Optional[str] = Field(None, description="Microsoft authorization code from OAuth login")
    token: Optional[str] = Field(None, description="Microsoft ID token or access token from Teams login")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI used during login")
    code_verifier: Optional[str] = Field(None, description="PKCE code verifier for OAuth code flow")
