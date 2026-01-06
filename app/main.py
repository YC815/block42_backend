"""FastAPI 應用入口"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine
from app.config import settings

# 導入路由
from app.api.v1 import auth, levels, designer, admin


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

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(levels.router, prefix="/api/v1")
app.include_router(designer.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
def health_check():
    """健康檢查端點"""
    return {"status": "ok"}
