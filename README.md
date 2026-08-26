# Projeto Integrador IV (PI4 Univesp) - ENEM 2025 Analytics & AI 🎓

Bem-vindo ao repositório final do Projeto Integrador IV focado na análise massiva dos microdados do ENEM 2025 utilizando Big Data, Machine Learning e visualização de dados.

## 🎯 Objetivo
Automatizar a ingestão, limpeza, unificação e enriquecimento de bases gigantes de participantes e resultados do ENEM 2025. Fornecer ferramentas interativas de Data Analytics e um modelo preditivo para classificar treineiros com base no perfil sociodemográfico do aluno.

## 🛠 Tecnologias Utilizadas
- **Python 3.11+**: Linguagem base.
- **PySpark**: Engine de Big Data para processamento em larga escala (ingestão e transformações usando Parquet).
- **Streamlit**: Framework web para o dashboard interativo.
- **Plotly**: Geração de gráficos e visualizações modernas.
- **Pandas & JSON**: Manipulação do dicionário de dados local e consumo no front-end.
- **Docker**: Conteinerização da aplicação final.
- **GitHub Actions (CI/CD)**: Automação do fluxo de desenvolvimento (dev ➔ hom ➔ prd).

## 📂 Arquitetura do Projeto

Abaixo a representação atual e fiel da estrutura de arquivos essenciais deste repositório após as etapas de sanitização e conclusão:

```text
my-data-project/
├── .github/
│   └── workflows/
│       └── ci-cd.yml             # Automação de deploy (dev -> hom -> prd)
├── data/
│   ├── dictionary/               # Dicionário processado
│   │   └── enem_2025_dict.json
│   ├── processed/                # Datasets no formato Parquet (Lakehouse local) e outputs ML
│   │   ├── enem_2025_parquet/
│   │   ├── enem_2025_resultados_parquet/
│   │   ├── enem_2025_enriched_parquet/
│   │   └── enem_2025_ml_insights.json
│   └── raw/                      # Dados brutos originais (csv e xlsx)
│       ├── PARTICIPANTES_2025.csv
│       ├── RESULTADOS_2025.csv
│       └── Dicionário_Microdados_Enem_2025.xlsx
├── src/
│   ├── app/                      # Front-End
│   │   └── dashboard.py          # Aplicação Streamlit (Interface e Visualizações)
│   └── data_pipeline/            # Back-End (Big Data e ML)
│       ├── clean.py              # Script de higienização de colunas e limpeza de nulos
│       ├── extract_dictionary.py # Parser do arquivo Excel para JSON dinâmico
│       ├── ingest.py             # Script de Ingestão e conversão de CSV para Parquet
│       ├── report_or_ml.py       # Modelo de Machine Learning (treinamento e output)
│       └── transform.py          # Processamento pesado (Join, cruzamentos socioeconômicos)
├── Dockerfile                    # Arquivo de build do container
├── requirements.txt              # Bibliotecas necessárias do Python
├── TASK.md                       # Documentação mestre de governança e controle de fases (COFRE)
└── README.md                     # Documentação oficial e guia do projeto (Você está aqui)
```

## 🚀 Como Executar Localmente

### 1. Pré-Requisitos
Certifique-se de ter instalado:
- **Python 3.11**
- **Java (JRE/JDK 11+)** (obrigatório para o PySpark)
- **Docker** (apenas se for executar conteinerizado)

### 2. Configurando o Ambiente
Instale todas as bibliotecas necessárias presentes no `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Processamento de Dados (ETL)
Siga o fluxo sequencial do pipeline caso deseje processar novamente os dados da base local `data/raw`:

1. **Extração do Dicionário:**
```bash
python src/data_pipeline/extract_dictionary.py
```
2. **Ingestão (CSV para Parquet):**
```bash
python src/data_pipeline/ingest.py
```
3. **Limpeza e Transformação:**
```bash
python src/data_pipeline/clean.py
python src/data_pipeline/transform.py
```
4. **Machine Learning:**
```bash
python src/data_pipeline/report_or_ml.py
```

### 4. Iniciando o Dashboard Streamlit
Para visualizar o projeto e todas as integrações interativas de visualização, execute:
```bash
streamlit run src/app/dashboard.py
```
A aplicação abrirá no seu navegador no endereço: `http://localhost:8501`.

## 🐳 Execução via Docker (Fase 5.5)

Para subir rapidamente toda a plataforma em um container limpo e testar a entrega de homologação/produção localmente:

1. Gere a imagem:
```bash
docker build -t enem-dashboard-pi4 .
```

2. Execute o container:
```bash
docker run -p 8501:8501 enem-dashboard-pi4
```

## 📜 Metodologia COFRE & Governança

Todo este projeto seguiu a metodologia **COFRE** na sua concepção (Contexto, Objetivo, Formato, Regras e Execução), garantindo qualidade e reprodutibilidade nas entregas (acompanhe em `TASK.md`). As publicações seguem o fluxo contínuo restrito validado sob assinatura criptográfica CI/CD (`cicd@gaaj`).