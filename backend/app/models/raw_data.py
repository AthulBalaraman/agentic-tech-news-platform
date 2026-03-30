from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class RawData(BaseModel):
    source: str  # e.g., "github", "news"
    external_id: str  # URL or specific ID from source
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
