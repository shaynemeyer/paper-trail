# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import DATABASE_URL

# Async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,  # postgresql+asyncpg://user:pass@host/db
    echo=True,  # Log SQL queries in development
    future=True,
    pool_size=20,  # Default pool size
    max_overflow=10,  # Additional connections when needed
    pool_pre_ping=True,  # Test connection health before using
)
# Async session maker
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency for routes
async def get_session():
    async with async_session_maker() as session:
        yield session
