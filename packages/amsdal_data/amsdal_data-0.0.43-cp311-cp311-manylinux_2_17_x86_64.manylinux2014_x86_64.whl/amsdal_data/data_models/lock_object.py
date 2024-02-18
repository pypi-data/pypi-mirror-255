from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from pydantic import Field


class LockObject(BaseModel):
    lock_id: str = Field(default_factory=lambda: uuid4().hex)
    expires_at: int
    data: dict[str, Any]
