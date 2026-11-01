"""Descriptive ranking and fuzzy synthetic evaluation (FSE) of five-point ratings.

For every item: mean score (MS), standard deviation, relative importance index
(RII = sum W / (A x N), A = 5), rank, and a one-sample t-test against a test value
(default 3.5, one-tailed, H1: mean > 3.5).

For every group of items, FSE follows Xu et al. (2010) and Ameyaw and Chan (2015):
  weights        w_i = M_i / sum(M_i) within the group              (thesis Eq. 3.4)
  membership     R_i = proportion of respondents choosing grades 1..5
  group vector   D   = w . R
  group index    FSE = sum(D_g x g), g = 1..5
A second level combines groups into an overall index, weighting each group by its
mean score.

Usage:
    python src/fse.py --ratings data/synthetic_ce_ratings.csv --items data/ce_items.csv --label circularity
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

GRADES = np.arange(1, 6)


def descriptives(df: pd.DataFrame, items: pd.DataFrame, test_value: float) -> pd.DataFrame:
    n = len(df)
    out = []
    for code, group, item in items[["code", "group", "item"]].itertuples(index=False):
        x = df[code].dropna()
        t, p = stats.ttest_1samp(x, test_value, alternative="greater")
        out.append({"code": code, "group": group, "item": item, "n": len(x),
                    "mean": x.mean(), "sd": x.std(ddof=1), "rii": x.sum() / (5 * n),
                    "t": t, "p_one_tailed": p, "significant_0.05": p < 0.05})
    res = pd.DataFrame(out)
    res["rank"] = res["mean"].rank(ascending=False, method="min").astype(int)
    return res.sort_values("rank")


def membership(x: pd.Series) -> np.ndarray:
    counts = x.value_counts().reindex(GRADES, fill_value=0).to_numpy()
    return counts / counts.sum()


def fse(df: pd.DataFrame, items: pd.DataFrame) -> tuple:
    rows, vectors = [], {}
    for group, sub in items.groupby("group", sort=True):
        codes = sub["code"].tolist()
        means = df[codes].mean()
        w = (means / means.sum()).to_numpy()
        R = np.vstack([membership(df[c]) for c in codes])
        D = w @ R
        vectors[group] = D
        rows.append({"group": group, "n_items": len(codes), "group_mean": means.mean(),
                     **{f"mu_{g}": D[g - 1] for g in GRADES}, "fse_index": float(D @ GRADES)})
    groups = pd.DataFrame(rows)
    gw = (groups["group_mean"] / groups["group_mean"].sum()).to_numpy()
    overall_D = gw @ np.vstack([vectors[g] for g in groups["group"]])
    groups["group_weight"] = gw
    groups["rank"] = groups["fse_index"].rank(ascending=False, method="min").astype(int)
    overall = float(overall_D @ GRADES)
    return groups.sort_values("rank"), overall


def plot(groups: pd.DataFrame, labels: dict, title: str, path: str) -> None:
    g = groups.sort_values("fse_index")
    fig, ax = plt.subplots(figsize=(9, 0.55 * len(g) + 1.4))
    names = [f"{x}: {labels.get(x, '')}" if labels.get(x) else x for x in g["group"]]
    ax.barh(names, g["fse_index"], color="#4a7c59")
    for y, v in enumerate(g["fse_index"]):
        ax.text(v + 0.03, y, f"{v:.2f}", va="center", fontsize=9)
    ax.axvline(3.5, ls="--", lw=1, color="grey")
    ax.set_xlim(1, 5)
    ax.set_xlabel("FSE index (1 = very low, 5 = very high)")
    fig.suptitle(title, x=0.02, ha="left", fontsize=12)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ratings", required=True)
    ap.add_argument("--items", required=True, help="CSV with columns code, group, item")
    ap.add_argument("--label", required=True, help="name used for output files, e.g. circularity")
    ap.add_argument("--test-value", type=float, default=3.5)
    ap.add_argument("--outdir", default="results")
    a = ap.parse_args()

    from items import CE_CLUSTERS, NZS_GROUPS
    labels = {**CE_CLUSTERS, **NZS_GROUPS}
    os.makedirs(a.outdir, exist_ok=True)
    df, items = pd.read_csv(a.ratings), pd.read_csv(a.items)

    desc = descriptives(df, items, a.test_value)
    groups, overall = fse(df, items)
    desc.round(4).to_csv(f"{a.outdir}/{a.label}_item_ranking.csv", index=False)
    groups.round(4).to_csv(f"{a.outdir}/{a.label}_fse_index.csv", index=False)
    plot(groups, labels, f"Fuzzy synthetic evaluation: {a.label} index", f"{a.outdir}/{a.label}_fse_index.png")

    print(f"\n=== {a.label} (n = {len(df)}) ===")
    print(f"Items significantly above {a.test_value}: {int(desc['significant_0.05'].sum())} of {len(desc)}")
    print("Top five items:")
    print(desc.head(5)[["rank", "code", "item", "mean", "sd", "rii"]].round(3).to_string(index=False))
    print("\nGroup FSE indices:")
    print(groups[["rank", "group", "fse_index", "group_weight"]].round(3).to_string(index=False))
    print(f"Overall {a.label} index: {overall:.3f}")


if __name__ == "__main__":
    main()
