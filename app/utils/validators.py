# app/utils/validators.py
from datetime import date
from decimal import Decimal
import re
from typing import Dict, Any, Tuple


def validate_policy_data(policy_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    保险业务规则校验 + 反欺诈 + OSFI 合规
    返回: (是否通过, 错误信息, 处理后的数据)
    """
    errors = []
    processed_data = policy_data.copy()

    # 1. 日期逻辑校验
    if processed_data.get("start_date") and processed_data.get("end_date"):
        if processed_data["start_date"] > processed_data["end_date"]:
            errors.append("保单起始日期不能晚于结束日期")

    # 2. Premium 合理性校验（加拿大保险场景）
    premium = processed_data.get("premium")
    if isinstance(premium, (int, float, Decimal)):
        premium = Decimal(str(premium))
        if premium <= 0:
            errors.append("保费必须大于0")
        elif premium > Decimal("10000") and processed_data.get("product_type") == "Life":
            processed_data["fraud_check"] = "review"
            errors.append("高额寿险保单触发人工审核")

    # 3. 反欺诈规则（Risk Score）
    risk_score = processed_data.get("risk_score", 0.0)
    if risk_score > 85:
        processed_data["fraud_check"] = "flag"
        errors.append("风险分数过高，触发反欺诈标记")
    elif risk_score > 70:
        processed_data["fraud_check"] = "review"

    # 4. Policy Number 格式校验（模拟加拿大保单号规则）
    policy_number = processed_data.get("policy_number", "")
    if not re.match(r"^[A-Z]{1,4}\d{6,10}$", policy_number):
        processed_data["fraud_check"] = "review"
        errors.append("保单号格式不符合标准，建议人工复核")

    # 5. OSFI 合规字段自动生成
    if not processed_data.get("osfi_compliance_flag"):
        year = date.today().year
        processed_data["osfi_compliance_flag"] = f"OSFI-{year}-{policy_number[-4:]}"

    if errors:
        return False, "; ".join(errors), processed_data

    return True, "", processed_data