# app/api/endpoints/policies.py
import json
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, status, Query, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_db, require_role
from app.models.user import User
from app.schemas.policy import PolicyCreate, PolicyOut, PolicyUpdate
from app.api.deps import get_current_active_user


# app/api/endpoints/policies.py
import importlib
import app.services.policy as p_mod

# 强制 Python 重新从磁盘读取该文件并更新内存对象
importlib.reload(p_mod)
from app.services.policy import PolicyService # 重新导入、
from loguru import logger
from app.middleware.correlation_id import request_id_var

router = APIRouter()


async def clear_policy_cache(request: Request):
    """手动清除所有保单相关的缓存"""
    count = 0
    redis = request.app.state.redis
    # 找到所有匹配前缀的 key 并删除
    async for key in redis.scan_iter("policy:list*"):
        await redis.delete(key)
        count += 1
    if count > 0:
        logger.info(f"CACHE_SAFE_PURGE | Deleted {count} keys")


@router.post("/", response_model=PolicyOut, status_code=status.HTTP_201_CREATED)
async def create_policy(
        request: Request,
        policy_in: PolicyCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # 直接在入口绑定 ID
    rid = request_id_var.get()
    log = logger.bind(request_id=rid, user=current_user.username)
    input_data = policy_in.model_dump()

    log.info(f"REQ_IN | Policy Number: {policy_in.policy_number} | Action: Create\nFull Payload: {input_data}")

    try:
        # 这里可以加入更多业务逻辑，比如记录是谁创建的
        new_policy = await PolicyService.create_policy(
            db=db,
            policy_in=policy_in,
            underwriter_id=current_user.id
        )
        # 成功日志
        log.info(f"REQ_SUCCESS | Created ID: {new_policy.id}\nFull Payload: {input_data}")
        await clear_policy_cache(request)
        # 注意：Redis delete 不支持直接用通配符，需要配合 keys() 或使用特定的逻辑。

        return new_policy
    except HTTPException as http_exc:
        # 如果是 HTTPException，直接原样抛出，不要拦截
        log.error(f"REQ_REJECTED | Detail: {http_exc.detail}\nFull Payload: {input_data}")
        raise http_exc
    except Exception as e:
        # 可以在这里统一捕获并记录日志（生产中建议加 logging）
        # 只有真正的程序崩溃（如数据库断开、变量未定义）才进这里报 500
        import traceback
        print("CRITICAL ERROR IN CREATE_POLICY:")
        traceback.print_exc()  # 这会强制把错误堆栈打印到标准输出
        log.exception(f"REQ_CRASHED | Critical Error: {str(e)}\nFull Payload: {input_data}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建保单失败: {str(e)}"
        )

@router.get("/", response_model=List[PolicyOut])
# @cache(expire=300, namespace="policies")  # 缓存 5 分钟，命名空间为 policies，如果使用decorator
async def list_policies(
        request: Request,
        db: AsyncSession = Depends(get_db),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        current_user: User = Depends(get_current_active_user)  # 登录后才能查看
):

    # 直接在入口绑定 ID
    rid = request_id_var.get("no-id")
    log = logger.bind(request_id=rid, user=current_user.username)

    # 1. 构造唯一的 Cache Key
    # 建议包含用户ID（如果数据是私有的）和分页参数
    cache_key = f"policy:list:u{current_user.id}:s{skip}:l{limit}"

    # 获取 redis 实例 (你在 init_cache 中存入的)
    redis = request.app.state.redis

    # 2. 尝试从 Redis 获取数据
    cached_data = await redis.get(cache_key)
    if cached_data:
        log.info(f"CACHE_HIT | Key: {cache_key}")
        # 注意：Redis 存的是字符串，需要解析回 JSON
        return json.loads(cached_data)

    # 3. 缓存未命中，查询数据库
    log.info(f"REQ_IN | Action: List Review | Skip: {skip} | Limit: {limit}")

    """获取保单列表 - 当前登录用户可见"""
    try:
        # if current_user.role != "admin":  如果想要检验用户身份的话
        policies = await PolicyService.get_policies(db, skip, limit)

        # 4. 序列化并存入 Redis (设置 60 秒过期)
        # 使用 jsonable_encoder 把 SQLAlchemy 对象转为可序列化的 dict
        serialized_data = jsonable_encoder(policies)
        await redis.setex(
            cache_key,
            120,  # 120秒过期
            json.dumps(serialized_data)
        )
        # 成功日志
        log.info(f"REQ_SUCCESS | Found: {len(policies)} items | Skip: {skip} | Limit: {limit}")
        return policies
    except HTTPException as http_exc:
        log.error(f"REQ_REJECTED | Detail: {http_exc.detail}")
        raise
    except Exception as e:
        log.exception(f"REQ_CRASHED | Unexpected error during policy listing")  # 生产环境不建议把具体的代码错误抛给前端
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询保单列表失败: {str(e)}"
        )


@router.get("/{policy_id}", response_model=PolicyOut)
async def get_policy(
        request: Request,
        policy_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # 直接在入口绑定 ID
    rid = request_id_var.get()
    log = logger.bind(request_id=rid, user=current_user.username)
    # 1. 构造详情缓存 Key
    detail_cache_key = f"policy:detail:{policy_id}"
    redis = request.app.state.redis

    # 2. 尝试获取缓存
    cached_policy = await redis.get(detail_cache_key)
    if cached_policy:
        log.info(f"CACHE_HIT | Key: {detail_cache_key}")
        return json.loads(cached_policy)

    log.info(f"REQ_IN | Action: GetDetail")

    """根据ID获取单个保单"""
    try:
        # 3. 缓存未命中，查数据库
        policy = await PolicyService.get_policy(db, policy_id)
        # if not current_user.is_superuser and policy.underwriter_id != current_user.id:
        #     log.warning(f"REQ_DENIED | User tried to access unauthorized policy")
        #     raise HTTPException(status_code=403, detail="无权访问该保单")
        # 4. 存入缓存 (详情建议设置稍长一点，比如 5 分钟/300秒)
        serialized_policy = jsonable_encoder(policy)
        await redis.setex(detail_cache_key, 300, json.dumps(serialized_policy))
        log.info(f"REQ_SUCCESS | Found: {policy.policy_number}")
        # 可选：未来可以加权限检查，比如只能看自己处理的保单
        return policy
    except HTTPException:
        raise  # 让 Service 抛出的 404 继续往上抛
    except Exception as e:
        log.exception("REQ_CRASHED | Unexpected system error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取保单失败: {str(e)}"
        )


@router.put("/{policy_id}", response_model=PolicyOut)
async def update_policy(
        request: Request,
        policy_id: int,
        policy_in: PolicyUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    rid = request_id_var.get()
    log = logger.bind(request_id=rid, user=current_user.username, policy_id=policy_id)
    """更新保单信息"""
    # 打印更新量，model_dump(exclude_unset=True) 只打印用户实际传了的字段
    update_data = policy_in.model_dump(exclude_unset=True)
    log.info(f"REQ_IN | Action: Update | Changes: {update_data}")
    try:
        updated_policy = await PolicyService.update_policy(db, policy_id, policy_in)
        log.info(f"REQ_SUCCESS | Status: {updated_policy.status}")
        await clear_policy_cache(request)
        redis = request.app.state.redis
        await redis.delete(f"policy:detail:{updated_policy.id}")  # 清理该 ID 的详情
        return updated_policy
    except HTTPException:
        raise
    except Exception as e:
        log.exception("REQ_CRASHED | Update failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新保单失败: {str(e)}"
        )


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
        request: Request,
        policy_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_role("admin"))
):
    rid = request_id_var.get()
    # 注意：这里使用 WARNING 级别，因为删除是不可逆的高危行为
    log = logger.bind(request_id=rid, user=current_user.username, policy_id=policy_id)
    log.warning(f"REQ_IN | Action: DELETE_START | Target: {policy_id}")
    """删除保单（仅 admin 可删，一般也不会用）"""
    try:
        await PolicyService.delete_policy(db, policy_id)
        await clear_policy_cache(request)
        redis = request.app.state.redis
        await redis.delete(f"policy:detail:{policy_id}")  # 清理该 ID 的详情
        log.warning(f"REQ_SUCCESS | Action: DELETE_COMPLETE")
        # 无需返回内容，204 状态码即可
    except HTTPException:
        raise
    except Exception as e:
        log.exception("REQ_CRASHED | Delete failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除保单失败: {str(e)}"
        )

