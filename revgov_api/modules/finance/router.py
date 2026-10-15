import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db
from core.dependencies import get_current_active_user, RoleChecker
from core.constants import (
    ROLE_FINANCE_MANAGER,
    ROLE_PROJECT_MANAGER,
)
from auth.models import User
from . import schemas, service

router = APIRouter()


# /po-trackers Endpoints
@router.get(
    "/po-trackers",
    response_model=schemas.POTrackerListWithKPIs,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def list_potrackers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await service.potracker_service.get_all_with_kpis_by_user(db, current_user)


@router.get(
    "/po-trackers/{item_id}",
    response_model=schemas.POTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def get_potracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.potracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="POTracker not found")
    return obj


@router.post(
    "/po-trackers",
    response_model=schemas.POTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def create_potracker(
    payload: schemas.POTrackerCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    if payload.request_order_id:
        ro = await service.requestordertracker_service.get(db, payload.request_order_id)
        if not ro or not ro.approval_status or ro.approval_status.lower() != "approved":
            raise HTTPException(
                status_code=400,
                detail="Cannot create Purchase Order: The associated Purchase Request is not Approved yet.",
            )
    return await service.potracker_service.create_by_user(db, payload, current_user)


@router.put(
    "/po-trackers/{item_id}",
    response_model=schemas.POTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def update_potracker(
    item_id: int, payload: schemas.POTrackerUpdate, db: AsyncSession = Depends(get_db)
):
    db_obj = await service.potracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="POTracker not found")
    if payload.request_order_id and payload.request_order_id != db_obj.request_order_id:
        ro = await service.requestordertracker_service.get(db, payload.request_order_id)
        if not ro or not ro.approval_status or ro.approval_status.lower() != "approved":
            raise HTTPException(
                status_code=400,
                detail="Cannot update Purchase Order: The associated Purchase Request is not Approved yet.",
            )
    return await service.potracker_service.update(db, db_obj, payload)


@router.delete(
    "/po-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def delete_potracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.potracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="POTracker not found")
    return None


# /invoice-trackers Endpoints
@router.get(
    "/invoice-trackers",
    response_model=schemas.InvoiceTrackerListWithKPIs,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def list_invoicetrackers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await service.invoicetracker_service.get_all_with_kpis_by_user(db, current_user)


@router.get(
    "/invoice-trackers/{item_id}",
    response_model=schemas.InvoiceTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def get_invoicetracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.invoicetracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="InvoiceTracker not found")
    return obj


@router.post(
    "/invoice-trackers",
    response_model=schemas.InvoiceTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def create_invoicetracker(
    payload: schemas.InvoiceTrackerCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    if payload.po_id:
        po = await service.potracker_service.get(db, payload.po_id)
        if not po or not po.approval_status or po.approval_status.lower() != "approved":
            raise HTTPException(
                status_code=400,
                detail="Cannot create Invoice: The associated Purchase Order is not Approved yet.",
            )
    res = await service.invoicetracker_service.create_by_user(db, payload, current_user)
    
    # Create Payment Tracker if status is Completed
    if payload.payment_status and payload.payment_status.lower() == "completed":
        import uuid
        payment_payload = schemas.PaymentTrackerCreate(
            payment_id=f"PAY-{uuid.uuid4().hex[:6].upper()}",
            invoice_id=res.id,
            vendor_id=res.vendor_id,
            amount=res.invoice_amount,
            status="Completed"
        )
        await service.paymenttracker_service.create_by_user(db, payment_payload, current_user)
        
    return res


@router.put(
    "/invoice-trackers/{item_id}",
    response_model=schemas.InvoiceTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def update_invoicetracker(
    item_id: int,
    payload: schemas.InvoiceTrackerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_obj = await service.invoicetracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="InvoiceTracker not found")
        
    old_status = getattr(db_obj, "payment_status", None)
    
    if payload.po_id and payload.po_id != db_obj.po_id:
        po = await service.potracker_service.get(db, payload.po_id)
        if not po or not po.approval_status or po.approval_status.lower() != "approved":
            raise HTTPException(
                status_code=400,
                detail="Cannot update Invoice: The associated Purchase Order is not Approved yet.",
            )
            
    res = await service.invoicetracker_service.update(db, db_obj, payload)
    
    # Create Payment Tracker if status changed to Completed
    if payload.payment_status and payload.payment_status.lower() == "completed":
        if not old_status or old_status.lower() != "completed":
            import uuid
            payment_payload = schemas.PaymentTrackerCreate(
                payment_id=f"PAY-{uuid.uuid4().hex[:6].upper()}",
                invoice_id=res.id,
                vendor_id=res.vendor_id,
                amount=res.invoice_amount,
                status="Completed"
            )
            await service.paymenttracker_service.create_by_user(db, payment_payload, current_user)
            
    return res


@router.delete(
    "/invoice-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def delete_invoicetracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.invoicetracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="InvoiceTracker not found")
    return None


def _compute_budget_fields(budget):
    budget.remaining = (getattr(budget, "budget", 0) or 0) - (getattr(budget, "consumed", 0) or 0)
    budget.variance = (getattr(budget, "budget", 0) or 0) - (getattr(budget, "forecast", 0) or 0)
    return budget


# /budget-trackers Endpoints
@router.get(
    "/budget-trackers",
    response_model=schemas.BudgetTrackerListWithKPIs,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def list_budgettrackers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    result = await service.budgettracker_service.get_all_with_kpis_by_user(db, current_user)
    for b in result["data"]:
        _compute_budget_fields(b)
    return result


@router.get(
    "/budget-trackers/{item_id}",
    response_model=schemas.BudgetTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def get_budgettracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.budgettracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="BudgetTracker not found")
    return _compute_budget_fields(obj)


@router.post(
    "/budget-trackers",
    response_model=schemas.BudgetTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def create_budgettracker(
    payload: schemas.BudgetTrackerCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    obj = await service.budgettracker_service.create_by_user(db, payload, current_user)
    obj.remaining = (getattr(obj, "budget", 0) or 0) - (getattr(obj, "consumed", 0) or 0)
    obj.variance = (getattr(obj, "budget", 0) or 0) - (getattr(obj, "forecast", 0) or 0)
    await db.commit()
    await db.refresh(obj)
    
    if getattr(payload, "approval_status", None) and payload.approval_status.lower() == "approved":
        ro_payload = schemas.RequestOrderTrackerCreate(
            project_id=obj.project_id,
            cost=obj.budget,
            item="Budget Approval Request Order",
            reason="Auto-generated from Approved Budget",
        )
        await service.requestordertracker_service.create_by_user(db, ro_payload, current_user)
        
    return _compute_budget_fields(obj)


@router.put(
    "/budget-trackers/{item_id}",
    response_model=schemas.BudgetTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def update_budgettracker(
    item_id: int,
    payload: schemas.BudgetTrackerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_obj = await service.budgettracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="BudgetTracker not found")
        
    old_status = getattr(db_obj, "approval_status", None)
    
    obj = await service.budgettracker_service.update(db, db_obj, payload)
    obj.remaining = (getattr(obj, "budget", 0) or 0) - (getattr(obj, "consumed", 0) or 0)
    obj.variance = (getattr(obj, "budget", 0) or 0) - (getattr(obj, "forecast", 0) or 0)
    await db.commit()
    await db.refresh(obj)
    
    if getattr(payload, "approval_status", None) and payload.approval_status.lower() == "approved":
        if not old_status or old_status.lower() != "approved":
            ro_payload = schemas.RequestOrderTrackerCreate(
                project_id=obj.project_id,
                cost=obj.budget,
                item="Budget Approval Request Order",
                reason="Auto-generated from Approved Budget",
            )
            await service.requestordertracker_service.create_by_user(db, ro_payload, current_user)
            
    return _compute_budget_fields(obj)


@router.delete(
    "/budget-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def delete_budgettracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.budgettracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="BudgetTracker not found")
    return None


# /request-order-trackers Endpoints (Purchase Request Order)
@router.get(
    "/request-order-trackers",
    response_model=schemas.RequestOrderTrackerListWithKPIs,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def list_requestordertrackers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await service.requestordertracker_service.get_all_with_kpis_by_user(db, current_user)


@router.get(
    "/request-order-trackers/{item_id}",
    response_model=schemas.RequestOrderTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def get_requestordertracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.requestordertracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="RequestOrderTracker not found")
    return obj


@router.post(
    "/request-order-trackers",
    response_model=schemas.RequestOrderTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def create_requestordertracker(
    payload: schemas.RequestOrderTrackerCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    # Check if an approved budget tracker exists for this project
    from sqlalchemy import select
    from .models import BudgetTracker

    stmt = select(BudgetTracker).where(
        BudgetTracker.project_id == payload.project_id,
        BudgetTracker.approval_status.ilike("approved"),
    )
    res = await db.execute(stmt)
    approved_budget = res.scalars().first()
    if not approved_budget:
        raise HTTPException(
            status_code=400,
            detail="Cannot create Purchase Request / Request Order: The budget for this project is not approved yet.",
        )

    res = await service.requestordertracker_service.create_by_user(db, payload, current_user)
    
    if getattr(payload, "approval_status", None) and payload.approval_status.lower() == "approved":
        import uuid
        po_payload = schemas.POTrackerCreate(
            po_number=f"PO-{uuid.uuid4().hex[:6].upper()}",
            request_order_id=res.id,
            vendor_id=res.vendor_id,
            department_id=res.department_id,
            amount=res.cost,
            approval_status="Pending Approval"
        )
        await service.potracker_service.create_by_user(db, po_payload, current_user)
        
    return res


@router.put(
    "/request-order-trackers/{item_id}",
    response_model=schemas.RequestOrderTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def update_requestordertracker(
    item_id: int,
    payload: schemas.RequestOrderTrackerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_obj = await service.requestordertracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="RequestOrderTracker not found")

    old_status = getattr(db_obj, "approval_status", None)

    if payload.project_id and payload.project_id != db_obj.project_id:
        from sqlalchemy import select
        from .models import BudgetTracker

        stmt = select(BudgetTracker).where(
            BudgetTracker.project_id == payload.project_id,
            BudgetTracker.approval_status.ilike("approved"),
        )
        res = await db.execute(stmt)
        approved_budget = res.scalars().first()
        if not approved_budget:
            raise HTTPException(
                status_code=400,
                detail="Cannot update Purchase Request / Request Order: The budget for this project is not approved yet.",
            )

    res = await service.requestordertracker_service.update(db, db_obj, payload)
    
    if getattr(payload, "approval_status", None) and payload.approval_status.lower() == "approved":
        if not old_status or old_status.lower() != "approved":
            import uuid
            po_payload = schemas.POTrackerCreate(
                po_number=f"PO-{uuid.uuid4().hex[:6].upper()}",
                request_order_id=res.id,
                vendor_id=res.vendor_id,
                department_id=res.department_id,
                amount=res.cost,
                approval_status="Pending Approval"
            )
            await service.potracker_service.create_by_user(db, po_payload, current_user)
            
    return res


@router.delete(
    "/request-order-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER, ROLE_PROJECT_MANAGER])),
    ],
)
async def delete_requestordertracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.requestordertracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="RequestOrderTracker not found")
    return None


# /payment-trackers Endpoints (Payment Tracker)
@router.get(
    "/payment-trackers",
    response_model=schemas.PaymentTrackerListWithKPIs,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def list_paymenttrackers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await service.paymenttracker_service.get_all_with_kpis_by_user(db, current_user)


@router.get(
    "/payment-trackers/{item_id}",
    response_model=schemas.PaymentTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def get_paymenttracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.paymenttracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="PaymentTracker not found")
    return obj


@router.post(
    "/payment-trackers",
    response_model=schemas.PaymentTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def create_paymenttracker(
    payload: schemas.PaymentTrackerCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    if payload.invoice_id:
        inv = await service.invoicetracker_service.get(db, payload.invoice_id)
        if not inv:
            raise HTTPException(
                status_code=404,
                detail="Cannot create Payment Tracker: Associated Invoice not found.",
            )
            
        if not inv.payment_status or inv.payment_status.lower() != "completed":
            raise HTTPException(
                status_code=400,
                detail="Cannot create Payment Tracker: Associated Invoice's payment status must be 'Completed'.",
            )

    return await service.paymenttracker_service.create(db, payload)


@router.put(
    "/payment-trackers/{item_id}",
    response_model=schemas.PaymentTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def update_paymenttracker(
    item_id: int,
    payload: schemas.PaymentTrackerUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.paymenttracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="PaymentTracker not found")

    if payload.invoice_id and payload.invoice_id != db_obj.invoice_id:
        inv = await service.invoicetracker_service.get(db, payload.invoice_id)
        if not inv:
            raise HTTPException(
                status_code=404,
                detail="Cannot update Payment Tracker: Associated Invoice not found.",
            )

    res = await service.paymenttracker_service.update(db, db_obj, payload)
    if payload.status and payload.status.lower() == "completed" and res.invoice_id:
        inv = await service.invoicetracker_service.get(db, res.invoice_id)
        if inv:
            inv.payment_status = "Completed"
            await db.commit()
            await db.refresh(inv)
    return res


@router.delete(
    "/payment-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def delete_paymenttracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.paymenttracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="PaymentTracker not found")
    return None


# /revenue-trackers Endpoints
@router.get(
    "/revenue-trackers",
    response_model=schemas.RevenueTrackerListWithKPIs,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def list_revenuetrackers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return await service.revenuetracker_service.get_all_with_kpis_by_user(db, current_user)


@router.get(
    "/revenue-trackers/{item_id}",
    response_model=schemas.RevenueTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def get_revenuetracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.revenuetracker_service.get(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="RevenueTracker not found")
    return obj


@router.post(
    "/revenue-trackers",
    response_model=schemas.RevenueTrackerOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def create_revenuetracker(
    payload: schemas.RevenueTrackerCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    if payload.payment_id:
        pay = await service.paymenttracker_service.get(db, payload.payment_id)
        if not pay or not pay.status or pay.status.lower() != "completed":
            raise HTTPException(
                status_code=400,
                detail="Cannot create Revenue Tracker: The associated Payment is not Completed yet.",
            )
    return await service.revenuetracker_service.create_by_user(db, payload, current_user)


@router.put(
    "/revenue-trackers/{item_id}",
    response_model=schemas.RevenueTrackerOut,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def update_revenuetracker(
    item_id: int,
    payload: schemas.RevenueTrackerUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_obj = await service.revenuetracker_service.get(db, item_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="RevenueTracker not found")
    if payload.payment_id and payload.payment_id != db_obj.payment_id:
        pay = await service.paymenttracker_service.get(db, payload.payment_id)
        if not pay or not pay.status or pay.status.lower() != "completed":
            raise HTTPException(
                status_code=400,
                detail="Cannot update Revenue Tracker: The associated Payment is not Completed yet.",
            )
    return await service.revenuetracker_service.update(db, db_obj, payload)


@router.delete(
    "/revenue-trackers/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Finance & Procurement"],
    dependencies=[
        Depends(get_current_active_user),
        Depends(RoleChecker([ROLE_FINANCE_MANAGER])),
    ],
)
async def delete_revenuetracker(item_id: int, db: AsyncSession = Depends(get_db)):
    obj = await service.revenuetracker_service.delete(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="RevenueTracker not found")
    return None

