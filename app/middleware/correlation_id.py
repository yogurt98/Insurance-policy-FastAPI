# app/middleware/correlation_id.py
import uuid
import time
from contextvars import ContextVar
from typing import Callable

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp, Scope, Receive, Send


# 使用 ContextVar 存储当前请求的 request_id（线程安全）
request_id_var = ContextVar("request_id", default='no-request-id')


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 从请求头获取 X-Request-ID，如果没有则生成一个 UUID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # 设置到 ContextVar 中，全局可访问
        token = request_id_var.set(request_id)

        try:
            # 使用 logger.contextualize 注入 request_id 到所有日志
            with logger.contextualize(request_id=request_id):
                # 记录请求开始（可选）
                logger.info(
                    "Request started | method={method} path={path} client={client}",
                    method=request.method,
                    path=request.url.path,
                    client=request.client.host if request.client else "unknown"
                )

                # 继续处理请求
                response = await call_next(request)

                # 记录请求结束（可选）
                logger.info(
                    "Request completed | status={status} duration={duration}ms",
                    status=response.status_code,
                    duration=response.headers.get("X-Process-Time", "unknown")
                )

                # 把 request_id 写回响应头
                response.headers["X-Request-ID"] = request_id
                return response

        finally:
            # 清理 ContextVar
            request_id_var.reset(token)




