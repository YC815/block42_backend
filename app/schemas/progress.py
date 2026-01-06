"""Progress schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class LevelProgressUpdate(BaseModel):
    """Upsert payload for progress."""

    is_completed: bool = False
    best_steps: int | None = Field(default=None, ge=0)
    stars_collected: int | None = Field(default=None, ge=0)


class LevelProgressOut(BaseModel):
    """Progress response for a level."""

    level_id: str
    is_completed: bool
    best_steps: int | None = None
    stars_collected: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
