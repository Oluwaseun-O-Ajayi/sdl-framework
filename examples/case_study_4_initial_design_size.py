"""Case study 4: how large should the initial design be?

Question: with a fixed budget of 30 experiments, how does the number of initial
Latin hypercube points (3, 5, 10, 20) affect the final result?
Objective: Branin function (minimum 0.397887), expected improvement, 10 seeds.
Output: examples/case_study_results/case4_initial_design_size.csv
"""

import pandas as pd
from _case_study_common import BRANIN_BOUNDS, BRANIN_MIN, N_SEEDS, RESULTS, branin, run_campaign

rows = []
for n_initial in [3, 5, 10, 20]:
    for seed in range(N_SEEDS):
        traj, _ = run_campaign(branin, BRANIN_BOUNDS, "EI", seed, n_initial=n_initial)
        rows.append({"n_initial": n_initial, "seed": seed, "gap_after_30": traj[29] - BRANIN_MIN})

table = pd.DataFrame(rows)
table.to_csv(RESULTS / "case4_initial_design_size.csv", index=False)
summary = table.groupby("n_initial")["gap_after_30"].describe()[["50%", "max"]]
summary.columns = ["median_gap_after_30", "worst_gap_after_30"]
print(f"{N_SEEDS} seeds per design size, budget 30:")
print(summary.to_string(float_format=lambda v: f"{v:.3g}"))
