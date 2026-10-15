from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Optional
from core.database import get_db
from core.constants import ROLE_SUPER_ADMIN
from .models import SystemLookup
from .schemas import SystemLookupCreate, SystemLookupUpdate, SystemLookupOut
from app.api.crud_factory import make_router

router = APIRouter(prefix="/masters", tags=["Masters"])


# Custom Endpoint for grouped lookups as per standard pattern
@router.get("/lookups")
async def get_grouped_lookups(
    lookup_type: Optional[str] = Query(
        None, description="Filter by a specific lookup type (e.g., MATURITY_LEVEL)"
    ),
    db: AsyncSession = Depends(get_db),
):
    query = select(SystemLookup).where(SystemLookup.is_active.is_(True))

    if lookup_type:
        query = query.where(SystemLookup.type == lookup_type)

    query = query.order_by(SystemLookup.type, SystemLookup.sort_order)

    result = await db.execute(query)
    lookups = result.scalars().all()

    grouped_lookups: Dict[str, List[Dict[str, str]]] = {}
    for lookup in lookups:
        # Convert type to lowercase plural for the key (e.g., USER_ROLE -> user_roles)
        # This is a simple conversion, might need a mapping for complex plurals
        key = lookup.type.lower() + "s"

        if key not in grouped_lookups:
            grouped_lookups[key] = []

        grouped_lookups[key].append({"value": lookup.code, "label": lookup.label})

    return grouped_lookups


# Standard CRUD for managing lookups (Restricted to SUPER_ADMIN)
crud_router = make_router(
    SystemLookup,
    SystemLookupCreate,
    SystemLookupUpdate,
    SystemLookupOut,
    "/sys-lookups",
    ["Masters"],
    allowed_roles=[ROLE_SUPER_ADMIN],
)

router.include_router(crud_router)
