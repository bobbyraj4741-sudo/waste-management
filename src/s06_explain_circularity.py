"""Modules 9 & 10 - Explainability + Circularity Opportunity Mapping.

Module 9: for each top anomalous facility, give an indicator-based reason it was
          flagged (compared against its cluster peers) and a plausible practical
          explanation.
Module 10: identify landfill/disposal-dependent facilities and regions, waste
           categories that repeatedly pass through transfer sites without
           recovery, and propose concrete circularity opportunities.

Outputs:
  * results/explainability_table.md      (Module 9 completion check: 3 columns)
  * results/circularity_opportunities.md (Module 10 completion check: >=5 ideas)
  * results/region_recovery_summary.csv
  * figures/circ_*.png

Run:  python -m src.s06_explain_circularity
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from . import config as C

FEATS = ["throughput", "recovery_fraction", "disposal_fraction",
         "transfer_fraction", "hazardous_fraction", "waste_diversity",
         "n_waste_types", "n_counterparties"]


# --------------------------------------------------------------------------- #
# Module 9 - indicator-based explanation
# --------------------------------------------------------------------------- #
def explain(ranked: pd.DataFrame) -> pd.DataFrame:
    cluster_mean = ranked.groupby("cluster")[FEATS].transform("mean")
    cluster_std = ranked.groupby("cluster")[FEATS].transform("std").replace(0, 1e-9)
    z = (ranked[FEATS] - cluster_mean) / cluster_std

    rows = []
    for i, r in ranked.head(20).iterrows():
        zr = z.loc[i]
        reasons, expl = [], []
        if zr["throughput"] > 2:
            reasons.append("unusually high volume vs cluster peers")
            expl.append("dominant regional consolidation point")
        if r["disposal_fraction"] > 0.5:
            reasons.append("high landfill/disposal dependence")
            expl.append("little recovery - candidate for diversion")
        if r["transfer_fraction"] > 0.7:
            reasons.append("high transfer intensity (waste passes through)")
            expl.append("bulking site; recovery happens elsewhere or not at all")
        if r["recovery_fraction"] < 0.05 and r["disposal_fraction"] < 0.05 and r["transfer_fraction"] < 0.05:
            reasons.append("outgoing waste has no clear recovery/disposal fate recorded")
            expl.append("data gap or storage-only site - worth manual review")
        if r["hazardous_fraction"] > 0.6:
            reasons.append("hazardous-waste dominated")
            expl.append("specialised handler; compare only with hazardous peers")
        if zr["n_waste_types"] > 2 or zr["n_counterparties"] > 2:
            reasons.append("unusually diverse waste mix / many counterparties")
            expl.append("acts as a broad regional hub")
        if not reasons:
            reasons.append("multivariate outlier on combined behaviour")
            expl.append("unusual combination of otherwise-normal indicators")
        rows.append({
            "flagged_facility": r["site_name"],
            "region": r["facility_region"],
            "reason_for_flagging": "; ".join(reasons),
            "possible_practical_explanation": "; ".join(expl),
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Module 10 - circularity opportunity mapping
# --------------------------------------------------------------------------- #
def region_recovery(df: pd.DataFrame) -> pd.DataFrame:
    remv = df[df.direction == "removed"]
    g = remv.groupby("facility_region").agg(
        total_out=("tonnes", "sum"),
        recovered=("tonnes", lambda s: s[remv.loc[s.index, "is_recovery"]].sum()),
        disposed=("tonnes", lambda s: s[remv.loc[s.index, "is_disposal"]].sum()),
        transferred=("tonnes", lambda s: s[remv.loc[s.index, "is_transfer"]].sum()),
    )
    g["recovery_rate"] = g["recovered"] / g["total_out"]
    g["disposal_rate"] = g["disposed"] / g["total_out"]
    g["transfer_rate"] = g["transferred"] / g["total_out"]
    return g.sort_values("disposal_rate", ascending=False).round(4)


def transfer_without_recovery(df: pd.DataFrame) -> pd.DataFrame:
    """Waste categories heavily sent to Transfer (D) rather than recovered."""
    remv = df[df.direction == "removed"]
    g = remv.groupby("ewc_chapter").agg(
        total=("tonnes", "sum"),
        transferred=("tonnes", lambda s: s[remv.loc[s.index, "is_transfer"]].sum()),
        recovered=("tonnes", lambda s: s[remv.loc[s.index, "is_recovery"]].sum()),
    )
    g = g[g["total"] > 50_000]
    g["transfer_share"] = g["transferred"] / g["total"]
    g["recovery_share"] = g["recovered"] / g["total"]
    return g.sort_values("transfer_share", ascending=False).round(4)


def opportunities_md(region: pd.DataFrame, cats: pd.DataFrame,
                     ranked: pd.DataFrame) -> str:
    worst_region = region.index[0]
    worst_rate = region["disposal_rate"].iloc[0]
    top_transfer_cat = cats.index[0] if len(cats) else "n/a"
    disp_sites = ranked[ranked["disposal_fraction"] > 0.5].nlargest(5, "throughput")
    disp_list = "\n".join(
        f"  - **{r.site_name}** ({r.facility_region}) - "
        f"{r.disposal_fraction:.0%} disposal on {r.throughput:,.0f} t throughput"
        for r in disp_sites.itertuples()
    ) or "  - (none above threshold)"

    return f"""\
# Module 10 - Circularity Opportunity Mapping

Derived from 2024 removed-waste fates. "Circularity" here means moving tonnage
up the hierarchy: disposal -> recovery, and cutting waste that merely passes
through transfer sites without being recovered.

## Highest-disposal regions (targets for local recovery capacity)
{region[['total_out', 'recovery_rate', 'disposal_rate', 'transfer_rate']].head(5).to_markdown(floatfmt=',.3f')}

## Waste chapters most sent to *transfer* rather than recovered
{cats[['total', 'transfer_share', 'recovery_share']].head(6).to_markdown(floatfmt=',.3f')}

## Facilities with heavy disposal dependence
{disp_list}

## Five concrete improvement opportunities

1. **Add local recovery capacity in {worst_region}** - it has the highest
   disposal rate ({worst_rate:.0%}) of removed waste. Diverting even part of
   this to recovery would materially lift its circularity.
2. **Target EWC chapter "{top_transfer_cat}"** - the category most dominated by
   *transfer* rather than recovery. Waste is being bulked and moved on without
   value being recovered; introduce segregation-at-source or a dedicated
   reprocessing route.
3. **Review high-disposal, high-volume facilities** (listed above) for
   on-site or nearby recovery alternatives before landfill/incineration.
4. **Shorten routing for waste that crosses many intermediate nodes** - high
   transfer-intensity hubs (cluster "High-volume transfer hubs") indicate waste
   travelling through several handlers; direct routing to a recovery endpoint
   cuts cost and emissions.
5. **Improve fate recording for "no-fate" anomalies** - several flagged
   facilities record large throughput with no recovery/disposal/transfer fate;
   fixing this data gap (or confirming storage-only status) is a prerequisite
   for trusting any recovery target.
"""


def plots(region: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    r = region.sort_values("recovery_rate")
    ax.barh(r.index, r["recovery_rate"], color="#55A868", label="recovery")
    ax.barh(r.index, r["disposal_rate"], left=r["recovery_rate"], color="#C44E52", label="disposal")
    ax.barh(r.index, r["transfer_rate"], left=r["recovery_rate"] + r["disposal_rate"],
            color="#8172B3", label="transfer")
    ax.set_xlabel("Share of removed waste"); ax.set_title("Recovery vs disposal vs transfer by region")
    ax.legend(loc="lower right", fontsize=8)
    fig.savefig(C.FIGURES / "circ_01_region_fate_mix.png"); plt.close(fig)
    print("  wrote circularity figure")


def main() -> None:
    print("Modules 9 & 10: explainability + circularity ...")
    df = pd.read_parquet(C.DATA_PROCESSED / "movements_clean.parquet")
    ranked = pd.read_parquet(C.DATA_PROCESSED / "facility_clusters.parquet")

    expl = explain(ranked)
    (C.RESULTS / "explainability_table.md").write_text(
        "# Module 9 - Explainability Table\n\n" + expl.to_markdown(index=False) + "\n")

    region = region_recovery(df)
    region.to_csv(C.RESULTS / "region_recovery_summary.csv")
    cats = transfer_without_recovery(df)
    (C.RESULTS / "circularity_opportunities.md").write_text(
        opportunities_md(region, cats, ranked))
    plots(region)
    print("  wrote explainability_table.md + circularity_opportunities.md")


if __name__ == "__main__":
    main()
