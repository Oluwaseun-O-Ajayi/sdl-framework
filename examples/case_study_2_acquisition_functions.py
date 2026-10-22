"""Case study 2: comparing acquisition functions.

Question: on the same benchmark and budget, how do expected improvement (EI),
upper confidence bound (UCB) and probability of improvement (PI) compare?
Objective: Branin function (minimum 0.397887), budget 30, 5 initial points, 10 seeds.
Output: examples/case_study_results/case2_acquisition_functions.csv
"""

import numpy as np
import pandas as pd
from _case_study_common import BRANIN_BOUNDS, BRANIN_MIN, N_SEEDS, RESULTS, branin, run_campaign

rows = []
for acq in ["EI", "UCB", "PI"]:
    for seed in range(N_SEEDS):
        traj, _ = run_campaign(branin, BRANIN_BOUNDS, acq, seed)
        gap = traj - BRANIN_MIN
        hit = np.flatnonzero(gap < 0.01)
        rows.append({"acquisition": acq, "seed": seed, "gap_after_15": gap[14], "gap_after_30": gap[29],
                     "experiments_to_gap_0.01": int(hit[0] + 1) if hit.size else None})

table = pd.DataFrame(rows)
table.to_csv(RESULTS / "case2_acquisition_functions.csv", index=False)
summary = table.groupby("acquisition", sort=False).agg(
    median_gap_15=("gap_after_15", "median"), median_gap_30=("gap_after_30", "median"),
    runs_reaching_0_01=("experiments_to_gap_0.01", "count"),
    median_experiments_to_0_01=("experiments_to_gap_0.01", "median"))
print(f"{N_SEEDS} seeds per acquisition function:")
print(summary.to_string(float_format=lambda v: f"{v:.3g}"))
