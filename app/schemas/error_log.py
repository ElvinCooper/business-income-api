from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ErrorLogCreate(BaseModel):
    endpoint: str
    method: str
    status_code: int
    user_id: Optional[int] = None
    error_message: str
    traceback: str
    request_headers: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class ErrorLogResponse(BaseModel):
    id: int
    timestamp: datetime
    endpoint: str
    method: str
    status_code: int
    user_id: Optional[int]
    error_message: str
    traceback: str
    request_headers: Optional[dict[str, Any]]
