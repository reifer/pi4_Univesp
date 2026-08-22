# Plano de Ação - Enriquecimento do Pipeline e Dashboard (ENEM 2025)

## Contexto
O pipeline básico sociodemográfico e o modelo de machine learning de treineiros foram concluídos. Vamos agora expandir o projeto para integrar os arquivos de Notas/Resultados e Itens de Prova, criando um dashboard de alto impacto analítico para a faculdade (PI4).

## Objetivo
Processar a base de resultados e itens de prova usando PySpark, cruzar com o perfil sociodemográfico e exibir novas métricas no dashboard Streamlit.

## Regras e Restrições
- Utilizar PySpark para processar grandes volumes de dados de forma otimizada.
- Garantir a modularidade para permitir a futura expansão para outros anos do ENEM.
- Manter o ecossistema de dados em formato Parquet (`data/processed/`).

## Execução
- [x] **Fase 1:** Ingerir o arquivo `RESULTADOS_2025.csv` (Notas) e convertê-lo para Parquet em `src/data_pipeline/ingest.py`.
- [x] **Fase 2:** Realizar o cruzamento (*Join*) entre `PARTICIPANTES` e `RESULTADOS` por `NU_INSCRICAO` em `src/data_pipeline/transform.py` para correlacionar notas com renda e status de treineiro.
- [x] **Fase 3:** Atualizar `src/app/dashboard.py` para incluir a aba de **Análise de Desempenho e Notas**.
- [ ] **Fase 4 (Avançada):** Processar métricas agregadas do arquivo `ITENS_PROVA_2025.csv` (taxa de acerto/dificuldade por questão) para enriquecer o projeto acadêmico.