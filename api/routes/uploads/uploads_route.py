import uuid
from fastapi import APIRouter, UploadFile, HTTPException, Depends
import pandas as pd
import io
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.db_config import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Estado, Idade, Instituicao, PopulacaoPorIdade  
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
      if cod_estado not in estados:
        novo_estado = Estado(
          id=str(uuid.uuid4()), 
          codigo=cod_estado, 
          uf=row['sigla'], 
          nome=row['local']
        )
        estados[cod_estado] = novo_estado
        novos_estados.append(novo_estado)
      
      idade_val = convert_to_int(row['idade'])
      if idade_val not in idades:
        nova_idade = Idade(
          id=str(uuid.uuid4()), 
          idade=idade_val
        )
        idades[idade_val] = nova_idade
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
    raise HTTPException(status_code=500, detail=str(e))
  
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
    raise HTTPException(status_code=500, detail=str(e))