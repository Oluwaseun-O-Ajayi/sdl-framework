"""
SDL Framework: closed-loop experimental optimization following self-driving laboratory principles.

Author: Oluwaseun O. Ajayi
License: MIT
"""

__version__ = "1.1.0"
__author__ = "Oluwaseun O. Ajayi"
__license__ = "MIT"
__email__ = "oluwaseun.ajayi@uga.edu"

from .orchestrator import SDLOrchestrator, OptimizationConfig, Experiment
from .experiment_designer import ExperimentDesigner, DesignSpace, AcquisitionFunction

__all__ = [
    'SDLOrchestrator',
    'OptimizationConfig',
    'Experiment',
    'ExperimentDesigner',
    'DesignSpace',
    'AcquisitionFunction',
    '__version__',
]