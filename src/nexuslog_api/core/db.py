import os
from typing import AsyncGenerator

# SQLAlchemy 异步支持
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base # declarative_base 保持不变
from sqlalchemy import text # 导入 text 用于执行原生 SQL

import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool
import asyncio # 导入 asyncio 用于运行异步测试代码

# --- 环境变量配置 ---
# 确保使用支持异步的数据库驱动连接字符串
# 例如:
# MYSQL_ASYNC_DATABASE_URL="mysql+aiomysql://user:password@mysql_host:3306/mydatabase"
# POSTGRES_ASYNC_DATABASE_URL="postgresql+asyncpg://user:password@postgres_host:5432/mydatabase"
# REDIS_URL="redis://redis_host:6379/0"

MYSQL_ASYNC_DATABASE_URL = os.getenv("MYSQL_ASYNC_DATABASE_URL")
POSTGRES_ASYNC_DATABASE_URL = os.getenv("POSTGRES_ASYNC_DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# --- SQLAlchemy (MySQL) 异步配置 ---
mysql_async_engine = None
MySQLAsyncSessionLocal = None

async def test_mysql_connection():
    if not mysql_async_engine:
        print("MySQL engine not initialized, skipping connection test.")
        return False
    try:
        async with mysql_async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            if result.scalar_one() == 1:
                print("MySQL connection test successful (SELECT 1).")
                return True
            else:
                print("MySQL connection test failed (SELECT 1 did not return 1).")
                return False
    except Exception as e:
        print(f"MySQL connection test failed: {e}")
        return False

if MYSQL_ASYNC_DATABASE_URL:
    try:
        mysql_async_engine = create_async_engine(
            MYSQL_ASYNC_DATABASE_URL,
            echo=False,
        )
        MySQLAsyncSessionLocal = sessionmaker(
            bind=mysql_async_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
        )
        print("MySQL async engine and session created.")
        # 在引擎创建后执行连接测试
        # 注意：在模块顶层直接 await 可能不合适，取决于如何运行
        # 通常这类测试会在应用启动的异步上下文中进行
        # 为了简单起见，这里我们尝试在事件循环中运行它（如果模块被导入到异步环境中）
        # 或者在 main.py 中显式调用
        # asyncio.run(test_mysql_connection()) # 不建议在模块顶层直接运行
    except Exception as e:
        print(f"Error creating MySQL async engine or session: {e}")
        mysql_async_engine = None
        MySQLAsyncSessionLocal = None
else:
    print("MYSQL_ASYNC_DATABASE_URL not set. MySQL async support will be disabled.")

# --- SQLAlchemy (PostgreSQL) 异步配置 ---
postgres_async_engine = None
PostgreSQLAsyncSessionLocal = None
if POSTGRES_ASYNC_DATABASE_URL:
    try:
        postgres_async_engine = create_async_engine(
            POSTGRES_ASYNC_DATABASE_URL,
            echo=False, # 根据需要设置
        )
        PostgreSQLAsyncSessionLocal = sessionmaker(
            bind=postgres_async_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
        )
        print("PostgreSQL async engine and session created successfully.")
    except Exception as e:
        print(f"Error creating PostgreSQL async engine or session: {e}")
        postgres_async_engine = None
        PostgreSQLAsyncSessionLocal = None
else:
    print("POSTGRES_ASYNC_DATABASE_URL not set. PostgreSQL async support will be disabled.")

# SQLAlchemy Base for ORM models (保持不变)
Base = declarative_base()

# --- Redis 配置 (保持不变, 本身就是异步的) ---
redis_pool = None

async def test_redis_connection():
    if not redis_pool:
        print("Redis pool not initialized, skipping connection test.")
        return False
    try:
        r = aioredis.Redis(connection_pool=redis_pool)
        if await r.ping():
            print("Redis connection test successful (PING).")
            # 注意：对于从连接池获取的客户端，通常不需要显式关闭，但如果创建了独立的客户端，则需要
            # await r.close() # 如果 r 不是从池中获取，或者希望立即释放资源
            return True
        else:
            print("Redis connection test failed (PING did not return True).")
            return False
    except Exception as e:
        print(f"Redis connection test failed: {e}")
        return False

if REDIS_URL:
    try:
        redis_pool = ConnectionPool.from_url(REDIS_URL, decode_responses=True, max_connections=10)
        print("Redis connection pool created.")
        # asyncio.run(test_redis_connection()) # 不建议在模块顶层直接运行
    except Exception as e:
        print(f"Error creating Redis connection pool: {e}")
        redis_pool = None
else:
    print("REDIS_URL not set. Redis support will be disabled.")


# --- 依赖注入函数 (更新为使用 AsyncSession) ---

async def get_mysql_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖项，用于获取 MySQL 异步数据库会话。
    在请求处理完成后自动关闭会话。
    """
    if not MySQLAsyncSessionLocal:
        raise RuntimeError("MySQLAsyncSessionLocal is not initialized. Check MYSQL_ASYNC_DATABASE_URL and ensure it's an async driver URL.")
    async with MySQLAsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # 默认在成功时提交，如果需要更细致的控制，可以在业务逻辑中处理
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close() # 虽然 async with 会处理，显式关闭更清晰

async def get_postgres_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖项，用于获取 PostgreSQL 异步数据库会话。
    在请求处理完成后自动关闭会话。
    """
    if not PostgreSQLAsyncSessionLocal:
        raise RuntimeError("PostgreSQLAsyncSessionLocal is not initialized. Check POSTGRES_ASYNC_DATABASE_URL and ensure it's an async driver URL.")
    async with PostgreSQLAsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """
    FastAPI 依赖项，用于获取 Redis 连接。
    连接从连接池中获取。
    """
    if not redis_pool:
        raise RuntimeError("Redis connection pool is not initialized. Check REDIS_URL.")
    
    redis_client = aioredis.Redis(connection_pool=redis_pool)
    try:
        yield redis_client
    finally:
        # 对于从连接池获取的客户端，通常不需要显式关闭连接，
        # 但关闭客户端实例可以帮助释放其内部资源。
        # await redis_client.close() # 这会关闭客户端，但不一定关闭池中的连接
        # 对于 aioredis.Redis(connection_pool=...) 的实例，通常让其自然被垃圾回收即可
        # 或者在应用关闭时关闭整个连接池 (见 close_db_connections)
        pass

# --- 数据库初始化函数 (更新为异步) ---
async def init_db(engine_type: str = "postgres"):
    """
    初始化数据库，创建所有表 (异步)。
    仅在应用启动时或特定维护脚本中调用。
    """
    target_engine = None
    if engine_type == "mysql" and mysql_async_engine:
        target_engine = mysql_async_engine
    elif engine_type == "postgres" and postgres_async_engine:
        target_engine = postgres_async_engine
    
    if target_engine:
        async with target_engine.begin() as conn:
            # 在这里导入你的所有 SQLAlchemy 模型
            # from ..models import user, item # 示例
            # await conn.run_sync(Base.metadata.drop_all) # 可选：开发时清空表
            # await conn.run_sync(Base.metadata.create_all)
            print(f"Database tables for {engine_type} would be created here if models were imported and Base.metadata.create_all was called.")
    else:
        print(f"Async engine for {engine_type} not available or not specified correctly for init_db.")

# 示例：如何在应用关闭时清理资源 (更新为异步)
async def close_db_connections():
    """
    在 FastAPI 应用关闭时调用，以优雅地关闭数据库引擎和 Redis 连接池。
    """
    if mysql_async_engine:
        await mysql_async_engine.dispose()
        print("MySQL async engine disposed.")
    if postgres_async_engine:
        await postgres_async_engine.dispose()
        print("PostgreSQL async engine disposed.")
    if redis_pool:
        await redis_pool.disconnect(inuse_connections=True) # 确保关闭所有连接
        print("Redis connection pool disconnected.")

# 你可以在 main.py 中使用 lifespan 事件来管理这些连接的打开和关闭
# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# from .core.db import close_db_connections, init_db

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # 应用启动时
#     # await init_db("postgres") # 例如，初始化 PostgreSQL
#     print("Application startup: Async database connections configured.")
#     yield
#     # 应用关闭时
#     await close_db_connections()
#     print("Application shutdown: Async database connections closed.")

# app = FastAPI(lifespan=lifespan)