import numpy as np
import pandas as pd


def engineer_features_lite(
    df: pd.DataFrame, ema_span: int = 21, vol_window: int = 20
) -> pd.DataFrame:
  df = df.copy()
  df.columns = [c.lower() for c in df.columns]

  # Verifica colonne obbligatorie
  required_cols = ["open", "high", "low", "close", "volume"]
  for col in required_cols:
    if col not in df.columns:
      raise ValueError(
          f"Colonna obbligatoria mancante nel CSV: '{col}'. Il dataset deve"
          " contenere Open, High, Low, Close e Volume."
      )

  # 1. VOLATILITÀ STANDARD (Dev. Std. dei rendimenti)
  df["returns"] = df["close"].pct_change()
  df["std_vol"] = df["returns"].rolling(window=vol_window).std()

  # 2. FEATURE 1: Distanza percentuale dalla EMA (Il trigger principale)
  df["ema_target"] = df["close"].ewm(span=ema_span, adjust=False).mean()
  df["dist_ema_pct"] = (df["close"] - df["ema_target"]) / df["ema_target"]

  # 3. FEATURE 2: Close Location Value (Posizione di chiusura nel range della barra)
  hl = df["high"] - df["low"]
  range_hl = np.where(hl == 0, 0.0001, hl)
  df["close_location"] = (df["close"] - df["low"]) / range_hl

  # 4. FEATURE 3: Volume Ratio (Volume attuale / Media volumi a 20 periodi)
  vol_sma = df["volume"].rolling(window=vol_window).mean().replace(0, 1.0)
  df["volume_ratio"] = df["volume"] / vol_sma

  # Pulizia delle colonne di supporto temporanee e dei valori NaN
  df.drop(columns=["returns"], inplace=True, errors="ignore")
  df.dropna(inplace=True)
  
  return df