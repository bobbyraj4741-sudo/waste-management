"""Run the full pipeline end to end (Modules 2-10).

  python -m src.run_all

Each stage reads the previous stage's output from data/ and writes its own
artefacts to data/, results/, and figures/.
"""
from __future__ import annotations

import time

from . import s01_load, s02_clean, s03_indicators, s04_graph, s05_ml, s06_explain_circularity

STAGES = [
    ("Module 2  - load & organise", s01_load.main),
    ("Module 3  - clean & standardise", s02_clean.main),
    ("Module 4  - indicators & EDA", s03_indicators.main),
    ("Modules 5-6 - graph & network analysis", s04_graph.main),
    ("Modules 7-8 - clustering & anomaly detection", s05_ml.main),
    ("Modules 9-10 - explainability & circularity", s06_explain_circularity.main),
]


def main() -> None:
    t0 = time.time()
    for title, fn in STAGES:
        print(f"\n{'='*70}\n{title}\n{'='*70}")
        fn()
    print(f"\nPipeline complete in {time.time() - t0:.1f}s. "
          f"See results/ and figures/.")


if __name__ == "__main__":
    main()
