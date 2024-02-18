from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class PortScans(BaseModel):
    id: Optional[str] = None
    scan_profile_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    status : Optional[str] = None