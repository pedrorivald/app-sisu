from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import func, select
from database.db_config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Chamada, Estado, Idade, Instituicao, PopulacaoPorIdade  

router = APIRouter(prefix="/complexas", tags=["Consultas Complexas"])
  
@router.get("/estados/vagas-por-faixa-etaria")
async def get_vagas_por_estado_faixa_etaria(
  idade_inicial: int = Query(None, alias="Idade Incial"),
  idade_final: int = Query(None, alias="Idade Final"),
  ano: int = Query(None, alias="Ano da projeção"),
  session: AsyncSession = Depends(get_session)):
  """
  Filtra pela faixa etária de acordo com o ano de projeção e retorna as vagas pela população filtrada em cada Estado.
  Conferir em https://www.gov.br/mec/pt-br/assuntos/noticias/2025/janeiro/sisu-97-das-vagas-sao-preenchidas-em-chamada-regular
  """
  try:
    queryVagasPorEstado = (
      select(
        Estado.codigo,
        Estado.uf,
        Estado.nome,
        func.count(Chamada.id).label("total_de_vagas_estado"),
      )
      .join(Instituicao, Instituicao.id_estado == Estado.id)
      .join(Chamada, Chamada.id_ies == Instituicao.id, isouter=True)
      .group_by(Estado.id)
      .order_by(Estado.nome)
    )
    
    queryPopulacaoPorFaixaIdadeEstado = (
      select(
        Estado.codigo,
        Estado.uf,
        Estado.nome,
        func.coalesce(func.sum(PopulacaoPorIdade.quantidade), 0).label("populacao_faixa_no_ano")
      )
      .join(PopulacaoPorIdade, PopulacaoPorIdade.estado_id == Estado.id)
      .join(Idade, Idade.id == PopulacaoPorIdade.idade_id)
      .where(PopulacaoPorIdade.ano == ano)
      .where(Idade.idade >= idade_inicial, Idade.idade <= idade_final)
      .group_by(Estado.id)
      .order_by(Estado.nome)
    )
      
    result = await session.execute(queryPopulacaoPorFaixaIdadeEstado)
    resultPopulacaoPorFaixaIdadeEstado = result.all()
    
    result2 = await session.execute(queryVagasPorEstado)
    resultVagasPorEstado = result2.all()
    
    def get_total_de_vagas_estado(codigo: int):
      for res in resultVagasPorEstado:
        if res.codigo == codigo:
          return res.total_de_vagas_estado
      
    return [
      {
        "codigo_estado": res.codigo,
        "uf_estado": res.uf,
        "nome_estado": res.nome,
        "total_de_vagas_estado": get_total_de_vagas_estado(res.codigo),
        "populacao_faixa_no_ano": res.populacao_faixa_no_ano,
        "total_pessoas_por_vaga": round(res.populacao_faixa_no_ano / get_total_de_vagas_estado(res.codigo)) if get_total_de_vagas_estado(res.codigo) else None,
      }
      for res in resultPopulacaoPorFaixaIdadeEstado
    ]
    
  except Exception as e:
    await session.rollback()
    raise HTTPException(status_code=500, detail=str(e))
  
@router.get("/estados/nota-media")
async def get_nota_media_por_estado(
  session: AsyncSession = Depends(get_session)):
  """
  Retorna a nota média de cada estado.
  """
  try:
    query = (
      select(
        Estado.codigo,
        Estado.uf,
        Estado.nome,
        func.coalesce(func.avg(Chamada.nu_nota_candidato), 0).label("nota_media_estado")
      )
      .join(Instituicao, Instituicao.id_estado == Estado.id)
      .join(Chamada, Chamada.id_ies == Instituicao.id)
      .group_by(Estado.id)
      .order_by(func.avg(Chamada.nu_nota_candidato).desc())
    )
    
    result = await session.execute(query)
    estados = result.all()
    
    return [
      {
        "codigo_estado": estado.codigo,
        "uf_estado": estado.uf,
        "nome_estado": estado.nome,
        "nota_media_estado": round(estado.nota_media_estado, 2),
      }
      for estado in estados
    ]
    
  except Exception as e:
    await session.rollback()
    raise HTTPException(status_code=500, detail=str(e))
  
@router.get("/instituicoes/top-10")
async def get_top_10_instituicoes(
  session: AsyncSession = Depends(get_session)):
  """
  Retorna as 10 instituições com maiores médias.
  """
  try:
    query = (
      select(
        Instituicao.no_ies,
        Instituicao.sg_ies,
        Instituicao.no_sitio_ies,
        Instituicao.co_ies,
        Estado.codigo,
        Estado.uf,
        Estado.nome,
        func.coalesce(func.avg(Chamada.nu_nota_candidato), 0).label("nota_media_instituicao")
      )
      .join(Estado, Estado.id == Instituicao.id_estado)
      .join(Chamada, Chamada.id_ies == Instituicao.id)
      .group_by(Instituicao.id, Estado.id)
      .order_by(func.avg(Chamada.nu_nota_candidato).desc())
      .limit(10)
    )
    
    result = await session.execute(query)
    instituicoes = result.all()
    
    return [
      {
        "nome_instituicao": inst.no_ies,
        "sigla_instituicao": inst.sg_ies,
        "site_instituicao": inst.no_sitio_ies,
        "codigo_instituicao": inst.co_ies,
        "codigo_estado": inst.codigo,
        "uf_estado": inst.uf,
        "nome_estado": inst.nome,
        "nota_media_instituicao": round(inst.nota_media_instituicao, 2),
      }
      for inst in instituicoes
    ]
    
  except Exception as e:
    await session.rollback()
    raise HTTPException(status_code=500, detail=str(e))
  
@router.get("/instituicoes/alunos/top-10")
async def get_top_10_alunos_por_instituicao(
  sigla_instituicao: str = Query(None, alias="Sigla da Insttuição. Ex.: UFC"),
  session: AsyncSession = Depends(get_session)):
  """
  Filtra pela sigla da instituição e retorna os 10 alunos com as maiores notas.
  """
  try:
    query = (
      select(
        Instituicao.no_ies,
        Instituicao.sg_ies,
        Instituicao.no_sitio_ies,
        Instituicao.co_ies,
        Estado.codigo,
        Estado.uf,
        Estado.nome,
        Chamada.no_inscrito,
        Chamada.nu_nota_candidato
      )
      .join(Estado, Estado.id == Instituicao.id_estado)
      .join(Chamada, Chamada.id_ies == Instituicao.id)
      .where(Instituicao.sg_ies == sigla_instituicao)
      .order_by(Chamada.nu_nota_candidato.desc())
      .limit(10)
    )
    
    result = await session.execute(query)
    alunos = result.all()
    
    return [
      {
        "nome_instituicao": aluno.no_ies,
        "sigla_instituicao": aluno.sg_ies,
        "site_instituicao": aluno.no_sitio_ies,
        "codigo_instituicao": aluno.co_ies,
        "codigo_estado": aluno.codigo,
        "uf_estado": aluno.uf,
        "nome_estado": aluno.nome,
        "nome_aluno": aluno.no_inscrito,
        "nota_aluno": round(aluno.nu_nota_candidato, 2),
      }
      for aluno in alunos
    ]
    
  except Exception as e:
    await session.rollback()
    raise HTTPException(status_code=500, detail=str(e))
  
@router.get("/estados/alunos/top-10-nomes")
async def get_nome_que_mais_passaram_por_estado(
  uf_estado: str = Query(None, alias="UF do Estado. Ex. CE, SP..."),
  session: AsyncSession = Depends(get_session)):
  """
  Filtra por estado e lista os 10 nomes que mais passaram em vagas na primeira chamada do SISU. (Apenas o primeiro nome do nome completo)
  """
  try:
    query = (
      select(
        func.split_part(Chamada.no_inscrito, ' ', 1).label("parte_do_nome_aluno"),
        func.count(Chamada.id).label("quantidade_aprovados"),
        Estado.codigo,
        Estado.uf,
        Estado.nome
      )
      .join(Instituicao, Instituicao.id == Chamada.id_ies)
      .join(Estado, Estado.id == Instituicao.id_estado)
      .group_by("parte_do_nome_aluno", Estado.codigo, Estado.uf, Estado.nome)
      .order_by(func.count(Chamada.id).desc())
      .limit(10)
    )
    
    if uf_estado:
      query = query.where(Estado.uf == uf_estado)
    
    result = await session.execute(query)
    nomes = result.all()
    
    return [
      {
        "parte_do_nome_aluno": nome.parte_do_nome_aluno,
        "quantidade_aprovados": nome.quantidade_aprovados,
        "codigo_estado": nome.codigo,
        "uf_estado": nome.uf,
        "nome_estado": nome.nome,
      }
      for nome in nomes
    ]
    
  except Exception as e:
    await session.rollback()
    raise HTTPException(status_code=500, detail=str(e))
  
@router.get("/alunos/top-10-nomes")
async def get_nome_que_mais_passaram(
  session: AsyncSession = Depends(get_session)):
  """
  Lista os 10 nomes que mais passaram em vagas na primeira chamada do SISU. (Apenas o primeiro nome do nome completo)
  """
  try:
    query = (
      select(
        func.split_part(Chamada.no_inscrito, ' ', 1).label("parte_do_nome_aluno"),
        func.count(Chamada.id).label("quantidade_aprovados"),
      )
      .group_by("parte_do_nome_aluno")
      .order_by(func.count(Chamada.id).desc())
      .limit(10)
    )
    
    result = await session.execute(query)
    nomes = result.all()
    
    return [
      {
        "parte_do_nome_aluno": nome.parte_do_nome_aluno,
        "quantidade_aprovados": nome.quantidade_aprovados,
      }
      for nome in nomes
    ]
    
  except Exception as e:
    await session.rollback()
    raise HTTPException(status_code=500, detail=str(e))