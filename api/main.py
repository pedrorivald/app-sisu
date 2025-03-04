from fastapi import FastAPI
from routes.uploads.uploads_route import router as uploads_route
from routes.complexas_route import router as complexas_route
from database.db_config import init_db

app = FastAPI()

@app.on_event("startup")
async def startup():
  await init_db()

app.include_router(uploads_route, prefix="/api")
app.include_router(complexas_route, prefix="/api")

@app.get("/")
def root():
  return {"message": "API de dados do Sisu"}