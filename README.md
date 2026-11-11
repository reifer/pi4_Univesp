# ENEM Analytics & AI — Projeto Integrador IV (UNIVESP)

## Sobre o projeto

O ENEM Analytics & AI é um dashboard interativo para explorar os microdados do Exame Nacional do Ensino Médio (ENEM), divulgados pelo INEP, entre 2021 e 2025. O projeto organiza indicadores de participação, desempenho e perfil socioeconômico em módulos analíticos, com o objetivo de apoiar gestores, pesquisadores e demais interessados na análise da série histórica.

A aplicação combina processamento distribuído com PySpark, armazenamento de dados em Apache Parquet, análises em Pandas, um modelo de referência de Machine Learning e visualizações em Streamlit e Plotly.

## Arquitetura e engenharia de dados

O pipeline processa os dados separadamente por ano:

1. **Ingestão dos arquivos brutos**
   - Para 2021–2023, o pipeline lê um CSV único por ano (`MICRODADOS_ENEM_{ano}.csv`).
   - Para 2024–2025, lê os arquivos de participantes e resultados em separado. O código associa os registros por índices sequenciais gerados separadamente no Spark e seleciona campos para formar uma base padronizada.
2. **Padronização e transformação**
   - Os dados são gravados em Parquet e enriquecidos com dimensões como ano, UF e descrições categóricas.
   - O pipeline gera agregações por tema, entre elas notas por UF, notas por renda, rede de ensino, demografia, renda por raça/cor e perfil socioeconômico por escola.
   - Nas agregações de notas, são armazenados somatórios e contagens para recompor médias ponderadas sem calcular uma média simples das médias.
   - As gravações das agregações configuram compressão Zstandard.
3. **Consumo pelo dashboard**
   - O carregador lê apenas os agregados dos anos selecionados, concatena-os em Pandas e mantém os dados em cache.
   - Os filtros de ano, UF e tipo de candidato são aplicados às agregações usadas pelos módulos analíticos.

### Observação sobre a associação dos arquivos de 2024–2025

O vínculo entre participantes e resultados é feito por índices sequenciais gerados separadamente para cada arquivo, não por uma chave explícita de inscrição. A associação, portanto, pressupõe que os registros mantenham ordenação compatível nos arquivos de origem. Essa premissa deve ser verificada em relação aos dados oficiais antes de interpretar o vínculo como garantia de correspondência individual.

### Etapas do pipeline

O ponto de entrada do fluxo é `src/data_pipeline/ingest_all.py`. Ele executa a ingestão, aciona a transformação e, em seguida, a geração dos insights de Machine Learning por subprocessos. O processo é interrompido se uma dessas etapas falhar.

A rotina `src/data_pipeline/clean.py` existe separadamente, mas não é chamada pelo orquestrador plurianual atual. Assim, as operações de limpeza descritas nesse arquivo não são apresentadas como etapa efetivamente executada no fluxo completo.

## Módulo de Machine Learning

O projeto inclui um modelo de referência de classificação baseado em **Regressão Logística do PySpark ML**, com `IN_TREINEIRO` como variável-alvo. O treinamento usa uma amostra de 10% dos dados de 2025, dividida em conjuntos de treino e teste na proporção de 80/20, com semente fixa.

As variáveis preditoras incluem faixa etária, sexo, raça/cor, situação de conclusão do Ensino Médio e variáveis socioeconômicas. As métricas são calculadas no conjunto de teste e registradas em `data/processed/enem_2025_ml_insights.json`.

O artefato de insights presente no workspace registra:

| Métrica | Valor registrado |
|---|---:|
| Acurácia | 0,9817 (~98,17%) |
| ROC AUC | 0,9821 |
| PR AUC | 0,8269 |
| F1-Score | 0,9820 |

Esses valores descrevem o artefato de referência de 2025; não são métricas recalculadas para cada ano ou para toda a série histórica. O dashboard informa essa limitação quando a seleção inclui outros anos. O fluxo gera um relatório JSON com métricas e informações resumidas; não há evidência de persistência de um modelo treinado para inferência em produção. O gráfico de importância de variáveis só é exibido caso o JSON contenha esse campo; ele não está presente no artefato atual.

## Interface e módulos analíticos

A interface é construída em Streamlit, com gráficos interativos em Plotly. A navegação entre módulos é feita por `st.pills` no corpo principal da página. Os filtros globais permitem selecionar anos, UFs ou regiões e tipos de candidato.

- **Panorama Geográfico:** distribuição de inscritos por UF e distribuição por sexo.
- **Perfil Socioeconômico:** distribuição dos candidatos por faixa de renda familiar.
- **Redes de Ensino:** volumetria e desempenho por dependência administrativa, com recortes por ano, UF e tipo de candidato.
- **Desempenho TRI:** médias das notas por área e UF, calculadas a partir de somatórios e contagens.
- **Machine Learning:** métricas do modelo de referência e aviso de contexto quando o recorte selecionado não corresponde ao ano do modelo.
- **Geopolítica:** comparativos de desempenho por macrorregião e evolução temporal. O módulo apresenta gráficos regionais e séries históricas; não é um mapa temático.
- **Conclusão Estratégica:** síntese analítica com subseções sobre rede de ensino, renda, raça/cor, trabalho, demografia e visão consolidada.

## Stack tecnológica

## Stack tecnológica

| Área | Tecnologias e componentes |
|---|---|
| Linguagem | Python |
| Processamento de dados | PySpark e Spark SQL |
| Machine Learning | PySpark ML |
| Análise e leitura de dados | Pandas e PyArrow |
| Armazenamento processado | Apache Parquet; compressão Zstandard configurada para as agregações |
| Dashboard e Nuvem | **Streamlit** (desenvolvimento da interface) e **Streamlit Community Cloud** (hospedagem e provisionamento em nuvem) |
| Visualização | Plotly Express e Plotly Graph Objects |
| Testes | Pytest |
| Análise estática | Pyright |
| Dependência de sistema para Spark | Java, declarada em `packages.txt` |
| Containerização | Dockerfile baseado em imagem Python slim |

## Testes e qualidade de software

A suíte contém **53 casos de teste**, que cobrem, entre outros aspectos:

- dimensões, contagens e médias ponderadas das agregações Parquet;
- cálculo e filtragem de dados no carregador;
- estado dos filtros e renderização dos módulos do dashboard;
- estrutura dos artefatos JSON de Machine Learning.

Na execução auditada no workspace, **53 testes passaram**. Para executar a suíte:

```bash
python -m pytest -q
```

O Pyright está configurado para analisar `src/`, com a versão de linguagem definida em `pyrightconfig.json`. Na auditoria do workspace, a execução reportou **66 erros de tipagem**. Portanto, a verificação estática está configurada, mas o código não deve ser descrito como livre de erros Pyright até que os diagnósticos sejam resolvidos.

O workflow disponível em `.github/workflows/ci_cd.yml` instala dependências, mas não executa Pytest nem Pyright. Os resultados de testes acima correspondem à execução local auditada, não a uma validação automatizada demonstrada pelo workflow. Pytest e Pyright também não estão listados em `requirements.txt`.

## Como executar

### Pré-requisitos

- Python compatível com as dependências do projeto;
- Java para executar as etapas PySpark;
- dados brutos disponíveis em `data/raw/` com os nomes esperados pelo pipeline.

As configurações atuais divergem quanto à versão Python: `pyrightconfig.json` indica 3.12, o Dockerfile usa Python 3.11 e o workflow do GitHub Actions configura Python 3.14. Recomenda-se harmonizar essas versões antes de declarar uma versão única oficialmente suportada.

### Preparar o ambiente local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Pytest e Pyright são ferramentas de desenvolvimento e não estão listados em `requirements.txt`. Instale-os no ambiente, se ainda não estiverem disponíveis:

```bash
pip install pytest pyright
```

### Executar o pipeline

Com os arquivos brutos presentes em `data/raw/`:

```bash
python src/data_pipeline/ingest_all.py
```

O pipeline grava dados intermediários e agregações em `data/processed/`. A execução completa requer recursos compatíveis com o processamento dos microdados via Spark.

### Iniciar o dashboard

Com os agregados necessários já gerados:

```bash
streamlit run src/app/dashboard.py
```

### Executar testes e análise estática

```bash
python -m pytest -q
python -m pyright
```

## Docker, Streamlit Community Cloud e execução em nuvem

O projeto utiliza o ecossistema **Streamlit** de ponta a ponta para a entrega do produto:
- **Streamlit Community Cloud:** Plataforma oficial utilizada para o provisionamento, hospedagem e acesso público do painel interativo na nuvem.
- **Docker:** O `Dockerfile` oferece uma alternativa containerizada para execução local ou implantação em outras plataformas de nuvem compatíveis, instalando Java e as dependências Python, copiando o projeto para a imagem e configurando o Streamlit para escutar na porta `8501`.

Para construir e iniciar o container localmente:

```bash
docker build -t enem-analytics .
docker run --rm -p 8501:8501 enem-analytics
```

O Dockerfile oferece uma alternativa de execução em container e pode servir de base para implantação em uma plataforma de nuvem compatível com Docker. Isso, por si só, não comprova que exista um deploy ativo. O workspace não contém configuração ou evidência suficiente para afirmar que o aplicativo esteja implantado no Streamlit Cloud ou em outro serviço de nuvem.
