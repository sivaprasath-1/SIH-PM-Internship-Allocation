import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app.routers import auth, students, companies, internships, admin, ai_matching, notifications

# Create tables
Base.metadata.create_all(bind=engine)

# Create upload directories
os.makedirs(os.path.join(settings.UPLOAD_DIR, "resumes"), exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-based Smart Allocation Engine for PM Internship Scheme. "
                "Intelligently matches students with internships using NLP, "
                "semantic similarity, and constraint optimization.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(companies.router)
app.include_router(internships.router)
app.include_router(admin.router)
app.include_router(ai_matching.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
    )
