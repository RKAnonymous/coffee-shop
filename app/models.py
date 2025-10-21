import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum
from .db import Base

class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String, default="user")
    verification_code = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # is_deleted = Column(Boolean, default=False)
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # deleted_at = Column(DateTime(timezone=True))
