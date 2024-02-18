from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ScanProfile(BaseModel):
    id: Optional[str] = None
    title: str
    schedule: Optional[str] = None
    enabled: Optional[bool] = None
    nmap_options: Optional[str] = None
    last_run_at: Optional[datetime] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    project_id: Optional[str] = None
