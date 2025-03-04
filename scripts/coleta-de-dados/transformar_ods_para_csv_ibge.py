import pandas as pd
from pyexcel_ods3 import get_data

path_planilha_ibge_ods = 'dados/ibge/projecoes_2024_tab1_idade_simples.ods'
path_planilha_ibge_csv = 'dados/ibge/projecoes_idade_simples.csv'

try:  
  data = get_data(path_planilha_ibge_ods)

  sheet_name = list(data.keys())[0]
  sheet_data = data[sheet_name]

  # Converter os dados da planilha para um DataFrame
  df = pd.DataFrame(sheet_data)

  # Remover as 5 primeiras linhas
  df = df.iloc[5:].reset_index(drop=True)

  # Salvar o DataFrame em um arquivo CSV
  df.to_csv(path_planilha_ibge_csv, encoding="utf-8-sig", sep=';', index=False, header=False)
  
  print("Planilha convertida com sucesso para CSV")
except:
  print("Erro ao converter planilha")
