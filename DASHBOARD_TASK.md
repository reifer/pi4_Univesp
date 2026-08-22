# Plano de Ação - Dashboard Interativo (Streamlit)

## Contexto
O pipeline de dados do ENEM 2025 está concluído. Temos as bases consolidadas em Parquet (`data/processed/`) e o relatório de machine learning (`data/processed/enem_2025_ml_insights.json`).

## Objetivo
Criar uma aplicação web interativa utilizando Streamlit em `src/app/dashboard.py` para visualizar os insights do projeto acadêmico.

## Regras e Restrições
- Utilizar Streamlit para a interface web.
- Utilizar Pandas ou PySpark para ler os dados Parquet gerados anteriormente.
- Incluir gráficos interativos (ex: distribuição por UF, faixa de renda e métricas do modelo ML).

## Execução
- [x] **Passo 1:** Instalar dependências necessárias (`streamlit`, `pandas`, `plotly`).
- [x] **Passo 2:** Criar o script `src/app/dashboard.py` contendo abas/filtros para análise demográfica e resultados do modelo.
- [x] **Passo 3:** Validar a execução rodando `streamlit run src/app/dashboard.py`.