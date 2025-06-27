from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_alerts():
    # This is a placeholder for future implementation
    return [{"alert_name": "High CPU Usage"}]
