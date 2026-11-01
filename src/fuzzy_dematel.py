"""Fuzzy DEMATEL with a leave-one-expert-out stability check.

Steps (Wu and Lee, 2007; Opricovic and Tzeng, 2003):
  1. Convert each expert's linguistic ratings (0-4) to triangular fuzzy numbers.
  2. Defuzzify each expert's matrix with CFCS (converting fuzzy data into crisp scores).
  3. Average the crisp matrices across experts to give the direct-relation matrix Z.
  4. Normalise: X = Z / max(max row sum, max column sum).
  5. Total-relation matrix: T = X (I - X)^-1                         (thesis Eq. 3.5)
  6. D = row sums, R = column sums; prominence = D + R, relation = D - R.
     Positive relation marks a cause factor, negative an effect factor.
  7. Threshold = mean of T; links above it are reported as significant influences.
  8. Stability: T is recomputed with each expert left out in turn. The panel is
     judged adequate if no factor switches between cause and effect in any run.
     Factors with |D - R| close to zero sit on the boundary and can switch with
     any panel size, so switches inside a borderline band (--band) are reported
     separately from switches of clearly classified factors.

Usage:
    python src/fuzzy_dematel.py --data data/synthetic_dematel_experts.csv --outdir results
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from items import DEMATEL_FACTORS, LINGUISTIC_SCALE


def cfcs(L: np.ndarray, M: np.ndarray, U: np.ndarray) -> np.ndarray:
    """CFCS defuzzification of one expert's fuzzy matrix (Opricovic and Tzeng, 2003)."""
    lo, hi = L.min(), U.max()
    delta = hi - lo if hi > lo else 1.0
    xl, xm, xr = (L - lo) / delta, (M - lo) / delta, (U - lo) / delta
    xls = xm / (1 + xm - xl)
    xrs = xr / (1 + xr - xm)
    x = (xls * (1 - xls) + xrs * xrs) / (1 - xls + xrs)
    return lo + x * delta


def expert_matrices(long: pd.DataFrame, factors: list) -> dict:
    idx = {f: i for i, f in enumerate(factors)}
    k = len(factors)
    tfn = {code: v[1] for code, v in LINGUISTIC_SCALE.items()}
    mats = {}
    for e, sub in long.groupby("expert"):
        L, M, U = np.zeros((k, k)), np.zeros((k, k)), np.zeros((k, k))
        for r in sub.itertuples(index=False):
            l, m, u = tfn[int(r.rating)]
            i, j = idx[r[1]], idx[r[2]]
            L[i, j], M[i, j], U[i, j] = l, m, u
        crisp = cfcs(L, M, U)
        np.fill_diagonal(crisp, 0)
        mats[e] = crisp
    return mats


def dematel(mats: list, factors: list) -> tuple:
    Z = np.mean(mats, axis=0)
    s = max(Z.sum(axis=1).max(), Z.sum(axis=0).max())
    X = Z / s
    T = X @ np.linalg.inv(np.eye(len(factors)) - X)
    D, R = T.sum(axis=1), T.sum(axis=0)
    res = pd.DataFrame({"D": D, "R": R, "prominence": D + R, "relation": D - R}, index=factors)
    res["role"] = np.where(res["relation"] > 0, "cause", "effect")
    return pd.DataFrame(T, index=factors, columns=factors), res


def stability(mats: dict, factors: list, full: pd.DataFrame, band: float) -> pd.DataFrame:
    """Leave-one-expert-out check. Factors whose full-panel |D - R| is below `band`
    are treated as borderline: a switch there is reported but not counted as failure."""
    borderline = set(full.index[full["relation"].abs() < band])
    rows = []
    for left_out in mats:
        _, res = dematel([m for e, m in mats.items() if e != left_out], factors)
        switched = [f for f in factors if res.loc[f, "role"] != full.loc[f, "role"]]
        firm = [f for f in switched if f not in borderline]
        rows.append({"left_out": left_out, "n_switched": len(switched), "switched": "; ".join(switched),
                     "n_switched_outside_band": len(firm), "switched_outside_band": "; ".join(firm)})
    return pd.DataFrame(rows)


def plot(res: pd.DataFrame, path: str) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    colours = np.where(res["relation"] > 0, "#b5562f", "#2f6f8f")
    ax.scatter(res["prominence"], res["relation"], c=colours, s=60, zorder=3)
    xr = res["prominence"].max() - res["prominence"].min() or 1
    yr = res["relation"].max() - res["relation"].min() or 1
    placed = []
    for f, r in res.sort_values("relation", ascending=False).iterrows():
        x, y = r["prominence"], r["relation"]
        k = sum(1 for (px, py) in placed if abs(px - x) / xr < 0.06 and abs(py - y) / yr < 0.06)
        placed.append((x, y))
        ax.annotate(f, (x, y), xytext=(6, 4 - 12 * k), textcoords="offset points", fontsize=9)
    ax.axhline(0, color="grey", lw=1)
    ax.set_xlabel("Prominence (D + R)")
    ax.set_ylabel("Relation (D - R)")
    ax.set_title("Fuzzy DEMATEL cause-effect diagram")
    ax.text(0.01, 0.97, "Cause group", transform=ax.transAxes, va="top", color="#b5562f")
    ax.text(0.01, 0.03, "Effect group", transform=ax.transAxes, va="bottom", color="#2f6f8f")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default="data/synthetic_dematel_experts.csv",
                    help="long format: expert, from, to, rating (0-4)")
    ap.add_argument("--outdir", default="results")
    ap.add_argument("--band", type=float, default=0.05,
                    help="|D - R| below this value marks a borderline factor (default 0.05)")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    long = pd.read_csv(a.data)
    factors = [f for f in DEMATEL_FACTORS if f in set(long["from"]) | set(long["to"])]
    mats = expert_matrices(long, factors)
    T, res = dematel(list(mats.values()), factors)
    threshold = float(T.to_numpy().mean())
    links = (T.stack().rename("t").reset_index().rename(columns={"level_0": "from", "level_1": "to"}))
    links = links[(links["from"] != links["to"]) & (links["t"] > threshold)].sort_values("t", ascending=False)
    stab = stability(mats, factors, res, a.band)

    res.insert(0, "factor_name", [DEMATEL_FACTORS[f] for f in res.index])
    T.round(4).to_csv(f"{a.outdir}/dematel_total_relation.csv")
    res.round(4).sort_values("relation", ascending=False).to_csv(f"{a.outdir}/dematel_cause_effect.csv")
    links.round(4).to_csv(f"{a.outdir}/dematel_significant_links.csv", index=False)
    stab.to_csv(f"{a.outdir}/dematel_stability.csv", index=False)
    plot(res, f"{a.outdir}/dematel_cause_effect.png")

    print(f"Experts: {len(mats)}  |  factors: {len(factors)}  |  threshold (mean of T): {threshold:.4f}")
    print(res.sort_values("relation", ascending=False)[["factor_name", "prominence", "relation", "role"]].round(3).to_string())
    print(f"\nLinks above threshold: {len(links)}")
    border = res.index[res["relation"].abs() < a.band].tolist()
    print(f"\nBorderline factors (|D - R| < {a.band}): {', '.join(border) if border else 'none'}")
    strict = (stab["n_switched"] == 0).all()
    banded = (stab["n_switched_outside_band"] == 0).all()
    print("Leave-one-expert-out, strict rule (no factor may switch):", "PASS" if strict else "FAIL")
    print("Leave-one-expert-out, outside the borderline band:", "PASS" if banded else "FAIL")
    if not strict:
        print(stab[stab.n_switched > 0][["left_out", "switched", "switched_outside_band"]].to_string(index=False))


if __name__ == "__main__":
    main()
