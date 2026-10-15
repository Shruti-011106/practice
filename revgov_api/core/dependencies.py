from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.config import settings
from core.constants import (
    ERR_CREDENTIALS_VALIDATE,
    ERR_INACTIVE_USER,
    AUTH_HEADER,
    TOKEN_TYPE,
)
from core.database import get_db
from auth.models import User

security = HTTPBearer()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    auth: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ERR_CREDENTIALS_VALIDATE,
        headers={AUTH_HEADER: TOKEN_TYPE},
    )
    try:
        payload = jwt.decode(
            auth.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == int(user_id))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail=ERR_INACTIVE_USER)
    return current_user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, request: Request, user: User = Depends(get_current_active_user)):
        from core.constants import (
            ROLE_SUPER_ADMIN,
            ROLE_CEO,
            ROLE_RECRUITER,
            ROLE_EMPLOYEE,
            ERR_PERMISSION_DENIED,
            PREFIX_MODULE_MAP,
        )

        user_roles = [role.name for role in user.roles]

        # --- Switch Role Logic ---
        active_role = request.headers.get("X-Active-Role")
        if active_role:
            if active_role not in user_roles:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid active role. You do not have the '{active_role}' role.",
                )
            eval_roles = [r for r in user.roles if r.name == active_role]
            eval_role_names = [active_role]
        else:
            eval_roles = user.roles
            eval_role_names = user_roles
        # -------------------------

        # 1. Super admin gets FULL access to everything automatically
        if ROLE_SUPER_ADMIN in eval_role_names:
            return True

        # 2. Try dynamic database-backed permissions check
        # Match request path to a module name
        path = request.url.path
        if path.startswith("/api/v1"):
            path = path[len("/api/v1") :]

        from core.constants import PREFIX_SUBMODULE_MAP, PREFIX_TRACKER_MAP
        
        module_name = None
        submodule_name = None
        tracker_name = None

        for prefix, mod in PREFIX_MODULE_MAP.items():
            if path.startswith(prefix):
                module_name = mod
                break
                
        for prefix, submod in PREFIX_SUBMODULE_MAP.items():
            if path.startswith(prefix):
                submodule_name = submod
                break
                
        for prefix, track in PREFIX_TRACKER_MAP.items():
            if path.startswith(prefix):
                tracker_name = track
                break

        # If we successfully mapped to a module, evaluate role permissions
        if module_name:
            # Check maximum allowed permission level across all user roles
            max_access = "—"
            access_rank = {"—": 0, "R": 1, "CU": 2, "CR": 3, "CRUD": 4}

            has_db_perms = False
            for role in eval_roles:
                if role.permissions is not None:
                    has_db_perms = True
                    
                    # Hierarchical Fallback: Tracker -> Submodule -> Module
                    role_access = "—"
                    
                    # 1. Backwards Compatibility for flat JSON
                    if tracker_name and tracker_name in role.permissions:
                        role_access = role.permissions.get(tracker_name)
                    elif submodule_name and submodule_name in role.permissions:
                        role_access = role.permissions.get(submodule_name)
                    elif module_name in role.permissions:
                        role_access = role.permissions.get(module_name)
                        
                    # 2. New Nested Tree Logic
                    else:
                        def slugify(text: str) -> str:
                            if not text:
                                return ""
                            return text.lower().replace(" & ", "_and_").replace(" / ", "_").replace(" ", "_")
                            
                        module_slug = slugify(module_name)
                        submodule_slug = slugify(submodule_name)
                        tracker_slug = slugify(tracker_name)
                        
                        current_node = role.permissions
                        if isinstance(current_node, dict):
                            # Module level
                            mod_node = current_node.get(module_slug) or current_node.get(module_name)
                            if mod_node:
                                if isinstance(mod_node, dict):
                                    role_access = mod_node.get("permission", role_access)
                                    current_node = mod_node.get("children", {})
                                elif isinstance(mod_node, str):
                                    role_access = mod_node
                                    current_node = {}
                                    
                                # Submodule level
                                if submodule_slug:
                                    sub_node = current_node.get(submodule_slug) or current_node.get(submodule_name)
                                    if sub_node:
                                        if isinstance(sub_node, dict):
                                            role_access = sub_node.get("permission", role_access)
                                            current_node = sub_node.get("children", {})
                                        elif isinstance(sub_node, str):
                                            role_access = sub_node
                                            current_node = {}
                                            
                                # Tracker level
                                if tracker_slug:
                                    track_node = current_node.get(tracker_slug) or current_node.get(tracker_name)
                                    if track_node:
                                        if isinstance(track_node, dict):
                                            role_access = track_node.get("permission", role_access)
                                        elif isinstance(track_node, str):
                                            role_access = track_node

                    if access_rank.get(role_access, 0) > access_rank.get(max_access, 0):
                        max_access = role_access

            # If database permissions were configured for this user, enforce them
            if has_db_perms:
                is_read = request.method in ["GET", "OPTIONS", "HEAD"]
                is_create = request.method == "POST"
                is_update = request.method in ["PUT", "PATCH"]

                allowed = False
                if max_access == "CRUD":
                    allowed = True
                elif max_access == "CR":
                    if is_read or is_create:
                        allowed = True
                elif (
                    max_access == "CU"
                ):  # Historically used for CRU (Read, Create, Update)
                    if is_read or is_create or is_update:
                        allowed = True
                elif max_access == "R":
                    if is_read:
                        allowed = True

                if allowed:
                    return True
                else:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Your role permissions do not allow {request.method} operations on {module_name}.",
                    )

        # 3. Fallback: Static configuration check (old logic)
        # CEO gets READ-ONLY access to everything automatically
        if ROLE_CEO in eval_role_names and request.method in ["GET", "OPTIONS", "HEAD"]:
            return True

        # Check if user has at least one module-specific allowed role
        if self.allowed_roles:
            matching_roles = [r for r in self.allowed_roles if r in eval_role_names]
            if matching_roles:
                # Delete logic fallback
                if request.method == "DELETE":
                    # Whitelist approach: Only explicit roles are trusted to delete if no DB perms are set
                    # If the matching roles (intersection of user's roles and route's allowed roles)
                    # only contains low-level roles, block the delete.
                    low_level_roles = [ROLE_RECRUITER, ROLE_EMPLOYEE]
                    if all(r in low_level_roles for r in matching_roles):
                        raise HTTPException(
                            status_code=403,
                            detail="Your role does not have permission to delete records.",
                        )
                return True

        # If no matching role, deny access
        raise HTTPException(status_code=403, detail=ERR_PERMISSION_DENIED)
