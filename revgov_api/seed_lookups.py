import asyncio
import os
import sys

# Add the current directory to sys.path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import AsyncSessionLocal
from modules.masters.models import SystemLookup
from sqlalchemy.future import select

# Data to seed
LOOKUPS_TO_SEED = [
    {"type": "STATUS", "code": "ACTIVE", "label": "Active", "sort_order": 1},
    {"type": "STATUS", "code": "INACTIVE", "label": "Inactive", "sort_order": 2},
    {"type": "STATUS", "code": "ONBOARDING", "label": "Onboarding", "sort_order": 3},
    {"type": "EMPLOYMENT_TYPE", "code": "INTERN", "label": "Intern", "sort_order": 1},
    {
        "type": "EMPLOYMENT_TYPE",
        "code": "CONFIRMED",
        "label": "Confirmed",
        "sort_order": 2,
    },
    {"type": "CATEGORY", "code": "NOT_REUSED", "label": "Not Reused", "sort_order": 1},
    {"type": "CATEGORY", "code": "LOW_REUSE", "label": "Low Reuse", "sort_order": 2},
    {
        "type": "CATEGORY",
        "code": "MODERATE_REUSE",
        "label": "Moderate Reuse",
        "sort_order": 3,
    },
    {"type": "CATEGORY", "code": "HIGH_REUSE", "label": "High Reuse", "sort_order": 4},
    {
        "type": "CATEGORY",
        "code": "HIGHLY_REUSABLE",
        "label": "Highly Reusable / Enterprise Asset",
        "sort_order": 5,
    },
    {"type": "MATURITY_LEVEL", "code": "STAGE_1", "label": "Stage 1", "sort_order": 1},
    {"type": "MATURITY_LEVEL", "code": "STAGE_2", "label": "Stage 2", "sort_order": 2},
    {"type": "MATURITY_LEVEL", "code": "STAGE_3", "label": "Stage 3", "sort_order": 3},
    # Innovation Status
    {
        "type": "INNOVATION_STATUS",
        "code": "IDEA_SUBMITTED",
        "label": "Idea Submitted",
        "sort_order": 1,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "UNDER_REVIEW",
        "label": "Under Review",
        "sort_order": 2,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "FEASIBILITY_ASSESSMENT",
        "label": "Feasibility Assessment",
        "sort_order": 3,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "APPROVED_FOR_POC",
        "label": "Approved for POC",
        "sort_order": 4,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "POC_IN_PROGRESS",
        "label": "POC in Progress",
        "sort_order": 5,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "POC_COMPLETED",
        "label": "POC Completed",
        "sort_order": 6,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "PILOT_INITIATED",
        "label": "Pilot Initiated",
        "sort_order": 7,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "PILOT_SUCCESSFUL",
        "label": "Pilot Successful",
        "sort_order": 8,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "PILOT_FAILED",
        "label": "Pilot Failed",
        "sort_order": 9,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "BUSINESS_APPROVAL_PENDING",
        "label": "Business Approval Pending",
        "sort_order": 10,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "APPROVED_FOR_IMPLEMENTATION",
        "label": "Approved for Implementation",
        "sort_order": 11,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "DEVELOPMENT_IN_PROGRESS",
        "label": "Development in Progress",
        "sort_order": 12,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "UAT_IN_PROGRESS",
        "label": "UAT in Progress",
        "sort_order": 13,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "READY_FOR_DEPLOYMENT",
        "label": "Ready for Deployment",
        "sort_order": 14,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "IMPLEMENTED",
        "label": "Implemented",
        "sort_order": 15,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "ADOPTION_IN_PROGRESS",
        "label": "Adoption in Progress",
        "sort_order": 16,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "BENEFITS_REALIZATION_TRACKING",
        "label": "Benefits Realization Tracking",
        "sort_order": 17,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "SCALED_ACROSS_TEAMS",
        "label": "Scaled Across Teams",
        "sort_order": 18,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "ON_HOLD",
        "label": "On Hold",
        "sort_order": 19,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "REJECTED",
        "label": "Rejected",
        "sort_order": 20,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "CLOSED",
        "label": "Closed",
        "sort_order": 21,
    },
    {
        "type": "INNOVATION_STATUS",
        "code": "ARCHIVED",
        "label": "Archived",
        "sort_order": 22,
    },
]


async def seed_data():
    print("Starting data seeding...")
    async with AsyncSessionLocal() as session:
        for lookup_data in LOOKUPS_TO_SEED:
            # Check if it already exists
            query = select(SystemLookup).where(
                SystemLookup.type == lookup_data["type"],
                SystemLookup.code == lookup_data["code"],
            )
            result = await session.execute(query)
            existing = result.scalar_one_or_none()

            if not existing:
                print(f"Adding: {lookup_data['type']} -> {lookup_data['label']}")
                new_lookup = SystemLookup(**lookup_data)
                session.add(new_lookup)
            else:
                print(
                    f"Already exists: {lookup_data['type']} -> {lookup_data['label']}"
                )

        await session.commit()
    print("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
