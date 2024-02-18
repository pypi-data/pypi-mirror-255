from pydantic import BaseModel
from typing import Any

class LockObject(BaseModel):
    lock_id: str
    expires_at: int
    data: dict[str, Any]
