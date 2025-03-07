from typing import List
from pydantic import BaseModel
  
class InstituicaoBase(BaseModel):
  co_ies: int
  no_ies: str
  sg_ies: str
  id_estado: str
  co_municipio: int
  no_municipio: str
  no_sitio_ies: str

class InstituicaoCreate(InstituicaoBase):
  pass

class InstituicaoUpdate(InstituicaoBase):
  pass

class InstituicaoOut(InstituicaoBase):
  id: str

  class Config:
    from_attributes = True

class InstituicaoPaginationResponse(BaseModel):
  page: int
  size: int
  total: int
  data: List[InstituicaoOut]