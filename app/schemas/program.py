"""Program schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class LevelProgramUpdate(BaseModel):
    """Upsert payload for program commands."""

    commands_f0: list[str] = Field(default_factory=list)
    commands_f1: list[str] = Field(default_factory=list)
    commands_f2: list[str] = Field(default_factory=list)


class LevelProgramOut(BaseModel):
    """Program response for a level."""

    level_id: str
    commands_f0: list[str]
    commands_f1: list[str]
    commands_f2: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
