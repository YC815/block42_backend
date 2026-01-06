"""Level Pydantic Schemas - 重構版"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal
from datetime import datetime

# --- 地圖限制常數 ---
COORD_MIN = -512
COORD_MAX = 512
MAX_DIMENSION = 128

# --- 遊戲資料結構 (保持原樣) ---
class Coordinate(BaseModel):
    """座標"""
    x: int
    y: int

    @field_validator('x', 'y')
    @classmethod
    def validate_coordinates(cls, v: int) -> int:
        """驗證座標落在允許範圍內（允許編輯時使用負座標）"""
        if not (COORD_MIN <= v <= COORD_MAX):
            raise ValueError(f'座標必須在 {COORD_MIN}-{COORD_MAX} 範圍內，收到: {v}')
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


class MapBounds(BaseModel):
    """地圖邊界（包含 padding 後的渲染範圍）"""
    minX: int
    minY: int
    maxX: int
    maxY: int

    @property
    def width(self) -> int:
        return self.maxX - self.minX + 1

    @property
    def height(self) -> int:
        return self.maxY - self.minY + 1


class MapData(BaseModel):
    """地圖資料"""
    # gridSize 將於驗證後自動回填，保留與前端相容
    gridSize: int | None = Field(
        default=None,
        description="棋盤尺寸 (自動計算：內容最大邊 + padding*2)",
        ge=1,
        le=MAX_DIMENSION
    )
    padding: int = Field(1, ge=0, le=8, description="渲染預留空氣的格數")
    bounds: MapBounds | None = None
    start: StartPoint
    stars: list[Coordinate]
    tiles: list[Tile]

    @model_validator(mode="before")
    @classmethod
    def default_padding(cls, data: dict) -> dict:
        """舊資料若缺少 padding，預設為 0 以避免平移既有座標"""
        if isinstance(data, dict) and "padding" not in data:
            data = {**data, "padding": 0}
        return data

    @model_validator(mode="after")
    def validate_bounds(self) -> "MapData":
        """自動平移原點並計算邊界，保留 padding 以便動態渲染"""
        all_points = [(self.start.x, self.start.y)] + [
            (coord.x, coord.y) for coord in (self.stars + self.tiles)
        ]
        if not all_points:
            raise ValueError("地圖必須至少包含起點或一個地板")

        min_x = min(x for x, _ in all_points)
        min_y = min(y for _, y in all_points)
        max_x = max(x for x, _ in all_points)
        max_y = max(y for _, y in all_points)

        width_with_padding = (max_x - min_x + 1) + self.padding * 2
        height_with_padding = (max_y - min_y + 1) + self.padding * 2

        if width_with_padding > MAX_DIMENSION or height_with_padding > MAX_DIMENSION:
            raise ValueError(
                f"地圖尺寸過大，最多 {MAX_DIMENSION}x{MAX_DIMENSION} (含預留空氣)"
            )

        # 平移座標，確保最左/上邊界落在 padding 之後
        shift_x = self.padding - min_x
        shift_y = self.padding - min_y

        normalized_tiles = [
            Tile(x=tile.x + shift_x, y=tile.y + shift_y, color=tile.color)
            for tile in self.tiles
        ]
        normalized_stars = [
            Coordinate(x=star.x + shift_x, y=star.y + shift_y)
            for star in self.stars
        ]
        normalized_start = StartPoint(
            x=self.start.x + shift_x,
            y=self.start.y + shift_y,
            dir=self.start.dir
        )

        # 確保起點有地板
        has_start_tile = any(
            tile.x == normalized_start.x and tile.y == normalized_start.y
            for tile in normalized_tiles
        )
        if not has_start_tile:
            normalized_tiles.append(
                Tile(x=normalized_start.x, y=normalized_start.y, color="R")
            )

        self.tiles = normalized_tiles
        self.stars = normalized_stars
        self.start = normalized_start
        self.bounds = MapBounds(
            minX=0,
            minY=0,
            maxX=width_with_padding - 1,
            maxY=height_with_padding - 1,
        )
        self.gridSize = max(width_with_padding, height_with_padding)
        return self


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
