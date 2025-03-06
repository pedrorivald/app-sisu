from typing import List
from pydantic import BaseModel

class PopulacaoPorIdadeBase(BaseModel):
  estado_id: str
  idade_id: str
  ano: int
  quantidade: int

class PopulacaoPorIdadeCreate(PopulacaoPorIdadeBase):
  pass

class PopulacaoPorIdadeUpdate(PopulacaoPorIdadeBase):
  pass  

class PopulacaoPorIdadeOut(PopulacaoPorIdadeBase):
  id: str

  class Config:
    orm_mode = True

class PopulacaoPorIdadePaginationResponse(BaseModel):
  page: int
  size: int
  total: int
  data: List[PopulacaoPorIdadeOut]