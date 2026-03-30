from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class Trend(BaseModel):
    trend_name: str
    description: str
    related_insights: List[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
