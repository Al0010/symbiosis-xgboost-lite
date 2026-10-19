import json
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import roc_auc_score


def get_adaptive_rolling_limit(df: pd.DataFrame) -> int:
  """Restituisce un limite di rolling adattivo basato sulla lunghezza del dataset."""
  if len(df) > 10000:
    return 5000
  elif len(df) > 1000:
    return 1000
  else:
    return len(df)


def train_xgboost_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    scale_weight: float = 1.0,
    params: dict = None,
) -> xgb.XGBClassifier:
  """Esegue il training diretto del classificatore XGBoost con parametri fissi o passati esternamente."""
  if params is None:
    params = {}

  model = xgb.XGBClassifier(
      n_estimators=params.get("n_estimators", 25),
      max_depth=params.get("max_depth", 2),
      learning_rate=params.get("learning_rate", 0.02),
      subsample=0.7,
      colsample_bytree=0.7,
      scale_pos_weight=scale_weight,
      reg_alpha=1.5,
      reg_lambda=3.0,
      min_child_weight=params.get("min_child_weight", 15),
      eval_metric="logloss",
      random_state=42,
  )
  
  model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
  return model


def walk_forward_validation(
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 5,
    train_size_ratio: float = 0.5,
    scale_weight: float = 1.0,
    params: dict = None,
    rolling_limit: int = None,
):
  """Esegue la validazione Walk-Forward per testare la stabilità Out-of-Sample."""
  if params is None:
    params = {}

  total_len = len(X)
  fold_size = int(total_len / (n_splits + 1))

  if fold_size < 10:
    return [0.5], pd.DataFrame({"Fold": [1], "Train Size": [len(X)], "ROC AUC": [0.5]})

  auc_scores = []
  fold_records = []

  for i in range(n_splits):
    train_end = int(total_len * train_size_ratio) + (i * fold_size)
    val_end = train_end + fold_size

    if val_end > total_len:
      break

    X_tr = X.iloc[:train_end]
    y_tr = y.iloc[:train_end]
    X_va = X.iloc[train_end:val_end]
    y_va = y.iloc[train_end:val_end]

    if rolling_limit is not None and len(X_tr) > rolling_limit:
      X_tr = X_tr.iloc[-rolling_limit:]
      y_tr = y_tr.iloc[-rolling_limit:]

    if len(np.unique(y_va)) < 2 or len(np.unique(y_tr)) < 2:
      continue

    try:
      model = xgb.XGBClassifier(
          n_estimators=params.get("n_estimators", 25),
          max_depth=params.get("max_depth", 2),
          learning_rate=params.get("learning_rate", 0.02),
          subsample=0.7,
          colsample_bytree=0.7,
          scale_pos_weight=scale_weight,
          reg_alpha=1.5,
          reg_lambda=3.0,
          min_child_weight=params.get("min_child_weight", 15),
          eval_metric="logloss",
          random_state=42,
      )
      model.fit(X_tr, y_tr, verbose=False)

      preds = model.predict_proba(X_va)[:, 1]
      score = roc_auc_score(y_va, preds)

      auc_scores.append(score)
      fold_records.append({
          "Fold": i + 1,
          "Train Size": len(X_tr),
          "Val Size": len(X_va),
          "ROC AUC": score,
      })
    except Exception:
      continue

  if not auc_scores:
    auc_scores = [0.5]
    fold_records = [{"Fold": 1, "Train Size": len(X), "ROC AUC": 0.5}]

  return auc_scores, pd.DataFrame(fold_records)


def generate_tradingview_payload(
    model: xgb.XGBClassifier,
    features: list,
    best_params: dict = None,
    entry_dist_pct: float = 0.0005,
) -> str:
  """Estrae gli alberi di decisione di XGBoost e formatta l'header CFG

  (esente da timestamp) per la compatibilità con il Pine Script v6.
  """
  try:
    booster = model.get_booster()
    dump_json = booster.get_dump(dump_format="json")

    all_trees_data = []
    for tree_str in dump_json:
      tree_data = json.loads(tree_str)

      def flatten(node, n_list=None):
        if n_list is None:
          n_list = {}
        n_list[node["nodeid"]] = node
        if "children" in node:
          for child in node["children"]:
            flatten(child, n_list)
        return n_list

      nodes_dict = flatten(tree_data)
      tree_serialized = []
      for i in sorted(nodes_dict.keys()):
        node = nodes_dict[i]
        if "leaf" in node:
          tree_serialized.append(f"-1:{float(node['leaf'])}:0:0")
        else:
          split_str = node["split"]
          feat = (
              int(split_str[1:])
              if split_str.startswith("f")
              else (
                  features.index(split_str)
                  if split_str in features
                  else 0
              )
          )
          thresh = float(node["split_condition"])
          left = int(node["yes"])
          right = int(node["no"])
          tree_serialized.append(f"{feat}:{thresh}:{left}:{right}")
      all_trees_data.append(";".join(tree_serialized))

    forest_str = "|".join(all_trees_data)

    pt = best_params.get("pt_mult", 2.5) if best_params else 2.5
    sl = best_params.get("sl_mult", 1.0) if best_params else 1.0
    mb = best_params.get("max_bars", 15) if best_params else 15

    # Header privo di timestamp: CFG:tp,sl,max_bars,entry_dist_pct#
    config_header = f"CFG:{pt},{sl},{mb},{entry_dist_pct}#"
    return config_header + forest_str
  except Exception as e:
    return f"ERROR_SERIALIZING_PAYLOAD: {str(e)}"