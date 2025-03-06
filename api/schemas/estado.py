from pydantic import BaseModel
from typing import List

class EstadoBase(BaseModel):
  codigo: int
  uf: str
  nome: str

class EstadoCreate(EstadoBase):
  pass

class EstadoUpdate(EstadoBase):
  pass

class EstadoOut(EstadoBase):
  id: str

  class Config:
    orm_mode = True

class EstadoPaginationResponse(BaseModel):
  page: int
  size: int
  total: int
  data: List[EstadoOut]