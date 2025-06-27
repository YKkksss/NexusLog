from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), index=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
