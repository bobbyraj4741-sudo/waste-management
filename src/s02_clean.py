"""Module 3 - Clean and Standardize the Data.

Takes data/interim/movements_raw.parquet and produces an analysis-ready table:

  * data/processed/movements_clean.parquet
  * results/data_quality_report.md   (missing values, duplicates, summary stats)

Cleaning steps (mirroring the roadmap):
  1. Drop empty / non-informative rows (no permit or no tonnes).
  2. Column names are already lowercase snake_case from the load stage.
  3. Coerce tonnes to numeric, drop negatives, treat 0 as valid-but-flagged.
  4. Standardise categorical text (strip, collapse whitespace, title/lower).
  5. Record missingness of key fields.
  6. Derive recovery / disposal / transfer / treatment flags from `fate`.

Run:  python -m src.s02_clean
"""
from __future__ import annotations

import pandas as pd

from . import config as C


def _std_text(s: pd.Series) -> pd.Series:
    """Strip, collapse internal whitespace; keep original casing for names."""
    return (
        s.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .replace({"": pd.NA})
    )


def clean(df: pd.DataFrame) -> pd.DataFrame:
    n0 = len(df)

    # 1. Standardise all object/string columns.
    text_cols = df.select_dtypes(include=["object", "string"]).columns
    for c in text_cols:
        df[c] = _std_text(df[c])

    # Lower-case the categorical fields we group / branch on (robust matching).
    for c in ("fate", "site_category", "basic_waste_cat", "form"):
        if c in df.columns:
            df[c] = df[c].str.lower()
    if "r_and_d_code" in df.columns:
        df["r_and_d_code"] = df["r_and_d_code"].str.upper()

    # 2. Numeric tonnes; drop rows that can't anchor an edge weight.
    df["tonnes"] = pd.to_numeric(df["tonnes"], errors="coerce")
    df = df[df["tonnes"].notna()]
    df = df[df["tonnes"] >= 0]

    # 3. Drop rows with no facility permit (can't be a node).
    df = df[df["permit"].notna() & (df["permit"].str.len() > 0)]

    # 4. Derive recovery/disposal signals from `fate`.
    fate = df["fate"].fillna("")
    df["is_recovery"] = fate.isin(C.RECOVERY_FATES)
    df["is_disposal"] = fate.isin(C.DISPOSAL_FATES)
    df["is_transfer"] = fate.isin(C.TRANSFER_FATES)
    df["is_treatment"] = fate.isin(C.TREATMENT_FATES)

    # Secondary recovery signal from the R/D operation code.
    code = df["r_and_d_code"].fillna("")
    df["code_is_recovery"] = code.str.startswith(C.RECOVERY_CODE_PREFIX)
    df["code_is_disposal"] = code.str.startswith(C.DISPOSAL_CODE_PREFIX)

    print(f"  cleaned {n0:,} -> {len(df):,} rows ({n0 - len(df):,} dropped)")
    return df.reset_index(drop=True)


def quality_report(raw: pd.DataFrame, clean_df: pd.DataFrame) -> str:
    key_fields = ["permit", "site_name", "waste_code", "counterparty", "fate", "tonnes"]
    miss = raw[key_fields].isna().mean().mul(100).round(2)
    miss_tbl = "\n".join(f"| `{k}` | {v}% |" for k, v in miss.items())

    n_dup = raw.duplicated().sum()
    t = clean_df["tonnes"]
    stats = t.describe(percentiles=[0.25, 0.5, 0.75, 0.95, 0.99])
    stats_tbl = "\n".join(f"| {k} | {v:,.2f} |" for k, v in stats.items())

    zero_share = (t == 0).mean() * 100

    return f"""\
# Data Quality Report - 2024 Waste Data Interrogator

## Row accounting
- Raw movement rows: **{len(raw):,}**
- Clean movement rows: **{len(clean_df):,}**
- Rows dropped (missing permit / tonnes, negative tonnes): **{len(raw) - len(clean_df):,}**
- Exact duplicate rows in raw table: **{n_dup:,}**
  (kept intentionally - identical multi-load records are legitimate repeat movements)

## Missing values in key fields (raw)
| Field | % missing |
|---|---|
{miss_tbl}

## Tonnes distribution (clean)
| Statistic | Tonnes |
|---|---|
{stats_tbl}

- Records with exactly 0 tonnes: **{zero_share:.2f}%** (kept; represent permitted-but-nil movements)

## Categorical coverage (clean)
- Unique facilities (permits): **{clean_df['permit'].nunique():,}**
- Unique waste codes: **{clean_df['waste_code'].nunique():,}**
- Fate categories: {', '.join(sorted(clean_df['fate'].dropna().unique()))}
- Site categories: {', '.join(sorted(clean_df['site_category'].dropna().unique()))}
"""


def main() -> None:
    print("Module 3: cleaning & standardising ...")
    raw = pd.read_parquet(C.DATA_INTERIM / "movements_raw.parquet")
    clean_df = clean(raw.copy())

    out = C.DATA_PROCESSED / "movements_clean.parquet"
    clean_df.to_parquet(out, index=False)
    print(f"  wrote {out}")

    report = quality_report(raw, clean_df)
    (C.RESULTS / "data_quality_report.md").write_text(report)
    print(f"  wrote {C.RESULTS / 'data_quality_report.md'}")


if __name__ == "__main__":
    main()
