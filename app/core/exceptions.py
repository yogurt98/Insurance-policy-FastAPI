# app/core/exceptions.py
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextvars import ContextVar

# 从 correlation-id middleware 拿 request_id
from app.middleware.correlation_id import request_id_var

def add_exception_handlers(app: FastAPI):
    """
    统一注册 RFC 7807 格式的错误响应
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = request_id_var.get("no-request-id")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": f"https://httpstatuses.com/{exc.status_code}",
                "title": exc.detail or "HTTP Error",
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": str(request.url),
                "traceId": request_id
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = request_id_var.get("no-request-id")
        problem_details = {
            "type": "https://api.yourdomain.com/errors/validation-error",
            "title": "Validation Error",
            "status": 422,
            "detail": str(exc),
            "instance": request.url.path,
            "trace_id": request_id_var.get("no-request-id")
        }
        return JSONResponse(
            status_code=422,
            # 这一步是灵魂，把 Pydantic 模型、Decimal、datetime 等各种“高级”对象，
            # 全部转换成 json.dumps() 认识的“平民”对象
            content=jsonable_encoder(problem_details),

        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = request_id_var.get("no-request-id")
        return JSONResponse(
            status_code=500,
            content={
                "type": "https://tools.ietf.org/html/rfc7231#section-6.6.1",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred. Please contact support.",
                "instance": str(request.url),
                "traceId": request_id
            }
        )