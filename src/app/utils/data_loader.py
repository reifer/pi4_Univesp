import json
from pathlib import Path
from typing import TypedDict

import numpy as np
import pandas as pd
import streamlit as st


PROCESSED_DIR = Path("data/processed")
DICTIONARY_DIR = Path("data/dictionary")
SUPPORTED_YEARS = (2021, 2022, 2023, 2024, 2025)
AGGREGATE_NAMES = {
    "df_notas_uf": "agg_notas_uf",
    "df_notas_renda": "agg_notas_renda",
    "df_rede": "agg_rede_ensino",
    "df_socio_escola": "agg_socio_escola",
    "df_demografia": "agg_demografia",
    "df_renda_raca": "agg_renda_raca",
}


class DashboardData(TypedDict):
    df_notas_uf: pd.DataFrame
    df_notas_renda: pd.DataFrame
    df_rede: pd.DataFrame
    df_rede_plurianual: pd.DataFrame
    df_socio_escola: pd.DataFrame
    df_demografia: pd.DataFrame
    df_renda_raca: pd.DataFrame
    ml_insights: dict
    enem_dict: dict


def calc_weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    """Calcula média ponderada ignorando valores ausentes e pesos não positivos."""
    if len(values) != len(weights):
        raise ValueError("Values and weights must have the same length.")

    numeric_values = pd.to_numeric(values, errors="raise").to_numpy(dtype=float)
    numeric_weights = pd.to_numeric(weights, errors="raise").to_numpy(dtype=float)
    valid = (
        np.isfinite(numeric_values)
        & np.isfinite(numeric_weights)
        & (numeric_weights > 0)
    )
    total_weight = numeric_weights[valid].sum()
    if total_weight == 0:
        return float("nan")
    return float(np.dot(numeric_values[valid], numeric_weights[valid]) / total_weight)


def filter_aggregate_frame(
    frame: pd.DataFrame,
    years: tuple[int, ...] | list[int],
    ufs: list[str],
    treineiro_labels: list[str],
) -> pd.DataFrame:
    filtered = frame
    if "NU_ANO" in filtered.columns:
        filtered = filtered[filtered["NU_ANO"].isin(years)]
    if "SG_UF_PROVA" in filtered.columns:
        filtered = filtered[filtered["SG_UF_PROVA"].isin(ufs)]
    if "IN_TREINEIRO_DESC" in filtered.columns:
        filtered = filtered[filtered["IN_TREINEIRO_DESC"].isin(treineiro_labels)]
    elif "IN_TREINEIRO" in filtered.columns:
        values_by_label = {"Treineiro": 1, "Não Treineiro": 0}
        selected_values = [values_by_label[label] for label in treineiro_labels]
        filtered = filtered[filtered["IN_TREINEIRO"].isin(selected_values)]
    return filtered.copy()


def get_global_filter_state() -> tuple[list[int], list[str], list[str]]:
    years = st.session_state.get("filter_years", list(SUPPORTED_YEARS))
    ufs = st.session_state.get("filter_ufs", [])
    treineiro_labels = st.session_state.get(
        "filter_treineiro",
        ["Não Treineiro", "Treineiro"],
    )
    return list(years), list(ufs), list(treineiro_labels)


def load_filtered_aggregate(aggregate_key: str) -> pd.DataFrame:
    result_name_by_aggregate = {
        aggregate_name: result_name
        for result_name, aggregate_name in AGGREGATE_NAMES.items()
    }
    if aggregate_key not in result_name_by_aggregate:
        raise ValueError(f"Agregado desconhecido: {aggregate_key}")
    years, ufs, treineiro_labels = get_global_filter_state()
    data = load_data(years)
    frame = data[result_name_by_aggregate[aggregate_key]]
    return filter_aggregate_frame(frame, years, ufs, treineiro_labels)


def weighted_group_summary(
    frame: pd.DataFrame,
    group_columns: list[str],
    score_metrics: dict[str, tuple[str, str]],
) -> pd.DataFrame:
    aggregations: dict[str, tuple[str, str]] = {
        "total_candidatos": ("total_candidatos", "sum"),
    }
    for output_name, (sum_column, count_column) in score_metrics.items():
        aggregations[f"_sum_{output_name}"] = (sum_column, "sum")
        aggregations[f"_count_{output_name}"] = (count_column, "sum")

    if frame.empty:
        return pd.DataFrame(columns=[*group_columns, "total_candidatos", *score_metrics])
    if group_columns:
        summary = frame.groupby(group_columns, dropna=False).agg(**aggregations).reset_index()
    else:
        summary = pd.DataFrame([{
            name: frame[column].sum()
            for name, (column, _) in aggregations.items()
        }])
    for output_name in score_metrics:
        numerator = summary.pop(f"_sum_{output_name}")
        denominator = summary.pop(f"_count_{output_name}")
        summary[output_name] = numerator.div(denominator.where(denominator > 0))
    return summary


def _normalize_years(years: tuple[int, ...] | list[int] | int) -> tuple[int, ...]:
    selected_years = (years,) if isinstance(years, int) else tuple(sorted(set(years)))
    if not selected_years:
        raise ValueError("Selecione pelo menos um ano.")
    invalid_years = set(selected_years) - set(SUPPORTED_YEARS)
    if invalid_years:
        raise ValueError(f"Anos ENEM não suportados: {sorted(invalid_years)}")
    return selected_years


def _read_aggregate(aggregate_name: str, years: tuple[int, ...]) -> pd.DataFrame:
    yearly_frames = []
    for year in years:
        path = PROCESSED_DIR / f"enem_{year}_{aggregate_name}_parquet"
        if not path.is_dir():
            raise FileNotFoundError(f"Agregado {aggregate_name} de {year} não encontrado em {path}.")
        frame = pd.read_parquet(path)
        if frame.empty:
            raise ValueError(f"Agregado {aggregate_name} de {year} está vazio em {path}.")
        if "NU_ANO" not in frame.columns:
            raise ValueError(f"Coluna NU_ANO ausente em {path}.")
        if not frame["NU_ANO"].eq(year).all():
            raise ValueError(f"Valores de NU_ANO inconsistentes em {path}.")
        yearly_frames.append(frame)
    return pd.concat(yearly_frames, ignore_index=True)


@st.cache_data(ttl=3600, max_entries=16)
def _load_aggregate_data(years: tuple[int, ...]) -> DashboardData:
    aggregates = {
        result_name: _read_aggregate(aggregate_name, years)
        for result_name, aggregate_name in AGGREGATE_NAMES.items()
    }

    reference_year = max(years)
    dictionary_path = DICTIONARY_DIR / f"enem_{reference_year}_dict.json"
    if not dictionary_path.is_file():
        dictionary_path = DICTIONARY_DIR / "enem_2025_dict.json"
    with dictionary_path.open(encoding="utf-8") as dictionary_file:
        enem_dict = json.load(dictionary_file)

    insights_path = PROCESSED_DIR / f"enem_{reference_year}_ml_insights.json"
    if not insights_path.is_file():
        insights_path = PROCESSED_DIR / "enem_2025_ml_insights.json"
    ml_insights = {}
    if insights_path.is_file():
        with insights_path.open(encoding="utf-8") as insights_file:
            ml_insights = json.load(insights_file)

    return {
        **aggregates,
        "df_rede_plurianual": aggregates["df_rede"],
        "ml_insights": ml_insights,
        "enem_dict": enem_dict,
    }


def load_data(years: tuple[int, ...] | list[int] | int = (2025,)) -> DashboardData:
    """Carrega, com cache, somente os cubos agregados dos anos selecionados."""
    return _load_aggregate_data(_normalize_years(years))
