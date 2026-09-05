                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        # ENEM Analytics & AI — Dashboard Plurianual (PI4 Univesp)

## Visão Geral do Projeto

Este projeto é um **dashboard analítico interativo** para exploração dos microdados do ENEM ao longo de uma série histórica plurianual (2021–2025). A aplicação combina um pipeline de dados em **PySpark** (ingestão, limpeza, enriquecimento e agregações) com uma camada de **Machine Learning** para identificação de perfil de treineiros, e uma interface web construída em **Streamlit** com visualizações interativas em **Plotly**.

A arquitetura é composta por três camadas independentes, coordenadas por um orquestrador mestre:

1. **Pipeline de Dados** (`src/data_pipeline/`): o orquestrador mestre (`ingest_all.py`) controla a execução ponta a ponta, em etapas isoladas e sequenciais, da ingestão, limpeza, transformação e agregação dos microdados brutos em arquivos Parquet otimizados, processados via PySpark.
2. **Dashboard Streamlit** (`src/app/`): camada de visualização, escrita em Pandas/Plotly, que consome os Parquets processados. O layout foi totalmente migrado para **containers nativos do Streamlit** (`st.container(border=True)`), garantindo consistência visual sem depender de HTML/CSS customizado para agrupamento de conteúdo.
3. **Modelos de ML** (`src/data_pipeline/report_or_ml.py`): treinamento de um classificador (Regressão Logística via PySpark ML) e exportação de métricas/insights em JSON (`data/processed/enem_*_ml_insights.json`), consumidos pela aba de Machine Learning do dashboard.

O `ingest_all.py` funciona exclusivamente como controlador/dispatcher: executa a ingestão e limpeza, aguarda seu sucesso, aciona `transform.py`, aguarda novamente e então aciona `report_or_ml.py`. As fases posteriores são executadas por subprocessos com validação de status (`check=True`), reduzindo o risco de estouro de memória e interrompendo o fluxo imediatamente em caso de falha. O encerramento de cada etapa e do pipeline completo é sinalizado com status `[OK]` ou `[NOK]`.

O projeto também conta com uma **suíte de testes automatizados (Pytest)**, cobrindo pipeline de dados, artefatos de ML e a importabilidade das views do dashboard, e é **verificado estaticamente com Pyright** para tipagem, sem depender de containers Docker em tempo de execução (execução via interpretador Python local/`.venv`).

---

## Tratativa de Dados Plurianuais (2021–2025)

O pipeline resolve as mudanças de formato do INEP ao longo dos anos:

- **2021 a 2023 (Arquivo Único):** Microdados lidos de `MICRODADOS_ENEM_{ano}.csv`. Schema padronizado e salvo em Parquet.
- **2024 a 2025 (Arquivos Fragmentados):** O INEP dividiu os dados em `PARTICIPANTES_{ano}.csv` e `RESULTADOS_{ano}.csv`. O pipeline realiza o *join* por índice sequencial, reconstrói a base completa e padroniza o schema longitudinal.

---

## Stack Tecnológica

| Categoria | Tecnologias |
|---|---|
| **Linguagem / Ambiente** | Python 3.12+, ambiente virtual (`.venv`) |
| **Processamento de Dados** | PySpark (Spark SQL, Spark ML), Pandas, PyArrow |
| **Machine Learning** | PySpark ML (`StringIndexer`, `VectorAssembler`, `LogisticRegression`, avaliadores binário/multiclasse) |
| **Dashboard Web** | Streamlit, com layout nativo via `st.container(border=True)` e `st.expander` |
| **Visualização de Dados** | Plotly Express & Plotly Graph Objects |
| **Formato de Dados** | Apache Parquet (armazenamento colunar dos dados processados) |
| **Testes Automatizados** | Pytest |
| **Tipagem Estática** | Pyright (configurado em `pyrightconfig.json`) |
| **Infraestrutura** | Execução local via interpretador Python/`.venv` (sem Docker em runtime) |

---

## Estrutura de Diretórios

```text
my-data-project/
├── data/
│   ├── dictionary/                        # Dicionários JSON dos microdados (enem_{ano}_dict.json)
│   ├── raw/                               # Dados brutos CSV baixados do INEP
│   └── processed/                         # Agregados Parquet gerados pelo pipeline
│       ├── enem_{ano}_cleaned_parquet/
│       ├── enem_{ano}_enriched_parquet/
│       ├── enem_{ano}_agg_notas_uf_parquet/
│       ├── enem_{ano}_agg_notas_renda_parquet/
│       ├── enem_{ano}_agg_rede_ensino_parquet/
│       ├── enem_{ano}_agg_socio_escola_parquet/
│       ├── enem_{ano}_agg_demografia_parquet/
│       ├── enem_{ano}_agg_renda_raca_parquet/
│       └── enem_{ano}_ml_insights.json
├── notebooks/                              # Notebooks Jupyter para exploração exploratória
├── src/
│   ├── app/                                # Dashboard Streamlit
│   │   ├── dashboard.py                    # Ponto de entrada principal (streamlit run)
│   │   ├── config/
│   │   │   └── settings.py                 # Paleta de cores, CSS global e apply_custom_css()
│   │   ├── components/                     # Módulos de visualização por tema
│   │   │   ├── desempenho_view.py
│   │   │   ├── geo_view.py
│   │   │   ├── geopolitica_view.py
│   │   │   ├── ml_view.py
│   │   │   ├── rede_view.py
│   │   │   └── socio_view.py
│   │   ├── pages/
│   │   │   ├── conclusao_estrategica.py    # Orquestrador da aba de conclusão
│   │   │   └── conclusao_modules/          # Módulos da análise estratégica
│   │   │       ├── rede_estrategica.py
│   │   │       ├── renda_estrategica.py
│   │   │       ├── raca_estrategica.py
│   │   │       ├── trabalho_estrategica.py
│   │   │       ├── demografia_estrategica.py
│   │   │       └── sintese_estrategica.py
│   │   └── utils/
│   │       └── data_loader.py              # Carregamento cacheado (st.cache_data) de todos os Parquets
│   └── data_pipeline/                      # Pipeline de ingestão e transformação (PySpark)
│       ├── ingest_all.py                   # Orquestrador mestre/dispatcher do pipeline completo via subprocessos
│       ├── downloader.py                   # Download e indexação sequencial dos CSVs do INEP
│       ├── parser.py                       # Leitura e padronização dos CSVs brutos
│       ├── clean.py                        # Limpeza e tratamento de nulos
│       ├── transform.py                    # Geração dos agregados por tema
│       ├── extract_dictionary.py           # Geração do dicionário JSON de variáveis
│       └── report_or_ml.py                 # Treinamento do modelo preditivo e export JSON
├── tests/                                  # Suíte de testes automatizados (Pytest)
│   ├── test_data_pipeline.py               # Valida estrutura e integridade dos Parquets processados
│   ├── test_ml.py                          # Valida artefatos e métricas de Machine Learning
│   └── test_views.py                       # Valida importabilidade das views do dashboard
├── .streamlit/
│   └── config.toml                         # Tema e configurações do servidor Streamlit
├── .vscode/
│   └── settings.json                       # Intérprete, perfil de terminal e excludes do explorer
├── pyrightconfig.json                      # Configuração do verificador de tipos estático Pyright
├── requirements.txt                        # Dependências Python do projeto
├── packages.txt                            # Dependências de sistema (ex: Java, para PySpark)
├── TASK.md                                 # Plano mestre de tarefas do projeto
└── README.md                               # Documentação principal
```

> Diretórios virtuais/temporários (`.venv/`, `venv/`, `__pycache__/`, `.pytest_cache/`, `.git/`, `data/tmp_spill/`) foram omitidos da árvore acima por não fazerem parte da arquitetura lógica do projeto.

---

## Pré-requisitos e Configuração

Você precisará de **Python 3.12+** instalado no sistema. O **Java** é necessário apenas para executar o pipeline PySpark (veja `packages.txt`). Não há dependência de Docker: toda a stack roda diretamente via interpretador Python local.

### 1. Acesse o diretório do projeto

```bash
cd my-data-project
```

### 2. Crie e ative um ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> **Nota:** O arquivo `.vscode/settings.json` já está configurado para ativar automaticamente o `.venv` em terminais integrados do VS Code.

### 3. Instale as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Guia de Execução

### Etapa 1 — Executar o Pipeline Completo

Antes de iniciar o dashboard, certifique-se de que os dados brutos estão em `data/raw/` com a nomenclatura correta (ex: `MICRODADOS_ENEM_2021.csv`, `PARTICIPANTES_2024.csv`, `RESULTADOS_2024.csv`).

Todo o pipeline plurianual (2021–2025) é executado de ponta a ponta por um único comando centralizado. O orquestrador processa sequencialmente:

1. a ingestão e limpeza, cobrindo os anos legados de 2021–2023 e a unificação dos arquivos fragmentados de 2024–2025;
2. a transformação e geração das agregações em `transform.py`;
3. a geração do relatório e dos artefatos de Machine Learning em `report_or_ml.py`.

Cada subprocesso precisa retornar com sucesso antes que a próxima fase seja iniciada. Em caso de falha, o orquestrador encerra o fluxo com uma mensagem crítica `[NOK]`; ao final, informa o status completo `[OK]`.

Para executar:

```bash
# Com o ambiente virtual ativado:
python3 src/data_pipeline/ingest_all.py
```

O uso de fases isoladas e subprocessos controlados permite liberar recursos entre as etapas e reduzir o risco de estouro de RAM. Os arquivos agregados Parquet e os insights de ML serão gerados em `data/processed/`.

### Etapa 2 — Iniciar o Dashboard

```bash
streamlit run src/app/dashboard.py
```

O dashboard será aberto automaticamente no navegador padrão em `http://localhost:8501`.

---

## Suíte de Testes Automatizados (Pytest)

O projeto conta com uma suíte de **13 testes automatizados** organizados em três módulos dentro de `tests/`, cobrindo os três pilares da aplicação:

| Arquivo | Cobertura |
|---|---|
| `tests/test_data_pipeline.py` | Existência do diretório de dados processados e integridade estrutural dos Parquets de rede de ensino para cada ano (2021–2025), além da lógica de agrupamento de faixas de renda. |
| `tests/test_ml.py` | Existência dos artefatos/diretórios de Machine Learning e validação estrutural do JSON de insights (`enem_*_ml_insights.json`), incluindo ranges lógicos de métricas (acurácia, AUC, F1-Score). |
| `tests/test_views.py` | Importabilidade sem erros de todos os módulos de visualização (`src/app/components/`) e dos módulos estratégicos de conclusão (`src/app/pages/conclusao_modules/`). |

### Como executar os testes

Com o ambiente virtual ativado e as dependências instaladas:

```bash
python -m pytest tests/ -v
```

Resultado esperado: **13 passed** (100% de sucesso).

Para checar a tipagem estática do código-fonte (Pyright), rode:

```bash
python -m pyright
```

---

## Módulos do Dashboard

| Módulo | Descrição |
|---|---|
| 📊 Panorama Geográfico | Distribuição de inscritos por UF e gênero |
| 💰 Perfil Socioeconômico | Distribuição por faixa de renda familiar (Q006) |
| 🏫 Redes de Ensino | Desempenho e volumetria por dependência administrativa |
| 📈 Desempenho TRI | Notas médias por área de conhecimento e UF |
| 🤖 Machine Learning | Métricas do modelo preditivo e features importantes |
| 🌎 Geopolítica | Séries temporais e comparativo por macrorregião |
| 🎓 Conclusão Estratégica | Análise qualitativa plurianual com 6 subseções temáticas (rede, renda, raça, trabalho, demografia e síntese) |

---

## Notas de Qualidade e Tipagem

- Todo o código sob `src/` é verificado com **Pyright** (`pyrightconfig.json`), com **zero erros estáticos** reportados na configuração atual.
- Nos pontos em que os stubs de tipagem do Pandas resolvem incorretamente encadeamentos de `groupby(...).sum()/mean().reset_index()` ou `Series.isin()/value_counts()` sobre colunas dinamicamente selecionadas (limitação conhecida dos stubs, não um erro de lógica), o código utiliza comentários `# type: ignore[...]` pontuais, mantendo o tratamento defensivo de colunas/DataFrames opcionais (`if not df.empty and "coluna" in df.columns`) já existente em todas as views.
