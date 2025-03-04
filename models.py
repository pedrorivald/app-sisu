from sqlalchemy import Column, Integer, String, Float, Boolean
from db import Base

class ChamadaRegular(Base):
  __tablename__ = 'chamada_regular'

  id = Column(String, primary_key=True)
  co_ies = Column(Integer, nullable=True)
  no_ies = Column(String, nullable=True)
  sg_ies = Column(String, nullable=True)
  sg_uf_ies = Column(String, nullable=True)
  no_campus = Column(String, nullable=True)
  co_ies_curso = Column(Integer, nullable=True)
  no_curso = Column(String, nullable=True)
  ds_turno = Column(String, nullable=True)
  ds_formacao = Column(String, nullable=True)
  qt_vagas_concorrencia = Column(Integer, nullable=True)
  co_inscricao_enem = Column(String, nullable=True)
  no_inscrito = Column(String, nullable=True)
  no_modalidade_concorrencia = Column(String, nullable=True)
  st_bonus_perc = Column(Boolean, nullable=True)
  qt_bonus_perc = Column(Float, nullable=True)
  no_acao_afirmativa_bonus = Column(String, nullable=True)
  nu_nota_candidato = Column(Float, nullable=True)
  nu_notacorte_concorrida = Column(Float, nullable=True)
  nu_classificacao = Column(Integer, nullable=True)
  ensino_medio = Column(Boolean, nullable=True) 
  quilombola = Column(Boolean, nullable=True) 
  deficiente = Column(Boolean, nullable=True) 
  tipo_concorrencia = Column(String, nullable=True)

class Instituicao(Base):
  __tablename__ = 'instituicoes'

  id_ies = Column(String, primary_key=True)
  co_ies = Column(Integer, unique=True, nullable=False) 
  no_ies = Column(String, nullable=True) 
  sg_ies = Column(String, nullable=True)
  sg_uf = Column(String, nullable=True)
  co_municipio = Column(Integer, nullable=True) 
  no_municipio = Column(String, nullable=True)
  no_sitio_ies = Column(String, nullable=True)
  
class Campus(Base):
  id_campus = Column(String, primary_key=True)
  no_campus = Column(String, nullable=True)
  
class Curso(Base):
  id_curso = Column(String, primary_key=True)
  co_ies_curso = Column(Integer, nullable=True, unique=True)
  no_curso = Column(String, nullable=True)
  ds_formacao = Column(String, nullable=True)
  
class Chamada(Base):
  id_chamada = Column(String, primary_key=True)
  
  id_ies = Column(String, nullable=False)
  id_campus = Column(String, nullable=False)
  id_curso = Column(String, nullable=False)
  
  ds_turno = Column(String, nullable=True)
  
  co_inscricao_enem = Column(String, nullable=True)
  no_inscrito = Column(String, nullable=True)
  
  no_modalidade_concorrencia = Column(String, nullable=True)
  tipo_concorrencia = Column(String, nullable=True)
  qt_vagas_concorrencia = Column(Integer, nullable=True)
  
  # st_bonus_perc = Column(Boolean, nullable=True)
  # qt_bonus_perc = Column(Float, nullable=True)
  # no_acao_afirmativa_bonus = Column(String, nullable=True)
  
  nu_nota_candidato = Column(Float, nullable=True)
  nu_notacorte_concorrida = Column(Float, nullable=True)
  nu_classificacao = Column(Integer, nullable=True)
  
  ensino_medio = Column(Boolean, nullable=True) 
  quilombola = Column(Boolean, nullable=True) 
  deficiente = Column(Boolean, nullable=True) 