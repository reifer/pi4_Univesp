import streamlit as st

# Importação usando ponto (.) para indicar que está na mesma pasta (pages)
from .conclusao_modules.rede_estrategica import render as render_rede
from .conclusao_modules.renda_estrategica import render as render_renda
from .conclusao_modules.raca_estrategica import render as render_raca
from .conclusao_modules.trabalho_estrategica import render as render_trabalho
from .conclusao_modules.demografia_estrategica import render as render_demografia
from .conclusao_modules.sintese_estrategica import render as render_sintese

def render():
    """Função principal que orquestra e renderiza todas as fases da Conclusão Estratégica em sequência."""
    render_rede()
    render_renda()
    render_raca()
    render_trabalho()
    render_demografia()
    render_sintese()

if __name__ == "__main__":
    render()