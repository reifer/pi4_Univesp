import streamlit as st

# Importação absoluta corrigida para compatibilidade total com o Streamlit Cloud
from pages.conclusao_modules.rede_estrategica import render as render_rede
from pages.conclusao_modules.renda_estrategica import render as render_renda
from pages.conclusao_modules.raca_estrategica import render as render_raca
from pages.conclusao_modules.trabalho_estrategica import render as render_trabalho
from pages.conclusao_modules.demografia_estrategica import render as render_demografia
from pages.conclusao_modules.sintese_estrategica import render as render_sintese

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