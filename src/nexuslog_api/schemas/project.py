from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None

class Project(ProjectBase):
    id: int
    api_key: str
    created_at: datetime

    class Config:
        from_attributes = True
