#!/usr/bin/env python3
"""
Block42 Backend - Create Superuser Script

描述:
    安全且快速地將指定用戶提升為 superuser。
    自動讀取 .env 文件配置，並提供完整的錯誤處理。

依賴:
    pip install sqlalchemy psycopg2-binary python-dotenv

Usage:
    python scripts/create_superuser.py <username>
"""
import argparse
import logging
import os
import sys
from typing import Optional

# 設定日誌格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# 嘗試引入第三方庫，若失敗則提供友善提示
try:
    from dotenv import load_dotenv
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import SQLAlchemyError
except ImportError as e:
    logger.error(f"缺少必要套件: {e.name}")
    logger.error("請執行: pip install sqlalchemy psycopg2-binary python-dotenv")
    sys.exit(1)


def get_database_url() -> str:
    """獲取並驗證資料庫連線字串"""
    # 優先讀取 .env 文件
    load_dotenv()

    url = os.getenv("DATABASE_URL")
    if not url:
        # 這裡可以保留預設值，但在生產環境建議強制要求配置
        default_url = "postgresql://user:password@localhost:5432/block42"
        logger.warning(f"未檢測到 DATABASE_URL，使用預設開發配置: {default_url}")
        return default_url
    return url


def promote_user(username: str, db_url: str) -> bool:
    """
    執行提升權限的邏輯

    Returns:
        bool: 操作是否成功
    """
    try:
        engine = create_engine(db_url)

        # 使用 connect() 上下文管理器確保連線自動關閉
        with engine.connect() as conn:
            # 1. 查詢用戶
            stmt_check = text("SELECT id, is_superuser FROM users WHERE username = :username")
            result = conn.execute(stmt_check, {"username": username}).fetchone()

            if not result:
                logger.error(f"用戶 '{username}' 不存在，請先註冊。")
                return False

            user_id, is_superuser = result

            if is_superuser:
                logger.info(f"用戶 '{username}' (ID: {user_id}) 已經是 Superuser，無需變更。")
                return True

            # 2. 更新權限
            stmt_update = text("UPDATE users SET is_superuser = true WHERE username = :username")
            conn.execute(stmt_update, {"username": username})
            conn.commit()  # SQLAlchemy 2.0 風格需要顯式 commit

            logger.info(f"✅ 成功！用戶 '{username}' (ID: {user_id}) 已提升為 Superuser。")
            return True

    except SQLAlchemyError as e:
        logger.error(f"資料庫錯誤: {e}")
        return False
    except Exception as e:
        logger.error(f"未預期的錯誤: {e}")
        return False


def main() -> None:
    """CLI 入口點"""
    parser = argparse.ArgumentParser(description="將 Block42 用戶提升為管理員")
    parser.add_argument("username", help="目標用戶的 username")

    args = parser.parse_args()

    # 獲取配置
    db_url = get_database_url()

    # 執行邏輯
    success = promote_user(args.username, db_url)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
