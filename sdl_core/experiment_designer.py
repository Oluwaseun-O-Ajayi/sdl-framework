"""
Experiment designer: Gaussian-process Bayesian optimization for closed-loop experiments.

Inputs are rescaled to the unit hypercube before modeling, and the kernel has one
length scale per parameter, so fitted length scales are comparable across
parameters and can be used as a rough indicator of parameter importance.

Author: Oluwaseun O. Ajayi
License: MIT
"""

import logging
import warnings
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, Matern, WhiteKernel

logger = logging.getLogger(__name__)

ACQUISITION_TYPES = ("EI", "UCB", "PI")
DEFAULT_EXPLORATION = {"EI": 0.01, "PI": 0.01, "UCB": 2.0}


@dataclass
class DesignSpace:
    """Experimental design space with continuous parameter bounds and optional constraints.

    Each constraint is a callable that takes a parameter dictionary and returns True
    when the point is allowed.
    """

    continuous_params: Dict[str, Tuple[float, float]]
    categorical_params: Optional[Dict[str, List[str]]] = None
    constraints: List[Callable[[Dict[str, float]], bool]] = field(default_factory=list)

    def __post_init__(self):
        if not self.continuous_params:
            raise ValueError("continuous_params must contain at least one parameter")
        for name, (lower, upper) in self.continuous_params.items():
            if not lower < upper:
                raise ValueError(f"Lower bound must be below upper bound for '{name}'")
        if self.constraints is None:
            self.constraints = []

    @property
    def names(self) -> List[str]:
        return list(self.continuous_params.keys())

    @property
    def bounds(self) -> np.ndarray:
        return np.array([self.continuous_params[p] for p in self.names], dtype=float)

    def get_dimensionality(self) -> int:
        return len(self.continuous_params)

    def validate_point(self, point: Dict[str, float]) -> bool:
        """Return True if the point lies within bounds and satisfies all constraints."""
        for name, (lower, upper) in self.continuous_params.items():
            if not lower <= point[name] <= upper:
                return False
        return all(constraint(point) for constraint in self.constraints)

    def to_unit(self, X: np.ndarray) -> np.ndarray:
        b = self.bounds
        return (np.asarray(X, dtype=float) - b[:, 0]) / (b[:, 1] - b[:, 0])

    def from_unit(self, U: np.ndarray) -> np.ndarray:
        b = self.bounds
        return b[:, 0] + np.asarray(U, dtype=float) * (b[:, 1] - b[:, 0])

    def to_dict(self, x: np.ndarray) -> Dict[str, float]:
        return {name: float(v) for name, v in zip(self.names, x)}


class AcquisitionFunction:
    """Acquisition functions for Bayesian optimization. Larger values are better."""

    @staticmethod
    def expected_improvement(mu, sigma, best_f, xi=0.01, maximize=True):
        mu, sigma = np.asarray(mu, float), np.asarray(sigma, float)
        improvement = (mu - best_f - xi) if maximize else (best_f - mu - xi)
        with np.errstate(divide="ignore", invalid="ignore"):
            z = np.where(sigma > 0, improvement / sigma, 0.0)
        ei = improvement * norm.cdf(z) + sigma * norm.pdf(z)
        return np.where(sigma > 0, np.maximum(ei, 0.0), 0.0)

    @staticmethod
    def upper_confidence_bound(mu, sigma, beta=2.0, maximize=True):
        mu, sigma = np.asarray(mu, float), np.asarray(sigma, float)
        return mu + beta * sigma if maximize else -(mu - beta * sigma)

    @staticmethod
    def probability_of_improvement(mu, sigma, best_f, xi=0.01, maximize=True):
        mu, sigma = np.asarray(mu, float), np.asarray(sigma, float)
        improvement = (mu - best_f - xi) if maximize else (best_f - mu - xi)
        with np.errstate(divide="ignore", invalid="ignore"):
            z = np.where(sigma > 0, improvement / sigma, np.where(improvement > 0, np.inf, -np.inf))
        return norm.cdf(z)


class ExperimentDesigner:
    """Propose experiments with a Gaussian-process surrogate and an acquisition function.

    Args:
        design_space: parameter bounds and constraints.
        acquisition_type: "EI", "UCB" or "PI".
        kernel_type: "RBF" or "Matern" (nu = 2.5).
        n_restarts: random restarts for optimizing the acquisition function.
        random_state: seed for all random choices; set it for reproducible campaigns.
        noise: if True, the kernel includes a learned white-noise term.
    """

    def __init__(self, design_space: DesignSpace, acquisition_type: str = "EI",
                 kernel_type: str = "RBF", n_restarts: int = 25,
                 random_state: Optional[int] = None, noise: bool = True):
        if acquisition_type not in ACQUISITION_TYPES:
            raise ValueError(f"acquisition_type must be one of {ACQUISITION_TYPES}")
        self.design_space = design_space
        self.acquisition_type = acquisition_type
        self.kernel_type = kernel_type
        self.n_restarts = n_restarts
        self.rng = np.random.default_rng(random_state)
        self.noise = noise
        self.gp = self._build_gp(random_state)
        self.X_data = np.empty((0, design_space.get_dimensionality()))
        self.y_data = np.empty(0)

    def _build_gp(self, random_state):
        d = self.design_space.get_dimensionality()
        if self.kernel_type == "RBF":
            base = RBF(length_scale=np.full(d, 0.3), length_scale_bounds=(1e-2, 1e2))
        elif self.kernel_type == "Matern":
            base = Matern(length_scale=np.full(d, 0.3), length_scale_bounds=(1e-2, 1e2), nu=2.5)
        else:
            raise ValueError(f"Unknown kernel type: {self.kernel_type}")
        kernel = ConstantKernel(1.0, (1e-3, 1e3)) * base
        if self.noise:
            kernel = kernel + WhiteKernel(1e-3, (1e-8, 1e0))
        return GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=5, alpha=1e-8,
                                        normalize_y=True, random_state=random_state)

    # ------------------------------------------------------------------ designs
    def propose_initial_designs(self, n_designs: int = 10, method: str = "LHS",
                                max_attempts: int = 100) -> List[Dict[str, float]]:
        """Initial designs by Latin hypercube ("LHS"), uniform random ("random"),
        or a three-level full factorial ("factorial", which ignores n_designs).
        Points that violate constraints are redrawn (LHS and random) or dropped (factorial)."""
        d = self.design_space.get_dimensionality()
        if method == "factorial":
            U = self._factorial_design(d)
            pts = [self.design_space.to_dict(x) for x in self.design_space.from_unit(U)]
            return [p for p in pts if self.design_space.validate_point(p)]
        designs: List[Dict[str, float]] = []
        for _ in range(max_attempts):
            need = n_designs - len(designs)
            if need <= 0:
                break
            if method == "LHS":
                U = self._latin_hypercube_sampling(need, d)
            elif method == "random":
                U = self.rng.uniform(0, 1, (need, d))
            else:
                raise ValueError(f"Unknown sampling method: {method}")
            for x in self.design_space.from_unit(U):
                p = self.design_space.to_dict(x)
                if self.design_space.validate_point(p):
                    designs.append(p)
        if len(designs) < n_designs:
            logger.warning("Only %d of %d initial designs satisfy the constraints", len(designs), n_designs)
        return designs[:n_designs]

    def _latin_hypercube_sampling(self, n_samples: int, n_dims: int) -> np.ndarray:
        """One sample in each of n_samples equal strata per dimension, strata shuffled independently."""
        samples = np.empty((n_samples, n_dims))
        for j in range(n_dims):
            samples[:, j] = (self.rng.permutation(n_samples) + self.rng.uniform(0, 1, n_samples)) / n_samples
        return samples

    @staticmethod
    def _factorial_design(n_params: int, levels: int = 3) -> np.ndarray:
        grid_1d = np.linspace(0.1, 0.9, levels)
        grids = np.meshgrid(*[grid_1d] * n_params, indexing="ij")
        return np.stack([g.ravel() for g in grids], axis=1)

    # ------------------------------------------------------------------- model
    def fit(self, X: np.ndarray, y: np.ndarray):
        """Replace the stored data with (X, y) and refit the surrogate."""
        X = np.atleast_2d(np.asarray(X, dtype=float))
        y = np.asarray(y, dtype=float).ravel()
        if len(X) != len(y):
            raise ValueError("X and y must have the same number of rows")
        self.X_data, self.y_data = X, y
        with warnings.catch_warnings():
            # Hyperparameters at a bound are expected with few observations.
            warnings.simplefilter("ignore", ConvergenceWarning)
            self.gp.fit(self.design_space.to_unit(X), y)
        return self

    def update_model(self, X_new: np.ndarray, y_new: np.ndarray):
        """Append new observations and refit the surrogate."""
        X_new = np.atleast_2d(np.asarray(X_new, dtype=float))
        return self.fit(np.vstack([self.X_data, X_new]),
                        np.concatenate([self.y_data, np.asarray(y_new, dtype=float).ravel()]))

    def predict_objective(self, X: np.ndarray, return_std: bool = True):
        U = self.design_space.to_unit(np.atleast_2d(X))
        if return_std:
            return self.gp.predict(U, return_std=True)
        return self.gp.predict(U), None

    def acquisition(self, X: np.ndarray, maximize: bool = True,
                    exploration_weight: Optional[float] = None) -> np.ndarray:
        """Acquisition values at points X (original parameter units)."""
        if len(self.y_data) == 0:
            raise ValueError("Fit the model with data before computing the acquisition function")
        w = DEFAULT_EXPLORATION[self.acquisition_type] if exploration_weight is None else exploration_weight
        mu, sigma = self.predict_objective(X)
        best_f = np.max(self.y_data) if maximize else np.min(self.y_data)
        if self.acquisition_type == "EI":
            return AcquisitionFunction.expected_improvement(mu, sigma, best_f, w, maximize)
        if self.acquisition_type == "UCB":
            return AcquisitionFunction.upper_confidence_bound(mu, sigma, w, maximize)
        return AcquisitionFunction.probability_of_improvement(mu, sigma, best_f, w, maximize)

    def propose_next_experiment(self, maximize: bool = True,
                                exploration_weight: Optional[float] = None) -> Dict[str, float]:
        """Maximize the acquisition function over the design space with random restarts."""
        d = self.design_space.get_dimensionality()

        def negative_acquisition(u):
            x = self.design_space.from_unit(u.reshape(1, -1))
            return -float(self.acquisition(x, maximize, exploration_weight)[0])

        best_u, best_val = None, np.inf
        for _ in range(self.n_restarts):
            u0 = self.rng.uniform(0, 1, d)
            res = minimize(negative_acquisition, u0, bounds=[(0.0, 1.0)] * d, method="L-BFGS-B")
            candidate = self.design_space.to_dict(self.design_space.from_unit(np.clip(res.x, 0, 1)))
            if res.fun < best_val and self.design_space.validate_point(candidate):
                best_u, best_val = np.clip(res.x, 0, 1), res.fun
        if best_u is None:
            logger.warning("No feasible optimum of the acquisition function; using a random feasible point")
            return self.propose_initial_designs(1, method="random")[0]
        return self.design_space.to_dict(self.design_space.from_unit(best_u))

    def get_parameter_importance(self) -> Dict[str, float]:
        """Normalized inverse length scales of the fitted kernel (inputs on the unit scale).

        This is a heuristic: a short length scale means the objective changes quickly
        along that parameter within the explored region."""
        try:
            params = self.gp.kernel_.get_params()
        except AttributeError:
            return {}
        scales = None
        for key, value in params.items():
            if key.endswith("length_scale") and np.ndim(value) == 1:
                scales = np.asarray(value, dtype=float)
                break
        if scales is None:
            return {}
        inv = 1.0 / scales
        inv = inv / inv.sum()
        return {name: float(v) for name, v in zip(self.design_space.names, inv)}

    def get_acquisition_surface(self, n_points: int = 50, param1: Optional[str] = None,
                                param2: Optional[str] = None, fixed_params: Optional[Dict] = None,
                                maximize: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Acquisition values on a 2-D grid; other parameters held at fixed_params
        (default: centre of their range). Returns (grid1, grid2, values)."""
        names = self.design_space.names
        param1 = param1 or names[0]
        param2 = param2 or (names[1] if len(names) > 1 else names[0])
        fixed = {n: float(np.mean(self.design_space.continuous_params[n])) for n in names}
        fixed.update(fixed_params or {})
        b1, b2 = self.design_space.continuous_params[param1], self.design_space.continuous_params[param2]
        g1, g2 = np.meshgrid(np.linspace(*b1, n_points), np.linspace(*b2, n_points))
        rows = []
        for v1, v2 in zip(g1.ravel(), g2.ravel()):
            p = dict(fixed)
            p[param1], p[param2] = v1, v2
            rows.append([p[n] for n in names])
        values = self.acquisition(np.array(rows), maximize).reshape(g1.shape)
        return g1, g2, values
