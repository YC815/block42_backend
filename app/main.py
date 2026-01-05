"""FastAPI 應用入口"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import engine
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用啟動/關閉時的生命週期管理"""
    # 啟動時：檢查資料庫連線
    try:
        with engine.connect() as conn:
            print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

    yield

    # 關閉時：清理資源
    engine.dispose()


app = FastAPI(
    title="Block42 Backend",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan
)


@app.get("/")
def health_check():
    """健康檢查端點"""
    return {"status": "ok"}
