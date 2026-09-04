import streamlit as st

# Paleta oficial para Dependência Administrativa da Escola
COLOR_MAP_REDE = {
    "Federal":       "#2563EB",
    "Estadual":      "#10B981",
    "Municipal":     "#F59E0B",
    "Privada":       "#8B5CF6",
    "Pública":       "#0EA5E9",
    "Não Informado": "#94A3B8"
}

def apply_custom_css():
    """Aplica a estilização CSS personalizada e responsiva do dashboard."""
    st.markdown("""
    <style>
        .stApp, .main, .block-container {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            max-width: 100%;
        }
        .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
            color: #0F172A !important;
            font-weight: 700 !important;
        }
        .main p, .main span, .main label {
            color: #334155;
        }
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0;
        }
        section[data-testid="stSidebar"] *,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] div,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] li,
        section[data-testid="stSidebar"] .stMarkdown {
            color: #1E293B !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stAlert"] {
            background-color: #F1F5F9 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
        }
        span[data-baseweb="tag"] {
            background-color: #2563EB !important;
            border-radius: 6px !important;
        }
        span[data-baseweb="tag"] span {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        .clean-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        }
        .badge-primary {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: #ffffff;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 700;
            display: inline-block;
        }
        .metric-value-clean {
            font-size: 2.0rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.2;
        }
        .metric-label-clean {
            font-size: 0.80rem;
            color: #64748B;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }
        .metric-sub-clean {
            font-size: 0.82rem;
            color: #10B981;
            font-weight: 600;
            margin-top: 4px;
        }
        
        /* Ajustes responsivos avançados para mobile */
        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .clean-card {
                padding: 14px;
                margin-bottom: 12px;
            }
            .metric-value-clean {
                font-size: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)