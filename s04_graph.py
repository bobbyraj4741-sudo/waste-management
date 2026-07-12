"""Modules 5 & 6 - Build the Waste Flow Network + Classical Network Analysis.

Because the public data records the counterparty as a *place* (origin/destination
region/WPA), not a counterparty permit, we build an honest **directed weighted
graph** with two node kinds:

    place  --(received)-->  facility        (weight = tonnes in)
    facility --(removed)--> place            (weight = tonnes out)

Node key convention:
    facilities:  "F:<permit>"
    places:      "P:<place name>"

Edges are aggregated by (source, target): weight = total tonnes, plus attributes
for dominant waste category, dominant fate, and number of distinct waste codes.

Outputs:
  * data/processed/waste_flow_graph.graphml.gz   (gzip-compressed GraphML;
      networkx reads it transparently via read_graphml. ~1.6 MB vs ~31 MB raw,
      so it stays well under GitHub's upload limits.)
  * results/graph_summary.txt
  * results/top20_centrality.md          (Module 6 completion check)
  * data/processed/facility_network_metrics.parquet
  * figures/net_*.png

Run:  python -m src.s04_graph
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from . import config as C

try:
    import community as community_louvain  # python-louvain
    _HAS_LOUVAIN = True
except Exception:  # pragma: no cover
    _HAS_LOUVAIN = False


def build_edges(df: pd.DataFrame) -> pd.DataFrame:
    """Directed edges place->facility (received) and facility->place (removed)."""
    df = df.copy()
    df["fac_node"] = "F:" + df["permit"].astype(str)
    place = df["counterparty"].fillna("Not Codeable").astype(str)
    df["place_node"] = "P:" + place

    recv = df[df.direction == "received"].copy()
    recv["src"], recv["dst"] = recv["place_node"], recv["fac_node"]
    remv = df[df.direction == "removed"].copy()
    remv["src"], remv["dst"] = remv["fac_node"], remv["place_node"]
    edges = pd.concat([recv, remv], ignore_index=True)

    agg = (
        edges.groupby(["src", "dst"])
        .agg(
            weight=("tonnes", "sum"),
            n_records=("tonnes", "size"),
            n_waste_codes=("waste_code", "nunique"),
            dom_waste_cat=("basic_waste_cat", lambda s: s.mode().iat[0] if not s.mode().empty else None),
            dom_fate=("fate", lambda s: s.mode().iat[0] if not s.mode().empty else None),
        )
        .reset_index()
    )
    return agg


def build_graph(df: pd.DataFrame, ind: pd.DataFrame) -> nx.DiGraph:
    edges = build_edges(df)
    G = nx.DiGraph()
    for r in edges.itertuples(index=False):
        G.add_edge(r.src, r.dst, weight=float(r.weight), n_records=int(r.n_records),
                   n_waste_codes=int(r.n_waste_codes),
                   dom_waste_cat=r.dom_waste_cat, dom_fate=r.dom_fate)

    # Node attributes: facilities get their indicators; places get kind=place.
    ind_by_node = ind.set_index("F:" + ind["permit"].astype(str))
    for n in G.nodes():
        if n.startswith("F:") and n in ind_by_node.index:
            row = ind_by_node.loc[n]
            G.nodes[n].update(
                kind="facility",
                site_name=str(row["site_name"]),
                site_category=str(row["site_category"]),
                facility_type=str(row["facility_type"]),
                region=str(row["facility_region"]),
                tonnes_received=float(row["tonnes_received"]),
                tonnes_removed=float(row["tonnes_removed"]),
                recovery_fraction=float(row["recovery_fraction"]),
                disposal_fraction=float(row["disposal_fraction"]),
                waste_diversity=float(row["waste_diversity"]),
            )
        else:
            G.nodes[n].setdefault("kind", "place")
    return G


def network_metrics(G: nx.DiGraph) -> pd.DataFrame:
    """Module 6: degrees, weighted degrees, betweenness, community."""
    in_deg = dict(G.in_degree())
    out_deg = dict(G.out_degree())
    w_in = dict(G.in_degree(weight="weight"))
    w_out = dict(G.out_degree(weight="weight"))

    # Betweenness on the largest weakly-connected component, using tonnage as a
    # capacity (invert to a distance so heavy routes are "shorter" / preferred).
    print("  computing betweenness (this can take a moment) ...", flush=True)
    dist = {(u, v): 1.0 / max(d["weight"], 1e-6) for u, v, d in G.edges(data=True)}
    nx.set_edge_attributes(G, dist, "distance")
    # Sample-based approximation keeps it tractable on ~7k+ nodes.
    btw = nx.betweenness_centrality(G, k=min(600, G.number_of_nodes()),
                                    weight="distance", seed=C.RANDOM_STATE, normalized=True)

    # Community detection on the undirected projection (Louvain).
    if _HAS_LOUVAIN:
        part = community_louvain.best_partition(G.to_undirected(), weight="weight",
                                                random_state=C.RANDOM_STATE)
    else:  # fallback: greedy modularity
        comms = nx.community.greedy_modularity_communities(G.to_undirected(), weight="weight")
        part = {n: i for i, c in enumerate(comms) for n in c}

    rows = []
    for n, d in G.nodes(data=True):
        rows.append({
            "node": n, "kind": d.get("kind"),
            "label": d.get("site_name", n[2:]),
            "region": d.get("region"),
            "site_category": d.get("site_category"),
            "in_degree": in_deg[n], "out_degree": out_deg[n],
            "w_in_tonnes": w_in[n], "w_out_tonnes": w_out[n],
            "betweenness": btw.get(n, 0.0),
            "community": part.get(n, -1),
            "recovery_fraction": d.get("recovery_fraction"),
        })
    return pd.DataFrame(rows)


def _sanitize_for_graphml(G: nx.DiGraph) -> None:
    """GraphML cannot serialise pandas NA/None; coerce to safe scalar types.

    Also rounds floats to 4 dp: full binary precision (e.g. 0.9367264191207854)
    bloats the XML with no analytical value at this scale.
    """
    def fix(d):
        for k, v in list(d.items()):
            if v is None or (isinstance(v, float) and pd.isna(v)) or v is pd.NA:
                d[k] = "" if isinstance(v, str) or v is pd.NA else 0.0
            elif isinstance(v, float) and not isinstance(v, bool):
                d[k] = round(v, 4)
            elif not isinstance(v, (str, int, float, bool)):
                d[k] = str(v)
    for _, d in G.nodes(data=True):
        fix(d)
    for *_e, d in G.edges(data=True):
        fix(d)


def summarise(G: nx.DiGraph) -> str:
    und = G.to_undirected()
    lcc = max(nx.connected_components(und), key=len)
    n_fac = sum(1 for _, d in G.nodes(data=True) if d.get("kind") == "facility")
    n_place = G.number_of_nodes() - n_fac
    avg_deg = sum(d for _, d in G.degree()) / G.number_of_nodes()
    return (
        "Waste Flow Network - summary\n"
        "============================\n"
        f"nodes                     : {G.number_of_nodes():,}\n"
        f"  facilities              : {n_fac:,}\n"
        f"  places (origins/dests)  : {n_place:,}\n"
        f"edges (directed)          : {G.number_of_edges():,}\n"
        f"average degree            : {avg_deg:.2f}\n"
        f"largest connected comp.   : {len(lcc):,} nodes "
        f"({len(lcc)/G.number_of_nodes()*100:.1f}%)\n"
        f"total flow (edge weight)  : {sum(d['weight'] for *_ , d in G.edges(data=True)):,.0f} tonnes\n"
    )


def top20_table(metrics: pd.DataFrame) -> str:
    fac = metrics[metrics.kind == "facility"].copy()
    top = fac.nlargest(20, "betweenness")
    cols = ["label", "region", "site_category", "in_degree", "out_degree",
            "w_in_tonnes", "w_out_tonnes", "betweenness"]
    tbl = top[cols].to_markdown(index=False, floatfmt=(",.0f"))
    return f"""\
# Module 6 - Top 20 Facilities by Betweenness Centrality

Betweenness is computed on a tonnage-weighted directed graph (heavy routes
treated as shorter). High-betweenness facilities sit on many efficient waste
paths - they act as **routing bottlenecks / regional hubs**: if they are
disrupted or inefficient, a lot of waste has to re-route.

{tbl}

*Interpretation*: facilities combining high weighted in/out degree with high
betweenness are the network's load-bearing hubs (large transfer stations and
treatment sites that consolidate waste for a whole sub-region). They are the
first places where a recovery improvement propagates widely.
"""


def plots(metrics: pd.DataFrame) -> None:
    fac = metrics[metrics.kind == "facility"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    top = fac.nlargest(20, "betweenness").sort_values("betweenness")
    ax.barh(top["label"].str.slice(0, 34), top["betweenness"], color="#4C72B0")
    ax.set_xlabel("Betweenness centrality"); ax.set_title("Top 20 hub facilities (betweenness)")
    fig.savefig(C.FIGURES / "net_01_betweenness_top20.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    sizes = metrics.groupby("community").size().sort_values(ascending=False).head(15)
    ax.bar(sizes.index.astype(str), sizes.values, color="#55A868")
    ax.set_xlabel("Community id"); ax.set_ylabel("Nodes")
    ax.set_title("Largest 15 detected communities")
    fig.savefig(C.FIGURES / "net_02_communities.png"); plt.close(fig)
    print(f"  wrote 2 network figures")


def main() -> None:
    print("Modules 5 & 6: build graph + classical network analysis ...")
    df = pd.read_parquet(C.DATA_PROCESSED / "movements_clean.parquet")
    ind = pd.read_parquet(C.DATA_PROCESSED / "facility_indicators.parquet")

    G = build_graph(df, ind)
    _sanitize_for_graphml(G)
    # .gz suffix -> networkx gzip-compresses on write and decompresses on read.
    nx.write_graphml(G, C.DATA_PROCESSED / "waste_flow_graph.graphml.gz")
    summary = summarise(G)
    (C.RESULTS / "graph_summary.txt").write_text(summary)
    print(summary)

    metrics = network_metrics(G)
    metrics.to_parquet(C.DATA_PROCESSED / "facility_network_metrics.parquet", index=False)
    (C.RESULTS / "top20_centrality.md").write_text(top20_table(metrics))
    plots(metrics)
    print(f"  communities detected: {metrics['community'].nunique():,}")
    print("  wrote results/top20_centrality.md")


if __name__ == "__main__":
    main()
