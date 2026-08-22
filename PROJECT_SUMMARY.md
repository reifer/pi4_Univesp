# Project Summary - Sistema de Análise e Machine Learning do ENEM (Projeto Integrador IV - PI4)

## 1. Visão Geral do Projeto
Este projeto consiste em um sistema completo de Engenharia de Dados, Ciência de Dados e Desenvolvimento Web voltado à análise dos Microdados do ENEM (edição de 2025). O objetivo é fornecer uma ferramenta analítica de alto nível para apresentação acadêmica, cruzando dados sociodemográficos, comportamentais e de desempenho.

## 2. Pilha Tecnológica (Tech Stack)
- **Linguagem:** Python
- **Processamento de Dados (Big Data):** PySpark
- **Manipulação e Análise:** Pandas, PyArrow
- **Machine Learning:** Scikit-Learn (Regressão Logística para classificação de perfil)
- **Interface Web / Dashboard:** Streamlit, Plotly (Estilo Dark / Glassmorphism)
- **Metodologia de Prompting:** Framework COFRE (Contexto, Objetivo, Formato, Regras, Execução)

## 3. Estrutura e Arquitetura Atual Concluída
O pipeline de ponta a ponta para a base sociodemográfica já está implementado e validado:
- **Ingestão (`src/data_pipeline/ingest.py`):** Converte os arquivos CSV brutos da pasta `DADOS/` (como participantes) em arquivos otimizados no formato Parquet armazenados em `data/processed/`.
- **Transformação (`src/data_pipeline/transform.py`):** Processa os dados limpos, tratando nulos e preparando as colunas analíticas.
- **Machine Learning / Relatório (`src/models/` ou scripts de ML):** Treinamento de modelo preditivo para identificar o perfil de **Treineiros** com alta acurácia (~98,14%).
- **Dashboard Web (`src/app/dashboard.py`):**
  - Servidor rodando localmente em `http://localhost:8501`.
  - Layout em Dark Mode com abas estruturadas:
    1. *Panorama Geográfico (UF):* Distribuição por estado, gênero e proporção de treineiros com título dinâmico com base nos filtros da barra lateral.
    2. *Perfil Socioeconômico:* Análise baseada na renda familiar (`Q006`).
    3. *Machine Learning & IA:* Métricas de performance do modelo (Acurácia, ROC AUC, F1-Score).
  - **Regra de Negócio Integrada:** Filtro lateral interativo (`st.sidebar.multiselect`) para alternar entre "Treineiros" e "Não Treineiros", acompanhado de nota explicativa de negócio definindo o papel dos treineiros (estudantes do 1º ou 2º ano que não concorrem a vagas/bolsas).

## 4. Próximos Passos (Imediatos)
Conforme definido no plano de ação `PIPELINE_ENRICHED_TASK.md`, os próximos passos consistem em:
1. Ingerir o arquivo de resultados (`RESULTADOS_2025.csv`).
2. Realizar o *Join* estruturado entre participantes e resultados no PySpark.
3. Adicionar novas abas no dashboard Streamlit focadas em correlação de notas vs. renda, tipo de escola e desempenho.
4. Processar métricas do arquivo de itens de prova (`ITENS_PROVA_2025.csv`).