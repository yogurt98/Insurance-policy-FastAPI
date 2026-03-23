# app/schemas/bulk.py
from pydantic import BaseModel
from typing import Optional, List

class BulkUploadResponse(BaseModel):
    total: int
    success: int
    failed: int
    errors: Optional[List[str]] = None
    message: str


class BulkUploadResult(BaseModel):
    success_count: int
    failed_count: int
    errors: List[str]