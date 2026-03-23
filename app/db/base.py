# app/db/base.py
"""
导入所有模型，让 Alembic 和 create_all 可以自动识别所有表
避免循环导入问题
"""

from app.db.base_class import Base
# 导入所有模型，让 Alembic 和 create_all 能识别
from app.models.user import User
from app.models.policy import Policy
__all__ = ["Base", "User", "Policy"]