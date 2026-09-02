# Análise de Microdados do ENEM (Série Histórica 2021–2025)

## Visão Geral da Arquitetura

Este é um projeto de Engenharia de Dados em **PySpark** focado no processamento e análise da série histórica de microdados do ENEM (2021 a 2025). 

Recentemente, a arquitetura de ingestão foi centralizada e otimizada. Todo o fluxo de processamento — leitura de dados brutos, padronização, cruzamento de dados fragmentados e exportação final — é coordenado por um único script unificado. Os dados processados são salvos em formato colunar (Parquet) na camada de dados limpos, garantindo performance e escalabilidade nas análises futuras.

## Tratativa de Dados Plurianuais (2021–2025)

O pipeline resolve de forma transparente as mudanças de formato impostas pelo INEP ao longo dos anos:

- **2021 a 2023 (Arquivos Únicos):**
  Os microdados são lidos de um arquivo CSV anual único (`MICRODADOS_ENEM_{ano}.csv`). O schema é padronizado e os dados são salvos diretamente em Parquet.
  
- **2024 a 2025 (Arquivos Fragmentados):**
  Nesses anos, o INEP dividiu os dados em `PARTICIPANTES_{ano}.csv` e `RESULTADOS_{ano}.csv`. O script faz o cruzamento (Join) dessas duas bases de forma cirúrgica utilizando índices sequenciais, reconstrói a base completa do aluno e padroniza as colunas de acordo com o mesmo schema histórico, garantindo consistência longitudinal.

## Estrutura de Diretórios

```text
my-data-project/
├── data/
│   ├── raw/                  # Diretório de dados brutos (CSV) baixados do INEP
│   └── processed/            # Diretório de dados processados unificados (Parquet)
├── notebooks/                # Notebooks Jupyter para análise e exploração de dados
├── src/
│   └── data_pipeline/
│       └── ingest_all.py     # Script mestre unificado de ingestão de todo o período
├── tests/                    # Testes unitários do pipeline
├── Dockerfile                # Configuração para containerização do ambiente
├── requirements.txt          # Dependências Python do projeto
└── README.md                 # Documentação principal
```

## Pré-requisitos e Configuração

Para executar este projeto, você precisará do **Python 3** e do **Java** instalado no sistema (requisito do PySpark). 

Siga os passos abaixo para preparar o ambiente local:

1. **Clone o repositório e acesse o diretório do projeto:**
   ```bash
   cd my-data-project
   ```

2. **Crie e ative um ambiente virtual (venv):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows, use: venv\Scripts\activate
   ```

3. **Instale as dependências do projeto:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Guia de Execução Passo a Passo

Antes de iniciar o pipeline, certifique-se de que os dados brutos estão posicionados corretamente na pasta `data/raw/` seguindo a nomenclatura dos anos correspondentes (ex: `MICRODADOS_ENEM_2021.csv`, `PARTICIPANTES_2024.csv`, `RESULTADOS_2024.csv`, etc).

Para rodar todo o fluxo de ingestão e processamento da série histórica (2021-2025), execute o script mestre na raiz do projeto:

```bash
# Com o ambiente virtual ativado:
python src/data_pipeline/ingest_all.py
```

O script fará a ingestão de todos os anos programados, informará o status no terminal, e depositará os resultados limpos em arquivos `parquet` dentro da pasta `data/processed/`, por exemplo:
- `data/processed/enem_2021_cleaned_parquet/`
- `data/processed/enem_2024_cleaned_parquet/`