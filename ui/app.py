import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.features import engineer_features_lite
from core.labeling import get_triple_barrier_labels_lite
from core.model import (
    generate_tradingview_payload,
    train_xgboost_model,
    walk_forward_validation,
    get_adaptive_rolling_limit,
)
from sklearn.metrics import classification_report
import streamlit as st
from ui.components import load_quant_theme
from ui.sidebar import render_sidebar
from ui.widgets import render_payload_box
import numpy as np
import pandas as pd


# Configurazione della pagina
st.set_page_config(
    page_title="SYMBIOSIS XGBOOST // LITE DESK",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Carica il design system Ciano & Viola Fluorescente
load_quant_theme()

# --- GESTIONE SIDEBAR (Senza autenticazione) ---
params, is_authenticated = render_sidebar()

# --- HEADER PRINCIPALE ---
st.markdown(
    """
    <h1>GENESIS DESK // <span style="color: #bd00ff; text-shadow: 0 0 10px #bd00ff;">LITE VERSION MODEL</span></h1>
    <p style="color: #c9d1d9; margin-top: -5px;">Streamlined XGBoost Core for Pine Script v6</p>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# --- UPLOAD DATASET ---
st.markdown(
    """
    <div class="quant-card">
        <div class="quant-header">
            <span class="quant-title">[01] INGEST HISTORICAL DATA</span>
            <span class="status-badge">CSV PIPELINE</span>
        </div>
""",
    unsafe_allow_html=True,
)
uploaded_file = st.file_uploader(
    "Upload historical data CSV (OHLCV)", type=["csv"]
)
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is not None:
  if st.button("🧪 EXECUTE TRAINING & MODEL COMPILE"):
    status_container = st.status(
        "🧬 [XGBOOST LITE] INITIALIZING PIPELINE...", expanded=True
    )

    with status_container:
      progress_bar = st.progress(0)
      status_text = st.empty()
      start_time = time.time()

      try:
        # 1. Feature Engineering (Versione Lite con std_vol)
        status_text.markdown("⚙️ [25%] Parsing CSV e feature engineering (Lite)...")
        progress_bar.progress(25)
        raw_df = pd.read_csv(uploaded_file)
        df = engineer_features_lite(raw_df)

        adaptive_rolling_limit = get_adaptive_rolling_limit(df)

        # Le 3 feature essenziali + volatilità standard
        features = [
            "dist_ema_pct",
            "close_location",
            "volume_ratio",
            "std_vol",
        ]
        
        fixed_xgb_params = {
            "n_estimators": params.get("n_estimators", 25),
            "max_depth": params.get("max_depth", 2),
            "learning_rate": params.get("learning_rate", 0.02),
            "min_child_weight": params.get("min_child_weight", 15),
        }

        active_pt = params.get("pt_mult", 2.5)
        active_sl = params.get("sl_mult", 1.0)
        active_bars = params.get("max_bars", 15)
        active_entry_dist = params.get("entry_dist_pct", 0.005)

        # 2. Labeling con Triple Barrier
        status_text.markdown("⚙️ [50%] Running Triple Barrier Labelling...")
        progress_bar.progress(50)

        labels = get_triple_barrier_labels_lite(
            df,
            entry_dist_pct=active_entry_dist,
            pt_mult=active_pt,
            sl_mult=active_sl,
            max_bars=active_bars,
        )
        if labels is None or len(labels) == 0:
          st.error("⚠️ Labeling did not return any data.")
          st.stop()
          
        df["target"] = labels
        df = df.dropna(subset=["target"])
        
        if df.empty or len(df) < 30:
          st.error("⚠️ Dataset too short after filtering.")
          st.stop()

        X = df[features]
        y = df["target"].astype(int)

        neg_count = len(y[y == 0])
        pos_count = len(y[y == 1])
        scale_weight = neg_count / pos_count if pos_count > 0 else 1.0

        # 3. Walk-Forward Validation
        status_text.markdown("⚙️ [75%] Running Walk-Forward Validation...")
        progress_bar.progress(75)

        auc_scores, wfv_df = walk_forward_validation(
            X,
            y,
            n_splits=5,
            train_size_ratio=0.5,
            scale_weight=scale_weight,
            params=fixed_xgb_params,
            rolling_limit=adaptive_rolling_limit,
        )

        # 4. Training Finale
        status_text.markdown("⚙️ [90%] Training final model...")
        progress_bar.progress(90)

        split_idx = int(len(X) * 0.8)
        X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

        model = train_xgboost_model(
            X_train,
            y_train,
            X_val,
            y_val,
            scale_weight,
            fixed_xgb_params,
        )

        val_probs = model.predict_proba(X_val)[:, 1]
        val_preds = (val_probs >= 0.5).astype(int)

        elapsed_time = time.time() - start_time
        progress_bar.progress(100)
        status_text.markdown(f"[100%] Pipeline completed in {elapsed_time:.2f}s!")

        status_container.update(
            label="🧬 [XGBOOST LITE] COMPLETED [OK]",
            state="complete",
            expanded=False,
        )

        # --- SEZIONE [02]: CONFIGURAZIONE ATTIVA ---
        st.markdown(
            """
            <div class="quant-card">
                <div class="quant-header">
                    <span class="quant-title">[02] CONFIGURATION SUMMARY</span>
                    <span class="status-badge">SYNCED</span>
                </div>
        """,
            unsafe_allow_html=True,
        )
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TP MULTIPLIER", f"{float(active_pt):.2f}x")
        c2.metric("SL MULTIPLIER", f"{float(active_sl):.2f}x")
        c3.metric("MAX BARS", f"{int(active_bars)}")
        c4.metric("ROLLING LIMIT", f"{int(adaptive_rolling_limit)}")
        st.markdown("</div>", unsafe_allow_html=True)

        # --- SEZIONE [03]: WALK-FORWARD METRICS ---
        mean_auc = np.mean(auc_scores) if auc_scores else 0.5
        std_auc = np.std(auc_scores) if auc_scores else 0.0

        st.markdown(
            """
            <div class="quant-card">
                <div class="quant-header">
                    <span class="quant-title">[03] WALK-FORWARD AUDIT METRICS</span>
                    <span class="status-badge">VALIDATED</span>
                </div>
        """,
            unsafe_allow_html=True,
        )
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Mean ROC AUC", f"{mean_auc:.4f}")
        m2.metric("AUC Std Dev", f"{std_auc:.4f}")
        m3.metric("Validation Folds", f"{len(auc_scores)}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(
            wfv_df.style.format({"ROC AUC": "{:.4f}"}), use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # --- SEZIONE [04]: CLASSIFICATION REPORT ---
        st.markdown(
            """
            <div class="quant-card">
                <div class="quant-header">
                    <span class="quant-title">[04] CLASSIFICATION REPORT</span>
                    <span class="status-badge">VAL_SET_OK</span>
                </div>
        """,
            unsafe_allow_html=True,
        )
        report_dict = classification_report(
            y_val, val_preds, output_dict=True, zero_division=0
        )
        report_df = pd.DataFrame(report_dict).transpose()
        st.dataframe(report_df.style.format("{:.2f}"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- SEZIONE [05]: VERDETTO AUTOMATICO (ROSSO / VERDE) ---
        is_auc_good = mean_auc >= 0.53
        is_stable = std_auc <= 0.05

        problems = []
        if not is_auc_good:
          problems.append("• Edge Statistico Debbole: ROC AUC medio inferiore a 0.53.")
        if not is_stable:
          problems.append("• Instabilità di Regime: L'AUC fluttua troppo tra i fold.")

        if is_auc_good and is_stable:
          verdict_title = "APPROVED // READY FOR PINE"
          verdict_color = "#00ff66"  # Verde brillante
          verdict_desc = "Il modello ha superato i requisiti minimi di stabilità statistica."
        else:
          verdict_title = "REJECTED // ADJUST PARAMETERS"
          verdict_color = "#ff0055"  # Rosso/Fucsia di errore
          verdict_desc = "Il modello non soddisfa i requisiti minimi quantitativi."

        st.markdown(
            f"""
            <div class="quant-card" style="border: 2px solid {verdict_color}; box-shadow: 0 0 20px {verdict_color}40;">
                <div class="quant-header">
                    <span class="quant-title">[05] QUANTITATIVE VERDICT</span>
                    <span class="status-badge" style="background-color: {verdict_color}; color: #000; font-weight: bold;">{verdict_title}</span>
                </div>
                <p style="color: #c9d1d9; font-size: 0.9rem; margin-top: 10px;">{verdict_desc}</p>
        """,
            unsafe_allow_html=True,
        )

        if problems:
          st.markdown(
              "<p style='color: #ff0055; font-size: 0.85rem; margin-top: 10px; font-weight: bold;'>CRITICITÀ RILEVATE:</p>",
              unsafe_allow_html=True,
          )
          for p in problems:
            st.markdown(
                f"<p style='color: #ff0055; font-size: 0.85rem; margin: 2px 0;'>{p}</p>",
                unsafe_allow_html=True,
            )
        else:
          st.markdown(
              "<p style='color: #00ff66; font-size: 0.85rem; margin-top: 10px; font-weight: bold;'>NESSUNA CRITICITÀ RILEVATA.</p>",
              unsafe_allow_html=True,
          )
        st.markdown("</div>", unsafe_allow_html=True)

        # --- SEZIONE [06]: TRADINGVIEW PAYLOAD (PINE SCRIPT v6) ---
        st.markdown(
            """
            <div class="quant-card">
                <div class="quant-header">
                    <span class="quant-title">[06] TRADINGVIEW PINE v6 PAYLOAD</span>
                    <span class="status-badge">READY</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        best_params_dict_payload = {
            "pt_mult": active_pt,
            "sl_mult": active_sl,
            "max_bars": active_bars,
        }

        full_model_string = generate_tradingview_payload(
            model=model,
            features=features,
            best_params=best_params_dict_payload,
            entry_dist_pct=active_entry_dist,
        )

        render_payload_box(full_model_string)

      except Exception as e:
        st.error(f"CRITICAL ERROR: {e}")
else:
  st.markdown(
      """
        <div class="quant-card" style="text-align: center; padding: 50px;">
            <h3 style="color: #00f2fe !important; text-shadow: 0 0 10px #00f2fe;">SYSTEM IDLE // WAITING FOR DATA</h3>
            <p style="color: #c9d1d9; max-width: 500px; margin: 0 auto;">Upload an OHLCV CSV file to run the lite feature pipeline and generate the trading matrix.</p>
        </div>
    """,
      unsafe_allow_html=True,
  )