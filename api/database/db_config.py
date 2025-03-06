from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

postgres_config = {"drivername": "postgresql+asyncpg",
                   "host": "sisu-postgres",
                   "port": "5432",
                   "database": "sisu",
                   "username": "postgres",
                   "password": "admin"}

Postgres_URL = URL.create(**postgres_config)

Base = declarative_base()

engine = create_async_engine(Postgres_URL, echo=True)

SessionLocal = sessionmaker(
    engine, class_=AsyncSession,
    future=True, 
    autocommit=False, 
    expire_on_commit=False
  )
  
async def get_session():
  session = SessionLocal()
  try:
    yield session
    await session.commit()
  except Exception:
    await session.rollback()
    raise
  finally:
    await session.close()

# Função para criar as tabelas no banco antes de rodar a API
async def init_db():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)