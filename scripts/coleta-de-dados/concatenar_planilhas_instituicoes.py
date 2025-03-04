import pandas as pd
import glob

path_planilhas = 'dados/instituicoes/planilhas/*.csv'
path_planilha_combinada = 'dados/instituicoes/planilha_combinada.csv'

try:
  arquivos = glob.glob(path_planilhas)
  
  # Le e concatena todos os arquivos CSV em um único DataFrame
  df_combinado = pd.concat((pd.read_csv(f, encoding='utf-8-sig', sep=';') for f in arquivos), ignore_index=True)

  # # Salva o DataFrame combinado em um novo arquivo CSV
  df_combinado.to_csv(path_planilha_combinada, index=False)
  
  print(f"Planilhas concatenadas com sucesso.")

except:
  print(f"Erro ao concatenar planilhas")


