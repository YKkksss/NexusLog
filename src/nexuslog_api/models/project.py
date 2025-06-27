from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(String(255))
    api_key = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
