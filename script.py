import json
import requests
import csv
from sqlalchemy.orm import Session
from db import SessionLocal
from models import ChamadaRegular 
from ulid import ULID

def convert_to_boolean(value):
  return value.strip().lower() in ['sim', 's', '1'] if value else None

def convert_to_float(value):
  try:
    return float(value.replace(',', '.').strip()) if value else None
  except ValueError:
    return None
    
# Carregar a lista JSON inicial
with open('instituicoes.json', 'r', encoding='utf-8') as file:
  instituicoes = json.load(file)

resultado = []
session = SessionLocal()

for ies in instituicoes:
  co_ies = ies['co_ies']
  api_url = f'https://sisu-api.sisu.mec.gov.br/api/v1/arquivo/{co_ies}/chamada_regular'
    
  try:    
    response = requests.get(api_url)
    response.raise_for_status()
    chamada_regular_ies = response.json()
        
    for chamada_regular_ies_item in chamada_regular_ies:
      csv_url = chamada_regular_ies_item['ds_caminho_arquivo']
      print(csv_url)
      csv_response = requests.get(csv_url)
      csv_response.raise_for_status()
                
      # Processar CSV
      csv_content = csv_response.content.decode('utf-8-sig')
      csv_reader = csv.DictReader(csv_content.splitlines(), delimiter=';')
      
      for row in csv_reader:
        row = {key.strip(): value for key, value in row.items()}  # Remover espaços extras nos cabeçalhos
        sisu_dado = ChamadaRegular(
          id=str(ULID()),
          co_ies=int(row.get('CO_IES')) if row.get('CO_IES') else None,
          no_ies=row.get('NO_IES') or None,
          sg_ies=row.get('SG_IES') or None,
          sg_uf_ies=row.get('SG_UF_IES') or None,
          no_campus=row.get('NO_CAMPUS') or None,
          co_ies_curso=int(row.get('CO_IES_CURSO')) if row.get('CO_IES_CURSO') else None,
          no_curso=row.get('NO_CURSO') or None,
          ds_turno=row.get('DS_TURNO') or None,
          ds_formacao=row.get('DS_FORMACAO') or None,
          qt_vagas_concorrencia=int(row.get('QT_VAGAS_CONCORRENCIA')) if row.get('QT_VAGAS_CONCORRENCIA') else None,
          co_inscricao_enem=row.get('CO_INSCRICAO_ENEM') or None,
          no_inscrito=row.get('NO_INSCRITO') or None,
          no_modalidade_concorrencia=row.get('NO_MODALIDADE_CONCORRENCIA') or None,
          st_bonus_perc=convert_to_boolean(row.get('ST_BONUS_PERC')),
          qt_bonus_perc=convert_to_float(row.get('QT_BONUS_PERC')) if row.get('QT_BONUS_PERC') else None,
          no_acao_afirmativa_bonus=row.get('NO_ACAO_AFIRMATIVA_BONUS') or None,
          nu_nota_candidato=convert_to_float(row.get('NU_NOTA_CANDIDATO')) if row.get('NU_NOTA_CANDIDATO') else None,
          nu_notacorte_concorrida=convert_to_float(row.get('NU_NOTACORTE_CONCORRIDA')) if row.get('NU_NOTACORTE_CONCORRIDA') else None,
          nu_classificacao=int(row.get('NU_CLASSIFICACAO')) if row.get('NU_CLASSIFICACAO') else None,
          ensino_medio=convert_to_boolean(row.get('ENSINO_MEDIO')),
          quilombola=convert_to_boolean(row.get('QUILOMBOLA')),
          deficiente=convert_to_boolean(row.get('DEFICIENTE')),
          tipo_concorrencia=row.get('TIPO_CONCORRENCIA') or None
        )
        session.add(sisu_dado)
    session.commit()

  except requests.exceptions.RequestException as e:
    print(f'Erro ao processar {co_ies}: {e}')

print("Processo concluído. Os dados foram salvos no banco de dados.")

