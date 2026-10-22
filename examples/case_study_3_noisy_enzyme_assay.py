"""Case study 3: a noisy simulated enzyme assay.

Question: when every measurement carries 5% noise, how close to the true optimum
are the conditions a campaign recommends, and how much does the best observed
value overstate the truth?
Objective: simulated reaction velocity over temperature (20 to 60 C), pH (5 to 9)
and substrate (10 to 300 uM). True optimum: 37 C, pH 7.4, 150 uM, velocity 92.31.
Budget 30, 5 initial points, expected improvement, 10 seeds.
Output: examples/case_study_results/case3_noisy_enzyme_assay.csv
"""

import numpy as np
import pandas as pd
from _case_study_common import N_SEEDS, RESULTS, run_campaign

BOUNDS = {"temperature": (20.0, 60.0), "pH": (5.0, 9.0), "substrate": (10.0, 300.0)}
TRUE_OPT = {"temperature": 37.0, "pH": 7.4, "substrate": 150.0}


def true_velocity(p):
    """Noise-free velocity: Gaussian temperature and pH optima, Michaelis-Menten in
    substrate (Km 45 uM) with substrate inhibition above 150 uM."""
    t, ph, s = p["temperature"], p["pH"], p["substrate"]
    temp = np.exp(-((t - 37) / 12) ** 2) if t < 45 else np.exp(-((t - 37) / 8) ** 2) * np.exp(-(t - 45) / 5)
    inhibition = 1.0 if s <= 150 else np.exp(-(s - 150) / 50)
    return 120.0 * temp * np.exp(-((ph - 7.4) / 1.2) ** 2) * inhibition * s / (45.0 + s)


V_OPT = true_velocity(TRUE_OPT)
rows = []
for seed in range(N_SEEDS):
    noise = np.random.default_rng(1000 + seed)

    def measured(p):
        return true_velocity(p) * (1 + noise.normal(0, 0.05))

    traj, params = run_campaign(measured, BOUNDS, "EI", seed, minimize=False)
    observed = [true_velocity(p) for p in params]  # noise-free value at each tested condition
    best_i = int(np.argmax(traj == traj[-1]))     # experiment that produced the best observation
    rec = params[best_i]
    rows.append({"seed": seed, "best_observed": traj[-1], "true_value_of_recommended": observed[best_i],
                 "pct_of_true_optimum": 100 * observed[best_i] / V_OPT,
                 "best_true_value_tested": max(observed),
                 "temperature": rec["temperature"], "pH": rec["pH"], "substrate": rec["substrate"]})

table = pd.DataFrame(rows)
table.to_csv(RESULTS / "case3_noisy_enzyme_assay.csv", index=False)
print(f"True optimum velocity: {V_OPT:.2f} at 37 C, pH 7.4, 150 uM\n")
print(table.round(2).to_string(index=False))
print(f"\nMedian % of true optimum reached by the recommended conditions: "
      f"{table['pct_of_true_optimum'].median():.1f}")
print(f"Median overstatement of best observed over its true value: "
      f"{(table['best_observed'] - table['true_value_of_recommended']).median():.2f}")
