from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import date
# Pydantic 默认不支持 Decimal，数据库也不支持


class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(20), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, nullable=False)
    product_type = Column(String(20), nullable=False)  # Auto/Home/Life/Other
    # asdecimal=True 确保 SQLAlchemy 返回的是 Python 的 Decimal 对象而非 float
    premium = Column(Numeric(scale=2, asdecimal=True), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default="pending")  # active/expired/cancelled/pending
    risk_score = Column(Float, default=0.0)  # 风险分数
    osfi_compliance_flag = Column(String(50), nullable=True)  # OSFI合规字段，如报告ID
    fraud_check = Column(String(20), nullable=True)  # 反欺诈结果

    # 关系：一个用户可以管理多个保单
    underwriter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    underwriter = relationship("User", back_populates="policies")


# 在 User 表里，你其实看不见任何关于保单的字段。
# User.policies 是 SQLAlchemy 背后偷偷执行了一句
# SELECT * FROM policies WHERE underwriter_id = ... 帮你拿到的
# User.policies = relationship("Policy", back_populates="underwriter")
