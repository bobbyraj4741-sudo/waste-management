# Graph AI for Industrial Waste Management

Graph-AI-based discovery of inefficiencies in England's industrial waste flow
network, using the Environment Agency **2024 Waste Data Interrogator**. A
reproducible Python workflow that cleans facility-level waste data, builds a
directed waste-flow graph, computes interpretable indicators, applies network
analysis, clustering, and graph-embedding anomaly detection, and maps
circularity opportunities.

This implements the 11-module roadmap in
`industrial_waste_graph_ai_roadmap.pdf`.

## Research question

> Can graph-based AI identify hidden inefficiencies in industrial waste
> management networks and highlight facilities, regions, or waste streams where
> recovery can be improved?

## Project layout

```
data/
  raw/         # source .xlsb workbooks + regional summary tables (git-ignored)
  interim/     # combined, renamed movements (movements_raw.parquet)
  processed/   # cleaned data, indicators, graph, embeddings, clusters
docs/
  01_industry_context.md   # Module 1 concept note
  data_dictionary.md       # Module 2 data dictionary + glossary
  final_report.md          # Module 11 final report
figures/       # EDA, network, ML, and circularity plots (PNG)
results/       # summaries and completion-check tables (txt / md / csv)
src/           # the pipeline (one module per roadmap stage)
```

## Setup

Requires Python 3.11+ (developed on 3.14).

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Place the two source workbooks in `data/raw/` (already there if you received the
repo with data):
- `2024 Waste Data Interrogator - Wastes Received (Excel) - Version 2.xlsb`
- `2024 Waste Data Interrogator - Wastes Removed (Excel) - Version 2.xlsb`

Download from the Environment Agency:
<https://environment.data.gov.uk/dataset/a6dc56e6-fdbd-4f06-b8bc-f358cb1ec471>

## Run

Whole pipeline (Modules 2-10) in one go:

```bash
python -m src.run_all
```

Or stage by stage:

```bash
python -m src.s01_load                  # Module 2  - load & organise
python -m src.s02_clean                 # Module 3  - clean & standardise
python -m src.s03_indicators            # Module 4  - indicators & EDA
python -m src.s04_graph                 # Modules 5-6 - graph + network analysis
python -m src.s05_ml                    # Modules 7-8 - clustering + anomaly detection
python -m src.s06_explain_circularity   # Modules 9-10 - explainability + circularity
```

Runtime is a few minutes end-to-end on a laptop.

## Roadmap module -> code / output map

| Module | Code | Key output |
|---|---|---|
| 1 Industry context | - | `docs/01_industry_context.md` |
| 2 Load & organise | `src/s01_load.py` | `docs/data_dictionary.md`, `results/load_summary.txt` |
| 3 Clean & standardise | `src/s02_clean.py` | `results/data_quality_report.md` |
| 4 Indicators & EDA | `src/s03_indicators.py` | `results/top_facilities.md`, `figures/eda_*.png` |
| 5 Build graph | `src/s04_graph.py` | `data/processed/waste_flow_graph.graphml`, `results/graph_summary.txt` |
| 6 Network analysis | `src/s04_graph.py` | `results/top20_centrality.md`, `figures/net_*.png` |
| 7 Clustering | `src/s05_ml.py` | `results/cluster_profiles.md`, `figures/ml_01_*.png` |
| 8 Graph AI anomaly detection | `src/s05_ml.py` | `results/anomalies_ranked.{csv,md}`, `figures/ml_02_*.png` |
| 9 Explainability | `src/s06_explain_circularity.py` | `results/explainability_table.md` |
| 10 Circularity mapping | `src/s06_explain_circularity.py` | `results/circularity_opportunities.md`, `figures/circ_*.png` |
| 11 Final report | - | `docs/final_report.md` |

## Method notes

- **Graph model.** The dataset records the counterparty of each movement as a
  *place/Waste Planning Authority*, not a counterparty permit, so we build a
  directed weighted graph between facilities and places: `place -> facility`
  (received) and `facility -> place` (removed). Edge weight = tonnes. This is
  the honest network the public data supports.
- **Graph embeddings without heavy deps.** gensim / node2vec / PyTorch-Geometric
  do not build on Python 3.14 (roadmap's optional tier). `s05_ml.py` implements
  DeepWalk via its matrix-factorisation equivalent (random walk -> PPMI ->
  Truncated SVD) using only numpy + scikit-learn. To use the "real" tooling on
  an older Python, uncomment the optional block in `requirements.txt`.

## Limitations

No producer-level facility links (confidential); no distance/economic data;
some facilities have missing fate records; anomaly flags indicate statistical
unusualness for human review, not non-compliance. See `docs/final_report.md` §6.

## Data source & licence

Environment Agency, *2024 Waste Data Interrogator* (Open Government Licence).
See `industrial_waste_graph_ai_roadmap.pdf` references.
