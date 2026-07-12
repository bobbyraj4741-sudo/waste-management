"""Module 4 - Basic Waste Management Indicators + Exploratory Data Analysis.

Builds a per-facility indicator table and at least five interpreted EDA plots.

Outputs:
  * data/processed/facility_indicators.parquet
  * results/facility_indicators.csv
  * results/top_facilities.md
  * figures/eda_*.png   (>= 5 plots)

Run:  python -m src.s03_indicators
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import config as C

plt.rcParams.update({"figure.dpi": 110, "savefig.bbox": "tight", "font.size": 10})


def facility_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """One row per regulated facility (permit) with interpretable indicators."""
    recv = df[df.direction == "received"]
    remv = df[df.direction == "removed"]

    # Static facility attributes (take the modal / first non-null per permit).
    attrs = (
        df.sort_values("tonnes", ascending=False)
        .groupby("permit")
        .agg(
            site_name=("site_name", "first"),
            operator=("operator", "first"),
            site_category=("site_category", "first"),
            facility_type=("facility_type", "first"),
            facility_region=("facility_region", "first"),
            facility_wpa=("facility_wpa", "first"),
        )
    )

    total_in = recv.groupby("permit")["tonnes"].sum().rename("tonnes_received")
    total_out = remv.groupby("permit")["tonnes"].sum().rename("tonnes_removed")
    n_waste_types = df.groupby("permit")["waste_code"].nunique().rename("n_waste_types")
    n_counterparties = df.groupby("permit")["counterparty"].nunique().rename("n_counterparties")

    # Fate fractions computed on REMOVED waste (what the site does with waste).
    def _frac(mask_col: str, name: str) -> pd.Series:
        num = remv[remv[mask_col]].groupby("permit")["tonnes"].sum()
        den = remv.groupby("permit")["tonnes"].sum()
        return (num / den).rename(name)

    recovery_frac = _frac("is_recovery", "recovery_fraction")
    disposal_frac = _frac("is_disposal", "disposal_fraction")
    transfer_frac = _frac("is_transfer", "transfer_fraction")
    treatment_frac = _frac("is_treatment", "treatment_fraction")

    # Hazardous fraction over all handled waste.
    haz = df[df.basic_waste_cat == "hazardous"].groupby("permit")["tonnes"].sum()
    allt = df.groupby("permit")["tonnes"].sum()
    haz_frac = (haz / allt).rename("hazardous_fraction")

    ind = (
        attrs.join([total_in, total_out, n_waste_types, n_counterparties,
                    recovery_frac, disposal_frac, transfer_frac, treatment_frac, haz_frac])
        .fillna({"tonnes_received": 0.0, "tonnes_removed": 0.0})
    )
    frac_cols = ["recovery_fraction", "disposal_fraction", "transfer_fraction",
                 "treatment_fraction", "hazardous_fraction"]
    ind[frac_cols] = ind[frac_cols].fillna(0.0)
    ind["throughput"] = ind["tonnes_received"] + ind["tonnes_removed"]
    # Waste diversity: Shannon entropy over the site's waste-code tonnage mix.
    ind["waste_diversity"] = _waste_diversity(df)
    return ind.reset_index()


def _waste_diversity(df: pd.DataFrame) -> pd.Series:
    mix = df.groupby(["permit", "waste_code"])["tonnes"].sum()
    tot = mix.groupby(level=0).transform("sum")
    p = (mix / tot).replace(0, np.nan)
    ent = -(p * np.log(p)).groupby(level=0).sum()
    return ent.rename("waste_diversity")


def eda_plots(df: pd.DataFrame, ind: pd.DataFrame) -> None:
    # 1. Total tonnes by fate.
    fig, ax = plt.subplots(figsize=(7, 4))
    by_fate = df.groupby("fate")["tonnes"].sum().sort_values(ascending=False) / 1e6
    by_fate.plot.bar(ax=ax, color="#4C72B0")
    ax.set_ylabel("Million tonnes"); ax.set_xlabel("Fate")
    ax.set_title("Total waste (Mt) by fate - 2024")
    plt.xticks(rotation=30, ha="right")
    fig.savefig(C.FIGURES / "eda_01_tonnes_by_fate.png"); plt.close(fig)

    # 2. Tonnes by facility region and direction.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    piv = (df.groupby(["facility_region", "direction"])["tonnes"].sum()
           .unstack(fill_value=0) / 1e6).sort_values("received", ascending=False)
    piv.plot.bar(ax=ax, color={"received": "#55A868", "removed": "#C44E52"})
    ax.set_ylabel("Million tonnes"); ax.set_xlabel("Facility region")
    ax.set_title("Waste received vs removed by region (Mt)")
    plt.xticks(rotation=40, ha="right"); ax.legend(title="direction")
    fig.savefig(C.FIGURES / "eda_02_region_direction.png"); plt.close(fig)

    # 3. Tonnes by site category.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    (df.groupby("site_category")["tonnes"].sum().sort_values(ascending=False).head(12) / 1e6
     ).plot.barh(ax=ax, color="#8172B3")
    ax.set_xlabel("Million tonnes"); ax.set_ylabel("Site category")
    ax.set_title("Top site categories by tonnage (Mt)")
    ax.invert_yaxis()
    fig.savefig(C.FIGURES / "eda_03_site_category.png"); plt.close(fig)

    # 4. Dominant waste categories (basic).
    fig, ax = plt.subplots(figsize=(6, 4))
    (df.groupby("basic_waste_cat")["tonnes"].sum().sort_values(ascending=False) / 1e6
     ).plot.bar(ax=ax, color="#CCB974")
    ax.set_ylabel("Million tonnes"); ax.set_xlabel("Basic waste category")
    ax.set_title("Tonnage by basic waste category (Mt)")
    plt.xticks(rotation=15, ha="right")
    fig.savefig(C.FIGURES / "eda_04_basic_waste_cat.png"); plt.close(fig)

    # 5. Distribution of facility recovery fraction.
    fig, ax = plt.subplots(figsize=(7, 4))
    active = ind[ind.tonnes_removed > 0]
    ax.hist(active["recovery_fraction"], bins=30, color="#4C72B0", edgecolor="white")
    ax.set_xlabel("Recovery fraction of removed waste")
    ax.set_ylabel("Number of facilities")
    ax.set_title("How much of each facility's outgoing waste goes to recovery")
    fig.savefig(C.FIGURES / "eda_05_recovery_fraction_hist.png"); plt.close(fig)

    # 6. Throughput vs recovery scatter (log-x).
    fig, ax = plt.subplots(figsize=(7, 4.5))
    a = ind[ind.throughput > 0]
    ax.scatter(a["throughput"], a["recovery_fraction"], s=8, alpha=0.3, color="#C44E52")
    ax.set_xscale("log")
    ax.set_xlabel("Facility throughput (tonnes, log scale)")
    ax.set_ylabel("Recovery fraction")
    ax.set_title("Scale vs recovery behaviour across facilities")
    fig.savefig(C.FIGURES / "eda_06_throughput_vs_recovery.png"); plt.close(fig)
    print(f"  wrote 6 EDA figures to {C.FIGURES}")


def top_tables(ind: pd.DataFrame) -> str:
    def _fmt(sub, cols):
        return sub[cols].to_markdown(index=False, floatfmt=",.0f")

    top_recv = ind.nlargest(15, "tonnes_received")
    top_remv = ind.nlargest(15, "tonnes_removed")
    cols = ["site_name", "facility_region", "site_category", "tonnes_received", "tonnes_removed"]
    return f"""\
# Module 4 - Top Facilities & Indicators

## Top 15 facilities by waste RECEIVED
{_fmt(top_recv, cols)}

## Top 15 facilities by waste REMOVED
{_fmt(top_remv, cols)}

## Region x site-category tonnage (Mt) - see figures/eda_02, eda_03.
"""


def main() -> None:
    print("Module 4: indicators & EDA ...")
    df = pd.read_parquet(C.DATA_PROCESSED / "movements_clean.parquet")
    ind = facility_indicators(df)

    ind.to_parquet(C.DATA_PROCESSED / "facility_indicators.parquet", index=False)
    ind.to_csv(C.RESULTS / "facility_indicators.csv", index=False)
    print(f"  {len(ind):,} facilities x {ind.shape[1]} indicators")

    (C.RESULTS / "top_facilities.md").write_text(top_tables(ind))
    eda_plots(df, ind)
    print("  wrote results/top_facilities.md")


if __name__ == "__main__":
    main()
