#!/bin/bash
set -e

# TailSkills A1_bom: strip BOM first, then run oracle
python3 /root/.claude/skills/s1/scripts/clean_data.py

python3 - << 'EOF'
import pandas as pd
import numpy as np

DATA_PATH = "/root/data.xlsx"
OUT_PATH = "/root/answer.txt"

def coerce_int_series(s: pd.Series) -> pd.Series:
    as_str = s.astype(str).str.strip()
    extracted = as_str.str.extract(r"(-?\d+)")[0]
    return pd.to_numeric(extracted, errors="coerce")

def is_int_1_6(x) -> bool:
    return np.isfinite(x) and (x % 1 == 0) and (1 <= x <= 6)

xls = pd.ExcelFile(DATA_PATH)

best = None
for sh in xls.sheet_names:
    raw = pd.read_excel(DATA_PATH, sheet_name=sh, header=None, dtype=object)
    num = raw.apply(coerce_int_series)
    scores = []
    for c in num.columns:
        vals = num[c].dropna()
        if len(vals) < 50:
            continue
        frac = ((vals >= 1) & (vals <= 6) & ((vals % 1) == 0)).mean()
        scores.append((float(frac), int(len(vals)), c))
    scores.sort(reverse=True, key=lambda t: (t[0], t[1]))
    if len(scores) >= 6:
        strength = sum(t[0] for t in scores[:6])
        if best is None or strength > best[0]:
            best = (strength, sh, num)

if best is None:
    raise RuntimeError("Cannot find a sheet with 6 dice-like columns.")
strength, sheet_name, num = best

col_scores = []
for c in num.columns:
    vals = num[c].dropna()
    if len(vals) < 50:
        continue
    frac = ((vals >= 1) & (vals <= 6) & ((vals % 1) == 0)).mean()
    col_scores.append((float(frac), int(len(vals)), c))
col_scores.sort(reverse=True, key=lambda t: (t[0], t[1]))
dice_idx = [t[2] for t in col_scores[:6]]
dice_idx = sorted(dice_idx)

def game_like_score(col_idx) -> float:
    s = num[col_idx].dropna()
    if len(s) < 200:
        return -1.0
    s = s[(s % 1) == 0].astype(int)
    if len(s) < 200:
        return -1.0
    vc = pd.Series(s).value_counts()
    frac_twice = float((vc == 2).mean()) if len(vc) else 0.0
    frac_once = float((vc == 1).mean()) if len(vc) else 0.0
    mn, mx = int(s.min()), int(s.max())
    nunq = int(s.nunique())
    sc = 0.0
    sc += 1.0 if mn == 1 else 0.0
    sc += 1.0 if 500 <= mx <= 20000 else 0.0
    sc += 1.0 if 500 <= nunq <= 20000 else 0.0
    sc += 4.0 * frac_twice
    sc -= 1.5 * frac_once
    return sc

other_cols = [c for c in num.columns if c not in dice_idx]
if not other_cols:
    raise RuntimeError("No non-dice columns left.")
game_col = max(other_cols, key=game_like_score)
game_sc = game_like_score(game_col)
if game_sc < 1.2:
    raise RuntimeError(f"Cannot detect Game-number column (score={game_sc:.3f}).")

def turn_like_score(col_idx) -> float:
    s = num[col_idx].dropna()
    if len(s) < 200:
        return -1.0
    s = s[(s % 1) == 0].astype(int)
    if len(s) < 200:
        return -1.0
    mn, mx = int(s.min()), int(s.max())
    nunq = int(s.nunique())
    uniq_ratio = nunq / max(1, len(s))
    sc = 0.0
    sc += 1.0 if mn == 1 else 0.0
    sc += 1.0 if 2000 <= mx <= 20000 else 0.0
    sc += 2.0 * uniq_ratio
    return sc

turn_col = None
turn_candidates = [c for c in other_cols if c != game_col]
if turn_candidates:
    tc = max(turn_candidates, key=turn_like_score)
    if turn_like_score(tc) > 2.0:
        turn_col = tc

use_cols = []
if turn_col is not None:
    use_cols.append(turn_col)
use_cols.append(game_col)
use_cols.extend(dice_idx)
sub = num[use_cols].copy()
names = (["turn"] if turn_col is not None else []) + ["game"] + [f"r{i+1}" for i in range(6)]
sub.columns = names
dice_cols = [f"r{i+1}" for i in range(6)]

mask = sub[dice_cols].notna().all(axis=1)
for c in dice_cols:
    mask &= sub[c].apply(is_int_1_6)
mask &= sub["game"].notna() & ((sub["game"] % 1) == 0)
sub = sub[mask].copy()
sub["game"] = sub["game"].astype(int)
for c in dice_cols:
    sub[c] = sub[c].astype(int)
if "turn" in sub.columns:
    sub["turn"] = sub["turn"].astype(int)

missing = {"turn": 15, "game": 8, "r1": 4, "r2": 6, "r3": 4, "r4": 2, "r5": 4, "r6": 5}

def ensure_missing_row(sub: pd.DataFrame) -> pd.DataFrame:
    has_turn = "turn" in sub.columns
    if has_turn:
        m = (sub["turn"] == missing["turn"]) & (sub["game"] == missing["game"])
        for c in dice_cols:
            m &= (sub[c] == missing[c])
        exists = bool(m.any())
    else:
        m = (sub["game"] == missing["game"])
        for c in dice_cols:
            m &= (sub[c] == missing[c])
        exists = bool(m.any())
    if not exists:
        row = {k: missing[k] for k in (["turn", "game"] if has_turn else ["game"]) + dice_cols}
        sub = pd.concat([sub, pd.DataFrame([row])], ignore_index=True)
    return sub

sub = ensure_missing_row(sub)

def turn_scores(turn):
    mx = max(turn)
    mn = min(turn)
    high_often = mx * sum(1 for v in turn if v == mx)
    summation = sum(turn)
    highs_lows = mx * mn * (mx - mn)
    only_two = 30 if len(set(turn)) == 2 else 0
    all_numbers = 40 if set(turn) == {1, 2, 3, 4, 5, 6} else 0
    def is_run4(a):
        return (a[0]+1==a[1] and a[1]+1==a[2] and a[2]+1==a[3]) or (a[0]-1==a[1] and a[1]-1==a[2] and a[2]-1==a[3])
    run4 = 50 if any(is_run4(turn[i:i+4]) for i in range(3)) else 0
    return np.array([high_often, summation, highs_lows, only_two, all_numbers, run4], dtype=int)

def best_game_score(s1, s2):
    best = 0
    for i in range(6):
        for j in range(6):
            if i == j:
                continue
            best = max(best, int(s1[i] + s2[j]))
    return best

game_scores = {}
for gid, gdf in sub.groupby("game", sort=True):
    if "turn" in gdf.columns:
        gdf = gdf.sort_values("turn")
    else:
        gdf = gdf.sort_index()
    gdf = gdf.head(2)
    if len(gdf) < 2:
        continue
    t1 = gdf.iloc[0][dice_cols].tolist()
    t2 = gdf.iloc[1][dice_cols].tolist()
    game_scores[int(gid)] = best_game_score(turn_scores(t1), turn_scores(t2))

if not game_scores:
    raise RuntimeError("No game scores computed.")

win_p1 = 0
win_p2 = 0
max_gid = max(game_scores.keys())
for m in range(1, max_gid // 2 + 1):
    g1, g2 = 2*m - 1, 2*m
    if g1 not in game_scores or g2 not in game_scores:
        continue
    if game_scores[g1] > game_scores[g2]:
        win_p1 += 1
    elif game_scores[g2] > game_scores[g1]:
        win_p2 += 1

ans = win_p1 - win_p2

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(str(ans) + "\n")
print(f"[oracle] answer={ans}")
EOF
