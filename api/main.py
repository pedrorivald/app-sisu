from fastapi import FastAPI
from database.db_config import init_db

app = FastAPI()

# Garantir que o banco de dados seja criado antes de rodar a API
@app.on_event("startup")
async def startup():
  await init_db()

# Registrando as Rotas
# app.include_router(bens_e_direitos, prefix="/api")

@app.get("/")
def root():
    return {"message": "API de dados do Sisu"}