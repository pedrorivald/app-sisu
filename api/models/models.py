from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from database.db_config import Base

class Instituicao(Base):
  __tablename__ = 'instituicoes'

  id = Column(String, primary_key=True, index=True)
  
  co_ies = Column(Integer, unique=True, index=True, nullable=False) 
  no_ies = Column(String, nullable=False) 
  sg_ies = Column(String, nullable=False)
  
  uf_estado = Column(String, ForeignKey("estados.uf"))  # 1:N
  estado = relationship("Estado", back_populates="instituicoes")  # 1:N
  
  co_municipio = Column(Integer, nullable=False) 
  no_municipio = Column(String, nullable=False)
  no_sitio_ies = Column(String, nullable=True)
  
  cursos = relationship("CursoInstituicao", back_populates="instituicao")  # 1:N
  chamadas = relationship("Chamada", back_populates="instituicao")  # 1:N
  
class CursoInstituicao(Base):
  __tablename__ = 'cursos_instituicoes'
  
  id = Column(String, primary_key=True, index=True)
  
  co_ies_curso = Column(Integer, nullable=False, unique=True)
  no_curso = Column(String, nullable=False)
  
  ds_formacao = Column(String, nullable=False)
  ds_turno = Column(String, nullable=False)
  
  id_ies = Column(String, ForeignKey("instituicoes.id"))  # 1:N
  instituicao = relationship("Instituicao", back_populates="cursos")  # 1:N
  
  chamadas = relationship("Chamada", back_populates="curso")  # 1:N
  
class Chamada(Base):
  __tablename__ = 'chamadas'
  
  id = Column(String, primary_key=True, index=True)
  
  id_ies = Column(String, ForeignKey("instituicoes.id"))  # 1:N
  instituicao = relationship("Instituicao", back_populates="chamadas")  # 1:N
  
  id_curso = Column(String, ForeignKey("cursos_instituicoes.id"))  # 1:N
  curso = relationship("CursoInstituicao", back_populates="chamadas")  # 1:N
  
  no_campus = Column(String, nullable=False)
  
  co_inscricao_enem = Column(String, nullable=False)
  no_inscrito = Column(String, nullable=False)
  
  no_modalidade_concorrencia = Column(String, nullable=False)
  qt_vagas_concorrencia = Column(Integer, nullable=False)
  
  nu_nota_candidato = Column(Float, nullable=False)
  nu_notacorte_concorrida = Column(Float, nullable=False)
  nu_classificacao = Column(Integer, nullable=False)
  
  ensino_medio = Column(Boolean, nullable=False) 
  quilombola = Column(Boolean, nullable=False) 
  deficiente = Column(Boolean, nullable=False) 
  
class PopulacaoPorIdade(Base):
  __tablename__ = 'populacao_por_idade'
  
  id = Column(String, primary_key=True, index=True)
  
  quantidade = Column(Integer, nullable=False)
  idade = Column(Integer, nullable=False)
  ano = Column(Integer, nullable=False)
  
  id_estado = Column(String, ForeignKey("estados.id"))  # 1:N
  
class Estado(Base):
  __tablename__ = 'estados'
  
  id = Column(String, primary_key=True, index=True)
  
  codigo = Column(Integer, unique=True, nullable=False)
  uf = Column(String, nullable=False, unique=True, index=True)
  nome = Column(String, nullable=False, unique=True)
  
  instituicoes = relationship("Instituicao", back_populates="estado")  # 1:N