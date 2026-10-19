<div align="center">

# 🧬 SYMBIOSIS XGBOOST LITE 
### *Quantitative Trading & Machine Learning Bridge for TradingView Pine Script v6*

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.20%2B-ff4b4b.svg)](https://streamlit.io/)
[![XGBoost](https://img.shields.io/badge/xgboost-1.5%2B-orange.svg)](https://xgboost.readthedocs.io/)
[![Pine Script v6](https://img.shields.io/badge/TradingView-Pine%20Script%20v6-131722.svg)](https://www.tradingview.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

</div>

---

## Executive Summary

**SYMBIOSIS XGBOOST LITE** is an institutional-grade, zero-latency quantitative XGBoost trading model designed to bridge advanced machine learning inference directly with TradingView charts. The *Lite Version Model* focuses strictly on core alpha generation using 4 features and a fixed hyperparameters configuration: transforming raw OHLCV tick data into robust, stateful decision trees executed natively inside **Pine Script v6**.

The desk integrates a **Streamlit** control center for dataset ingestion, feature engineering, triple-barrier labeling, and Walk-Forward Validation (WFV), outputting a streamlined matrix payload (`CFG:tp,sl,max_bars,entry_dist_pct#...`) that feeds the TradingView digital brain without external API dependencies.

---

## System Architecture

The architecture is built on a modular, decoupled design pattern separating data engineering, machine learning optimization, and client-side visualization:

```
symbiosis-xgboost-lite/
│
├── core/
│   ├── __init__.py           # Package initialization
│   ├── features.py           # Lite feature engineering
│   ├── labeling.py           # Triple Barrier Labeling engine
│   └── model.py              # XGBoost training, WFV, & payload serializer
│
├── ui/
│   ├── __init__.py           # Package initialization
│   ├── app.py                # Streamlit Quantitative Desk interface
│   ├── components.py         # Cyan & Neon Violet design system
│   ├── sidebar.py            # Hyperparameter control panel
│   └── widgets.py            # Interactive payload copy-box elements
│
├── requirements.txt          # Python dependency manifest
└── README.md                 # System documentation
```

---

## Core Technical Modules

### 1. Feature Engineering (`core/features.py`)
Standardized around 4 high-signal predictive features designed to prevent model overfitting while capturing momentum, liquidity, and volatility regimes:
*   $\text{dist\_ema\_pct}$: Percentage distance from the 20-period Exponential Moving Average.
*   $\text{close\_location}$: Relative position of the close within the high-low bar range.
*   $\text{volume\_ratio}$: Short-term volume liquidity relative to the 20-period moving average.
*   $\text{std\_vol}$: Standard deviation of percentage returns over 20 periods for dynamic risk sizing.

### 2. Triple Barrier Labeling (`core/labeling.py`)
Implements financial labeling based on Marcos López de Prado's Triple Barrier Method, mapping directional outcomes against dynamic volatility thresholds (Take Profit, Stop Loss, and Max Bar expiration).

### 3. Model Training & WFV (`core/model.py`)
*   **Fixed Hyperparameters**: Optimized for stability ($n\_estimators=25$, $max\_depth=2$, $learning\_rate=0.02$, $min\_child\_weight=15$).
*   **Walk-Forward Validation (WFV)**: Out-of-sample temporal cross-validation across 5 splits with adaptive rolling window constraints to prevent data leakage.
*   **Quantitative Verdict Engine**: Automatically audits models based on Mean ROC AUC ($\ge 0.53$) and Standard Deviation ($\le 0.05$), rendering an instant **Approved / Ready for Pine** (Green) or **Rejected** (Red) verdict.

### 4. Pine Script v6 Engine (`pine_lite`)
A zero-external-dependency matrix interpreter written in Pine Script v6. It parses the custom string payload into native `matrix<float>` structures, evaluates ensemble decision trees per bar, executes stateful trade logic on confirmed candle closes, and plots dynamic multi-tier risk corridors.

---

## Installation & Quick Start

1. **Clone the Repository & Navigate to Directory**:
   ```bash
   git clone https://github.com/your-username/symbiosis-xgboost-lite.git
   cd symbiosis-xgboost-lite
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Streamlit Desk**:
   ```bash
   streamlit run ui/app.py
   ```

4. **Workflow Execution**:
   * Upload your historical OHLCV dataset (`.csv`) in section `[01]`.
   * Configure hyperparameters in the sidebar (TP/SL multipliers, max bars, sensitivity).
   * Execute training to review WFV audit metrics and the automated **Quantitative Verdict**.
   * Copy the generated **TradingView Pine v6 Payload** from section `[06]` and paste it into the `Symbiosys XGBoost Lite` indicator settings on TradingView.

---
