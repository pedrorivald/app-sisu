from typing import List
from pydantic import BaseModel

class ChamadaBase(BaseModel):
  id_ies: str
  id_curso: str
  no_campus: str
  co_inscricao_enem: str
  no_inscrito: str
  no_modalidade_concorrencia: str
  qt_vagas_concorrencia: int
  nu_nota_candidato: float
  nu_notacorte_concorrida: float
  nu_classificacao: int
  ensino_medio: bool = False
  quilombola: bool = False
  deficiente: bool = False

class ChamadaCreate(ChamadaBase):
  pass

class ChamadaUpdate(ChamadaBase):
  pass

class ChamadaOut(ChamadaBase):
  id: str

  class Config:
    from_attributes = True

class ChamadaPaginationResponse(BaseModel):
  page: int
  size: int
  total: int
  data: List[ChamadaOut]