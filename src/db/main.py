from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from src.config import Config

engine = create_async_engine(
    Config.DATABASE_URL,
    pool_pre_ping=True,
)

# Crée un sessionmaker asynchrone au module-level pour réutilisation
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session