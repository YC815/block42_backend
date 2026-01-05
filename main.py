"""FastAPI 應用入口 - 移動到 app/main.py

此檔案保留作為向後相容，實際應用在 app/main.py
"""
from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
