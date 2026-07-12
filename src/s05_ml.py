"""Modules 7 & 8 - Facility Behaviour Clustering + Graph AI Anomaly Detection.

Module 7: cluster facilities by waste-management behaviour (KMeans on scaled
          features), then name each cluster.
Module 8: detect anomalous facilities via
            (a) Isolation Forest on the tabular facility features, and
            (b) graph node embeddings (dependency-light DeepWalk: biased random
                walks -> PPMI co-occurrence -> Truncated SVD) with a second
                Isolation Forest on the embeddings.
          The two anomaly signals are combined into a ranked list.

Why the home-grown DeepWalk? gensim / node2vec / torch-geometric do not build on
Python 3.14 (the roadmap lists them as the optional "if time permits" tier).
Random-walk -> PPMI -> SVD is the matrix-factorisation view of DeepWalk (Qiu et
al. 2018, "Network Embedding as Matrix Factorization") and needs only numpy +
scikit-learn, so the graph-embedding path stays honest and reproducible.

Outputs:
  * data/processed/facility_features.parquet
  * data/processed/facility_clusters.parquet
  * results/cluster_profiles.md
  * results/anomalies_ranked.csv  +  results/anomalies_ranked.md
  * figures/ml_*.png

Run:  python -m src.s05_ml
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from . import config as C

rng = np.random.default_rng(C.RANDOM_STATE)

FEATURES = [
    "tonnes_received", "tonnes_removed", "throughput",
    "n_waste_types", "n_counterparties", "waste_diversity",
    "recovery_fraction", "disposal_fraction", "transfer_fraction",
    "treatment_fraction", "hazardous_fraction",
]


# --------------------------------------------------------------------------- #
# Module 7 - clustering
# --------------------------------------------------------------------------- #
def build_feature_matrix(ind: pd.DataFrame):
    fac = ind[ind["throughput"] > 0].copy().reset_index(drop=True)
    X = fac[FEATURES].to_numpy(dtype=float)
    # log1p the heavy-tailed volume/count columns before scaling.
    for i, f in enumerate(FEATURES):
        if f in ("tonnes_received", "tonnes_removed", "throughput",
                 "n_waste_types", "n_counterparties"):
            X[:, i] = np.log1p(X[:, i])
    Xs = StandardScaler().fit_transform(X)
    return fac, Xs


def cluster_facilities(fac: pd.DataFrame, Xs: np.ndarray, k: int = 6) -> pd.DataFrame:
    km = KMeans(n_clusters=k, n_init=10, random_state=C.RANDOM_STATE)
    fac["cluster"] = km.fit_predict(Xs)
    return fac


def name_clusters(fac: pd.DataFrame) -> dict[int, str]:
    """Heuristically name clusters from their mean behaviour."""
    names = {}
    prof = fac.groupby("cluster")[FEATURES].mean()
    med_through = fac["throughput"].median()
    for c, row in prof.iterrows():
        if row["transfer_fraction"] > 0.4 and row["throughput"] > med_through:
            label = "High-volume transfer hubs"
        elif row["disposal_fraction"] > 0.4:
            label = "Landfill / disposal-dependent sites"
        elif row["recovery_fraction"] > 0.6 and row["waste_diversity"] > prof["waste_diversity"].median():
            label = "Diverse recovery facilities"
        elif row["hazardous_fraction"] > 0.5:
            label = "Hazardous-waste specialists"
        elif row["throughput"] < med_through:
            label = "Low-volume specialised handlers"
        else:
            label = "General treatment / mixed sites"
        names[c] = label
    return names


def cluster_profiles_md(fac: pd.DataFrame, names: dict[int, str]) -> str:
    prof = fac.groupby("cluster").agg(
        n=("permit", "size"),
        mean_throughput=("throughput", "mean"),
        recovery=("recovery_fraction", "mean"),
        disposal=("disposal_fraction", "mean"),
        transfer=("transfer_fraction", "mean"),
        hazardous=("hazardous_fraction", "mean"),
        diversity=("waste_diversity", "mean"),
    ).round(3)
    prof.insert(0, "name", prof.index.map(names))
    return "# Module 7 - Facility Behaviour Clusters\n\n" + prof.to_markdown(floatfmt=",.3f") + "\n"


# --------------------------------------------------------------------------- #
# Module 8 - graph embeddings (dependency-light DeepWalk) + anomaly detection
# --------------------------------------------------------------------------- #
def deepwalk_embeddings(G: nx.DiGraph, dim: int = 32, n_walks: int = 10,
                        walk_len: int = 40, window: int = 5) -> pd.DataFrame:
    """Random-walk -> PPMI -> Truncated SVD embeddings (DeepWalk-as-MF)."""
    Ug = G.to_undirected()
    nodes = list(Ug.nodes())
    idx = {n: i for i, n in enumerate(nodes)}
    N = len(nodes)

    # Pre-compute weighted neighbour transition tables.
    neigh = {}
    for n in nodes:
        nbrs = list(Ug[n])
        if nbrs:
            w = np.array([Ug[n][m].get("weight", 1.0) for m in nbrs], dtype=float)
            w = np.where(w <= 0, 1e-6, w)
            neigh[n] = (nbrs, w / w.sum())
        else:
            neigh[n] = ([], None)

    print(f"  generating random walks ({n_walks} x {N} x len {walk_len}) ...", flush=True)
    cooc = np.zeros((N, N), dtype=np.float64)  # 7k x 7k float64 ~ 400MB; ok here
    for _ in range(n_walks):
        order = nodes.copy()
        rng.shuffle(order)
        for start in order:
            walk = [start]
            cur = start
            for _ in range(walk_len - 1):
                nbrs, p = neigh[cur]
                if not nbrs:
                    break
                cur = nbrs[rng.choice(len(nbrs), p=p)]
                walk.append(cur)
            wi = [idx[x] for x in walk]
            for pos, a in enumerate(wi):
                lo, hi = max(0, pos - window), min(len(wi), pos + window + 1)
                for pos2 in range(lo, hi):
                    if pos2 != pos:
                        cooc[a, wi[pos2]] += 1.0

    # PPMI transform.
    print("  building PPMI + SVD embeddings ...", flush=True)
    total = cooc.sum()
    if total == 0:
        raise RuntimeError("empty co-occurrence matrix")
    row = cooc.sum(1, keepdims=True)
    col = cooc.sum(0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((cooc * total) / (row @ col))
    ppmi = np.nan_to_num(np.maximum(pmi, 0.0))

    emb = TruncatedSVD(n_components=dim, random_state=C.RANDOM_STATE).fit_transform(ppmi)
    return pd.DataFrame(emb, index=nodes, columns=[f"emb_{i}" for i in range(dim)])


def anomaly_detection(fac: pd.DataFrame, Xs: np.ndarray, emb: pd.DataFrame) -> pd.DataFrame:
    # (a) tabular Isolation Forest.
    iso_tab = IsolationForest(n_estimators=300, contamination=0.03,
                              random_state=C.RANDOM_STATE)
    iso_tab.fit(Xs)
    fac["tab_anom_score"] = -iso_tab.score_samples(Xs)  # higher = more anomalous

    # (b) embedding Isolation Forest (facility nodes only).
    fac_nodes = "F:" + fac["permit"].astype(str)
    E = emb.reindex(fac_nodes).to_numpy()
    ok = ~np.isnan(E).any(1)
    fac["emb_anom_score"] = np.nan
    iso_emb = IsolationForest(n_estimators=300, contamination=0.03,
                              random_state=C.RANDOM_STATE)
    iso_emb.fit(E[ok])
    fac.loc[ok, "emb_anom_score"] = -iso_emb.score_samples(E[ok])

    # Combine (rank-average of the two z-scored signals).
    def _z(s):
        s = s.astype(float)
        return (s - s.mean()) / (s.std() + 1e-9)
    fac["combined_anom_score"] = _z(fac["tab_anom_score"]) + _z(fac["emb_anom_score"].fillna(fac["emb_anom_score"].mean()))
    return fac.sort_values("combined_anom_score", ascending=False)


def anomalies_md(ranked: pd.DataFrame, names: dict[int, str]) -> str:
    top = ranked.head(25).copy()
    top["cluster_name"] = top["cluster"].map(names)
    cols = ["site_name", "facility_region", "site_category", "cluster_name",
            "throughput", "recovery_fraction", "disposal_fraction",
            "tab_anom_score", "emb_anom_score", "combined_anom_score"]
    return ("# Module 8 - Top 25 Anomalous Facilities (combined tabular + graph)\n\n"
            + top[cols].to_markdown(index=False, floatfmt=",.3f") + "\n")


def plots(fac: pd.DataFrame, Xs: np.ndarray, names: dict[int, str]) -> None:
    pca = PCA(n_components=2, random_state=C.RANDOM_STATE).fit_transform(Xs)
    fig, ax = plt.subplots(figsize=(7.5, 6))
    for c in sorted(fac["cluster"].unique()):
        m = fac["cluster"] == c
        ax.scatter(pca[m, 0], pca[m, 1], s=8, alpha=0.4, label=names[c])
    ax.set_title("Facility clusters (PCA of behaviour features)")
    ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
    ax.legend(fontsize=7, markerscale=2, loc="best")
    fig.savefig(C.FIGURES / "ml_01_clusters_pca.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 6))
    sc = ax.scatter(pca[:, 0], pca[:, 1], c=fac["combined_anom_score"],
                    cmap="magma_r", s=10, alpha=0.6)
    ax.set_title("Anomaly score across facilities (PCA layout)")
    ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
    fig.colorbar(sc, label="combined anomaly score")
    fig.savefig(C.FIGURES / "ml_02_anomaly_pca.png"); plt.close(fig)
    print("  wrote 2 ML figures")


def main() -> None:
    print("Modules 7 & 8: clustering + graph anomaly detection ...")
    ind = pd.read_parquet(C.DATA_PROCESSED / "facility_indicators.parquet")
    G = nx.read_graphml(C.DATA_PROCESSED / "waste_flow_graph.graphml")

    fac, Xs = build_feature_matrix(ind)
    fac = cluster_facilities(fac, Xs)
    names = name_clusters(fac)
    (C.RESULTS / "cluster_profiles.md").write_text(cluster_profiles_md(fac, names))
    print(f"  {len(fac):,} facilities clustered into {fac['cluster'].nunique()} groups")

    emb = deepwalk_embeddings(G)
    emb.to_parquet(C.DATA_PROCESSED / "node_embeddings.parquet")

    ranked = anomaly_detection(fac, Xs, emb)
    fac[FEATURES + ["cluster"]].assign(permit=fac["permit"]).to_parquet(
        C.DATA_PROCESSED / "facility_features.parquet", index=False)
    ranked.to_parquet(C.DATA_PROCESSED / "facility_clusters.parquet", index=False)
    keep = ["permit", "site_name", "facility_region", "site_category", "cluster",
            "throughput", "recovery_fraction", "disposal_fraction",
            "tab_anom_score", "emb_anom_score", "combined_anom_score"]
    ranked[keep].to_csv(C.RESULTS / "anomalies_ranked.csv", index=False)
    (C.RESULTS / "anomalies_ranked.md").write_text(anomalies_md(ranked, names))

    plots(fac, Xs, names)
    print("  wrote cluster_profiles.md + anomalies_ranked.{csv,md}")


if __name__ == "__main__":
    main()
