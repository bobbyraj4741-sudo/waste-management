# Codebase Walkthrough — A Beginner's Guide

This guide explains **how the whole project is built**, in plain language, for
someone new to the code (or to data pipelines in general). It assumes you can
read a little Python but not that you know pandas, networkx, or machine
learning. Read it top-to-bottom once and you'll understand every file.

If you just want to *run* the project, see [`README.md`](../README.md). This
document is about *how it works inside*.

---

## 1. The big idea in one picture

We take a government spreadsheet about waste, turn it into a **network** (dots
joined by arrows), and use that network to find where recycling is failing.

```
   A boring spreadsheet                     An interesting network
   (rows and columns)                       (who sends waste to whom)

   permit | fate     | tonnes               ┌──────────┐   500t   ┌──────────┐
   ───────┼──────────┼───────               │ Kent     │ ───────► │ Facility │
   100006 | recovery | 2359       ──►        │ (place)  │          │  #100006 │
   100006 | landfill | 187                   └──────────┘          └────┬─────┘
   ...    | ...      | ...                                    187t       │
                                                       (to landfill)     ▼
                                                                   ┌──────────┐
                                                                   │ Landfill │
                                                                   │ site     │
                                                                   └──────────┘
```

Once waste is a network, we can ask questions a spreadsheet can't answer easily:
*Which facilities are critical hubs? Which behave unusually? Where does waste get
stuck instead of recycled?*

---

## 2. The pipeline: six stages, run in order

The project is a **pipeline** — a series of steps where each step's output is
the next step's input. Think of an assembly line. Each stage is one Python file
in `src/`.

```
  RAW DATA                                                         DELIVERABLES
  (Excel)                                                          (reports,
     │                                                              figures)
     ▼                                                                  ▲
 ┌────────┐  ┌────────┐  ┌────────────┐  ┌───────┐  ┌──────┐  ┌───────────────┐
 │  s01   │─►│  s02   │─►│    s03     │─►│  s04  │─►│ s05  │─►│      s06      │
 │  load  │  │ clean  │  │ indicators │  │ graph │  │  ml  │  │ explain +     │
 │        │  │        │  │  + EDA     │  │       │  │      │  │ circularity   │
 └────────┘  └────────┘  └────────────┘  └───────┘  └──────┘  └───────────────┘
  Module 2    Module 3     Module 4      Mod 5-6    Mod 7-8      Module 9-10

  Each arrow ► = a file written to disk and read by the next stage.
```

**Why split it into stages?** Three reasons a beginner should internalise:

1. **Restartability.** If stage 5 crashes, you don't re-read the giant Excel
   file — the cleaned data is already saved on disk. You just re-run stage 5.
2. **Inspectability.** After each stage you can open the saved file and check it
   looks right *before* trusting the next step.
3. **One job per file.** Each file is small and does one thing, so it's easy to
   understand and change.

The file `src/run_all.py` simply calls the six stages one after another:

```python
STAGES = [
    ("Module 2  - load & organise",       s01_load.main),
    ("Module 3  - clean & standardise",    s02_clean.main),
    ("Module 4  - indicators & EDA",       s03_indicators.main),
    ("Modules 5-6 - graph & network",      s04_graph.main),
    ("Modules 7-8 - clustering & anomaly", s05_ml.main),
    ("Modules 9-10 - explain & circular",  s06_explain_circularity.main),
]
for title, fn in STAGES:
    fn()          # run each stage's main() function
```

Every stage is also runnable on its own, e.g. `python -m src.s03_indicators`.

---

## 3. Where things live (folder map)

```
waste-management/
│
├── src/                         ← THE CODE (the six stages + config)
│   ├── config.py                ← settings: file paths, column names, categories
│   ├── s01_load.py              ← read Excel → one combined table
│   ├── s02_clean.py             ← tidy the data
│   ├── s03_indicators.py        ← per-facility numbers + charts
│   ├── s04_graph.py             ← build & analyse the network
│   ├── s05_ml.py                ← clustering + anomaly detection (the "AI")
│   ├── s06_explain_circularity.py ← explain findings + recommendations
│   └── run_all.py               ← runs all six in order
│
├── data/
│   ├── raw/         ← the original Excel files (inputs, never edited)
│   ├── interim/     ← half-processed data (movements_raw.parquet)
│   └── processed/   ← finished data (clean table, graph, embeddings...)
│
├── figures/         ← all the PNG charts
├── results/         ← text/markdown/csv summaries & tables
├── docs/            ← written reports (incl. this file)
└── README.md        ← how to install & run
```

**Key principle: data flows one way** — `raw → interim → processed → figures/results`.
Code never edits the raw inputs. If everything downstream gets deleted, one
`run_all` rebuilds it all from `raw/`.

---

## 4. Two concepts you must understand first

### 4.1 A "movement" is one row of data

The dataset is a list of **waste movements**. Each row says:

> *"Facility #100006 sent 187 tonnes of waste to landfill"* — or —
> *"Facility #100006 received 2,359 tonnes from Kent."*

There are two spreadsheets: **Wastes Received** (waste coming *in*) and **Wastes
Removed** (waste going *out*). We stack them into one table and add a
`direction` column (`"received"` or `"removed"`) so we remember which is which.

### 4.2 "Fate" is the most important column

`fate` tells you what ultimately happens to the waste. We group fates into
buckets that map to "good" (circular) vs "bad" (wasteful):

```
   fate value        bucket        circularity meaning
   ───────────────   ──────────    ───────────────────────────────
   recovery          RECOVERY      ✅ good — recycled / reused / energy
   landfill          DISPOSAL      ❌ bad  — buried, gone forever
   incineration      DISPOSAL      ❌ bad  — burned without recovery
   transfer (d)      TRANSFER      ➡️ neutral — just passed along
   treatment         TREATMENT     ⚙️ processed before moving on
```

These buckets are defined once in `config.py` (as `RECOVERY_FATES`,
`DISPOSAL_FATES`, etc.), so the whole project agrees on what "recovery" means.

---

## 5. Stage-by-stage walkthrough

### `config.py` — the settings file (read this first)

Not a stage, but *everything* imports it. It's the project's single source of
truth. It holds:

- **Paths** — where raw data lives, where to write outputs. Computed from the
  file's own location, so the project works on any computer.
- **Column renames** — the Excel columns have messy names like `"Tonnes
  Received"` and `"Recorded Origin"`. We map them to clean names like `tonnes`
  and `counterparty`. Two dicts (`RECEIVED_RENAME`, `REMOVED_RENAME`) handle the
  fact that the two spreadsheets name things slightly differently.
- **Domain groupings** — the fate buckets from §4.2.
- **`RANDOM_STATE = 42`** — a fixed "seed" so random steps (clustering, random
  walks) give the *same* answer every run. This is what makes results
  **reproducible**.

> 💡 **Beginner takeaway:** putting all settings in one file means that if the
> government renames a column next year, you fix it in *one* place, not six.

---

### `s01_load.py` — Module 2: read and combine

**Goal:** turn two `.xlsb` Excel files into one clean table saved as a fast file.

```
   Wastes Received.xlsb ─┐
                         ├─► rename columns ─► add direction ─► stack ─► save
   Wastes Removed.xlsb  ─┘                                             (parquet)
```

What it does, step by step:
1. `_read_sheet()` opens each Excel sheet (using the `pyxlsb` engine because
   `.xlsb` is a binary Excel format) and renames columns to the clean names.
2. Adds a `direction` column: `"received"` or `"removed"`.
3. `pd.concat` stacks the two tables into one long table.
4. **Fixes type mismatches.** The `permit` id is stored as a number in one file
   and text in the other. We force it to text everywhere so it behaves
   consistently. `tonnes` is forced to be numeric.
5. Saves to `data/interim/movements_raw.parquet`.

> ❓ **What is parquet?** A file format that stores tables compactly and loads
> ~10× faster than CSV. You can't open it in a text editor, but pandas reads it
> instantly. We use it for all data passed between stages.

**Outputs:** `movements_raw.parquet`, `docs/data_dictionary.md` (explains every
column), `results/load_summary.txt` (row counts — a sanity check).

---

### `s02_clean.py` — Module 3: tidy the data

**Goal:** remove junk rows and standardise text so grouping works reliably.

```
   raw table ─► standardise text ─► drop bad rows ─► add TRUE/FALSE flags ─► clean table
                (trim spaces,        (no permit,      (is_recovery,
                 lowercase)           no tonnes,       is_disposal, ...)
                                      negative)
```

The important cleaning steps:
- **Standardise text**: trim spaces, collapse double-spaces, and lowercase the
  columns we group on (`fate`, `site_category`...). Why? So `"Recovery"`,
  `"recovery"`, and `"recovery "` all count as the same thing.
- **Drop rows we can't use**: no permit (can't be a network node), no tonnes
  (can't weight an edge), negative tonnes (impossible).
- **Derive boolean flags**: it adds columns like `is_recovery`, `is_disposal`,
  `is_transfer` that are simply `True`/`False`. These make later math trivial —
  to get "tonnes recovered" you just sum `tonnes` where `is_recovery` is `True`.

Only **54 rows out of 489,453** were dropped — the data is very clean.

**Outputs:** `data/processed/movements_clean.parquet`,
`results/data_quality_report.md` (missing-value stats — proof the data is sound).

---

### `s03_indicators.py` — Module 4: per-facility numbers + charts

**Goal:** collapse ~489k movement rows into **one row per facility** describing
how that facility behaves.

```
   many movement rows                          one row per facility
   ──────────────────                          ────────────────────
   #100006 received 2359t   ───► group by ───► #100006:
   #100006 removed  187t         permit &        tonnes_received = 2359
   #100006 removed  50t          summarise       tonnes_removed  = 237
   ...                                            recovery_fraction = 0.94
                                                  n_waste_types   = 12
                                                  waste_diversity = 1.8  ...
```

The key idea is **`groupby("permit")`** — "for each facility, calculate...".
For every facility it computes:
- **Volumes**: tonnes received, tonnes removed, total throughput.
- **Variety**: how many different waste codes, how many counterparties.
- **Fate fractions**: what % of its outgoing waste is recovered / disposed /
  transferred. (`recovery_fraction = recovered tonnes ÷ total removed tonnes`.)
- **`waste_diversity`**: *Shannon entropy* — one number saying whether a site
  handles one waste type (low) or a wide balanced mix (high). It's the same
  maths ecologists use to measure biodiversity.

It also draws **6 charts** (`figures/eda_*.png`) — e.g. tonnage by fate, recovery
distribution across facilities. "EDA" = *Exploratory Data Analysis*, i.e.
looking at the data before modelling it.

**Outputs:** `facility_indicators.parquet` + `.csv` (6,860 facilities × 18
columns), `results/top_facilities.md`, 6 EDA figures.

---

### `s04_graph.py` — Modules 5 & 6: build & analyse the network

This is the heart of the project. **Goal:** build the waste-flow network and
measure it.

#### Building the graph

A *graph* (network) is just **nodes** (dots) joined by **edges** (arrows). Here:
- **Nodes** = facilities *and* places. Facilities are keyed `F:100006`, places
  `P:Kent`.
- **Edges** = waste movements, pointing in the direction waste flowed, weighted
  by tonnes.

```
   direction = received:   place ──► facility     (waste came FROM the place)
   direction = removed:    facility ──► place      (waste went TO the place)

        P:Kent ──────► F:100006 ──────► P:Hampshire
               2359t            187t
```

> ⚠️ **An honest limitation, built into the design.** The data records the other
> end of a movement as a *place* (like "Kent"), **not** as another facility's
> permit. So we genuinely cannot draw facility → facility arrows. Our graph
> links facilities to places. This is explained everywhere in the code comments
> because it's the single most important caveat of the whole project.

`build_edges()` groups all movements between the same (source, target) pair and
adds up their tonnes — so multiple small loads become one weighted edge.
`build_graph()` then loads these edges into a networkx `DiGraph` (directed
graph) and attaches each facility's indicators (from stage 3) onto its node.

#### Analysing the graph (`network_metrics`)

For every node it computes classic network measures:

| Measure | Plain-English meaning |
|---|---|
| **in-degree / out-degree** | how many arrows point in / out (how many partners) |
| **weighted degree** | same but summing tonnes, not just counting arrows |
| **betweenness centrality** | how often this node sits *on the path between* others — high = a critical hub/bottleneck |
| **community** (Louvain) | which tightly-connected cluster of nodes it belongs to |

> 🐢 **Betweenness is slow** to compute exactly on 7,000 nodes, so the code uses
> a **sample** of 600 nodes (`k=min(600, ...)`) to approximate it — a common,
> honest speed trade-off.

#### The compression trick

The graph is saved as `waste_flow_graph.graphml.gz`. GraphML is an XML text
format (big and verbose); the `.gz` means it's **gzip-compressed**. This shrinks
it from ~31 MB to ~1.6 MB — small enough to upload to GitHub. networkx reads and
writes `.gz` automatically, so no extra code is needed.

**Outputs:** `waste_flow_graph.graphml.gz`, `facility_network_metrics.parquet`,
`results/graph_summary.txt`, `results/top20_centrality.md`, 2 network figures.

---

### `s05_ml.py` — Modules 7 & 8: the "AI" part

Two machine-learning tasks. Both are **unsupervised** — there are no "right
answers" to learn from; the algorithms find structure on their own.

#### Module 7 — Clustering (grouping similar facilities)

**Goal:** automatically sort 6,860 facilities into a handful of behaviour types.

```
   Step 1: build a feature matrix     Step 2: scale     Step 3: KMeans groups them
   (11 numbers per facility)          (fair units)      into k=6 clusters

   facility → [volume, diversity,     ──►  standardise  ──►   ● cluster 0  "recovery"
               recovery%, ...]             each column         ● cluster 1  "transfer hub"
                                                               ● cluster 2  "hazardous"...
```

- **`build_feature_matrix`** picks 11 numeric features and applies `log1p` to the
  volume columns. Why? Because tonnages range from 1 to millions — taking the
  log stops the giant sites from drowning out everything else. Then
  `StandardScaler` puts every feature on the same footing (mean 0, spread 1) so
  "handles 12 waste types" and "500,000 tonnes" are weighted fairly.
- **`KMeans(k=6)`** finds 6 natural groups. It's an algorithm that repeatedly
  nudges 6 "centre points" until each facility is attached to its nearest centre.
- **`name_clusters`** gives each cluster a human label (e.g. *"High-volume
  transfer hubs"*, *"Hazardous-waste specialists"*) using simple `if` rules on
  the cluster's average behaviour — so the output is readable, not just
  "cluster 3".

#### Module 8 — Anomaly detection (finding the weird ones)

**Goal:** flag facilities that behave unusually and deserve a human look. It
combines **two independent detectors** and averages them:

```
   ┌─ Detector A: on the 11 tabular features ──────────────┐
   │   IsolationForest → "tab_anom_score"                  │
   │   (weird numbers: huge volume + zero recovery, etc.)  │
   ├─ Detector B: on the graph structure ──────────────────┤   combine
   │   node embeddings → IsolationForest → "emb_anom_score"│ ──(z-score
   │   (weird position in the network)                     │    average)──► ranked list
   └───────────────────────────────────────────────────────┘
```

- **Isolation Forest** is an algorithm that finds outliers by seeing how *easily*
  a point can be "isolated" by random splits — genuine oddballs get isolated
  quickly.
- **Node embeddings** turn each node's *position in the network* into a list of
  32 numbers, so an Isolation Forest can judge structural weirdness too.

**The home-grown DeepWalk (the clever bit).** The usual tools for embeddings
(`gensim`, `node2vec`, `torch-geometric`) don't install on Python 3.14. So the
code implements the same idea from scratch using only numpy + scikit-learn:

```
   1. RANDOM WALKS   From each node, wander to random neighbours (following heavy
                     edges more often), recording the path. Like dropping a
                     marble in the network and noting where it rolls.

   2. CO-OCCURRENCE  Count which nodes show up near each other in those walks.
                     Nodes that appear together a lot are "similar".

   3. PPMI + SVD     Turn those counts into a meaningful score (PPMI), then
                     squeeze the big table down to 32 numbers per node (SVD).
                     Those 32 numbers ARE the embedding.
```

This is mathematically equivalent to the published DeepWalk method — the code
comment cites the paper (Qiu et al. 2018). A nice example of *understanding a
technique well enough to rebuild it* when the library isn't available.

**Outputs:** `facility_clusters.parquet`, `facility_features.parquet`,
`node_embeddings.parquet`, `results/cluster_profiles.md`,
`results/anomalies_ranked.{csv,md}`, 2 ML figures.

---

### `s06_explain_circularity.py` — Modules 9 & 10: explain + recommend

**Goal:** turn the anomaly list and the data into *human-readable insight and
recommendations*. Anomaly detection says "this site is weird" but not *why* —
this stage answers *why* and *so what*.

#### Module 9 — Explainability

For each of the top-20 flagged facilities, `explain()` compares it against its
own cluster's average (using a *z-score*: how many standard deviations from
normal) and writes a plain reason:

```
   if throughput is way above cluster peers   → "unusually high volume ..."
   if disposal_fraction > 0.5                 → "high landfill dependence ..."
   if transfer_fraction > 0.7                 → "waste just passes through ..."
   if no recovery/disposal/transfer recorded  → "data gap — needs review"
   ...
```

The result is a 3-column table: *flagged facility | reason | possible practical
explanation*. Each flag becomes something a human can act on.

#### Module 10 — Circularity opportunities

Finds *where recovery could improve* and writes 5 concrete recommendations:
- `region_recovery()` ranks regions by disposal rate (which region wastes most?).
- `transfer_without_recovery()` finds waste *categories* that mostly get passed
  along instead of recovered.
- `opportunities_md()` writes it up as a report with 5 actionable ideas.

**Outputs:** `results/explainability_table.md`,
`results/circularity_opportunities.md`, `results/region_recovery_summary.csv`,
1 circularity figure.

---

## 6. The full data-flow map (everything at once)

```
  data/raw/*.xlsb
        │  s01_load
        ▼
  data/interim/movements_raw.parquet
        │  s02_clean
        ▼
  data/processed/movements_clean.parquet ──────────────┐
        │  s03_indicators                              │ (also used by s04, s06)
        ▼                                               │
  facility_indicators.parquet + figures/eda_*.png       │
        │  s04_graph                                     │
        ▼                                               ▼
  waste_flow_graph.graphml.gz  +  facility_network_metrics.parquet
        │  s05_ml (reads graph + indicators)
        ▼
  facility_clusters.parquet, node_embeddings.parquet,
  results/anomalies_ranked.csv
        │  s06_explain_circularity (reads clean data + clusters)
        ▼
  results/explainability_table.md, circularity_opportunities.md
```

---

## 7. How to read the code yourself (a suggested path)

If you want to actually open the files, read them in this order:

1. **`config.py`** — 5 minutes. Understand the settings and fate buckets.
2. **`s01_load.py`** then **`s02_clean.py`** — see raw data become a clean table.
3. Open `results/data_quality_report.md` and `results/load_summary.txt` — look at
   what those two stages actually produced.
4. **`s03_indicators.py`** — the `facility_indicators()` function is the core.
   Open `figures/eda_01_tonnes_by_fate.png` alongside it.
5. **`s04_graph.py`** — `build_edges()` and `build_graph()` are the key
   functions. This is where the network is born.
6. **`s05_ml.py`** — read `name_clusters()` (easy) before `deepwalk_embeddings()`
   (harder).
7. **`s06_explain_circularity.py`** — see how findings become recommendations.

Every function has a docstring (the triple-quoted text at its top) explaining
its job. When lost, read those first.

---

## 8. Glossary of terms used in the code

| Term | Meaning |
|---|---|
| **pipeline** | a chain of steps where each feeds the next |
| **pandas / DataFrame** | Python's spreadsheet-in-code; a `DataFrame` is a table |
| **parquet** | a fast, compact file format for tables |
| **groupby** | "for each X, calculate..." (e.g. for each facility) |
| **node / edge** | a dot / an arrow in a network |
| **directed graph (DiGraph)** | a network where arrows have a direction |
| **edge weight** | a number on an arrow — here, tonnes of waste |
| **betweenness** | how much a node acts as a bridge between others |
| **community detection** | finding tightly-connected clusters of nodes |
| **feature** | one input number describing a thing (e.g. recovery %) |
| **scaling / StandardScaler** | putting features on a comparable range |
| **log1p** | `log(1 + x)`; tames huge, skewed numbers |
| **KMeans** | groups items into k clusters by similarity |
| **Isolation Forest** | an algorithm that flags outliers |
| **embedding** | turning a node into a list of numbers capturing its role |
| **z-score** | how many standard deviations from average (a "weirdness" unit) |
| **Shannon entropy** | a single number for how mixed/diverse something is |
| **reproducible** | same code + same seed → identical results every time |

---

*This document describes the code as implemented in `src/`. If you change a
stage, update the relevant section here so the guide stays trustworthy.*
