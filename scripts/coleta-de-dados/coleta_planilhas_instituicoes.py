import os
import time
import requests
import json

path_instituicoes_json = 'dados/instituicoes/instituicoes.json'
path_instituicoes_planilhas = 'dados/instituicoes/planilhas'

with open(path_instituicoes_json, 'r', encoding='utf-8') as arquivo:
  instituicoes = json.load(arquivo)

print(instituicoes) 

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
		
			nome_arquivo = os.path.basename(csv_url)
		
			# Cria o diretório se não existir
			os.makedirs(path_instituicoes_planilhas, exist_ok=True)

			caminho_arquivo = os.path.join(path_instituicoes_planilhas, nome_arquivo)
			response = requests.get(csv_url)
			response.raise_for_status()
		
			# Salva o conteúdo no arquivo
			with open(caminho_arquivo, 'wb') as arquivo:
				arquivo.write(response.content)

			print(f'Arquivo salvo em: {caminho_arquivo}')
    	
	except requests.exceptions.RequestException as e:
		print(f'Erro ao processar {co_ies}: {e}')
 
	time.sleep(1)
 