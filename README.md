# Block42 Backend

FastAPI + PostgreSQL 關卡管理系統後端

## 架構設計

### 核心理念
- **單表 JSONB 設計** - 使用 PostgreSQL JSONB 儲存完整關卡配置
- **零抽象層** - 直接使用 SQLAlchemy，拒絕過度設計
- **實用主義** - 同步實作，夠用就好

### 目錄結構

```
block42_backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用入口
│   ├── config.py            # 環境變數管理
│   ├── database.py          # 資料庫連線
│   ├── models/
│   │   └── level.py         # SQLAlchemy 模型（單表 JSONB）
│   ├── schemas/
│   │   └── level.py         # Pydantic schemas
│   ├── api/                 # API 路由（待實作）
│   └── services/            # 業務邏輯（待實作）
├── alembic/                 # 資料庫遷移
├── .env                     # 環境變數配置
├── pyproject.toml           # uv 專案配置
└── test_db_operations.py    # 資料庫操作測試腳本
```

## 環境設定

### 必要環境變數（.env）

```env
DATABASE_URL=postgresql://user:password@localhost:5432/block42
DEBUG=true
LOG_LEVEL=info
```

**注意**: `DATABASE_URL` 支援 `postgresql://` 或 `postgresql+psycopg://` 格式

## 安裝與啟動

### 1. 安裝依賴

```bash
uv sync
```

### 2. 執行資料庫遷移

```bash
uv run alembic upgrade head
```

### 3. 啟動應用

```bash
uv run uvicorn app.main:app --reload
```

或使用根目錄的 `main.py`：

```bash
python main.py
```

應用將在 http://localhost:8000 啟動

### 4. 測試資料庫操作

```bash
uv run python test_db_operations.py
```

## API 端點

### 健康檢查

```bash
curl http://localhost:8000/
```

回應：
```json
{"status": "ok"}
```

## 資料庫設計

### `levels` 資料表

| 欄位 | 型別 | 說明 |
|-----|------|------|
| `id` | VARCHAR(50) | 關卡 ID（主鍵） |
| `title` | VARCHAR(200) | 關卡標題 |
| `data` | JSONB | 完整配置資料 |

### JSONB 結構

```json
{
  "config": {
    "f0": 10,
    "f1": 0,
    "f2": 0,
    "tools": {
      "paint_red": true,
      "paint_green": false,
      "paint_blue": false
    }
  },
  "map": {
    "start": {"x": 0, "y": 0, "dir": 1},
    "stars": [{"x": 5, "y": 5}],
    "tiles": [
      {"x": 0, "y": 0, "color": "R"},
      {"x": 1, "y": 0, "color": "G"}
    ]
  }
}
```

## 技術棧

- **Python**: 3.13
- **FastAPI**: 0.128.0
- **SQLAlchemy**: 2.0+ (使用新語法)
- **PostgreSQL**: psycopg3 驅動
- **Alembic**: 資料庫遷移
- **Pydantic**: 資料驗證

## 開發指令

### 建立新的資料庫遷移

```bash
uv run alembic revision --autogenerate -m "描述"
```

### 查看遷移歷史

```bash
uv run alembic history
```

### 回滾遷移

```bash
uv run alembic downgrade -1
```

### 檢查資料庫狀態

```bash
uv run alembic current
```

## 下一步

目前架構已完成基礎建設，後續可擴展：

1. **API 層** - 實作 RESTful CRUD 端點
   - `POST /levels` - 建立關卡
   - `GET /levels` - 列出所有關卡
   - `GET /levels/{id}` - 取得單一關卡
   - `PUT /levels/{id}` - 更新關卡
   - `DELETE /levels/{id}` - 刪除關卡

2. **驗證邏輯** - 關卡資料合法性檢查
3. **測試** - 單元測試與整合測試
4. **文件** - 自動生成 OpenAPI 文件

## 設計決策

| 決策點 | 選擇 | 理由 |
|--------|------|------|
| 資料結構 | 單表 + JSONB | 關卡是整體讀寫，無單獨查詢需求 |
| ORM | SQLAlchemy 2.0 | 業界標準，文件完整 |
| 同步/非同步 | 同步 | 夠用就好，避免過度設計 |
| 遷移工具 | Alembic | SQLAlchemy 官方工具 |
| 抽象層 | 無 | 直接用 Session，拒絕 Repository Pattern |

## 驗證清單

- [x] 依賴安裝成功
- [x] 資料庫連線正常
- [x] 遷移系統運作
- [x] CRUD 操作測試通過
- [x] FastAPI 應用可啟動
- [ ] API 路由實作（待完成）
