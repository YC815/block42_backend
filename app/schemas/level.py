"""Pydantic schemas for Level data"""
from pydantic import BaseModel, Field
from typing import List, Literal, Optional


# --- 基礎元件定義 ---
class Coordinate(BaseModel):
    x: int
    y: int


class Tile(Coordinate):
    # 使用 Literal 做列舉檢查，只允許 R, G, B
    color: Literal['R', 'G', 'B']


class StartPoint(Coordinate):
    # 0:上, 1:右, 2:下, 3:左
    dir: Literal[0, 1, 2, 3]


# --- 設定區塊 ---
class ToolConfig(BaseModel):
    paint_red: bool = True
    paint_green: bool = False
    paint_blue: bool = False


class LevelConfig(BaseModel):
    f0: int = 10
    f1: int = 0
    f2: int = 0
    tools: ToolConfig


# --- 地圖結構 ---
class MapData(BaseModel):
    start: StartPoint
    stars: List[Coordinate]
    tiles: List[Tile]


# --- 完整關卡資料 (Request/Response Body) ---
class LevelSchema(BaseModel):
    id: str
    title: str
    config: LevelConfig
    map: MapData

    class Config:
        json_schema_extra = {
            "example": {
                "id": "lvl_101",
                "title": "新手教學",
                "config": {
                    "f0": 5, "f1": 0, "f2": 0,
                    "tools": {"paint_red": True, "paint_green": False, "paint_blue": False}
                },
                "map": {
                    "start": {"x": 0, "y": 0, "dir": 1},
                    "stars": [{"x": 2, "y": 0}],
                    "tiles": [{"x": 0, "y": 0, "color": "R"}, {"x": 1, "y": 0, "color": "R"}]
                }
            }
        }
