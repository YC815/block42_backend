#!/usr/bin/env python3
"""建立 admin 超級使用者"""
import sys
sys.path.insert(0, "/Users/yushunchen/.z/pr/block42/block42_backend")

from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

# 建立 admin 使用者
username = "admin"
password = "admin123"

db = SessionLocal()

# 檢查是否已存在
existing = db.query(User).filter(User.username == username).first()
if existing:
    print(f"⚠️  用戶 '{username}' 已存在")
    db.close()
    sys.exit(0)

# 建立新用戶
user = User(
    username=username,
    hashed_password=get_password_hash(password),
    is_superuser=True
)

db.add(user)
db.commit()
db.refresh(user)

print(f"✅ 超級使用者建立成功！")
print(f"   Username: {username}")
print(f"   Password: {password}")
print(f"   ID: {user.id}")

db.close()
