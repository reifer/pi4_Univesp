import os
import importlib.util
import pytest

# Caminho para os componentes de visualização do dashboard
VIEWS_DIR = "src/app/components"
CONCLUSAO_DIR = "src/app/pages/conclusao_modules"

def test_views_directories_exist():
    """Valida se os diretórios principais de visualização e módulos estratégicos existem."""
    assert os.path.exists(VIEWS_DIR), f"O diretório {VIEWS_DIR} não foi encontrado."
    assert os.path.exists(CONCLUSAO_DIR), f"O diretório {CONCLUSAO_DIR} não foi encontrado."

def test_core_views_can_be_imported():
    """
    Garante que os principais módulos de visualização do dashboard 
    podem ser importados sem erros de sintaxe ou quebras de dependência.
    """
    views_core = [
        "desempenho_view.py",
        "geo_view.py",
        "rede_view.py",
        "socio_view.py",
        "ml_view.py",
        "geopolitica_view.py"
    ]
    
    for view_file in views_core:
        caminho = os.path.join(VIEWS_DIR, view_file)
        if os.path.exists(caminho):
            module_name = view_file.replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, caminho)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception as e:
                pytest.fail(f"Erro ao importar a view principal {view_file}: {e}")

def test_conclusao_modules_can_be_imported():
    """
    Verifica se os módulos da conclusão estratégica carregam corretamente.
    """
    if not os.path.exists(CONCLUSAO_DIR):
        pytest.skip("Diretório de módulos estratégicos não encontrado.")

    arquivos_estrategicos = [f for f in os.listdir(CONCLUSAO_DIR) if f.endswith(".py") and f != "__init__.py"]
    
    assert len(arquivos_estrategicos) > 0, "Nenhum módulo estratégico de conclusão encontrado."

    for mod_file in arquivos_estrategicos:
        caminho = os.path.join(CONCLUSAO_DIR, mod_file)
        module_name = mod_file.replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, caminho)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            pytest.fail(f"Erro ao importar o módulo estratégico {mod_file}: {e}")

# O que esse teste valida?
    #1. Valida a árvore de views: Assegura que as pastas de componentes e conclusões estratégicas estão presentes.
    #2. Smoke Test de Importação (Views Core): Tenta carregar cada arquivo de view em memória para certificar-se de que não há erros de sintaxe, imports circulares ou bibliotecas faltando.
    #3. Smoke Test de Módulos Estratégicos: Varre todos os submódulos da aba de conclusão e valida individualmente a integridade de seus scripts.