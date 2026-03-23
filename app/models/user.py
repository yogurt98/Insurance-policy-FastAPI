# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # admin 或 underwriter
    is_active = Column(Boolean, default=True)

    # 关系：一个 underwriter 可以管理多个 policy
    policies = relationship("Policy", back_populates="underwriter", cascade="all, delete-orphan")
