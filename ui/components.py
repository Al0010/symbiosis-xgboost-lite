import streamlit as st

def load_quant_theme():
    """Inietta il design system HFT con palette Ciano e Viola Fluorescente ad alto contrasto."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');

        /* Sfondo terminale HFT */
        .stApp {
            background-color: #000000;
            color: #e2e8f0;
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Scanline effect leggero */
        .stApp::before {
            content: " ";
            display: block;
            position: fixed;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.15) 50%);
            z-index: 99999;
            background-size: 100% 4px;
            pointer-events: none;
        }

        /* Sidebar stile rack server */
        [data-testid="stSidebar"] {
            background-color: #050508;
            border-right: 1px solid rgba(0, 242, 254, 0.2);
        }

        /* Titoli Ciano Fluorescente */
        h1, h2, h3, h4 {
            font-family: 'JetBrains Mono', monospace !important;
            color: #00f2fe !important;
            text-shadow: 0 0 12px rgba(0, 242, 254, 0.5);
            letter-spacing: -1px;
            text-transform: uppercase;
        }
        
        p, span, label, div {
            font-family: 'JetBrains Mono', monospace !important;
            color: #c9d1d9;
        }

        /* Card Ologramma */
        .quant-card {
            background: linear-gradient(135deg, #05070f 0%, #020307 100%);
            border: 1px solid rgba(0, 242, 254, 0.3);
            border-radius: 6px;
            padding: 22px;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.1);
            margin-bottom: 20px;
        }

        .quant-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px dashed rgba(189, 0, 255, 0.4);
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        
        .quant-title {
            font-weight: 800;
            font-size: 1rem;
            color: #ffffff !important;
            text-transform: uppercase;
        }

        .status-badge {
            background: #bd00ff;
            color: #ffffff;
            padding: 3px 10px;
            font-weight: 800;
            font-size: 0.7rem;
            text-transform: uppercase;
            box-shadow: 0 0 10px #bd00ff;
            border-radius: 2px;
        }

        /* Bottoni Viola Fluorescente */
        .stButton>button {
            background: linear-gradient(135deg, #bd00ff 0%, #7b00ff) !important;
            color: #ffffff !important;
            font-weight: 800 !important;
            font-family: 'JetBrains Mono', monospace !important;
            border: 1px solid #00f2fe !important;
            border-radius: 4px !important;
            padding: 0.8rem 1.5rem;
            box-shadow: 0 0 15px rgba(189, 0, 255, 0.6);
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #00f2fe 0%, #bd00ff) !important;
            color: #000000 !important;
            box-shadow: 0 0 25px #00f2fe;
        }

        /* --- STILE DEFINITIVO E FORZATO PER IL PAYLOAD (st.code) --- */
        .stCodeBlock {
            background-color: #000000 !important;
            border: 1px solid #00f2fe !important;
            box-shadow: 0 0 25px rgba(0, 242, 254, 0.4) !important;
            border-radius: 6px !important;
        }
        
        /* Forza il blocco a espandersi in altezza senza scroll orizzontale */
        .stCodeBlock pre {
            white-space: pre-wrap !important;
            word-break: break-all !important;
            max-height: 400px !important;
            overflow-y: auto !important;
            background-color: #000000 !important;
        }

        /* Forza colore ciano fluorescente su qualsiasi elemento testuale o span interno */
        .stCodeBlock code, .stCodeBlock span, .stCodeBlock pre {
            color: #00f2fe !important;
            font-family: 'JetBrains Mono', monospace !important;
            text-shadow: 0 0 8px rgba(0, 242, 254, 0.8) !important;
            font-size: 0.85rem !important;
        }

        /* Pulsante di copia integrato in alto a destra */
        .stCodeBlock button {
            background-color: #bd00ff !important;
            color: #ffffff !important;
            border: 1px solid #00f2fe !important;
            box-shadow: 0 0 15px #bd00ff !important;
            border-radius: 4px !important;
            z-index: 10;
        }
        .stCodeBlock button:hover {
            background-color: #00f2fe !important;
            color: #000000 !important;
            border-color: #ffffff !important;
        }

        /* Metriche */
        [data-testid="stMetric"] {
            background: #03050a;
            border: 1px solid rgba(0, 242, 254, 0.3);
            padding: 12px;
            border-radius: 4px;
        }
        [data-testid="stMetricValue"] {
            color: #00f2fe !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 800;
            text-shadow: 0 0 10px rgba(0, 242, 254, 0.6);
        }
        [data-testid="stMetricLabel"] {
            color: #bd00ff !important;
            text-transform: uppercase;
        }

        </style>
    """, unsafe_allow_html=True)