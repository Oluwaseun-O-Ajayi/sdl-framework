"""Tests for the SDL Framework core: acquisition functions, designs, model updates and campaigns."""

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from sdl_core import (AcquisitionFunction, DesignSpace, ExperimentDesigner,
                      OptimizationConfig, SDLOrchestrator)

BOUNDS = {"x": (0.0, 10.0), "y": (-5.0, 5.0)}


def quadratic(params):
    """Smooth test objective with its maximum (value 0) at x = 7, y = -1."""
    return {"value": -((params["x"] - 7.0) ** 2) - (params["y"] + 1.0) ** 2}


def analyze(raw):
    return {"objective_value": raw["value"]}


# ------------------------------------------------------------------ acquisition
def test_expected_improvement_is_nonnegative_and_zero_without_uncertainty():
    mu = np.array([0.0, 1.0, 2.0])
    sigma = np.array([1.0, 0.5, 0.0])
    ei = AcquisitionFunction.expected_improvement(mu, sigma, best_f=1.5, xi=0.0)
    assert np.all(ei >= 0)
    assert ei[2] == 0.0


def test_expected_improvement_matches_closed_form():
    # For mu = best_f and xi = 0, EI = sigma * phi(0) = sigma / sqrt(2 pi)
    ei = AcquisitionFunction.expected_improvement(np.array([2.0]), np.array([3.0]), best_f=2.0, xi=0.0)
    assert ei[0] == pytest.approx(3.0 / np.sqrt(2 * np.pi))


def test_minimization_mirrors_maximization():
    mu, sigma = np.array([1.0, -1.0]), np.array([0.5, 0.5])
    ei_max = AcquisitionFunction.expected_improvement(mu, sigma, 0.0, 0.0, maximize=True)
    ei_min = AcquisitionFunction.expected_improvement(-mu, sigma, 0.0, 0.0, maximize=False)
    np.testing.assert_allclose(ei_max, ei_min)


def test_probability_of_improvement_is_a_probability():
    pi = AcquisitionFunction.probability_of_improvement(np.linspace(-3, 3, 7), np.ones(7), best_f=0.0)
    assert np.all((pi >= 0) & (pi <= 1))
    assert np.all(np.diff(pi) > 0)


def test_ucb_increases_with_uncertainty():
    ucb = AcquisitionFunction.upper_confidence_bound(np.zeros(3), np.array([0.0, 1.0, 2.0]), beta=2.0)
    np.testing.assert_allclose(ucb, [0.0, 2.0, 4.0])


# ------------------------------------------------------------------ design space
def test_design_space_rejects_invalid_bounds():
    with pytest.raises(ValueError):
        DesignSpace({"x": (1.0, 1.0)})


def test_unit_scaling_round_trip():
    space = DesignSpace(BOUNDS)
    X = np.array([[2.5, 0.0], [10.0, -5.0]])
    np.testing.assert_allclose(space.from_unit(space.to_unit(X)), X)


@pytest.mark.parametrize("method", ["LHS", "random", "factorial"])
def test_initial_designs_lie_within_bounds(method):
    designer = ExperimentDesigner(DesignSpace(BOUNDS), random_state=0)
    designs = designer.propose_initial_designs(8, method=method)
    assert len(designs) == (9 if method == "factorial" else 8)
    for d in designs:
        assert 0.0 <= d["x"] <= 10.0 and -5.0 <= d["y"] <= 5.0


def test_latin_hypercube_has_one_point_per_stratum():
    designer = ExperimentDesigner(DesignSpace(BOUNDS), random_state=1)
    U = designer._latin_hypercube_sampling(10, 2)
    for j in range(2):
        assert sorted(np.floor(U[:, j] * 10).astype(int)) == list(range(10))


def test_constraints_are_respected():
    space = DesignSpace(BOUNDS, constraints=[lambda p: p["x"] + p["y"] <= 6.0])
    designer = ExperimentDesigner(space, random_state=2)
    designs = designer.propose_initial_designs(10)
    assert all(d["x"] + d["y"] <= 6.0 for d in designs)
    X = np.array([[d["x"], d["y"]] for d in designs])
    designer.fit(X, np.array([quadratic(d)["value"] for d in designs]))
    proposal = designer.propose_next_experiment()
    assert proposal["x"] + proposal["y"] <= 6.0 + 1e-9


# ------------------------------------------------------------------ model
def test_proposal_is_in_bounds_and_seeded_runs_are_reproducible():
    def run():
        designer = ExperimentDesigner(DesignSpace(BOUNDS), random_state=3)
        designs = designer.propose_initial_designs(6)
        X = np.array([[d["x"], d["y"]] for d in designs])
        designer.fit(X, np.array([quadratic(d)["value"] for d in designs]))
        return designer.propose_next_experiment()

    a, b = run(), run()
    assert 0.0 <= a["x"] <= 10.0 and -5.0 <= a["y"] <= 5.0
    assert a == pytest.approx(b)


def test_update_model_appends_data():
    designer = ExperimentDesigner(DesignSpace(BOUNDS), random_state=4)
    designer.fit(np.array([[1.0, 1.0], [2.0, 2.0]]), np.array([0.0, 1.0]))
    designer.update_model(np.array([[3.0, 3.0]]), np.array([2.0]))
    assert designer.X_data.shape == (3, 2)
    assert designer.y_data.tolist() == [0.0, 1.0, 2.0]


def test_parameter_importance_identifies_the_active_parameter():
    # The objective depends on x only, so x should receive most of the importance.
    rng = np.random.default_rng(5)
    X = np.column_stack([rng.uniform(0, 10, 40), rng.uniform(-5, 5, 40)])
    y = np.sin(X[:, 0])
    designer = ExperimentDesigner(DesignSpace(BOUNDS), random_state=5)
    designer.fit(X, y)
    importance = designer.get_parameter_importance()
    assert set(importance) == {"x", "y"}
    assert sum(importance.values()) == pytest.approx(1.0)
    assert importance["x"] > importance["y"]


# ------------------------------------------------------------------ campaign
@pytest.mark.parametrize("acq", ["EI", "UCB", "PI"])
def test_campaign_approaches_the_known_optimum(tmp_path, acq):
    config = OptimizationConfig(objective="maximize", parameter_space=BOUNDS, acquisition_function=acq,
                                n_initial_experiments=6, max_iterations=15, patience=15, random_state=0)
    sdl = SDLOrchestrator(config, quadratic, analyze, output_dir=str(tmp_path))
    report = sdl.run_optimization_campaign()
    assert report["campaign_summary"]["acquisition_function"] == acq
    assert report["best_result"]["objective_value"] > -1.0  # within ~1 unit of the optimum (0)
    best_curve = report["optimization_trajectory"]["cumulative_best"]
    assert all(b2 >= b1 for b1, b2 in zip(best_curve, best_curve[1:]))


def test_campaign_stops_after_patience_without_improvement(tmp_path):
    flat = lambda p: {"value": 1.0}
    config = OptimizationConfig(objective="maximize", parameter_space=BOUNDS, n_initial_experiments=4,
                                max_iterations=50, patience=3, random_state=0)
    sdl = SDLOrchestrator(config, flat, analyze, output_dir=str(tmp_path))
    report = sdl.run_optimization_campaign()
    assert report["campaign_summary"]["iterations"] == 3
    assert "no improvement" in report["campaign_summary"]["stop_reason"]


def test_failed_experiments_are_recorded_not_fatal(tmp_path):
    calls = {"n": 0}

    def flaky(params):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("instrument error")
        return quadratic(params)

    config = OptimizationConfig(objective="maximize", parameter_space=BOUNDS, n_initial_experiments=4,
                                max_iterations=3, patience=10, random_state=0)
    sdl = SDLOrchestrator(config, flaky, analyze, output_dir=str(tmp_path))
    report = sdl.run_optimization_campaign()
    assert report["campaign_summary"]["failed_experiments"] == 1
    assert report["campaign_summary"]["completed_experiments"] == 6


def test_minimization_campaign(tmp_path):
    neg = lambda p: {"value": -quadratic(p)["value"]}
    config = OptimizationConfig(objective="minimize", parameter_space=BOUNDS, n_initial_experiments=6,
                                max_iterations=12, patience=12, random_state=1)
    sdl = SDLOrchestrator(config, neg, analyze, output_dir=str(tmp_path))
    report = sdl.run_optimization_campaign()
    assert report["best_result"]["objective_value"] < 1.0


def test_invalid_configuration_is_rejected():
    with pytest.raises(ValueError):
        OptimizationConfig(objective="best", parameter_space=BOUNDS)
    with pytest.raises(ValueError):
        ExperimentDesigner(DesignSpace(BOUNDS), acquisition_type="XYZ")


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("script", sorted(p.name for p in (ROOT / "examples").glob("case_study_*.py")))
def test_case_studies_run(script, tmp_path):
    """Each case study runs end to end (one seed; the documented results use ten)."""
    env = dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8", SDL_CASE_STUDY_SEEDS="1")
    proc = subprocess.run([sys.executable, str(ROOT / "examples" / script)], cwd=tmp_path, env=env,
                          capture_output=True, text=True, timeout=900)
    assert proc.returncode == 0, proc.stderr[-2000:]
