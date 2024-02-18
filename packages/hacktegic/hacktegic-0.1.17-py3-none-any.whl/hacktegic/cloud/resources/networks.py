from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Networks(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = None
    address: str
    project_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None