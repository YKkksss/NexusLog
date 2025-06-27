from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    """
    Base class for all SQLAlchemy models.
    It automatically sets the tablename and provides a default __repr__.
    """
    id: Any
    __name__: str

    # to generate tablename from classname
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"
