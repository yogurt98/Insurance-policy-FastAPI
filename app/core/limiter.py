# app/core/limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# 全局限流器（默认按 IP 限流）
limiter = Limiter(key_func=get_remote_address)


def add_rate_limit(app: FastAPI):
    """注册限流器 + 异常处理器"""
    app.state.limiter = limiter

    # 统一处理限流超限异常（返回 RFC 7807 格式，与之前统一错误响应风格一致）
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={
                "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
                "title": "Too Many Requests",
                "status": 429,
                "detail": str(exc),
                "instance": str(request.url),
                "traceId": request.headers.get("X-Request-ID", "no-trace")
            }
        )
