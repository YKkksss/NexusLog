import sys
import os
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text
import redis.asyncio as redis

# 将项目根目录添加到 sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from nexuslog_api.core.config import settings
from nexuslog_api.api.v1.v1_router import api_router as api_v1_router
from nexuslog_api.core.db import mysql_async_engine, redis_pool, close_db_connections
from nexuslog_api.models import Base # Import the Base for metadata

async def create_db_and_tables():
    async with mysql_async_engine.begin() as conn:
        # This will create all tables defined by models that inherit from Base
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created (if they didn't exist).")

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    # 应用启动时执行
    print("Application startup: Initializing...")
    
    # 1. Initialize Database Tables
    await create_db_and_tables()

    # 2. Test Connections
    try:
        async with mysql_async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("MySQL connection verified.")
    except Exception as e:
        print(f"MySQL connection test failed: {e}")

    try:
        r = redis.Redis(connection_pool=redis_pool)
        await r.ping()
        print("Redis connection verified.")
    except Exception as e:
        print(f"Redis connection test failed: {e}")

    print("Application startup complete.")
    yield
    # 应用关闭时执行
    print("Application shutdown: Closing connections...")
    await close_db_connections()
    print("Connections closed.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# 包含 v1 API 路由
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
async def read_root():
    """
    根路径，返回欢迎信息。
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_RELOAD,
    )