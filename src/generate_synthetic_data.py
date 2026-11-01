"""Generate synthetic survey and expert data shaped like the thesis instruments.

None of these files contain real responses. They are simulated so that the
analysis code can be shared publicly before (and without) releasing fieldwork data.

Outputs in data/:
  ce_items.csv, nzs_items.csv            item inventories (code, group, item)
  synthetic_ce_ratings.csv               385 x 29 five-point ratings (Instrument A, Section B)
  synthetic_nzs_operational.csv          385 x 30 ratings of operational contribution (Section C)
  synthetic_nzs_embodied.csv             385 x 30 ratings of embodied contribution (Section C)
  synthetic_dematel_experts.csv          12 experts' linguistic ratings of 10 x 10 factors (Instrument B)

Usage:
    python src/generate_synthetic_data.py --n 385 --experts 12 --seed 2026
"""
import argparse
import os

import numpy as np
import pandas as pd

from items import CE_ITEMS, DEMATEL_FACTORS, NZS_ITEMS


def likert(rng, n, centre, spread=0.9):
    """Draw five-point ratings around a latent centre."""
    x = rng.normal(centre, spread, n)
    return np.clip(np.rint(x), 1, 5).astype(int)


def survey(rng, items, centres, n):
    data = {code: likert(rng, n, centres[code]) for code, _, _ in items}
    df = pd.DataFrame(data)
    df.insert(0, "respondent_id", [f"R{i:03d}" for i in range(1, n + 1)])
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=385)
    ap.add_argument("--experts", type=int, default=12)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--outdir", default="data")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    os.makedirs(a.outdir, exist_ok=True)

    pd.DataFrame(CE_ITEMS, columns=["code", "group", "item"]).to_csv(f"{a.outdir}/ce_items.csv", index=False)
    pd.DataFrame(NZS_ITEMS, columns=["code", "group", "item"]).to_csv(f"{a.outdir}/nzs_items.csv", index=False)

    # Circular principles: design and efficiency items rated more applicable than
    # market-dependent reuse and enabling-infrastructure items (an assumed pattern).
    cluster_centre = {"A": 3.3, "B": 3.9, "C": 3.4, "D": 3.2, "E": 3.8, "F": 2.9}
    ce_c = {c: cluster_centre[g] + rng.normal(0, 0.25) for c, g, _ in CE_ITEMS}
    survey(rng, CE_ITEMS, ce_c, a.n).to_csv(f"{a.outdir}/synthetic_ce_ratings.csv", index=False)

    # Net-zero strategies: operational vs embodied contribution differ by group
    op = {"S1": 4.0, "S2": 3.9, "S3": 2.9, "S4": 3.0}
    em = {"S1": 3.1, "S2": 2.5, "S3": 4.0, "S4": 3.6}
    op_c = {c: op[g] + rng.normal(0, 0.2) for c, g, _ in NZS_ITEMS}
    em_c = {c: em[g] + rng.normal(0, 0.2) for c, g, _ in NZS_ITEMS}
    survey(rng, NZS_ITEMS, op_c, a.n).to_csv(f"{a.outdir}/synthetic_nzs_operational.csv", index=False)
    survey(rng, NZS_ITEMS, em_c, a.n).to_csv(f"{a.outdir}/synthetic_nzs_embodied.csv", index=False)

    # DEMATEL: an assumed "true" influence structure on the 0-4 scale.
    f = list(DEMATEL_FACTORS)
    k = len(f)
    base = np.full((k, k), 1.0)
    idx = {name: i for i, name in enumerate(f)}

    def set_(src, dst, v):
        base[idx[src], idx[dst]] = v

    for dst in f:                       # enabling factors drive most others
        set_("S4", dst, 3.0)
        set_("CE-F", dst, 2.8)
    for src in ["CE-A", "CE-B", "CE-E"]:  # design principles shape passive design
        set_(src, "S1", 3.0)
        set_(src, "S3", 2.6)
    for src in ["CE-C", "CE-D"]:        # material practices act on embodied measures
        set_(src, "S3", 3.2)
        set_(src, "S2", 1.6)
    set_("S1", "S2", 2.6)               # passive form reduces need for active measures
    for dst in f:                       # S2 mostly receives influence
        set_("S2", dst, 0.8)
    np.fill_diagonal(base, 0)

    rows = []
    for e in range(1, a.experts + 1):
        noisy = np.clip(np.rint(base + rng.normal(0, 0.7, (k, k))), 0, 4).astype(int)
        np.fill_diagonal(noisy, 0)
        for i in range(k):
            for j in range(k):
                if i != j:
                    rows.append({"expert": f"E{e:02d}", "from": f[i], "to": f[j], "rating": int(noisy[i, j])})
    pd.DataFrame(rows).to_csv(f"{a.outdir}/synthetic_dematel_experts.csv", index=False)
    print(f"Synthetic data written to {a.outdir}/")


if __name__ == "__main__":
    main()
