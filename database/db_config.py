from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuração do banco de dados PostgreSQL
DATABASE_URL = "postgresql://postgres:admin@localhost:5432/sisu"

Base = declarative_base()

# Criando o motor de conexão síncrono
engine = create_engine(DATABASE_URL, echo=True)

# Criando a fábrica de sessões síncronas
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Função para criar as tabelas no banco antes de rodar a API
def init_db():
  with engine.begin() as conn:
    Base.metadata.create_all(conn)

# Dependência para obter a sessão do banco
def get_session():
  with SessionLocal() as session:
    yield session
