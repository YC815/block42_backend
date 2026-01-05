"""Level Pydantic Schemas - 重構版"""
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import datetime


# --- 遊戲資料結構 (保持原樣) ---
class Coordinate(BaseModel):
    """座標"""
    x: int
    y: int

    @field_validator('x', 'y')
    @classmethod
    def validate_coordinates(cls, v: int) -> int:
        """驗證座標在 0-100 範圍內"""
        if not (0 <= v <= 100):
            raise ValueError(f'座標必須在 0-100 範圍內，收到: {v}')
        return v


class Tile(Coordinate):
    """地板（帶顏色）"""
    color: Literal['R', 'G', 'B']


class StartPoint(Coordinate):
    """起點（帶方向）"""
    dir: Literal[0, 1, 2, 3]  # 0:上, 1:右, 2:下, 3:左


class ToolConfig(BaseModel):
    """工具開關設定"""
    paint_red: bool = True
    paint_green: bool = False
    paint_blue: bool = False


class LevelConfig(BaseModel):
    """關卡配置"""
    f0: int = 10
    f1: int = 0
    f2: int = 0
    tools: ToolConfig

    @field_validator('f0', 'f1', 'f2')
    @classmethod
    def validate_function_slots(cls, v: int) -> int:
        """驗證函數槽位在 0-20 範圍內"""
        if not (0 <= v <= 20):
            raise ValueError(f'函數槽位必須在 0-20 範圍內，收到: {v}')
        return v


class MapData(BaseModel):
    """地圖資料"""
    start: StartPoint
    stars: list[Coordinate]
    tiles: list[Tile]


# --- Solution Schema ---
class Solution(BaseModel):
    """解題資料（提交時驗證格式）"""
    commands_f0: list[str]
    commands_f1: list[str] = []
    commands_f2: list[str] = []
    steps_count: int = Field(..., ge=0, description="步數（用於難度評估）")


# --- Request Schemas ---
class LevelCreate(BaseModel):
    """建立關卡（不提供 id，後端生成）"""
    title: str = Field(..., min_length=1, max_length=200)
    config: LevelConfig
    map: MapData


class LevelUpdate(BaseModel):
    """更新關卡（強制回到 draft 狀態）"""
    title: str = Field(..., min_length=1, max_length=200)
    config: LevelConfig
    map: MapData


class LevelPublish(BaseModel):
    """發布關卡（提交 solution）"""
    solution: Solution
    as_official: bool = False  # 管理員專用
    official_order: int | None = None  # 管理員專用


class LevelApprove(BaseModel):
    """審核通過"""
    as_official: bool = False
    official_order: int | None = None


class LevelReject(BaseModel):
    """駁回理由"""
    reason: str = Field(..., min_length=1)


# --- Response Schemas ---
class LevelOut(BaseModel):
    """公開回傳（含遊戲資料）"""
    id: str
    title: str
    author_id: int
    status: str
    is_official: bool
    official_order: int
    config: LevelConfig
    map: MapData
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LevelDetail(LevelOut):
    """詳細資訊（Designer/Admin 可見 solution）"""
    solution: Solution | None = None


class LevelListItem(BaseModel):
    """列表項目（簡化資訊）"""
    id: str
    title: str
    author_id: int
    status: str
    is_official: bool
    created_at: datetime

    model_config = {"from_attributes": True}
