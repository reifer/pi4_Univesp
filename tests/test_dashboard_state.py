from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_global_filter_state_updates_for_presets_and_custom_selections():
    dashboard_path = Path(__file__).resolve().parents[1] / "src/app/dashboard.py"
    app = AppTest.from_file(dashboard_path, default_timeout=90).run()

    assert not app.exception
    assert app.session_state["filter_years"] == [2025]
    assert app.session_state["filter_ufs"]
    assert app.session_state["filter_treineiro"] == ["Não Treineiro", "Treineiro"]

    app.segmented_control(key="year_preset").set_value("Série completa").run()
    assert not app.exception
    assert app.session_state["filter_years"] == [2021, 2022, 2023, 2024, 2025]

    app.multiselect(key="filter_years").set_value([2021, 2024]).run()
    assert not app.exception
    assert app.session_state["year_preset"] == "Personalizado"
    assert app.session_state["filter_years"] == [2021, 2024]

    app.multiselect(key="filter_ufs").set_value(["SP"]).run()
    app.pills(key="filter_treineiro").set_value(["Treineiro"]).run()
    assert not app.exception
    assert app.session_state["uf_preset"] == "Personalizado"
    assert app.session_state["filter_ufs"] == ["SP"]
    assert app.session_state["filter_treineiro"] == ["Treineiro"]


def test_geography_presets_and_region_selection():
    dashboard_path = Path(__file__).resolve().parents[1] / "src/app/dashboard.py"
    app = AppTest.from_file(dashboard_path, default_timeout=90).run()

    assert not app.exception
    assert app.session_state["uf_preset"] == "Brasil (Todos)"
    total_ufs = len(app.session_state["filter_ufs"])
    assert total_ufs >= 26

    # Muda para Por Região (região padrão é Sudeste)
    app.segmented_control(key="uf_preset").set_value("Por Região").run()
    assert not app.exception
    assert sorted(app.session_state["filter_ufs"]) == ["ES", "MG", "RJ", "SP"]

    # Altera para Sul
    app.pills(key="selected_region").set_value("Sul").run()
    assert not app.exception
    assert sorted(app.session_state["filter_ufs"]) == ["PR", "RS", "SC"]

    # Retorna para Brasil (Todos)
    app.segmented_control(key="uf_preset").set_value("Brasil (Todos)").run()
    assert not app.exception
    assert len(app.session_state["filter_ufs"]) == total_ufs


def test_all_analysis_modules_render_for_mixed_year_single_uf_and_treineers():
    dashboard_path = Path(__file__).resolve().parents[1] / "src/app/dashboard.py"
    app = AppTest.from_file(dashboard_path, default_timeout=90).run()
    all_ufs = list(app.session_state["filter_ufs"])
    app.multiselect(key="filter_years").set_value([2021, 2024]).run()
    app.multiselect(key="filter_ufs").set_value(["SP"]).run()
    app.pills(key="filter_treineiro").set_value(["Treineiro"]).run()

    modules = (
        "📊 Panorama Geográfico",
        "💰 Perfil Socioeconômico",
        "🏫 Redes de Ensino",
        "📈 Desempenho TRI",
        "🤖 Machine Learning",
        "🌎 Geopolítica",
        "🎓 Conclusão Estratégica",
    )
    for module in modules:
        app.pills(key="module_selection").set_value(module).run()
        assert not app.exception, f"Module {module} raised: {app.exception}"

    app.multiselect(key="filter_years").set_value([2021, 2022, 2023, 2024, 2025]).run()
    app.multiselect(key="filter_ufs").set_value(all_ufs).run()
    app.pills(key="filter_treineiro").set_value(["Não Treineiro", "Treineiro"]).run()
    for module in modules:
        app.pills(key="module_selection").set_value(module).run()
        assert not app.exception, f"Module {module} raised: {app.exception}"
