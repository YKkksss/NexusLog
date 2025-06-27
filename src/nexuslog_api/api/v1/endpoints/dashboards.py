from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_dashboards():
    # This is a placeholder for future implementation
    return [{"dashboard_name": "Main Dashboard"}]
