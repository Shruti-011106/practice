import logging
import os
from contextlib import asynccontextmanager


# 13/10/26
from modules.administration.router import router as administration_router
from modules.inventory.router import router as inventory_router

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from core.database import init_db
from seed_lookups import seed_data
from auth.router import router as auth_router
from auth.users import router as users_router
from auth.permissions import router as permissions_router
from modules.hr.router import router as hr_router
from modules.finance.router import router as finance_router
from modules.customer_success.router import router as cs_router
from modules.masters.router import router as masters_router
from modules.project.router import router as project_router
from modules.project.employee_router import router as employee_project_router
from modules.sales.router import router as sales_router
from modules.presales.router import router as presales_router
from modules.marketing.router import router as marketing_router
from modules.lnd.router import router as lnd_router
from modules.activities.router import router as activities_router
from modules.administration.router import router as administration_router
from app.api.routes.importer import router as importer_router
from app.api.routes.exporter import router as exporter_router
# from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.exporter import router as exporter_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_data()
    yield


app = FastAPI(
    title="RevGov Governance Tracker API",
    version="1.0.0",
    description="Complete REST API for the EGT RevGov portal.",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Trusted Host
allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts,
)

from fastapi.staticfiles import StaticFiles
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error. Please contact support."},
    )


PREFIX = "/api/v1"

# ── Auth & User Management ──────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix=PREFIX, tags=["User Management"])
app.include_router(
    permissions_router, prefix=f"{PREFIX}/permissions", tags=["Permissions"]
)

# ── Domain Modules ─────────────────────────────────────────────────────────────
app.include_router(hr_router, prefix=PREFIX)
app.include_router(finance_router, prefix=PREFIX)
app.include_router(cs_router, prefix=PREFIX)
app.include_router(masters_router, prefix=PREFIX)
app.include_router(activities_router)
app.include_router(project_router, prefix=PREFIX)
app.include_router(employee_project_router, prefix=PREFIX)
app.include_router(sales_router, prefix=PREFIX)
app.include_router(presales_router, prefix=PREFIX)
app.include_router(marketing_router, prefix=PREFIX)
app.include_router(lnd_router, prefix=PREFIX)
app.include_router(administration_router, prefix=PREFIX)

# ── Dashboards ─────────────────────────────────────────────────────────────
# app.include_router(dashboard_router, prefix=PREFIX)


# ── Generic Utilities ─────────────────────────────────────────────────────────────
app.include_router(importer_router, prefix=f"{PREFIX}/import", tags=["Bulk Import"])
app.include_router(exporter_router, prefix=f"{PREFIX}/export", tags=["Bulk Export"])



# 13/10/26
# ── domain modules ─────────────────────────────────────────────────────────────

app.include_router(administration_router, prefix=PREFIX)
app.include_router(inventory_router, prefix=PREFIX)