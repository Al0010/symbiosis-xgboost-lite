import streamlit as st


def render_sidebar():
  """Gestisce unicamente i controlli essenziali delle barriere e dei parametri

  per la versione lite, con accesso completamente libero.
  """
  # CSS pulito in stile terminale HFT
  st.sidebar.markdown(
      """
        <style>
            [data-testid="stSidebar"] {
                background-color: #0e1117;
                border-right: 1px solid #21262d;
            }
        </style>
        """,
      unsafe_allow_html=True,
  )

  # Header stile terminale HFT avanzato
  st.sidebar.markdown(
      """
        <div style="background: linear-gradient(135deg, #161b22 15%, #0d1117 100%); border: 1px solid #30363d; border-radius: 6px; padding: 12px; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            <h2 style="font-size: 1.1rem; margin: 0; color: #00f2fe; text-shadow: 0 0 8px #00f2fe60; font-family: monospace; letter-spacing: 1px;">[SYMBIOSIS LITE]</h2>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 6px; border-top: 1px solid #21262d;">
                <span style="font-size: 0.6rem; color: #8b949e; font-family: monospace;">CORE: v2.4-LITE</span>
                <span style="font-size: 0.6rem; color: #00ff66; font-family: monospace; text-shadow: 0 0 4px #00ff6640;">● UNLOCKED</span>
            </div>
        </div>
        """,
      unsafe_allow_html=True,
  )

  st.sidebar.markdown("---")

  # --- SEZIONE TRIPLE BARRIER TUNING CONFIG ---
  st.sidebar.markdown(
      """
        <div style="margin-bottom: 10px;">
            <span style="font-size: 0.8rem; color: #00f2fe; font-family: monospace; font-weight: bold; letter-spacing: 0.5px;">⚙️ //TRIPLE BARRIER CONFIG</span>
        </div>
        """,
      unsafe_allow_html=True,
  )
  
  pt_mult = st.sidebar.slider("TP Multiplier (Std Vol)", 0.5, 15.0, 2.5, 0.05)
  sl_mult = st.sidebar.slider("SL Multiplier (Std Vol)", 0.5, 10.0, 1.0, 0.05)
  max_bars = st.sidebar.slider("Horizon Limit (Bars)", 2, 100, 15, 1)

  entry_dist_pct = st.sidebar.slider(
      "Target Distance (%)",
      min_value=0.0001,
      max_value=0.0100,
      value=0.005,
      step=0.0001,
      format="%.4f",
      help="Short timeframes: 0.0002-0.0010 | Long timeframes: 0.0020-0.0100",
  )

  # --- DIZIONARIO FINALE DEI PARAMETRI (XGBoost fissi) ---
  params = {
      "pt_mult": pt_mult,
      "sl_mult": sl_mult,
      "max_bars": max_bars,
      "entry_dist_pct": entry_dist_pct,
      "max_depth": 2,
      "n_estimators": 25,
      "learning_rate": 0.02,
      "min_child_weight": 15,
  }

  # Ritorna sempre i parametri e True (accesso libero senza autenticazione)
  return params, True