from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class Insight(BaseModel):
    title: str
    source: str
    external_id: str
    what_is_it: str
    why_it_matters: str
    technical_implementation: str
    tags: List[str] = Field(default_factory=list)
    status: str = "pending"  # "pending", "approved", "rejected"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
