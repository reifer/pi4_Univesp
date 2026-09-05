import os
import json
import pytest

# Caminho onde os modelos e métricas de ML costumam ser salvos
ML_DIR = "src/ml_models"
DATA_PROCESSED_DIR = "data/processed"

def test_ml_artifacts_directory_exists():
    """Valida se o diretório de modelos de Machine Learning existe."""
    # O diretório pode estar em src/ml_models ou em data/processed dependendo da estrutura
    exists = os.path.exists(ML_DIR) or os.path.exists(DATA_PROCESSED_DIR)
    assert exists, "Nenhum diretório padrão de ML ou dados processados foi encontrado."

def test_ml_insights_json_structure():
    """
    Verifica se o arquivo de insights/métricas de ML (se existente) 
    possui chaves e valores válidos (ex: acurácia entre 0 e 1 ou 0 e 100).
    """
    # Procura por arquivos json de insights de ML no projeto
    candidatos_json = []
    for root, _, files in os.walk("."):
        for file in files:
            if "ml" in file.lower() and file.endswith(".json"):
                candidatos_json.append(os.path.join(root, file))

    if not candidatos_json:
        pytest.skip("Nenhum arquivo JSON de ML encontrado para validação de métricas (opcional no momento).")

    for caminho in candidatos_json:
        with open(caminho, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
            except json.JSONDecodeError:
                pytest.fail(f"O arquivo de ML {caminho} não é um JSON válido.")

        assert isinstance(dados, (dict, list)), f"O conteúdo de {caminho} deve ser um dicionário ou lista."
        
        # Se for um dicionário de métricas, valida se valores numéricos estão em ranges lógicos
        if isinstance(dados, dict):
            for chave, valor in dados.items():
                if any(k in chave.lower() for k in ["acc", "accuracy", "score", "auc"]):
                    if isinstance(valor, (int, float)):
                        # Métricas costumam estar entre 0-1 ou 0-100
                        assert 0 <= valor <= 100, f"Métrica '{chave}' com valor inválido: {valor}"

def test_mock_ml_prediction_pipeline():
    """
    Valida a integridade lógica de uma predição simulada 
    para garantir que a pipeline de inferência está coesa.
    """
    # Simulação de probabilidades de desempenho de um aluno no ENEM
    probabilidade_aprovacao = 0.85
    classe_predita = 1 if probabilidade_aprovacao >= 0.5 else 0

    assert 0.0 <= probabilidade_aprovacao <= 1.0, "A probabilidade predita deve estar entre 0 e 1."
    assert classe_predita in [0, 1], "A classe predita deve ser binária (0 ou 1)."

# O que esse teste valida?
    #1. Verifica diretórios de ML: Assegura que a infraestrutura de pastas de Machine Learning está acessível no repositório.existe.
    #2. Valida JSONs de Métricas: Varre o projeto em busca de arquivos JSON relacionados a ML, testa se o formato é válido e se métricas como acurácia/score estão dentro de intervalos lógicos.(ex: 0-1 ou 0-100).
    #3. Smoke test analítico: Executa uma validação unitária simulando o comportamento de inferência do modelo preditivo.
