from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import io
import csv

from app.core.import_registry import IMPORT_REGISTRY
from core.database import get_db
from core.dependencies import get_current_active_user

router = APIRouter(dependencies=[Depends(get_current_active_user)])


@router.get("/{tracker_type}")
async def export_data(tracker_type: str, db: AsyncSession = Depends(get_db)):
    if tracker_type not in IMPORT_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tracker type '{tracker_type}' is not supported for generic export.",
        )

    config = IMPORT_REGISTRY[tracker_type]
    ModelClass = config["model"]
    fk_config = config.get("foreign_keys", {})

    # 1. Fetch all records from the database
    stmt = select(ModelClass)
    result = await db.execute(stmt)
    records = result.scalars().all()

    # If there's no data, just return a template-like empty CSV with headers
    if not records:
        model_columns = [
            prop.key
            for prop in ModelClass.__mapper__.column_attrs
            if not prop.columns[0].primary_key
        ]
        headers = []
        for col in model_columns:
            if col in fk_config:
                headers.append(
                    fk_config[col].get(
                        "export_csv_column", fk_config[col]["csv_column"]
                    )
                )
            else:
                if col not in ["created_at", "updated_at"]:
                    headers.append(col)

        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(headers)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = (
            f"attachment; filename={tracker_type}_export.csv"
        )
        return response

    # 2. Build foreign key mapping cache to avoid N+1 queries
    # Format: fk_cache["manager_id"][1] = "Rahul Sharma"
    fk_cache: Dict[str, Dict[Any, Any]] = {}

    for db_fk_col, lookup_info in fk_config.items():
        lookup_model = lookup_info["lookup_model"]
        lookup_col = lookup_info.get(
            "export_lookup_column", lookup_info["lookup_column"]
        )

        # Collect all unique IDs for this foreign key column from our records
        unique_ids = {
            getattr(record, db_fk_col)
            for record in records
            if getattr(record, db_fk_col) is not None
        }

        fk_cache[db_fk_col] = {}
        if unique_ids:
            # Fetch all lookup values in a single query
            lookup_stmt = select(
                lookup_model.id, getattr(lookup_model, lookup_col)
            ).where(lookup_model.id.in_(unique_ids))
            lookup_res = await db.execute(lookup_stmt)
            for row in lookup_res.all():
                fk_cache[db_fk_col][row[0]] = row[1]

    # 3. Process rows and map them to CSV dictionaries
    csv_rows = []
    headers = []

    # We define headers from the first mapped row to preserve order
    model_columns = [
        prop.key
        for prop in ModelClass.__mapper__.column_attrs
        if not prop.columns[0].primary_key
    ]

    for col in model_columns:
        if col in fk_config:
            headers.append(
                fk_config[col].get("export_csv_column", fk_config[col]["csv_column"])
            )
        else:
            if col not in ["created_at", "updated_at"]:
                headers.append(col)

    for record in records:
        row_dict = {}
        for col in model_columns:
            if col in ["created_at", "updated_at"]:
                continue

            val = getattr(record, col)

            # Clean up Swagger default "string" values
            if isinstance(val, str) and val == "string":
                val = ""

            if col in fk_config:
                csv_col_name = fk_config[col].get(
                    "export_csv_column", fk_config[col]["csv_column"]
                )
                # Map ID to actual value using the cache
                if val is not None and val in fk_cache[col]:
                    row_dict[csv_col_name] = fk_cache[col][val]
                else:
                    row_dict[csv_col_name] = None
            else:
                row_dict[col] = val

        csv_rows.append(row_dict)

    # 4. Generate CSV Stream
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=headers)
    writer.writeheader()
    writer.writerows(csv_rows)

    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = (
        f"attachment; filename={tracker_type}_export.csv"
    )
    return response
