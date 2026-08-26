# 🎓 ENEM 2025 — Analytics & AI Dashboard (PI4 Univesp)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/PySpark-4.2.0-orange.svg)](https://spark.apache.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.62.0-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Projeto desenvolvido para a disciplina de **Projeto Integrador IV (PI4)** do curso de Engenharia da UNIVESP. Trata-se de uma solução completa de **Engenharia de Dados**, **Ciência de Dados** e **Desenvolvimento Web** voltada ao processamento, enriquecimento e visualização analítica dos **Microdados do ENEM 2025** do INEP.

---

## 📌 Visão Geral e Escopo

O objetivo principal do projeto é extrair *insights* valiosos sobre a educação brasileira a partir do cruzamento de dados demográficos, socioeconômicos e notas de desempenho do exame nacional (TRI).

A aplicação conta com:
- **Pipeline de Big Data (PySpark):** Processamento eficiente de milhões de registros em formato colunar Parquet.
- **Extração Automática de Dicionário:** Leitura inteligente do dicionário oficial em Excel (`Dicionário_Microdados_Enem_2025.xlsx`) para mapeamento automático de rótulos legíveis.
- **Modelo de Machine Learning:** Classificador preditivo para análise do perfil de **Treineiros** vs. **Concorrentes Regulares**.
- **Dashboard Web Interativo (Streamlit & Plotly):** Painel executivo com filtros geográficos (UF), perfil socioeconômico e médias de desempenho por área de conhecimento (Redação, Matemática, Linguagens, Humanas e Natureza).

---

## 🛠️ Pilha Tecnológica (Tech Stack)

| Componente | Tecnologia | Função |
| :--- | :--- | :--- |
| **Linguagem Principal** | Python 3.10+ | Desenvolvimento geral de scripts e pipeline |
| **Big Data & Processamento** | PySpark 4.2 | Ingestão, tratamento, Join de tabelas e agregações |
| **Armazenamento Otimizado** | Apache Parquet / PyArrow | Leitura e gravação eficiente em disco |
| **Manipulação & Dicionários** | Pandas / OpenPyXL | Parseamento de tabelas Excel e dicionários JSON |
| **Machine Learning** | Scikit-Learn / PySpark ML | Modelagem preditiva e métricas de acurácia |
| **Visualização Interativa** | Plotly Express | Gráficos dinâmicos e responsivos |
| **Interface Web** | Streamlit | Dashboard interativo e apresentação executiva |

---

## 📂 Arquitetura do Repositório

```text
my-data-project/
├── data/
│   ├── raw/                       # Arquivos brutos CSV e Excel originais do INEP (git-ignored)
│   │   ├── Dicionário_Microdados_Enem_2025.xlsx
│   │   ├── PARTICIPANTES_2025.csv
│   │   └── RESULTADOS_2025.csv
│   ├── processed/                 # Bases tratadas e agregadas em formato Parquet
│   │   ├── enem_2025_cleaned_parquet/
│   │   ├── enem_2025_enriched_parquet/
│   │   ├── enem_2025_agg_notas_uf_parquet/
│   │   └── enem_2025_ml_insights.json
│   └── dictionary/                # Mapeamento leve JSON extraído do Excel
│       └── enem_2025_dict.json
├── src/
│   ├── data_pipeline/             # Scripts do Pipeline de Engenharia de Dados
│   │   ├── ingest.py              # Ingestão de CSV para Parquet
│   │   ├── clean.py               # Limpeza de nulos e trim de textos
│   │   ├── transform.py           # Join de tabelas e geração de visões agregadas
│   │   ├── extract_dictionary.py  # Extrator de dicionários Excel para JSON
│   │   └── report_or_ml.py        # Modelo de Machine Learning & métricas
│   └── app/
│       └── dashboard.py           # Aplicação Web Streamlit
├── requirements.txt               # Dependências do projeto
├── TASK.md                        # Plano mestre de tarefas e fases do projeto
└── README.md                      # Documentação principal do repositório
```

---

## 🚀 Guia Prático de Instalação e Execução

Siga os passos abaixo para clonar o projeto e executá-lo em uma nova máquina.

### 1. Pré-requisitos
Certifique-se de ter instalado em sua máquina:
- **Python 3.10 ou superior**: [Download Python](https://www.python.org/downloads/)
- **Java OpenJDK 8, 11 ou 17** (necessário para a execução do PySpark):
  - *No Ubuntu/Debian:* `sudo apt update && sudo apt install default-jdk`
  - *No Windows/Mac:* Instale o OpenJDK ou Oracle JDK e defina a variável `JAVA_HOME`.

### 2. Clonar o Repositório
```bash
git clone https://github.com/reifer/pi4_Univesp.git
cd my-data-project
```

### 3. Criar e Ativar o Ambiente Virtual (`.venv`)
- **No Linux/macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **No Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

### 4. Instalar as Dependências
Com o ambiente virtual ativado, instale todas as bibliotecas necessárias:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ⚙️ Executando o Pipeline de Dados

Os scripts da pasta `src/data_pipeline/` devem ser executados na ordem abaixo para processar os dados brutos e gerar os artefatos consumidos pelo Dashboard.

> **Nota:** Certifique-se de colocar os arquivos brutos do ENEM 2025 na pasta `data/raw/` (`PARTICIPANTES_2025.csv`, `RESULTADOS_2025.csv` e `Dicionário_Microdados_Enem_2025.xlsx`).

**Base de dados do ENEM 2025:** [Dados do ENEM 2025](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)


1. **Ingestão dos dados CSV para Parquet:**
   ```bash
   python src/data_pipeline/ingest.py
   ```
2. **Limpeza e padronização dos dados:**
   ```bash
   python src/data_pipeline/clean.py
   ```
3. **Unificação (Join) e Agregação por UF e Renda:**
   ```bash
   python src/data_pipeline/transform.py
   ```
4. **Extração do Dicionário de Dados para JSON:**
   ```bash
   python src/data_pipeline/extract_dictionary.py
   ```
5. **Treinamento do Modelo de Machine Learning:**
   ```bash
   python src/data_pipeline/report_or_ml.py
   ```

---

## 🖥️ Inicializando o Dashboard Streamlit

Após a execução do pipeline (ou com as bases Parquet pré-existentes na pasta `data/processed/`), inicie a interface web:

```bash
streamlit run src/app/dashboard.py
```

O terminal exibirá o endereço local de acesso:
```text
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

Acesse `http://localhost:8501` no navegador para interagir com o dashboard!

---

## 📊 Abas do Dashboard

1. **📊 Panorama Geográfico (UF):** Distribuição de participantes por Estado, gênero e proporção de treineiros.
2. **💰 Perfil Socioeconômico:** Análise de vulnerabilidade e distribuição por faixa de renda familiar (`Q006` / `Q007`).
3. **📈 Desempenho & Notas (TRI):** Comparativo de notas médias nas provas objetivas e Redação por UF e Renda.
4. **🤖 Machine Learning & IA:** Performance e indicadores do modelo preditivo de treineiros.

---

## 📄 Licença e Autoria
Projeto acadêmico desenvolvido para a **UNIVESP (Universidade Virtual do Estado de São Paulo)** — Projeto Integrador IV (PI4).