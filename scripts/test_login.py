#!/usr/bin/env python3
"""測試登入功能"""
import sys
sys.path.insert(0, "/Users/yushunchen/.z/pr/block42/block42_backend")

from app.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password

username = "admin"
password = "admin123"

db = SessionLocal()

# 模擬登入流程
user = db.query(User).filter(User.username == username).first()

if not user:
    print(f"❌ 用戶 '{username}' 不存在")
    sys.exit(1)

print(f"🔍 用戶資訊:")
print(f"   ID: {user.id}")
print(f"   Username: {user.username}")
print(f"   Is Superuser: {user.is_superuser}")
print(f"   Hash (前20字元): {user.hashed_password[:20]}...")

# 測試密碼驗證
result = verify_password(password, user.hashed_password)

if result:
    print(f"\n✅ 登入成功！密碼驗證通過。")
else:
    print(f"\n❌ 登入失敗！密碼驗證失敗。")
    sys.exit(1)

db.close()
