from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_projects():
    # This is a placeholder for future implementation
    return [{"project_name": "Default Project"}]
