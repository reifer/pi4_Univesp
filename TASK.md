# Plano de Ação - Projeto Integrador (PI4)

## Contexto
Projeto de análise de dados educacionais do ENEM utilizando PySpark e Python, estruturado em camadas de dados (raw, processed, curated). O ambiente virtual `.venv` e o Java já estão configurados.

## Objetivo
Desenvolver as etapas restantes do pipeline de dados para gerar análises e modelos preditivos/descritivos para a faculdade.

## Regras e Restrições
- Utilizar PySpark para processamento de grandes volumes de dados.
- Manter a organização das pastas (`src/data_pipeline/`, `data/processed/`, etc.).
- Validar cada script no terminal antes de prosseguir.

## Execução (Próximos Passos)
- [x] **Passo 1:** Ingestão dos dados brutos e conversão para formato Parquet (`src/data_pipeline/ingest.py`).
- [x] **Passo 2:** Criar o script de limpeza e tratamento dos dados (`src/data_pipeline/clean.py`).
- [x] **Passo 3:** Desenvolver as agregações estatísticas principais (`src/data_pipeline/transform.py`).
- [x] **Passo 4:** Criar visualizações ou modelo de machine learning básico (`src/data_pipeline/report_or_ml.py`).