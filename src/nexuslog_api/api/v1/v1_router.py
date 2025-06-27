from fastapi import APIRouter

from nexuslog_api.api.v1.endpoints import (
    alerts,
    dashboards,
    ingestion,
    login,
    projects,
    search,
    users,
)

api_router = APIRouter()

api_router.include_router(login.router, tags=["Login"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(ingestion.router, prefix="/ingest", tags=["Ingestion"])
api_router.include_router(
    dashboards.router, prefix="/dashboards", tags=["Dashboards"]
)
