"""Admin schemas."""
from pydantic import BaseModel, Field


class LevelTransferItem(BaseModel):
    """Transfer a level to another user."""

    level_id: str = Field(..., min_length=1)
    new_author_id: int


class LevelTransferRequest(BaseModel):
    """Batch transfer payload."""

    transfers: list[LevelTransferItem]


class LevelTransferResult(BaseModel):
    """Batch transfer result."""

    transferred: int
