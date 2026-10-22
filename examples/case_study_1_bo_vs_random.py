"""Case study 1: Bayesian optimization against random search.

Question: on a benchmark with a known optimum, how many experiments does a
closed-loop campaign save compared with random sampling?
Objective: Branin function (minimum 0.397887), budget 30 experiments,
           5 initial Latin hypercube points, expected improvement, 10 seeds.
Output: examples/case_study_results/case1_bo_vs_random.csv
"""

import numpy as np
import pandas as pd
from _case_study_common import (BRANIN_BOUNDS, BRANIN_MIN, N_SEEDS, RESULTS, branin,
                                random_search, run_campaign)

CHECKPOINTS = [5, 10, 15, 20, 30]
rows = []
for seed in range(N_SEEDS):
    bo, _ = run_campaign(branin, BRANIN_BOUNDS, "EI", seed)
    rs = random_search(branin, BRANIN_BOUNDS, seed)
    for method, traj in [("Bayesian optimization (EI)", bo), ("Random search", rs)]:
        rows.append({"method": method, "seed": seed,
                     **{f"gap_after_{n}": traj[n - 1] - BRANIN_MIN for n in CHECKPOINTS}})

table = pd.DataFrame(rows)
table.to_csv(RESULTS / "case1_bo_vs_random.csv", index=False)
summary = table.groupby("method")[[f"gap_after_{n}" for n in CHECKPOINTS]].median()
print(f"Median gap to the true minimum over {N_SEEDS} seeds (lower is better):")
print(summary.map(lambda v: f"{v:.3g}").to_string())
THRESHOLD = 0.1
within = table.groupby("method")["gap_after_30"].apply(lambda s: int((s < THRESHOLD).sum()))
print(f"\nRuns within {THRESHOLD} of the minimum after 30 experiments (out of {N_SEEDS}):")
print(within.to_string())
