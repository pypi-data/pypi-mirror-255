from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Project(BaseModel):
    id: Optional[str] = None
    name: str
    owner_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
