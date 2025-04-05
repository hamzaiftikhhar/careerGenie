from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.endpoints import auth, users, scholarships, counseling
from app.core.config import settings

app = FastAPI(
    title="Career Counseling & Scholarship Platform API",
    description="API for managing career counseling and scholarship data",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"]
)
app.include_router(
    users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"]
)
app.include_router(
    scholarships.router, prefix=f"{settings.API_V1_STR}/scholarships", tags=["scholarships"]
)
app.include_router(
    counseling.router, prefix=f"{settings.API_V1_STR}/counseling", tags=["counseling"]
)


@app.get("/", include_in_schema=False)
def root():
    """Redirect to docs"""
    return RedirectResponse(url="/docs")