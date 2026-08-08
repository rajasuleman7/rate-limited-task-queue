
from fastapi import FastAPI
from .routes.auth  import router as auth_router
from .routes.tasks import router as task_router
from .routes.admin import router as admin_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Rate-Limited Task Queue Service",
        description="FastAPI + Celery + Redis task queue with JWT auth and RBAC",
        version="1.0.0",
    )
    app.include_router(auth_router,  prefix="/auth",  tags=["auth"])
    app.include_router(task_router,  prefix="/tasks", tags=["tasks"])
    app.include_router(admin_router, prefix="/admin", tags=["admin"])

    @app.get("/health")
    def health():
        return {"status": "healthy", "service": "task-queue-api"}

    return app

app = create_app()
