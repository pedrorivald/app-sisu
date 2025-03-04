# Dados da Chamada Regular do SISU

## Venv
python -m venv .venv
.venv\Scripts\activate

## Rodar docker compose com banco de dados
docker-compose up --build -d

## Pausar docker compose
docker-compose down

## Links para as base de dados
INEP:
  - https://sisu.mec.gov.br/#/selecionados
  - API https://sisu-api.sisu.mec.gov.br/api/v1/oferta/instituicoes
  - API https://sisu-api.sisu.mec.gov.br/api/v1/arquivo/{co_ies}/chamada_regular
IBGE:
  - https://www.ibge.gov.br/estatisticas/sociais/populacao/9109-projecao-da-populacao.html

## Coletar Instituições em JSON
Contém todas as instituições do SISU no Brasil
python .\scripts\coleta-de-dados\coleta_instituicoes.py

## Coletar planilha em CSV de cada Instituição
Contém uma planilha com as chamadas de alunos que passaram no SISU para cada instituição
python .\scripts\coleta-de-dados\coleta_planilhas_instituicoes.py

## Concatenar todas as planilhas coletadas
Contém todas as chamadas de alunos que passaram no SISU em uma unica planilha
python .\scripts\coleta-de-dados\concatenar_planilhas_instituicoes.py

## Converter a planilha .ODS dos dados do IBGE em .CSV
Além disso para padronizar e remover as 5 linhas iniciais desnecessárias
python .\scripts\coleta-de-dados\transformar_ods_para_csv_ibge.py

## Salvar planilhas da Chamada Regular no Banco
python .\coleta_chamada_regular.py