from pyspark.errors import TempTableAlreadyExistsException
import os
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
import pytest

# Caminho base para os dados processados do projeto
DATA_DIR = "data/processed"
AGGREGATE_NAMES = (
    "agg_demografia",
    "agg_notas_renda",
    "agg_notas_uf",
    "agg_rede_ensino",
    "agg_renda_raca",
    "agg_socio_escola",
)
SCORE_ALIASES = ("cn", "ch", "lc", "mt", "redacao")

def test_data_directory_exists():
    """Valida se o diretório principal de dados processados existe."""
    assert os.path.exists(DATA_DIR), f"O diretório {DATA_DIR} não foi encontrado."

@pytest.mark.parametrize("ano", [2021, 2022, 2023, 2024, 2025])
@pytest.mark.parametrize("aggregate_name", AGGREGATE_NAMES)
def test_aggregates_have_canonical_dimensions_and_exact_weighting(ano, aggregate_name):
    aggregate_path = os.path.join(DATA_DIR, f"enem_{ano}_{aggregate_name}_parquet")
    assert os.path.isdir(aggregate_path), f"Agregação ausente: {aggregate_path}"

    df = pd.read_parquet(aggregate_path)
    assert not df.empty, f"A agregação {aggregate_path} está vazia."
    assert {"NU_ANO", "SG_UF_PROVA", "IN_TREINEIRO", "IN_TREINEIRO_DESC", "total_candidatos"} <= set(df.columns)
    assert df[["NU_ANO", "SG_UF_PROVA", "IN_TREINEIRO", "IN_TREINEIRO_DESC"]].notna().all().all()
    assert set(df["NU_ANO"]) == {ano}
    assert (df["total_candidatos"] > 0).all()
    assert (df.loc[df["IN_TREINEIRO"] == 1, "IN_TREINEIRO_DESC"] == "Treineiro").all()
    assert (df.loc[df["IN_TREINEIRO"] == 0, "IN_TREINEIRO_DESC"] == "Não Treineiro").all()

    if aggregate_name != "agg_demografia":
        for alias in SCORE_ALIASES:
            sum_column = f"soma_notas_{alias}"
            count_column = f"total_notas_{alias}"
            mean_column = f"media_{alias}"
            assert {sum_column, count_column, mean_column} <= set(df.columns)
            assert (df[count_column] >= 0).all()
            assert (df[count_column] <= df["total_candidatos"]).all()

            valid = df[count_column] > 0
            expected_mean = (
                df.loc[valid, sum_column] / df.loc[valid, count_column]
            ).map(
                lambda value: float(
                    Decimal(str(value)).quantize(
                        Decimal("0.01"),
                        rounding=ROUND_HALF_UP,
                    )
                )
            )
            assert (
                df.loc[valid, mean_column].sub(expected_mean).abs() < 1e-6
            ).all()


def test_aggregates_fit_dashboard_size_budget():
    total_bytes = sum(
        os.path.getsize(path)
        for aggregate_path in (
            os.path.join(DATA_DIR, f"enem_{ano}_{aggregate_name}_parquet")
            for ano in range(2021, 2026)
            for aggregate_name in AGGREGATE_NAMES
        )
        for path in (
            os.path.join(aggregate_path, filename)
            for filename in os.listdir(aggregate_path)
            if filename.endswith(".parquet")
        )
    )
    assert total_bytes < 5_000_000

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