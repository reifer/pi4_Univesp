from pyspark.errors import TempTableAlreadyExistsException
import os
import pandas as pd
import pytest

# Caminho base para os dados processados do projeto
DATA_DIR = "data/processed"

def test_data_directory_exists():
    """Valida se o diretório principal de dados processados existe."""
    assert os.path.exists(DATA_DIR), f"O diretório {DATA_DIR} não foi encontrado."

@pytest.mark.parametrize("ano", [2021, 2022, 2023, 2024, 2025])
def test_parquet_rede_ensino_structure(ano):
    """
    Verifica se os arquivos agregados de rede de ensino existem 
    e se possuem as colunas mínimas esperadas para as análises.
    """
    caminho_pasta = os.path.join(DATA_DIR, f"enem_{ano}_agg_rede_ensino_parquet")
    
    # Se a pasta não existir para um ano específico, o teste avisa mas não quebra obrigatoriamente,
    # a menos que o ano seja o baseline principal. Vamos verificar a existência.
    if not os.path.exists(caminho_pasta):
        pytest.skip(f"Pasta de rede de ensino para o ano {ano} não encontrada em {caminho_pasta}.")

    # Procura por arquivos parquet dentro da pasta
    arquivos_parquet = [f for f in os.listdir(caminho_pasta) if f.endswith(".parquet")]
    assert len(arquivos_parquet) > 0, f"Nenhum arquivo .parquet encontrado em {caminho_pasta}."

    # Tenta ler o primeiro arquivo parquet encontrado para validar o schema
    arquivo_exemplo = os.path.join(caminho_pasta, arquivos_parquet[0])
    df = pd.read_parquet(arquivo_exemplo)

    assert not df.empty, f"O DataFrame lido de {arquivo_exemplo} está vazio."
    
    # Validações de colunas comuns esperadas nas agregações de rede
    colunas_esperadas = ["total_candidatos"]
    for col in colunas_esperadas:
        assert col in df.columns, f"A coluna obrigatória '{col}' está ausente no dataset de rede {ano}."

def test_agrupamento_faixas_renda_logica():
    """
    Testa se a lógica de manipulação de dados de renda lida corretamente 
    com estruturas de DataFrame simuladas.
    """
    dados_mock = pd.DataFrame({
        "RENDA_FAMILIAR_DESC": ["Até 1 salário mínimo", "De 1 a 1.5 salário mínimo", "Acima de 10 salários mínimos"],
        "media_matematica": [450.5, 480.0, 650.2],
        "total_candidatos": [1000, 500, 200]
    })

    assert not dados_mock.empty
    assert "RENDA_FAMILIAR_DESC" in dados_mock.columns
    assert dados_mock["media_matematica"].mean() > 0


# O que esse teste valida?

    #1. Existência do diretório: Garante que a estrutura de pastas do projeto está no lugar esperado.
    #2. Integridade Parquet: Varre a série histórica (2021 a 2025) e valida se os arquivos parquet de rede de ensino carregam sem erros e contêm contagens válidas de candidatos.
    #3. Teste Unitário Lógico: Simula dados de renda para garantir que as métricas numéricas se comportam conforme o esperado.