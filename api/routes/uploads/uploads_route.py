import uuid
from fastapi import APIRouter, UploadFile, Depends
import pandas as pd
import io
from sqlalchemy import insert, select
from exceptions.exceptions import InternalServerErrorException
from database.db_config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Chamada, CursoInstituicao, Estado, Idade, Instituicao, PopulacaoPorIdade  
import unidecode  

router = APIRouter(prefix="/uploads", tags=["Uploads"])

COLUNAS_PROJECOES_IBGE = {
  "idade": "idade",
  "sexo": "sexo",
  "cod": "cod",
  "sigla": "sigla",
  "local": "local",
  "2000": "2000",
  "2001": "2001",
  "2002": "2002",
  "2003": "2003",
  "2004": "2004",
  "2005": "2005",
  "2006": "2006",
  "2007": "2007",
  "2008": "2008",
  "2009": "2009",
  "2010": "2010",
  "2011": "2011",
  "2012": "2012",
  "2013": "2013",
  "2014": "2014",
  "2015": "2015",
  "2016": "2016",
  "2017": "2017",
  "2018": "2018",
  "2019": "2019",
  "2020": "2020",
  "2021": "2021",
  "2022": "2022",
  "2023": "2023",
  "2024": "2024",
  "2025": "2025",
  "2026": "2026",
  "2027": "2027",
  "2028": "2028",
  "2029": "2029",
  "2030": "2030",
  "2031": "2031",
  "2032": "2032",
  "2033": "2033",
  "2034": "2034",
  "2035": "2035",
  "2036": "2036",
  "2037": "2037",
  "2038": "2038",
  "2039": "2039",
  "2040": "2040",
  "2041": "2041",
  "2042": "2042",
  "2043": "2043",
  "2044": "2044",
  "2045": "2045",
  "2046": "2046",
  "2047": "2047",
  "2048": "2048",
  "2049": "2049",
  "2050": "2050",
  "2051": "2051",
  "2052": "2052",
  "2053": "2053",
  "2054": "2054",
  "2055": "2055",
  "2056": "2056",
  "2057": "2057",
  "2058": "2058",
  "2059": "2059",
  "2060": "2060",
  "2061": "2061",
  "2062": "2062",
  "2063": "2063",
  "2064": "2064",
  "2065": "2065",
  "2066": "2066",
  "2067": "2067",
  "2068": "2068",
  "2069": "2069",
  "2070": "2070"
}

def convert_to_int(value):
  """
  Converte um valor para inteiro, tratando valores NaN como 0.
  """
  if pd.isna(value):
    return 0
  else:
    return int(value)
  
def convert_to_boolean(value):
  """
  Converte um valor para boolean.
  """
  return value.strip().lower() in ['sim', 's', '1'] if value else False

def convert_to_float(value):
  """
  Converte um valor para float, tratando valores NaN como 0.
  """
  if pd.isna(value):
    return float(0)
  else:
    return float(value.replace(',', '.').strip()) if value else float(0)

def normalizar_nome_coluna(nome: str) -> str:
  """
  Normaliza o nome de uma coluna removendo acentos, 
  convertendo para minúsculas e substituindo espaços por underscores.
  """
  nome = unidecode.unidecode(nome).lower().strip()
  nome = nome.replace(" ", "_").replace("-", "_").replace(".0", "").replace(".", "")
  return nome

@router.post("/projecoes-ibge")
async def projecoes_ibge(file: UploadFile, session: AsyncSession = Depends(get_session)):
  """
  Recebe um arquivo CSV, processa os dados e insere os registros nas tabelas: Estados, Idades e PopulacaoPorIdade.
  """
  try:
    df = pd.read_csv(io.BytesIO(await file.read()), delimiter=';', encoding="utf-8-sig")
    df.columns = [normalizar_nome_coluna(col) for col in df.columns]

    colunas_para_usar = {csv_col: model_col for csv_col, model_col in COLUNAS_PROJECOES_IBGE.items() if csv_col in df.columns}
    df = df.rename(columns=colunas_para_usar)[list(colunas_para_usar.values())]
    
    print(df)

    # Filtrar dados (SEXO == "ambos" e COD >= 11)
    df = df[(df['sexo'] == 'Ambos') & (df['cod'].fillna(0).astype(int) >= 11)]
    
    estados = {}
    idades = {}
    novos_estados = []
    novos_idades = []
    registros = []
    
    for _, row in df.iterrows():
      cod_estado = convert_to_int(row['cod'])
      if str(cod_estado) not in estados:
        novo_estado = Estado(
          id=str(uuid.uuid4()), 
          codigo=cod_estado, 
          uf=row['sigla'], 
          nome=row['local']
        )
        estados[str(cod_estado)] = novo_estado
        novos_estados.append(novo_estado)
      
      idade_val = convert_to_int(row['idade'])
      if str(idade_val) not in idades:
        nova_idade = Idade(
          id=str(uuid.uuid4()), 
          idade=idade_val
        )
        idades[str(idade_val)] = nova_idade
        novos_idades.append(nova_idade) 
    
    if novos_estados:
      session.add_all(novos_estados)
      await session.commit()
      result = await session.execute(select(Estado))
      estados = result.scalars().all()
      
    print(estados)
    
    if novos_idades:
      session.add_all(novos_idades)
      await session.commit()
      result = await session.execute(select(Idade))
      idades = result.scalars().all()
      
    print(idades)
      
    for _, row in df.iterrows():
      cod_estado = convert_to_int(row['cod'])
      idade_val = convert_to_int(row['idade'])
      
      for ano in range(2000, 2071):
        quantidade = convert_to_int(row[str(ano)])
        registro = PopulacaoPorIdade(
          id=str(uuid.uuid4()),
          estado_id= next((e for e in estados if e.codigo == cod_estado), None).id,
          idade_id=next((i for i in idades if i.idade == idade_val), None).id,
          ano=ano,
          quantidade=quantidade
        )
        registros.append(registro)
        print(str(registro))
   
      session.add_all(registros)
      await session.commit()
      registros = []
    
    return {"message": "Dados inseridos com sucesso"}
  except Exception as e:
    await session.rollback()
    raise InternalServerErrorException(str(e))
  
COLUNAS_INSTITUICOES_INEP = {
  "co_ies": "co_ies",
  "no_ies": "no_ies",
  "sg_ies": "sg_ies",
  "sg_uf": "sg_uf",
  "co_municipio": "co_municipio",
  "no_municipio": "no_municipio",
  "no_sitio_ies": "no_sitio_ies",
}
  
@router.post("/instituicoes-inep")
async def instituicoes_inep(file: UploadFile, session: AsyncSession = Depends(get_session)):
  """
  Recebe um arquivo CSV, processa os dados e insere os registros na tabela: Instituicoes.
  """
  try:
    df = pd.read_csv(io.BytesIO(await file.read()), delimiter=',', encoding="utf-8-sig")
    df.columns = [normalizar_nome_coluna(col) for col in df.columns]

    colunas_para_usar = {csv_col: model_col for csv_col, model_col in COLUNAS_INSTITUICOES_INEP.items() if csv_col in df.columns}
    df = df.rename(columns=colunas_para_usar)[list(colunas_para_usar.values())]
    
    print(df)

    result = await session.execute(select(Estado))
    estados = result.scalars().all()
    registros = []
      
    for _, row in df.iterrows():
      registro = Instituicao(
        id = str(uuid.uuid4()),
        co_ies = convert_to_int(row['co_ies']),
        no_ies = row['no_ies'],
        sg_ies = row['sg_ies'],
        id_estado = next((e for e in estados if e.uf == row['sg_uf']), None).id,
        co_municipio = convert_to_int(row['co_municipio']),
        no_municipio = row['no_municipio'],
        no_sitio_ies = row['no_sitio_ies'],
      )
      
      registros.append(registro)
      print(str(registro))
   
    session.add_all(registros)
    await session.commit()
    registros = []
    
    return {"message": "Dados inseridos com sucesso"}
  except Exception as e:
    await session.rollback()
    raise InternalServerErrorException(str(e))
  
COLUNAS_CHAMADAS_INEP = {
  "co_ies": "co_ies",
  "no_ies": "no_ies",
  "sg_ies": "sg_ies",
  "sg_uf_ies": "sg_uf_ies",
  "no_campus": "no_campus",
  "co_ies_curso": "co_ies_curso",
  "no_curso": "no_curso",
  "ds_turno": "ds_turno",
  "ds_formacao": "ds_formacao",
  "qt_vagas_concorrencia": "qt_vagas_concorrencia",
  "co_inscricao_enem": "co_inscricao_enem",
  "no_inscrito": "no_inscrito",
  "no_modalidade_concorrencia": "no_modalidade_concorrencia",
  "nu_nota_candidato": "nu_nota_candidato",
  "nu_notacorte_concorrida": "nu_notacorte_concorrida",
  "nu_classificacao": "nu_classificacao",
  "ensino_medio": "ensino_medio",
  "quilombola": "quilombola",
  "deficiente": "deficiente",
  "tipo_concorrencia": "tipo_concorrencia"
}
  
@router.post("/chamadas-inep")
async def chamadas_inep(file: UploadFile, session: AsyncSession = Depends(get_session)):
  """
  Recebe um arquivo CSV, processa os dados e insere os registros nas tabelas: Chamada e CursoInstituicao.
  """
  try:
    df = pd.read_csv(io.BytesIO(await file.read()), delimiter=',', encoding="utf-8-sig")
    df.columns = [normalizar_nome_coluna(col) for col in df.columns]

    colunas_para_usar = {csv_col: model_col for csv_col, model_col in COLUNAS_CHAMADAS_INEP.items() if csv_col in df.columns}
    df = df.rename(columns=colunas_para_usar)[list(colunas_para_usar.values())]
    
    result = await session.execute(select(Instituicao))
    instituicoes = result.scalars().all()
    cursos = {}
    novos_cursos = []
    chamadas = []
      
    for _, row in df.iterrows():
      co_ies_curso = convert_to_int(row['co_ies_curso'])
      if str(co_ies_curso) not in cursos:
        novo_curso = CursoInstituicao(
          id = str(uuid.uuid4()),
          co_ies_curso = convert_to_int(row['co_ies_curso']),
          no_curso = row['no_curso'],
          ds_formacao = row['ds_formacao'],
          ds_turno = row['ds_turno'],
          id_ies = next((i for i in instituicoes if i.co_ies == row['co_ies']), None).id,
        )
        
        cursos[str(co_ies_curso)] = novo_curso
        novos_cursos.append(novo_curso)
        
    if novos_cursos:
      batch_size = 5_000
      for i in range(0, len(novos_cursos), batch_size):
        batch = novos_cursos[i:i + batch_size]
        
        data = [u.__dict__ for u in batch]
        for d in data:
          d.pop("_sa_instance_state", None)

        await session.execute(insert(CursoInstituicao), data)
        print(f"{i} lote de cursos inserido")
      
      await session.commit()
      result = await session.execute(select(CursoInstituicao))
      cursos = result.scalars().all()
      
    for _, row in df.iterrows():
      chamada = Chamada(
        id = str(uuid.uuid4()),
        no_campus = row['no_campus'],
        co_inscricao_enem = row['co_inscricao_enem'],
        no_inscrito = row['no_inscrito'],
        no_modalidade_concorrencia = row['no_modalidade_concorrencia'],
        qt_vagas_concorrencia = convert_to_int(row['qt_vagas_concorrencia']),
        nu_nota_candidato = convert_to_float(row['nu_nota_candidato']),
        nu_notacorte_concorrida = convert_to_float(row['nu_notacorte_concorrida']),
        nu_classificacao = convert_to_int(row['nu_classificacao']),
        ensino_medio = convert_to_boolean(row['ensino_medio']),
        quilombola = convert_to_boolean(row['quilombola']),
        deficiente = convert_to_boolean(row['deficiente']),
        id_ies = next((i for i in instituicoes if i.co_ies == row['co_ies']), None).id,
        id_curso = next((c for c in cursos if c.co_ies_curso == row['co_ies_curso']), None).id,
      )
      
      chamadas.append(chamada)
      
    batch_size = 10_000
    for i in range(0, len(chamadas), batch_size):
      batch = chamadas[i:i + batch_size]
      
      data = [u.__dict__ for u in batch]
      for d in data:
        d.pop("_sa_instance_state", None)
          
      await session.execute(insert(Chamada), data)
      print(f"{i} lote de chamadas inserido")
      
    await session.commit()
   
    return {"message": "Dados inseridos com sucesso"}
  except Exception as e:
    await session.rollback()
    raise InternalServerErrorException(str(e))