"""
SDL Framework - campaign orchestrator.

Runs a closed-loop campaign: initial design, user-supplied experiment execution,
result analysis, surrogate-model update and next-experiment proposal.

Author: Oluwaseun O. Ajayi
License: MIT
"""

import numpy as np
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
from pathlib import Path

from .experiment_designer import DesignSpace, ExperimentDesigner


logger = logging.getLogger(__name__)


@dataclass
class Experiment:
    """Represents a single experiment in the SDL workflow"""
    exp_id: str
    parameters: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, running, completed, failed
    results: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert experiment to dictionary for serialization"""
        return {
            'exp_id': self.exp_id,
            'parameters': self.parameters,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'results': self.results,
            'metadata': self.metadata
        }


@dataclass
class OptimizationConfig:
    """Configuration for an optimization campaign.

    Args:
        objective: "maximize" or "minimize".
        parameter_space: bounds for each continuous parameter.
        constraints: callables that take a parameter dictionary and return True if allowed.
        acquisition_function: "EI", "UCB" or "PI".
        n_initial_experiments: size of the initial Latin hypercube design.
        max_iterations: maximum number of model-guided experiments.
        convergence_threshold: an experiment counts as an improvement only if it beats the
            best value so far by more than this fraction of the best value's magnitude.
        patience: stop after this many consecutive model-guided experiments without improvement.
        exploration_weight: xi for EI and PI, beta for UCB; None uses 0.01 (EI, PI) or 2.0 (UCB).
        random_state: seed for reproducible campaigns.
        kernel_type: "RBF" or "Matern".
    """
    objective: str
    parameter_space: Dict[str, Tuple[float, float]]
    constraints: List[Callable[[Dict[str, float]], bool]] = field(default_factory=list)
    acquisition_function: str = "EI"
    n_initial_experiments: int = 5
    max_iterations: int = 50
    convergence_threshold: float = 0.001
    patience: int = 5
    exploration_weight: Optional[float] = None
    random_state: Optional[int] = None
    kernel_type: str = "RBF"

    def __post_init__(self):
        if self.objective not in ("maximize", "minimize"):
            raise ValueError("objective must be 'maximize' or 'minimize'")
        if self.n_initial_experiments < 2:
            raise ValueError("n_initial_experiments must be at least 2")


class SDLOrchestrator:
    """
    Main orchestrator for self-driving laboratory workflows
    
    Coordinates experiment design, execution, analysis, and optimization
    in a closed-loop autonomous fashion.
    """
    
    def __init__(self, 
                 config: OptimizationConfig,
                 experiment_executor: Callable,
                 result_analyzer: Callable,
                 output_dir: str = "sdl_output"):
        """
        Initialize SDL Orchestrator
        
        Args:
            config: Optimization configuration
            experiment_executor: Function to execute experiments (robot/instruments)
            result_analyzer: Function to analyze experimental results
            output_dir: Directory for output files and logs
        """
        self.config = config
        self.experiment_executor = experiment_executor
        self.result_analyzer = result_analyzer
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.design_space = DesignSpace(continuous_params=dict(config.parameter_space),
                                        constraints=list(config.constraints))
        self.designer = ExperimentDesigner(self.design_space,
                                           acquisition_type=config.acquisition_function,
                                           kernel_type=config.kernel_type,
                                           random_state=config.random_state)
        self.experiments: List[Experiment] = []
        self.iteration = 0
        
        # Storage for optimization data
        self.X_data = []
        self.y_data = []
        
        logger.info("SDL Orchestrator initialized")
    
    def run_optimization_campaign(self) -> Dict[str, Any]:
        """
        Execute complete SDL optimization campaign
        
        Returns:
            Dictionary with optimization results and statistics
        """
        logger.info("=" * 60)
        logger.info("Starting SDL Optimization Campaign")
        logger.info("=" * 60)
        
        # Phase 1: initial design
        logger.info("[Phase 1] Initial design (%d experiments)", self.config.n_initial_experiments)
        initial_params = self.designer.propose_initial_designs(self.config.n_initial_experiments, method="LHS")
        for i, params in enumerate(initial_params):
            exp = self._execute_experiment(params, f"init_{i+1}")
            if exp.status == "completed":
                self._add_to_dataset(exp)
        if len(self.y_data) < 2:
            raise RuntimeError("Fewer than two initial experiments completed; cannot fit the surrogate model")
        self.designer.fit(np.array(self.X_data), np.array(self.y_data))

        # Phase 2: model-guided experiments
        logger.info("[Phase 2] Bayesian optimization")
        maximize = self.config.objective == "maximize"
        best = self._best_value()
        stale = 0
        self.stop_reason = "max_iterations"
        while self.iteration < self.config.max_iterations:
            self.iteration += 1
            next_params = self.designer.propose_next_experiment(maximize, self.config.exploration_weight)
            exp = self._execute_experiment(next_params, f"opt_{self.iteration}")
            if exp.status != "completed":
                continue
            self._add_to_dataset(exp)
            self.designer.fit(np.array(self.X_data), np.array(self.y_data))
            new_best = self._best_value()
            gain = (new_best - best) if maximize else (best - new_best)
            if gain > self.config.convergence_threshold * max(abs(best), 1e-12):
                stale = 0
            else:
                stale += 1
            best = new_best
            logger.info("Iteration %d: best so far %.4g (%d without improvement)", self.iteration, best, stale)
            if stale >= self.config.patience:
                self.stop_reason = f"no improvement in {self.config.patience} consecutive experiments"
                break

        # Generate final report
        results = self._generate_report()
        
        logger.info("\n" + "=" * 60)
        logger.info("SDL Campaign Completed")
        logger.info("=" * 60)
        
        return results
    
    def _execute_experiment(self, params: Dict[str, float], exp_id: str) -> Experiment:
        """Execute a single experiment"""
        exp = Experiment(exp_id=exp_id, parameters=params, status="running")
        self.experiments.append(exp)
        
        logger.info(f"Executing experiment {exp_id}")
        logger.info(f"Parameters: {params}")
        
        try:
            # Execute experiment using provided executor function
            raw_results = self.experiment_executor(params)
            
            # Analyze results
            analyzed_results = self.result_analyzer(raw_results)
            
            exp.results = analyzed_results
            exp.status = "completed"
            
            logger.info(f"Experiment {exp_id} completed successfully")
            logger.info(f"Results: {analyzed_results}")
            
        except Exception as e:
            logger.error(f"Experiment {exp_id} failed: {str(e)}")
            exp.status = "failed"
            exp.metadata['error'] = str(e)
        
        return exp
    
    def _best_value(self) -> float:
        y = np.array(self.y_data)
        return float(np.max(y) if self.config.objective == "maximize" else np.min(y))

    def _add_to_dataset(self, exp: Experiment):
        """Add completed experiment to dataset"""
        if exp.results and 'objective_value' in exp.results:
            param_names = list(self.config.parameter_space.keys())
            X_point = [exp.parameters[p] for p in param_names]
            y_point = exp.results['objective_value']
            
            self.X_data.append(X_point)
            self.y_data.append(y_point)
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        completed_exps = [e for e in self.experiments
                          if e.status == "completed" and e.results and 'objective_value' in e.results]
        
        y_array = np.array(self.y_data)
        
        if self.config.objective == "maximize":
            best_idx = np.argmax(y_array)
            best_value = np.max(y_array)
        else:
            best_idx = np.argmin(y_array)
            best_value = np.min(y_array)
        
        best_exp = completed_exps[best_idx]
        
        report = {
            'campaign_summary': {
                'total_experiments': len(self.experiments),
                'completed_experiments': len(completed_exps),
                'failed_experiments': len([e for e in self.experiments if e.status == "failed"]),
                'iterations': self.iteration,
                'objective': self.config.objective,
                'acquisition_function': self.config.acquisition_function,
                'stop_reason': getattr(self, 'stop_reason', 'not run'),
                'random_state': self.config.random_state,
            },
            'best_result': {
                'experiment_id': best_exp.exp_id,
                'parameters': best_exp.parameters,
                'objective_value': float(best_value),
                'all_results': best_exp.results
            },
            'optimization_trajectory': {
                'iterations': list(range(len(self.y_data))),
                'objective_values': [float(v) for v in self.y_data],
                'cumulative_best': self._get_cumulative_best(y_array)
            },
            'parameter_importance': self._calculate_parameter_importance()
        }
        
        # Save report
        report_path = self.output_dir / f"campaign_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Report saved to {report_path}")
        
        return report
    
    def _get_cumulative_best(self, y_array: np.ndarray) -> List[float]:
        """Calculate cumulative best values"""
        if self.config.objective == "maximize":
            return np.maximum.accumulate(y_array).tolist()
        else:
            return np.minimum.accumulate(y_array).tolist()
    
    def _calculate_parameter_importance(self) -> Dict[str, float]:
        """Heuristic importance from the fitted kernel length scales (see ExperimentDesigner)."""
        return self.designer.get_parameter_importance()

    def export_data(self, filename: str = "sdl_data.csv"):
        """Export experimental data to CSV"""
        import pandas as pd
        
        data_rows = []
        for exp in self.experiments:
            if exp.status == "completed" and exp.results:
                row = {**exp.parameters, **exp.results, 'exp_id': exp.exp_id}
                data_rows.append(row)
        
        df = pd.DataFrame(data_rows)
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Data exported to {output_path}")
        
        return df


# Example usage and demonstration
if __name__ == "__main__":
    # Example: Optimize enzyme reaction conditions
    
    def mock_enzyme_experiment(params: Dict[str, float]) -> Dict[str, Any]:
        """Simulate enzyme kinetics experiment"""
        # Simulate Michaelis-Menten with optimal conditions
        temp = params['temperature']
        ph = params['pH']
        substrate = params['substrate_conc']
        
        # Optimal around 37°C, pH 7.4
        temp_factor = np.exp(-((temp - 37) / 10) ** 2)
        ph_factor = np.exp(-((ph - 7.4) / 1.5) ** 2)
        
        # Michaelis-Menten kinetics
        Km = 50  # μM
        Vmax = 100 * temp_factor * ph_factor
        velocity = (Vmax * substrate) / (Km + substrate)
        
        # Add noise
        velocity += np.random.normal(0, 2)
        
        return {
            'reaction_velocity': velocity,
            'activity': velocity / 100,  # Normalized
        }
    
    def analyze_enzyme_results(raw_results: Dict[str, Any]) -> Dict[str, float]:
        """Analyze enzyme experiment results"""
        return {
            'objective_value': raw_results['reaction_velocity'],
            'normalized_activity': raw_results['activity']
        }
    
    # Configure optimization
    config = OptimizationConfig(
        objective="maximize",
        parameter_space={
            'temperature': (20.0, 50.0),  # °C
            'pH': (5.0, 9.0),
            'substrate_conc': (10.0, 200.0),  # μM
        },
        n_initial_experiments=8,
        max_iterations=25,
        convergence_threshold=0.005
    )
    
    # Initialize and run SDL
    sdl = SDLOrchestrator(
        config=config,
        experiment_executor=mock_enzyme_experiment,
        result_analyzer=analyze_enzyme_results,
        output_dir="example_sdl_output"
    )
    
    results = sdl.run_optimization_campaign()
    
    print("\n" + "=" * 60)
    print("OPTIMIZATION RESULTS")
    print("=" * 60)
    print(f"\nBest conditions found:")
    print(f"Temperature: {results['best_result']['parameters']['temperature']:.2f} °C")
    print(f"pH: {results['best_result']['parameters']['pH']:.2f}")
    print(f"Substrate: {results['best_result']['parameters']['substrate_conc']:.2f} μM")
    print(f"\nOptimal velocity: {results['best_result']['objective_value']:.2f}")
    print(f"Total experiments: {results['campaign_summary']['completed_experiments']}")
    
    # Export data
    sdl.export_data()