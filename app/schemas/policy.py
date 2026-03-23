# app/schemas/policy.py
# Pydantic 默认不支持 Decimal
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Literal, Optional
from decimal import Decimal


class PolicyBase(BaseModel):
    policy_number: str = Field(..., min_length=8, max_length=20, pattern=r"^[A-Z0-9\-]+$")
    customer_id: int = Field(..., gt=0)
    product_type: Literal["Auto", "Home", "Life", "Other"]
    premium: Decimal = Field(..., gt=Decimal("0.0"), decimal_places=2)
    start_date: date
    end_date: date
    status: Literal["active", "expired", "cancelled", "pending"] = "pending"
    risk_score: Optional[float]= Field(None, ge=0.0, le=100.0)
    osfi_compliance_flag: Optional[str] = Field(None, max_length=50)  # eg: OSFI-2025-001
    fraud_check: Optional[Literal["pass", "review", "flag"]] = None


class PolicyCreate(PolicyBase):
    pass


# PolicyUpdate 不能继承 PolicyBase，因为 Base 里的字段大多是必填的，而 Update 应该全是可选的
class PolicyUpdate(BaseModel):
    premium: Optional[Decimal] = Field(None, decimal_places=2, gt=Decimal("0.0"))
    end_date: Optional[date] = None
    status: Optional[Literal["active", "expired", "cancelled"]] = None
    risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    fraud_check: Optional[Literal["pass", "review", "flag"]] = None
    osfi_compliance_flag: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PolicyOut(PolicyBase):
    id: int
    underwriter_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

