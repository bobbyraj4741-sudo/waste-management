# Graph-AI Discovery of Inefficiencies in England's Industrial Waste Flow Network

*A reproducible workflow over the 2024 Waste Data Interrogator (Environment Agency).*

---

## 1. Introduction

Descriptive waste statistics - total tonnage, landfill percentage, recycling
percentage - tell us *how much* waste exists but not *how it moves*. This project
treats England's 2024 regulated-waste data as a **directed weighted flow
network** and asks:

> *Can graph-based AI identify hidden inefficiencies in industrial waste
> management networks and highlight facilities, regions, or waste streams where
> recovery can be improved?*

## 2. Dataset

Environment Agency **2024 Waste Data Interrogator** - facility-level waste
**received** and **removed** for ~6,000 permitted sites in England.

- **489,399** clean movement records (352,275 received + 137,178 removed).
- **6,860** regulated facilities; **765** distinct EWC waste codes.
- **358 million tonnes** of movements recorded.

*Limitation baked into the model*: the counterparty is a **place/WPA**, not a
counterparty permit, so facility-to-facility links are not observable
(producer-level data is commercially confidential). See
[`docs/01_industry_context.md`](01_industry_context.md).

## 3. Methodology

| Step | Method | Output |
|---|---|---|
| Clean | drop no-permit / no-tonnage rows, standardise categoricals, derive recovery/disposal/transfer flags from `fate` + R/D codes | `data/processed/movements_clean.parquet` |
| Indicators | per-facility received/removed tonnage, waste diversity (Shannon entropy), recovery/disposal/transfer/hazardous fractions | `facility_indicators.parquet` |
| Graph | directed weighted graph: place -> facility (received), facility -> place (removed); edge weight = tonnes | `waste_flow_graph.graphml.gz` |
| Network analysis | in/out degree, weighted degree, tonnage-weighted betweenness, Louvain communities | `top20_centrality.md` |
| Clustering | KMeans (k=6) on scaled behaviour features | `cluster_profiles.md` |
| Graph AI | Isolation Forest on features **+** DeepWalk-as-matrix-factorisation node embeddings (random walk -> PPMI -> Truncated SVD) with a second Isolation Forest; scores combined | `anomalies_ranked.csv` |
| Explainability | indicator-based reason per flagged facility vs cluster peers | `explainability_table.md` |
| Circularity | region/chapter disposal & transfer analysis | `circularity_opportunities.md` |

> **Note on Graph AI tooling.** gensim / node2vec / PyTorch-Geometric do not
> build on Python 3.14 (the roadmap lists them as the optional "if time permits"
> tier). We implement DeepWalk via its matrix-factorisation equivalent (Qiu et
> al. 2018) using only numpy + scikit-learn, so the graph-embedding path is fully
> reproducible without those dependencies.

## 4. Results

### 4.1 The network
7,284 nodes (6,860 facilities + 424 places), 115,913 directed edges, average
degree 31.8, a single connected component covering 100% of nodes. England's
regulated waste system is one tightly-linked network, not isolated islands.

### 4.2 Fate mix (removed waste, 119.3 Mt)
- **Recovery 59.4%**, Treatment 9.6%, **Disposal 23.7%** (landfill +
  incineration), Transfer 5.8%. Roughly a quarter of removed waste still goes to
  disposal - the headline circularity gap.

### 4.3 Hubs (betweenness)
The top-20 betweenness facilities are large transfer stations and treatment sites
that consolidate waste for whole sub-regions - the network's load-bearing hubs
(see [`results/top20_centrality.md`](../results/top20_centrality.md)).

### 4.4 Facility behaviour clusters (k=6)
Diverse recovery facilities, near-pure recovery sites, hazardous-waste
specialists, high-volume transfer hubs, and disposal-dependent / general
treatment sites (see [`results/cluster_profiles.md`](../results/cluster_profiles.md)).

### 4.5 Anomalies
The combined tabular+graph detector surfaces high-throughput sites with no
recorded recovery fate, 100%-disposal transfer stations, and unusually
diverse-mix hubs (see [`results/anomalies_ranked.md`](../results/anomalies_ranked.md)).

### 4.6 Circularity gaps
Highest-disposal region: **East Midlands (31%)**. The most transfer-dominated
(rather than recovered) stream is **EWC ch.17 Construction & Demolition**. Five
concrete opportunities in
[`results/circularity_opportunities.md`](../results/circularity_opportunities.md).

## 5. Discussion

Graph framing turns a compliance dataset into operational intelligence: it
pinpoints *where* in the network recovery fails (specific regions, waste
chapters, and facilities) rather than only reporting an aggregate rate. The
hub and anomaly lists are directly actionable for planners - they name the sites
where a recovery intervention would propagate furthest.

## 6. Limitations

- **No producer-level links** - counterparty is a place, not a facility; true
  facility-to-facility routing is unobservable.
- **No distance/economic data** - "inefficiency" is measured by fate mix and
  network position, not by transport cost or emissions.
- **Fate data gaps** - some high-volume sites record no recovery/disposal/
  transfer fate; these are flagged but not resolved.
- **Anomaly != wrongdoing** - flags mark statistical unusualness needing human
  review, not non-compliance.

## 7. Conclusion

A public compliance dataset can be converted into circular-economy intelligence.
Representing 2024 waste movements as a graph and layering classical network
analysis, clustering, and graph-embedding anomaly detection on top identifies
concrete facilities, regions, and waste streams where recovery can be improved -
answering the research question in the affirmative.

---

### Reproducing
See [`README.md`](../README.md). One command: `python -m src.run_all`.
