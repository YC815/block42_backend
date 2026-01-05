#!/usr/bin/env python3
"""驗證密碼 hash 修復是否正確"""

import sys
sys.path.insert(0, "/Users/yushunchen/.z/pr/block42/block42_backend")

from app.core.security import get_password_hash, verify_password

# 測試案例
test_password = "test123!@#"

print("🔐 測試密碼驗證修復")
print("=" * 50)

# 1. 產生 hash
hashed = get_password_hash(test_password)
print(f"✅ 密碼雜湊成功: {hashed[:20]}...")

# 2. 驗證正確密碼
result = verify_password(test_password, hashed)
print(f"✅ 正確密碼驗證: {result}")

if not result:
    print("❌ FAIL: 正確密碼驗證失敗！")
    sys.exit(1)

# 3. 驗證錯誤密碼
wrong_result = verify_password("wrong_password", hashed)
print(f"✅ 錯誤密碼拒絕: {not wrong_result}")

if wrong_result:
    print("❌ FAIL: 錯誤密碼驗證通過！")
    sys.exit(1)

print("=" * 50)
print("✅ 所有測試通過！密碼驗證修復成功。")
