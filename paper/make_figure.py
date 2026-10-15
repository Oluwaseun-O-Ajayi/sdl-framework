"""Regenerate paper/figure.png: best value found against number of experiments on the
simulated enzyme example, for ten seeded SDL Framework campaigns and twenty random-sampling
runs with the same budget of 33 experiments."""

import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples"))
logging.disable(logging.INFO)

from enzyme_optimization_example import analyze_results, execute_experiment  # noqa: E402
from sdl_core import OptimizationConfig, SDLOrchestrator  # noqa: E402

SPACE = {"temperature": (25.0, 45.0), "pH": (6.0, 8.5),
         "substrate_conc": (20.0, 200.0), "enzyme_conc": (0.5, 3.0)}

N_INIT, N_TOTAL = 12, 33
bo_curves = []
for seed in range(10):
    np.random.seed(seed)  # simulator noise
    config = OptimizationConfig(objective="maximize", parameter_space=SPACE, n_initial_experiments=N_INIT,
                                max_iterations=N_TOTAL - N_INIT, patience=N_TOTAL, random_state=seed)
    sdl = SDLOrchestrator(config, execute_experiment, analyze_results,
                          output_dir=str(ROOT / "paper" / "_run"))
    report = sdl.run_optimization_campaign()
    bo_curves.append(report["optimization_trajectory"]["cumulative_best"])
bo_curves = np.array(bo_curves)
n = bo_curves.shape[1]

rng = np.random.default_rng(0)
np.random.seed(100)
curves = []
for _ in range(20):
    vals = [analyze_results(execute_experiment({k: rng.uniform(*b) for k, b in SPACE.items()}))["objective_value"]
            for _ in range(n)]
    curves.append(np.maximum.accumulate(vals))
curves = np.array(curves)

x = np.arange(1, n + 1)
fig, ax = plt.subplots(figsize=(6.5, 3.6), dpi=300)
ax.fill_between(x, np.percentile(curves, 25, axis=0), np.percentile(curves, 75, axis=0),
                color="0.8", label="Random sampling, interquartile range (20 runs)")
ax.plot(x, np.median(curves, axis=0), color="0.4", lw=1.5, label="Random sampling, median")
ax.fill_between(x, np.percentile(bo_curves, 25, axis=0), np.percentile(bo_curves, 75, axis=0),
                color="#1f6fb2", alpha=0.25, label="SDL Framework (EI), interquartile range (10 runs)")
ax.plot(x, np.median(bo_curves, axis=0), color="#1f6fb2", lw=2, label="SDL Framework (EI), median")
ax.axvline(N_INIT + 0.5, color="k", ls=":", lw=1)
ax.text(N_INIT + 0.8, 0.97, "model-guided experiments begin", fontsize=7, va="top", transform=ax.get_xaxis_transform())
ax.set_xlabel("Number of experiments")
ax.set_ylabel("Best velocity so far (uM/min)")
ax.legend(fontsize=8, frameon=False, loc="lower right")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(ROOT / "paper" / "figure.png")
print(f"{n} experiments. SDL median best {np.median(bo_curves[:, -1]):.1f} "
      f"(IQR {np.percentile(bo_curves[:, -1], 25):.1f} to {np.percentile(bo_curves[:, -1], 75):.1f}); "
      f"after initial design {np.median(bo_curves[:, N_INIT - 1]):.1f}. "
      f"Random median best {np.median(curves[:, -1]):.1f} "
      f"(IQR {np.percentile(curves[:, -1], 25):.1f} to {np.percentile(curves[:, -1], 75):.1f})")
