import pandas as pd
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Float, Numeric, Integer, Boolean
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any
import io
import csv

from app.core.import_registry import IMPORT_REGISTRY
from core.database import get_db
from core.dependencies import get_current_active_user

router = APIRouter(dependencies=[Depends(get_current_active_user)])


@router.get("/trackers")
async def get_supported_trackers():
    trackers = []
    for key, config in IMPORT_REGISTRY.items():
        model_class = config["model"]
        fk_config = config.get("foreign_keys", {})

        # Get standard columns, excluding PK and auto timestamps
        model_columns = [
            prop.key
            for prop in model_class.__mapper__.column_attrs
            if not prop.columns[0].primary_key
        ]

        required_cols = []
        for col in model_columns:
            if col in fk_config:
                required_cols.append(fk_config[col]["csv_column"])
            else:
                if col not in ["created_at", "updated_at"]:
                    required_cols.append(col)

        label = key.replace("_", " ").title()

        trackers.append(
            {
                "value": key,
                "label": label,
                "required_columns": required_cols,
                "template_url": f"/api/v1/import/{key}/template",
            }
        )
    return trackers


@router.get("/{tracker_type}/template")
async def download_template(tracker_type: str):
    if tracker_type not in IMPORT_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tracker type '{tracker_type}' is not supported.",
        )

    config = IMPORT_REGISTRY[tracker_type]
    model_class = config["model"]
    fk_config = config.get("foreign_keys", {})

    model_columns = [
        prop.key
        for prop in model_class.__mapper__.column_attrs
        if not prop.columns[0].primary_key
    ]

    headers = []
    for col in model_columns:
        if col in fk_config:
            headers.append(fk_config[col]["csv_column"])
        else:
            if col not in ["created_at", "updated_at"]:
                headers.append(col)

    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(headers)

    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = (
        f"attachment; filename={tracker_type}_template.csv"
    )
    return response


@router.post("/{tracker_type}")
async def import_data(
    tracker_type: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    if tracker_type not in IMPORT_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tracker type '{tracker_type}' is not supported for generic import.",
        )

    config = IMPORT_REGISTRY[tracker_type]
    ModelClass = config["model"]
    fk_config = config.get("foreign_keys", {})
    date_fields = config.get("date_fields", [])

    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV or Excel files are allowed.",
        )

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file, dtype=str)
        else:
            df = pd.read_excel(file.file, dtype=str)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}",
        )

    # Clean data: Replace NaN with None
    df = df.where(pd.notnull(df), None)

    success_count = 0
    errors = []

    # Process rows
    for index, row in df.iterrows():
        try:
            row_dict = row.to_dict()
            model_kwargs: Dict[str, Any] = {}

            # 1. Resolve Foreign Keys dynamically
            for db_fk_col, lookup_info in fk_config.items():
                csv_col = lookup_info["csv_column"]
                lookup_model = lookup_info["lookup_model"]
                lookup_col = lookup_info["lookup_column"]

                csv_val = row_dict.get(csv_col)
                if not csv_val or pd.isna(csv_val):
                    raise ValueError(
                        f"Missing '{csv_col}' required for foreign key resolution."
                    )

                # Auto-pad employee codes if they are purely numeric
                if (
                    lookup_model.__name__ == "Employee"
                    and lookup_col == "employee_code"
                ):
                    if isinstance(csv_val, str) and csv_val.isdigit():
                        csv_val = csv_val.zfill(3)

                # Query the lookup model
                stmt = select(lookup_model).where(
                    getattr(lookup_model, lookup_col) == csv_val
                )
                result = await db.execute(stmt)
                lookup_obj = result.scalar_one_or_none()

                if not lookup_obj:
                    raise ValueError(
                        f"{lookup_model.__name__} with {lookup_col}='{csv_val}' not found."
                    )

                model_kwargs[db_fk_col] = lookup_obj.id

            # Remove FK csv columns from row_dict mapping so it doesn't cause errors later
            for fk_info in fk_config.values():
                row_dict.pop(fk_info["csv_column"], None)

            # 2. Map remaining columns (ignoring any that don't belong to the model)
            model_columns = {
                prop.key: prop.columns[0] for prop in ModelClass.__mapper__.column_attrs
            }
            for col_name, col_value in row_dict.items():
                if pd.isna(col_value):
                    col_value = None

                if col_name in model_columns:
                    col_def = model_columns[col_name]
                    # Handle date parsing
                    if col_name in date_fields and col_value is not None:
                        try:
                            model_kwargs[col_name] = pd.to_datetime(col_value).date()
                        except Exception:
                            raise ValueError(f"Invalid date format for '{col_name}'.")
                    elif col_value is not None:
                        # Auto-cast based on SQLAlchemy type
                        if isinstance(col_def.type, (Float, Numeric)):
                            try:
                                model_kwargs[col_name] = float(col_value)
                            except ValueError:
                                raise ValueError(f"'{col_name}' must be a number.")
                        elif isinstance(col_def.type, Integer):
                            try:
                                model_kwargs[col_name] = int(float(col_value))
                            except ValueError:
                                raise ValueError(f"'{col_name}' must be an integer.")
                        elif isinstance(col_def.type, Boolean):
                            if str(col_value).lower() in ["true", "1", "yes", "y"]:
                                model_kwargs[col_name] = True
                            elif str(col_value).lower() in ["false", "0", "no", "n"]:
                                model_kwargs[col_name] = False
                            else:
                                raise ValueError(
                                    f"'{col_name}' must be a boolean (True/False)."
                                )
                        elif (
                            col_name == "employee_code"
                            and isinstance(col_value, str)
                            and col_value.isdigit()
                        ):
                            model_kwargs[col_name] = col_value.zfill(3)
                        else:
                            model_kwargs[col_name] = col_value
                    else:
                        model_kwargs[col_name] = None

            # Validate using Pydantic schema to catch missing required fields before DB insert
            from modules.hr import schemas
            from pydantic import ValidationError

            schema_class = getattr(
                schemas,
                ModelClass.__name__ + "Create",
                getattr(schemas, ModelClass.__name__ + "Base", None),
            )
            if schema_class:
                try:
                    schema_class.model_validate(model_kwargs)
                except ValidationError as e:
                    error_msgs = [
                        f"{err['loc'][0]}: {err['msg']}" for err in e.errors()
                    ]
                    raise ValueError(f"Validation failed: {', '.join(error_msgs)}")

            # Custom check for employee_code which is technically Optional in Pydantic but required for business logic
            if ModelClass.__name__ == "Employee" and not model_kwargs.get(
                "employee_code"
            ):
                raise ValueError(
                    "Validation failed: employee_code is required (Check your CSV headers, it must be 'employee_code' not 'employee_id')."
                )

            # 3. Create Model Instance
            new_record = ModelClass(**model_kwargs)
            db.add(new_record)
            success_count += 1

        except Exception as e:
            errors.append({"row": index + 2, "error": str(e)})

    # 4. Commit successful records
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        import re

        error_str = str(e.orig) if hasattr(e, "orig") else str(e)
        match = re.search(r"DETAIL:\s*(.*)", error_str)
        clean_msg = (
            f"Duplicate Entry: {match.group(1)}"
            if match
            else "Duplicate data found. A record with this unique information already exists."
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=clean_msg)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database commit failed: {str(e)}",
        )

    return {
        "message": "Import process completed.",
        "success_count": success_count,
        "failed_count": len(errors),
        "errors": errors,
    }
