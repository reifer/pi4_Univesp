# Plano Mestre de Tarefas — Projeto Integrador IV (PI4 Univesp)

> **Fonte Única da Verdade** para o acompanhamento do desenvolvimento do pipeline de dados, dicionários, inteligência artificial e dashboard do ENEM 2025.

---

## 📌 Status Geral do Projeto
- **Fase 1 (Ingestão & PySpark):** Concluída `[100%]`
- **Fase 2 (Dicionário de Dados):** Concluída `[100%]`
- **Fase 3 (Machine Learning):** Concluída `[100%]`
- **Fase 4 (Dashboard Streamlit):** Concluída `[100%]`
- **Fase 5 (Expansão & Séries Históricas):** Em planejamento `[0%]`

---

## 🚀 Fases de Desenvolvimento

### Fase 1 — Ingestão, Limpeza e Transformação de Dados (PySpark)
- [x] **Ingestão Sociodemográfica:** Ingerir `PARTICIPANTES_2025.csv` e converter para formato colunar Parquet (`src/data_pipeline/ingest.py`).
- [x] **Ingestão de Resultados (Notas):** Ingerir `RESULTADOS_2025.csv` e converter para Parquet (`src/data_pipeline/ingest.py`).
- [x] **Limpeza & Tratamento:** Aplicar `trim` em colunas string e tratamento de valores nulos em `TP_ENSINO` e questões socioeconômicas (`Q001` a `Q023`) (`src/data_pipeline/clean.py`).
- [x] **Unificação & Agregação (Join):** Realizar o cruzamento (*Join*) de grande porte entre `PARTICIPANTES` e `RESULTADOS` via PySpark e gerar agregações estatísticas por UF e Faixa de Renda (`src/data_pipeline/transform.py`).

### Fase 2 — Extração e Padronização do Dicionário de Dados
- [x] **Inspeção de Metadados:** Mapear tabelas de abas no arquivo Excel oficial `data/raw/Dicionário_Microdados_Enem_2025.xlsx`.
- [x] **Script de Extração Robusto:** Criar o script `src/data_pipeline/extract_dictionary.py` com tratamento de erros de leitura e suporte a múltiplas abas.
- [x] **Padronização de Tipos:** Garantir conversão de todos os códigos categóricos para `string` (evitando incompatibilidades Pandas/PySpark).
- [x] **Exportação do JSON:** Salvar dicionário estruturado leve (~16.8 KB, 57 variáveis) em `data/dictionary/enem_2025_dict.json` para consumo pelo Streamlit e pipeline.
- [x] **Enriquecimento via Pipeline PySpark:** Integrar `enem_2025_dict.json` no script `src/data_pipeline/transform.py` usando `create_map` para gerar 34 colunas descritivas legíveis (`*_DESC`) no Parquet enriquecido.

### Fase 3 — Modelagem Preditiva & Machine Learning
- [x] **Treinamento do Modelo:** Desenvolver o script `src/data_pipeline/report_or_ml.py` com modelo preditivo para identificação de perfil de **Treineiros** (`IN_TREINEIRO`).
- [x] **Avaliação de Desempenho:** Calcular métricas globais do modelo (Acurácia ~98,14%, ROC AUC, F1-Score).
- [x] **Relatório de Insights:** Exportar métricas estruturadas para `data/processed/enem_2025_ml_insights.json`.

### Fase 4 — Dashboard Web Interativo (Streamlit & Plotly)
- [x] **Interface Clean/Profissional:** Desenvolver o dashboard em `src/app/dashboard.py` com tema claro (*Clean Professional Analytics*) e suporte a sidebar responsiva.
- [x] **Filtros Globais Organizados:** Barra lateral interativa estruturada com componentes `st.expander` (Recorte Geográfico e Perfil do Candidato), mantendo intacta a lógica de filtragem original.
- [x] **Aba 1 (Panorama Geográfico):** Gráficos de barras por UF, percentual de treineiros e distribuição por sexo (`TP_SEXO_DESC`).
- [x] **Aba 2 (Perfil Socioeconômico & Demográfico):** Gráficos de distribuição por faixa de renda (`Q006_DESC`), cor/raça (`TP_COR_RACA_DESC`) e situação de conclusão (`TP_ST_CONCLUSAO_DESC`).
- [x] **Aba 3 (Desempenho & Notas TRI):** Métricas e gráficos comparativos de notas médias por UF e Renda com rótulos descritivos amigáveis.
- [x] **Aba 4 (Machine Learning & IA):** Gauges e cartões de métricas do modelo preditivo PySpark ML.
- [x] **Leitura Integrada de Colunas Descritivas:** Atualizar os seletores e gráficos do Streamlit para consumir diretamente as colunas enriquecidas (`_DESC`), garantindo amigabilidade visual sem comprometer as agregações.

### Fase 5 — Expansão Futura e Séries Históricas
- [ ] **Análise de Itens de Prova:** Processar o arquivo `ITENS_PROVA_2025.csv` para calcular taxas de acerto e nível de dificuldade por questão.
- [ ] **Séries Históricas:** Expandir a arquitetura do pipeline para suportar ingestão e comparação temporal com edições anteriores do ENEM (ex: 2022-2024).
- [ ] **Conteinerização & Deploy:** Criar `Dockerfile` e arquivos de configuração para deploy em nuvem (Render/AWS/GCP).