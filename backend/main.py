from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api import auth, expenses, dashboard, categories, accounts, incomes, savings, chat, admin
from app.models import user, expense, account, category, income, savings as savings_models, audit  # Import all models for SQLAlchemy
import json
import time
import logging

# Configure logging for performance monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Financial Tracker API - Track your expenses efficiently"
)

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"\n=== VALIDATION ERROR ===")
    print(f"URL: {request.url}")
    print(f"Method: {request.method}")
    try:
        body = await request.body()
        print(f"Request body: {body.decode('utf-8')}")
    except:
        print("Could not read request body")
    print(f"Validation errors: {exc.errors()}")
    print(f"======================\n")

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )

# Add timing middleware for performance monitoring
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    # Calculate processing time
    process_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    # Add timing header to response
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

    return response


# Activity logging: one row per authenticated API request (admin audit / "where they went").
# user_id is set on request.state by get_current_user during the request; we read it after.
# Best-effort: any failure here must never break the actual request.
_ACTIVITY_SKIP_PREFIXES = ("/api/admin", "/api/auth/login", "/api/auth/register")


@app.middleware("http")
async def activity_logging(request: Request, call_next):
    response = await call_next(request)
    try:
        path = request.url.path
        user_id = getattr(request.state, "user_id", None)
        if (
            user_id is not None
            and request.method != "OPTIONS"
            and path.startswith("/api/")
            and not path.startswith(_ACTIVITY_SKIP_PREFIXES)
        ):
            from app.core.database import SessionLocal
            from app.models.audit import ActivityEvent

            xff = request.headers.get("x-forwarded-for")
            ip = xff.split(",")[0].strip() if xff else (request.client.host if request.client else None)

            db = SessionLocal()
            try:
                db.add(ActivityEvent(
                    user_id=user_id,
                    method=request.method,
                    path=path[:255],
                    status_code=response.status_code,
                    ip_address=(ip or "")[:64] or None,
                ))
                db.commit()
            finally:
                db.close()
    except Exception as e:
        logger.warning(f"activity logging failed: {e}")
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(categories.router)
app.include_router(accounts.router)
app.include_router(incomes.router)
app.include_router(savings.router, prefix="/api")
app.include_router(chat.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Financial Tracker API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/debug/config")
async def debug_config():
    """Debug endpoint to check configuration"""
    return {
        "cors_origins": settings.cors_origins,
        "allowed_origins_raw": settings.ALLOWED_ORIGINS,
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

