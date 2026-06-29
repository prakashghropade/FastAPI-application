from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    SQLAlchemy Declarative Base class.
    All models inherit from this class to participate in schema definition and migration.
    """
    pass
