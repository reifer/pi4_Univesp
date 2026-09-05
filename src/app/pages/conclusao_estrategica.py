import sys
from pathlib import Path

import streamlit as st

src_dir = Path(__file__).resolve().parents[2]
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from app.pages.conclusao_modules.rede_estrategica import render as render_rede
from app.pages.conclusao_modules.renda_estrategica import render as render_renda
from app.pages.conclusao_modules.raca_estrategica import render as render_raca
from app.pages.conclusao_modules.trabalho_estrategica import render as render_trabalho
from app.pages.conclusao_modules.demografia_estrategica import render as render_demografia
from app.pages.conclusao_modules.sintese_estrategica import render as render_sintese

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