from typing import List
from pydantic import BaseModel

class CursoInstituicaoBase(BaseModel):
  co_ies_curso: int
  no_curso: str
  ds_formacao: str
  ds_turno: str
  id_ies: str

class CursoInstituicaoCreate(CursoInstituicaoBase):
  pass

class CursoInstituicaoUpdate(CursoInstituicaoBase):
  pass

class CursoInstituicaoOut(CursoInstituicaoBase):
  id: str

  class Config:
    orm_mode = True

class CursoInstituicaoPaginationResponse(BaseModel):
  page: int
  size: int
  total: int
  data: List[CursoInstituicaoOut]