#!/usr/bin/env python3
"""匯入官方關卡（scripts/official_levels.json）

Usage:
    python scripts/seed_official_levels.py <author_username>
    python scripts/seed_official_levels.py --dry-run <output.json>

- 地圖與設定經過 app.schemas 的 MapData / LevelConfig 驗證（與 API 建立關卡相同的正規化）
- 以標題判斷是否已存在，已存在的官方關卡會略過，可重複執行
- official_order 依 JSON 順序接在現有最大序號之後
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.level import LevelConfig, MapData, Solution  # noqa: E402

LEVELS_FILE = Path(__file__).resolve().parent / "official_levels.json"


def load_levels() -> list[dict]:
    levels = []
    for raw in json.loads(LEVELS_FILE.read_text(encoding="utf-8")):
        levels.append({
            "title": raw["title"],
            "map_data": MapData(**raw["map"]).model_dump(),
            "config": LevelConfig(**raw["config"]).model_dump(),
            "solution": Solution(**raw["solution"]).model_dump(),
        })
    return levels


def seed(username: str) -> None:
    from nanoid import generate
    from sqlalchemy import func

    from app.database import SessionLocal
    from app.models.level import Level, LevelStatus
    from app.models.user import User

    levels = load_levels()
    db = SessionLocal()
    try:
        author = db.query(User).filter(User.username == username).first()
        if not author:
            sys.exit(f"用戶 '{username}' 不存在")

        existing = {
            title for (title,) in db.query(Level.title).filter(Level.is_official.is_(True))
        }
        next_order = (db.query(func.max(Level.official_order)).scalar() or 0) + 1

        created = 0
        for item in levels:
            if item["title"] in existing:
                print(f"略過（已存在）：{item['title']}")
                continue
            db.add(Level(
                id=generate(size=12),
                author_id=author.id,
                title=item["title"],
                status=LevelStatus.PUBLISHED,
                is_official=True,
                official_order=next_order,
                map_data=item["map_data"],
                config=item["config"],
                solution=item["solution"],
            ))
            print(f"新增 #{next_order}：{item['title']}")
            next_order += 1
            created += 1

        db.commit()
        print(f"完成，新增 {created} 關")
    finally:
        db.close()


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--dry-run":
        Path(sys.argv[2]).write_text(
            json.dumps(load_levels(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    seed(sys.argv[1])


if __name__ == "__main__":
    main()
