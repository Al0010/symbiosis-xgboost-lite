import numpy as np
import pandas as pd


def get_triple_barrier_labels_lite(
    df: pd.DataFrame,
    entry_dist_pct: float = 0.005,
    pt_mult: float = 2.5,
    sl_mult: float = 1.0,
    max_bars: int = 15,
    slippage_pct: float = 0.0002,  # Es. 0.02%
    commission_pct: float = 0.0001,  # Es. 0.01% per lato
):
  """Calcola le etichette del Triple Barrier Method usando la volatilità standard

  (std_vol) incorporando slippage e commissioni.
  """
  labels = []
  close = df["close"].values

  # Fallback di sicurezza se mancano high o low nel DataFrame
  high = df["high"].values if "high" in df.columns else close
  low = df["low"].values if "low" in df.columns else close

  dist_pct = (
      df["dist_ema_pct"].values
      if "dist_ema_pct" in df.columns
      else np.zeros(len(df))
  )
  
  # Utilizzo della nuova volatilità standard generata dalla versione lite
  std_vol = (
      df["std_vol"].values
      if "std_vol" in df.columns
      else np.ones(len(df)) * 0.01
  )

  n = len(df)
  for i in range(n - max_bars):
    # Filtro basato sulla distanza dall'EMA (trigger di ingresso)
    if abs(dist_pct[i]) < entry_dist_pct:
      labels.append(np.nan)
      continue

    raw_entry_price = close[i]
    current_vol = std_vol[i]

    if np.isnan(current_vol) or current_vol <= 0:
      labels.append(np.nan)
      continue

    # Floor di sicurezza per evitare volatilità nulla o negativa
    min_vol_floor = 0.0003
    current_vol = max(current_vol, min_vol_floor)

    # Slittamento in entrata
    entry_price = raw_entry_price * (1.0 + slippage_pct)

    # Distanze teoriche basate sulla volatilità standard
    pt_distance = entry_price * current_vol * pt_mult
    sl_distance = entry_price * current_vol * sl_mult

    # Costi totali percentuali stimati per il round-trip
    total_cost_pct = (slippage_pct + commission_pct) * 2

    # Calcolo delle barriere nette
    net_pt_threshold = entry_price + pt_distance + (raw_entry_price * total_cost_pct)
    net_sl_threshold = entry_price - sl_distance - (raw_entry_price * total_cost_pct)

    hit_barrier = False
    for j in range(1, max_bars + 1):
      idx = i + j
      bar_high = high[idx]
      bar_low = low[idx]

      hit_tp = bar_high >= net_pt_threshold
      hit_sl = bar_low <= net_sl_threshold

      if hit_tp and hit_sl:
        labels.append(0)
        hit_barrier = True
        break
      elif hit_tp:
        labels.append(1)  # Successo (Profit Target)
        hit_barrier = True
        break
      elif hit_sl:
        labels.append(0)  # Fallimento (Stop Loss)
        hit_barrier = True
        break

    if not hit_barrier:
      labels.append(np.nan)

  # Padding finale per allineare la lunghezza delle etichette
  padding = [np.nan] * (len(df) - len(labels))
  labels.extend(padding)

  return labels