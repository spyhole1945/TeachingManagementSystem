"""
FastAPI Main Application
Teaching Management System API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tms.config import config
from tms.api.routes import (
    auth, courses, students, teachers, enrollments, 
    grades, assignments, materials, notifications, admin
)

# Create FastAPI application
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="A comprehensive teaching management system with 10 core modules",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(students.router)
app.include_router(teachers.router)
app.include_router(enrollments.router)
app.include_router(grades.router)
app.include_router(assignments.router)
app.include_router(materials.router)
app.include_router(notifications.router)
app.include_router(admin.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Teaching Management System API",
        "version": config.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"🚀 {config.APP_NAME} v{config.APP_VERSION} starting...")
    
    # Initialize database
    from tms.infra.database import init_db
    init_db()
    print("📦 Database initialized")
    
    print(f"📚 API documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("Shutting down Teaching Management System...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
