from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from database.db_config import Base

class Instituicao(Base):
  __tablename__ = 'instituicoes'

  id = Column(String, primary_key=True)
  
  co_ies = Column(Integer, unique=True, nullable=False) 
  no_ies = Column(String, nullable=False) 
  sg_ies = Column(String, nullable=False)
  
  id_estado = Column(String, ForeignKey("estados.id"))  # 1:N
  estado = relationship("Estado", back_populates="instituicoes")  # 1:N
  
  co_municipio = Column(Integer, nullable=False) 
  no_municipio = Column(String, nullable=False)
  no_sitio_ies = Column(String, nullable=True)
  
  cursos = relationship("CursoInstituicao", back_populates="instituicao")  # 1:N
  chamadas = relationship("Chamada", back_populates="instituicao")  # 1:N
  
class CursoInstituicao(Base):
  __tablename__ = 'cursos_instituicoes'
  
  id = Column(String, primary_key=True)
  
  co_ies_curso = Column(Integer, nullable=False, unique=True)
  no_curso = Column(String, nullable=False)
  
  ds_formacao = Column(String, nullable=False)
  ds_turno = Column(String, nullable=False)
  
  id_ies = Column(String, ForeignKey("instituicoes.id"))  # 1:N
  instituicao = relationship("Instituicao", back_populates="cursos")  # 1:N
  
  chamadas = relationship("Chamada", back_populates="curso")  # 1:N
  
class Chamada(Base):
  __tablename__ = 'chamadas'
  
  id = Column(String, primary_key=True)
  
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
  
  ensino_medio = Column(Boolean, nullable=False, default=False) 
  quilombola = Column(Boolean, nullable=False, default=False) 
  deficiente = Column(Boolean, nullable=False, default=False) 
  
class PopulacaoPorIdade(Base):
  __tablename__ = 'populacao_por_idade'
  
  id = Column(String, primary_key=True)
  
  estado_id = Column(String, ForeignKey("estados.id"), nullable=False)
  idade_id = Column(Integer, ForeignKey("idades.id"), nullable=False)
  ano = Column(Integer, nullable=False)  # Ano da projeção (ex: 2025, 2030, 2040)
  
  quantidade = Column(Integer, nullable=False)  # População projetada para essa idade no estado e ano

  estado = relationship("Estado", back_populates="populacao")
  idade = relationship("Idade", back_populates="populacao")
  
class Idade(Base):
  __tablename__ = 'idades'

  id = Column(String, primary_key=True)
  idade = Column(Integer, nullable=False)
  
  populacao = relationship("PopulacaoPorIdade", back_populates="idade")
  
class Estado(Base):
  __tablename__ = 'estados'
  
  id = Column(String, primary_key=True)
  
  codigo = Column(Integer, unique=True, nullable=False)
  uf = Column(String, nullable=False, unique=True)
  nome = Column(String, nullable=False, unique=True)
  
  populacao = relationship("PopulacaoPorIdade", back_populates="estado")
  instituicoes = relationship("Instituicao", back_populates="estado")  # 1:N