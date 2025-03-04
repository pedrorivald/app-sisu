import requests
import json
import os
import pandas as pd

url = 'https://sisu-api.sisu.mec.gov.br/api/v1/oferta/instituicoes'

diretorio_destino = 'dados/instituicoes'
nome_arquivo = 'instituicoes.json'

arquivo_csv = 'dados/instituicoes/instituicoes.csv'

try:
  # Cria o diretório se não existir
  os.makedirs(diretorio_destino, exist_ok=True)

  caminho_arquivo = os.path.join(diretorio_destino, nome_arquivo)

  response = requests.get(url)
  response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

  # Salva o conteúdo JSON no arquivo
  with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
    json.dump(response.json(), arquivo, ensure_ascii=False, indent=4)

  print(f'JSON de instituicoes salvo em: {caminho_arquivo}')

 # Salva o conteúdo CSV no arquivo
  df = pd.DataFrame(response.json())
  df.to_csv(arquivo_csv, index=False, encoding="utf-8")
  print(f'CSV de instituicoes salvo em: {caminho_arquivo}')
except:
  print("Não foi possível coletar as instituições")