"""Shared helpers for the case-study scripts: benchmark objectives with known
optima and a fixed-budget campaign runner.

Set the environment variable SDL_CASE_STUDY_SEEDS to run fewer repeats (the test
suite uses 1); the documented results use the default of 10.
"""

import logging
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
logging.disable(logging.CRITICAL)

from sdl_core import OptimizationConfig, SDLOrchestrator  # noqa: E402

N_SEEDS = int(os.environ.get("SDL_CASE_STUDY_SEEDS", "10"))
# Quick runs (fewer seeds) write to a temporary folder so the saved 10-seed results stay intact.
RESULTS = (Path(__file__).resolve().parent / "case_study_results" if N_SEEDS == 10
           else Path(tempfile.mkdtemp(prefix="sdl_case_study_")))
RESULTS.mkdir(exist_ok=True)

# Branin function: three global minima, value 0.397887 (Dixon and Szego 1978)
BRANIN_BOUNDS = {"x1": (-5.0, 10.0), "x2": (0.0, 15.0)}
BRANIN_MIN = 0.397887


def branin(p):
    x1, x2 = p["x1"], p["x2"]
    b, c, t = 5.1 / (4 * np.pi ** 2), 5 / np.pi, 1 / (8 * np.pi)
    return (x2 - b * x1 ** 2 + c * x1 - 6) ** 2 + 10 * (1 - t) * np.cos(x1) + 10


def run_campaign(objective, bounds, acquisition="EI", seed=0, n_initial=5, budget=30, minimize=True):
    """Run a fixed-budget campaign and return (best-so-far trajectory, all parameter dicts)."""
    config = OptimizationConfig(objective="minimize" if minimize else "maximize", parameter_space=bounds,
                                acquisition_function=acquisition, n_initial_experiments=n_initial,
                                max_iterations=budget - n_initial, patience=budget, random_state=seed)
    with tempfile.TemporaryDirectory() as tmp:
        sdl = SDLOrchestrator(config, lambda p: {"value": objective(p)},
                              lambda r: {"objective_value": r["value"]}, output_dir=tmp)
        report = sdl.run_optimization_campaign()
    return np.array(report["optimization_trajectory"]["cumulative_best"]), [e.parameters for e in sdl.experiments]


def random_search(objective, bounds, seed=0, budget=30, minimize=True):
    """Uniform random sampling with the same budget, as a baseline."""
    rng = np.random.default_rng(seed)
    values = [objective({k: rng.uniform(lo, hi) for k, (lo, hi) in bounds.items()}) for _ in range(budget)]
    return (np.minimum if minimize else np.maximum).accumulate(values)
