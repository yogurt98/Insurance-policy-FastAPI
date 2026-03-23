# app/services/policy.py
import sys
from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.middleware.correlation_id import request_id_var
from app.models.policy import Policy
from app.schemas.policy import PolicyCreate, PolicyUpdate
from app.utils.validators import validate_policy_data
from loguru import logger
from app.tasks import send_policy_created_notification


class PolicyService:
    @staticmethod
    async def create_policy(db: AsyncSession, policy_in: PolicyCreate, underwriter_id: int):
        try:
            db_policy = Policy(**policy_in.model_dump(), underwriter_id=underwriter_id)
            db.add(db_policy)
            await db.commit()
            await db.refresh(db_policy)
            return db_policy
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Policy number already exists"
            )



    @staticmethod
    async def get_policies(db: AsyncSession, skip: int = 0, limit: int = 100):
        # 建议明确排序，否则分页在某些数据库（如 PostgreSQL）下可能顺序错乱

        stmt = select(Policy).order_by(Policy.id.desc()).offset(skip).limit(limit)
        result = await db.execute(stmt)
        # 不能像 Django 那样直接调用 .all()，异步 Session 不支持
        policies = result.scalars().all()
        return policies


    @staticmethod
    async def get_policy(db: AsyncSession, policy_id: int):
        result = await db.execute(select(Policy).where(Policy.id == policy_id))
        policy = result.scalar_one_or_none()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        return policy


    @staticmethod
    async def update_policy(db: AsyncSession, policy_id: int, policy_in: PolicyUpdate):
        result = await db.execute(
            update(Policy)
            .where(Policy.id == policy_id)
            .values(**policy_in.model_dump(exclude_unset=True))
            .returning(Policy)  # 不用再次发送 SELECT 命令查询刚才改了什么
        )
        updated = result.scalar_one_or_none()
        if not updated:
            raise HTTPException(status_code=404, detail="Policy not found")
        await db.commit()
        await db.refresh(updated)  # refresh 能确保你的 Python 对象与数据库里的最新状态完全同步
        return updated

    # 一般来说不用delete
    @staticmethod
    async def delete_policy(db: AsyncSession, policy_id: int):
        result = await (db.execute(delete(Policy))
                        .where(Policy.id == policy_id)
                        .returning(Policy))
        deleted = result.scalar_one_or_none()
        if not deleted:
            raise HTTPException(status_code=404, detail="Policy not found")
        await db.commit()
        return deleted


    @staticmethod
    async def bulk_create_policies(
        db: AsyncSession,
        policies_in: List[dict],
        underwriter_id: int
    ) -> dict:
        """
        批量创建保单（适合10万条级别）
        返回成功数量、失败数量和错误信息
        """
        success = 0
        failed = 0
        errors = []

        # 获取当前的日志的request的id
        request_id = request_id_var.get("no-request-id")

        for i, policy_data in enumerate(policies_in):
            try:
                # 简单数据清洗
                if 'premium' in policy_data and isinstance(policy_data['premium'], (int, float)):
                    policy_data['premium'] = Decimal(str(policy_data['premium']))
                if 'start_date' in policy_data and isinstance(policy_data['start_date'], str):
                    policy_data['start_date'] = datetime.strptime(policy_data['start_date'], "%Y-%m-%d").date()
                if 'end_date' in policy_data and isinstance(policy_data['end_date'], str):
                    policy_data['end_date'] = datetime.strptime(policy_data['end_date'], "%Y-%m-%d").date()

                is_valid, error_msg, processed_data = validate_policy_data(policy_data)

                if not is_valid:
                    raise ValueError(f"校验未通过: {error_msg}")

                db_policy = Policy(**policy_data, underwriter_id=underwriter_id)
                db.add(db_policy)

                # 关键点：使用 flush() 将数据发送到数据库检查约束（如唯一索引）
                # 如果 policy_number 重复，这里会立即抛出异常并进入 except
                await db.flush()

                # 每1000条commit一次，防止爆内存
                if(i+1) % 1000 == 0:
                    await db.commit()
                    logger.info(f"Bulk Progress: {i + 1} rows committed | RID: {request_id}")

                success += 1
            except Exception as e:
                failed += 1
                error_detail = f"第 {i+1} 条失败：{str(e)}"
                errors.append(error_detail)

                # 如果单行出错，需要回滚当前 session 中的待处理操作，防止影响下一条数据
                await db.rollback()
                logger.warning(f"Bulk row failed | {error_detail} | RID: {request_id}")
                continue

        # 提交剩余数据
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            errors.append(f"Final commit failed: {str(e)}")
            logger.error(f"Bulk final commit failed | RID: {request_id}")
        return {
            "success_count": success,
            "failed_count": failed,
            "errors": errors[:50]  # 只返回前50条错误，避免响应过大
        }
    @staticmethod
    async def create_policy(db: AsyncSession, policy_in: PolicyCreate, underwriter_id: int):
        try:
            # 转换为 dict 并进行业务校验
            policy_data = policy_in.model_dump()
            is_valid, error_msg, processed_data = validate_policy_data(policy_data)

            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"保单校验失败: {error_msg}"
                )

            db_policy = Policy(**processed_data, underwriter_id=underwriter_id)
            db.add(db_policy)
            await db.commit()
            await db.refresh(db_policy)
            send_policy_created_notification.delay(db_policy.id, request_id_var.get("no-request-id"))
            return db_policy

        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"创建保单失败: {str(e)}"
            )

