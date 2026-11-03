import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app.utils.data_loader import (
    calc_weighted_mean,
    filter_aggregate_frame,
    load_data,
    weighted_group_summary,
)


def test_calc_weighted_mean_uses_valid_positive_weights():
    values = pd.Series([10.0, None, 30.0, 500.0])
    weights = pd.Series([1.0, 20.0, 3.0, 0.0])

    assert calc_weighted_mean(values, weights) == pytest.approx(25.0)


def test_calc_weighted_mean_returns_nan_when_no_valid_weight_exists():
    values = pd.Series([10.0, 20.0])
    weights = pd.Series([0.0, -1.0])

    assert np.isnan(calc_weighted_mean(values, weights))


def test_calc_weighted_mean_rejects_different_lengths():
    with pytest.raises(ValueError, match="same length"):
        calc_weighted_mean(pd.Series([1.0]), pd.Series([1.0, 2.0]))


def test_weighted_group_summary_reaggregates_exact_note_sums_and_counts():
    frame = pd.DataFrame(
        {
            "Regiao": ["Norte", "Norte", "Sul"],
            "total_candidatos": [100, 20, 50],
            "soma_notas_mt": [1000.0, 400.0, 1500.0],
            "total_notas_mt": [10, 2, 5],
        }
    )

    summary = weighted_group_summary(
        frame,
        ["Regiao"],
        {"media_mt": ("soma_notas_mt", "total_notas_mt")},
    )
    norte = summary.set_index("Regiao").loc["Norte"]

    assert norte["total_candidatos"] == 120
    assert norte["media_mt"] == pytest.approx(1400 / 12)


def test_filter_aggregate_frame_applies_year_uf_and_candidate_together():
    frame = pd.DataFrame(
        {
            "NU_ANO": [2021, 2021, 2024, 2024],
            "SG_UF_PROVA": ["SP", "RJ", "SP", "SP"],
            "IN_TREINEIRO": [1, 1, 0, 1],
            "IN_TREINEIRO_DESC": ["Treineiro", "Treineiro", "Não Treineiro", "Treineiro"],
        }
    )

    filtered = filter_aggregate_frame(frame, [2021, 2024], ["SP"], ["Treineiro"])

    assert filtered.index.tolist() == [0, 3]


@pytest.mark.parametrize(
    ("years", "expected_years"),
    [
        ((2021,), {2021}),
        ((2021, 2024), {2021, 2024}),
        ((2025, 2021, 2025), {2021, 2025}),
    ],
)
def test_load_data_reads_only_requested_years(years, expected_years):
    data = load_data(years)
    aggregate_names = (
        "df_notas_uf",
        "df_notas_renda",
        "df_rede",
        "df_socio_escola",
        "df_demografia",
        "df_renda_raca",
    )

    for aggregate_name in aggregate_names:
        frame = data[aggregate_name]
        assert not frame.empty
        assert set(frame["NU_ANO"].unique()) == expected_years
        assert {
            "SG_UF_PROVA",
            "IN_TREINEIRO",
            "IN_TREINEIRO_DESC",
            "total_candidatos",
        } <= set(frame.columns)


def test_load_data_rejects_empty_or_unsupported_year_selections():
    with pytest.raises(ValueError, match="pelo menos um ano"):
        load_data([])
    with pytest.raises(ValueError, match="não suportados"):
        load_data([2020])
