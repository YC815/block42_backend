"""清理資料庫並重置 alembic"""
from app.database import engine
from app.config import settings

def reset_database():
    """刪除所有表並重置 alembic_version"""
    with engine.connect() as conn:
        # 刪除 alembic_version 表
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))

        # 刪除所有業務表（如果存在）
        conn.execute(text("DROP TABLE IF EXISTS levels CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))

        # 刪除 enum 類型（如果存在）
        conn.execute(text("DROP TYPE IF EXISTS levelstatus CASCADE"))

        conn.commit()
        print("✅ 資料庫已清理完成")

if __name__ == "__main__":
    from sqlalchemy import text
    reset_database()
