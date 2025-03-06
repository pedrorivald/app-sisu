from datetime import datetime
import logging
from fastapi import FastAPI, HTTPException, Request, Response
from routes.uploads.uploads_route import router as uploads_route
from routes.complexas_route import router as complexas_route
from routes.graficos_route import router as graficos_route
from routes.estados_route import router as estados_route
from routes.chamadas_route import router as chamadas_route
from routes.curso_instituicoes_route import router as curso_instituicoes_route
from routes.idades_route import router as idades_route
from routes.instituicoes_route import router as instituicoes_route
from routes.populacao_por_idade_route import router as populacao_por_idade_route
from database.db_config import init_db
from exceptions.exceptions import BadRequestException, InternalServerErrorException, NotFoundException
from exceptions.global_exception_handler import bad_request_exception_handler, global_exception_handler, http_exception_handler, internal_server_error_exception_handler, not_found_exception_handler

app = FastAPI()

@app.on_event("startup")
async def startup():
  await init_db()
  
app.add_exception_handler(NotFoundException, not_found_exception_handler)
app.add_exception_handler(BadRequestException, bad_request_exception_handler)
app.add_exception_handler(InternalServerErrorException, internal_server_error_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(uploads_route, prefix="/api")
app.include_router(complexas_route, prefix="/api")
app.include_router(graficos_route, prefix="/api")
app.include_router(estados_route, prefix="/api")
app.include_router(chamadas_route, prefix="/api")
app.include_router(curso_instituicoes_route, prefix="/api")
app.include_router(idades_route, prefix="/api")
app.include_router(instituicoes_route, prefix="/api")
app.include_router(populacao_por_idade_route, prefix="/api")

def get_log_level(status_code):
  log_levels = {
    2: logging.INFO,      # 2xx: Sucesso
    3: logging.WARNING,   # 3xx: Redirecionamento
    4: logging.ERROR,     # 4xx: Erro do cliente
    5: logging.CRITICAL,  # 5xx: Erro do servidor
  }
  return log_levels.get(status_code // 100, logging.DEBUG)

@app.middleware("http")
async def log(request: Request, call_next):
  start_time = datetime.now()
  method = request.method
  path = request.url.path

  response: Response = await call_next(request)
  status_code = response.status_code

  log_level = get_log_level(status_code)
  logging.log(log_level, f"Metodo: {method} | Caminho: {path} | Status: {status_code} | Data/Hora: {start_time}")

  return response

@app.get("/")
def root():
  return {"message": "API de dados do Sisu"}