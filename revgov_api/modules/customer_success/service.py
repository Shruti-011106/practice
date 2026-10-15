from sqlalchemy.ext.asyncio import AsyncSession
from core.service import BaseService
from . import models, schemas


class QBRTrackerService(
    BaseService[models.QBRTracker, schemas.QBRTrackerCreate, schemas.QBRTrackerUpdate]
):
    pass


qbrtracker_service = QBRTrackerService(models.QBRTracker)


class EscalationTrackerService(
    BaseService[
        models.EscalationTracker,
        schemas.EscalationTrackerCreate,
        schemas.EscalationTrackerUpdate,
    ]
):
    pass


escalationtracker_service = EscalationTrackerService(models.EscalationTracker)


class ExecutiveContentTrackerService(
    BaseService[
        models.ExecutiveContentTracker,
        schemas.ExecutiveContentTrackerCreate,
        schemas.ExecutiveContentTrackerUpdate,
    ]
):
    pass


executivecontenttracker_service = ExecutiveContentTrackerService(
    models.ExecutiveContentTracker
)


class CustomerMasterService(
    BaseService[
        models.CustomerMaster,
        schemas.CustomerMasterCreate,
        schemas.CustomerMasterUpdate,
    ]
):
    async def create(
        self, db: AsyncSession, obj_in: schemas.CustomerMasterCreate, **extra_data
    ) -> models.CustomerMaster:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        query = select(self.model.customer_id)
        result = await db.execute(query)
        all_cids = result.scalars().all()

        max_num = 0
        for cid in all_cids:
            if cid and cid.startswith("C"):
                try:
                    num = int(cid[1:])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass

        new_num = max_num + 1
        obj_in.customer_id = f"C{new_num:03d}"

        db_obj = await super().create(db, obj_in, **extra_data)

        query = (
            select(self.model)
            .options(selectinload(self.model.account_manager))
            .filter(self.model.id == db_obj.id)
        )
        result = await db.execute(query)
        return result.scalar_one()


customermaster_service = CustomerMasterService(models.CustomerMaster)
