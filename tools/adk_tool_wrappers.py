from typing import Any, Dict
from pydantic import BaseModel

class ToolResult(BaseModel):
    ok: bool
    data: Any = None
    error: str | None = None
    meta: Dict[str, Any] = {}

def success(data: Any = None, meta: dict | None = None) -> dict:
    return ToolResult(ok=True, data=data, meta=meta or {}).dict()

def failure(error: str, meta: dict | None = None) -> dict:
    return ToolResult(ok=False, error=error, meta=meta or {}).dict()
