# app/api/endpoints/bulk.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import json
from typing import List
from decimal import Decimal

from app.api.deps import get_db, get_current_active_user
from app.core.limiter import limiter
from app.db.session import AsyncSessionLocal
from app.middleware.correlation_id import request_id_var
from app.models.user import User
from app.schemas.bulk import BulkUploadResponse
from app.schemas.policy import PolicyCreate
from app.services.policy import PolicyService
from loguru import logger

from app.utils.validators import validate_policy_data

router = APIRouter()

# app/api/endpoints/bulk.py

async def process_bulk_task(
        policies_data: List[dict],
        underwriter_id: int,
        request_id: str
):
    """
    后台任务：执行实际的批量创建逻辑
    """


    logger.info(f"Task Started | RID: {request_id} | Total: {len(policies_data)}")
    # 核心：手动开启一个新的、受控的 Session
    async with AsyncSessionLocal() as new_db:
        try:
            # 调用 Service 层的批量处理逻辑
            result = await PolicyService.bulk_create_policies(
                db=new_db,
                policies_in=policies_data,
                underwriter_id=underwriter_id
            )
            logger.success(
                f"Bulk task finished | RequestID: {request_id} | "
                f"Success: {result['success_count']}, Failed: {result['failed_count']}"
            )
        except Exception as e:
            logger.error(f"Background bulk task failed | RequestID: {request_id} | Error: {str(e)}")



@router.post("/bulk-upload", response_model=BulkUploadResponse)
@limiter.limit("20/hour")  # 每小时最多 20 次
async def bulk_upload_policies(
    request: Request,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_active_user)
):
    """
    批量上传保单（完全异步化）
    支持格式：CSV 或 JSON
    适合处理10万条级别数据
    """
    if not file.filename.endswith(('.csv', '.json')):
        raise HTTPException(
            status_code=400,
            detail="Only support .csv or .json file"
        )


    try:
        content = await file.read()
        policies_list = []
        if file.filename.endswith('.csv'):
            df = pd.read_csv(pd.io.common.BytesIO(content))
            policies_list = df.to_dict(orient='records')
        elif file.filename.endswith('.json'):
            policies_list = json.loads(content.decode('utf-8'))
            if not isinstance(policies_list, list):
                raise ValueError("JSON must be an array format")

    except Exception as e:
        logger.error(f"File parse error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"文件解析失败：{str(e)}"
        )

    # 数量校验
    if len(policies_list) > 200000:
        raise HTTPException(
            status_code=400,
            detail="单次最多上传20万数据"
        )

    # 尝试从中间件设置的 state 中获取，如果没有则生成一个占位符
    request_id = request_id_var.get("no-id")

    # 批量创建

    background_tasks.add_task(
        process_bulk_task,
        policies_list,
        current_user.id,
        request_id
    )

    return BulkUploadResponse(
        total=len(policies_list),
        success=0,
        failed=0,
        message="批量任务已接受，正在后台异步处理，请稍后查看结果。\n"
                "Bulk upload has been accepted and is being processed asynchronously. "
                "Please check back later for the results."
    )



