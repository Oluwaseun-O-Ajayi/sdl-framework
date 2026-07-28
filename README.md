# SDL Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**SDL Framework for closed-loop experimental optimization**

An open-source Python framework for designing, simulating, and analyzing self-driving laboratory (SDL) workflows. The framework combines Bayesian optimization, Gaussian-process surrogate modeling, acquisition-function-guided experiment selection, campaign orchestration, and experiment tracking to support reproducible closed-loop experimental optimization
 
The current release focuses on SDL workflow simulation, educational demonstrations, and computational prototyping. The included examples illustrate simulated enzyme optimization workflows, reproducible closed-loop optimization campaigns, and campaign-level reporting. Physical laboratory deployment requires validated experiment executors, instrument-control interfaces, safety systems, and independent experimental validation

---

## Overview

Traditional pharmaceutical research relies on manual experimentation where scientists design, execute, and analyze experiments sequentially. This approach is time-intensive, resource-heavy, and struggles with high-dimensional parameter spaces. SDL Framework addresses these challenges by providing reusable software components for closed-loop experimental optimization and self-driving laboratory workflow simulation:

- **Designs experiments intelligently** using Bayesian optimization and active learning
- **Supports experiment execution** through user-defined experiment executors and integration interfaces 
- **Analyzes results in real-time** with automated data processing pipelines
- **Makes decisions** about next experiments based on accumulating data
- **Supports reproducible closed-loop optimization workflows** through user-defined experiment executors and result-analysis pipelines
- **Demonstration workflows** illustrate adaptive Bayesian optimization strategies in representative simulated parameter spaces

## Scope and Limitations

The SDL Framework repository provides a computational framework for closed-loop experimental optimization using self-driving laboratory principles

The current version includes:

- **Bayesian optimization workflows**
- **Gaussian-process surrogate modeling**
- **Acquisition-function-guided experiment selection**
- **Campaign orchestration**
- **Tutorial examples**
- **Simulated enzyme optimization workflows**
- **Campaign reporting and visualization**

The repository should not be interpreted as a validated autonomous laboratory platform, drug-discovery system, or production laboratory execution environment

Examples included in the repository are primarily simulation-based demonstrations intended for education, workflow prototyping, and reproducibility-focused research

Users deploying the framework in physical laboratory environments are responsible for validation of instrument interfaces, optimization outputs, data integrity procedures, quality-control logic, and safety systems


## Simulation Versus Physical Experiments

The bundled enzyme optimization campaigns demonstrate expected behavior of closed-loop optimization workflows using simulated experimental systems

These demonstrations are intended to show:

- Bayesian optimization logic
- Campaign orchestration
- Experiment selection
- Result analysis
- Visualization
- Data export

Physical laboratory adoption requires validated instrument interfaces, independent experimental confirmation of optimized conditions, and documented safety procedures

Repository examples should therefore be interpreted as workflow demonstrations unless otherwise stated
---

##  Key Features

### Intelligent Experiment Design
- Bayesian optimization for efficient parameter space exploration
- Active learning strategies (Expected Improvement, UCB, Probability of Improvement)
- Multi-objective optimization support
- Constraint handling for practical experimental limitations
- Adaptive exploration-exploitation balancing

### Laboratory Automation Integration Framework
- Unified interface for diverse laboratory instruments
- Interface patterns and examples for connecting liquid handlers, analytical instruments, and laboratory automation systems through user-defined integrations
- Actual instrument support depends on implementation of communication layers by the user

### Real-Time Analytics
- Automated data processing and quality control
- Statistical validation and confidence intervals
- Response surface visualization
- Parameter importance analysis
- Performance metric tracking

### Complete Provenance Tracking
- Comprehensive logging of all experimental decisions
- Full reproducibility with experiment metadata
- Automated report generation
- Publication-ready data export

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Oluwaseun-O-Ajayi/sdl-framework.git
cd sdl-framework

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .

# Run example
python examples/enzyme_optimization_example.py
```

### Dependencies

Core scientific computing:
```
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
scikit-learn>=1.0.0
```

Visualization:
```
matplotlib>=3.4.0
seaborn>=0.11.0
plotly>=5.0.0
```

Optional (for full functionality):
```
jupyter>=1.0.0
pymongo>=4.0.0  # For database integration
redis>=4.0.0    # For distributed computing
```

---

## Quick Example

```python
from sdl_core.orchestrator import SDLOrchestrator, OptimizationConfig

# Define optimization problem
config = OptimizationConfig(
    objective="maximize",
    parameter_space={
        'temperature': (25.0, 45.0),
        'pH': (6.0, 8.5),
        'substrate_conc': (10.0, 200.0),
    },
    n_initial_experiments=10,
    max_iterations=30
)

# Define experimental functions
def run_experiment(params):
    # Interface with your instruments here
    result = plate_reader.measure(params)
    return result

def analyze_results(data):
    return {'objective_value': calculate_activity(data)}

# Initialize and run SDL
sdl = SDLOrchestrator(
    config=config,
    experiment_executor=run_experiment,
    result_analyzer=analyze_results
)

results = sdl.run_optimization_campaign()
print(f"Optimal conditions: {results['best_result']}")
```

---

## Documentation

### Protocol-Style Workflows

Publication-ready protocols for common SDL workflows:

1. **[Closed-Loop Optimization](docs/protocols/protocol_01_closed_loop_optimization.md)**
   - Closed-loop optimization of enzymatic reactions
   - Bayesian optimization implementation
   - Example optimization campaigns

2. **[High-Throughput ADMET Screening](docs/protocols/protocol_02_automated_admet_screening.md)**
   - Reproducible compound assessment workflow
   - Multi-parameter compound profiling
   - Integration with computational predictions

3. **[Automated Enzymatic Kinetics](docs/protocols/protocol_03_enzymatic_kinetics_workflow.md)**
   - Michaelis-Menten parameter determination
   - Inhibition constant measurements
   - High-throughput kinetic characterization

4. **[LC-MS Quantification Pipeline](docs/protocols/protocol_04_lcms_quantification_pipeline.md)**
   - Workflow simulation for sample-processing pipelines
   - Automated calibration and quantification
   - Quality control and validation

5. **[Robotic Workcell Integration](docs/protocols/protocol_05_robotic_workcell_integration.md)**
   - Multi-instrument coordination
   - Error recovery and fault tolerance
   - Safety systems and monitoring

### Demonstration Workflows

The current repository includes simulation-based workflows demonstrating:

- Closed-loop experimental optimization
- Bayesian optimization strategies
- Campaign orchestration
- Experiment selection workflows
- Parameter-importance analysis
- Optimization reporting and visualization

Additional validation datasets may be incorporated in future releases

### API Reference

- **[Orchestrator API](docs/api_reference.md#orchestrator)** - Core SDL coordination engine
- **[Experiment Designer API](docs/api_reference.md#designer)** - Bayesian optimization implementation
- **[Integration API](docs/api_reference.md#integrations)** - Instrument interface specifications

---

## Supported Applications

### Drug Discovery
- Lead compound optimization
- ADMET property screening  
- Structure-activity relationship studies
- Formulation development

### Biocatalysis
- Enzyme reaction optimization
- Protein engineering screening
- Biocatalytic process development
- Kinetic parameter determination

### Assay Development
- High-throughput screening assay optimization
- Detection method development
- Quality control protocol optimization
- Analytical method validation

### Process Development
- Manufacturing process optimization
- Scale-up parameter studies
- Stability testing protocols
- Quality by design (QbD) workflows

---

## Performance Assessment

The repository includes simulation-based examples demonstrating optimization workflow behavior, campaign orchestration, adaptive experiment selection, and optimization reporting

Performance characteristics should be evaluated independently for specific experimental systems and deployment environments

No claims of experimental efficiency gains, cost reductions, workflow acceleration, or laboratory performance improvements are made without independent validation

---

## Integration with Existing Tools

This SDL framework integrates seamlessly with other tools in the automation ecosystem:

### Related Repositories

From my automation toolkit:

- **[drugability-toolkit](https://github.com/Oluwaseun-O-Ajayi/drugability-toolkit)** - ADMET prediction integration
- **[enzymatic-kinetics-analyzer](https://github.com/Oluwaseun-O-Ajayi/enzymatic-kinetics-analyzer)** - Automated kinetic analysis
- **[lcms-data-processor](https://github.com/Oluwaseun-O-Ajayi/lcms-data-processor)** - LC-MS data pipeline
- **[robot-workcell-simulator](https://github.com/Oluwaseun-O-Ajayi/robot-workcell-simulator)** - Robot control interface
- **[sample-tracking-database](https://github.com/Oluwaseun-O-Ajayi/sample-tracking-database)** - LIMS integration
- **[assay-design-calculator](https://github.com/Oluwaseun-O-Ajayi/assay-design-calculator)** - Assay optimization

### Example Integration

```python
from drugability_toolkit import ADMETPredictor
from lcms_data_processor import LCMSAnalyzer
from sdl_core.orchestrator import SDLOrchestrator

# Combine tools in SDL workflow
def integrated_experiment(params):
    # Predict ADMET properties
    predictions = ADMETPredictor().predict(compound)
    
    # If promising, run physical experiment
    if predictions['drugability_score'] > 0.7:
        result = lcms.quantify(params)
        return result
    
    return {'skip': True}
```

---

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{ajayi2025sdlframework,
  title={SDL Framework: A Reproducible Python Framework for Closed-Loop Experimental Optimization Using Self-Driving Laboratory Principles},
  author={Ajayi, Oluwaseun O.},
  year={2025},
  publisher={GitHub},
  url={https://github.com/Oluwaseun-O-Ajayi/sdl-framework},
  doi={10.5281/zenodo.XXXXXXX}
}
```

### Publications
Protocol-style drafts are included to document self-driving laboratory workflows and may serve as the foundation for future protocol and methods publications

---
## Scientific Software Contribution

The primary contribution of this repository is a reusable software framework for closed-loop experimental optimization

Key implemented capabilities include:

- Gaussian-process surrogate modeling
- Expected Improvement acquisition
- Probability of Improvement acquisition
- Upper Confidence Bound acquisition
- Latin Hypercube experimental design
- Constraint-aware parameter spaces
- Campaign orchestration
- Parameter importance estimation
- Optimization visualization
- Reproducible campaign reporting

The framework is intended to help researchers understand, prototype, and extend self-driving laboratory workflows

## Contributing

Contributions are welcome! This project aims to support reproducible research and software development for closed-loop experimental optimization and self-driving laboratory workflows

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Areas for Contribution

- Additional instrument integrations
- New optimization algorithms
- Constraint handling methods
- Multi-objective optimization
- Distributed SDL coordination
- Documentation improvements

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Oluwaseun O. Ajayi**

Chemistry PhD Researcher specializing in:
- Bioanalytical Chemistry
- Structural Biology  
- Enzymology
- Laboratory Automation
- Computational Modeling

**Research Interests:** Self-driving laboratories, laboratory automation, closed-loop experimental optimization, scientific software, machine learning in chemistry

**Connect:**
- GitHub: [@Oluwaseun-O-Ajayi](https://github.com/Oluwaseun-O-Ajayi)
- Email: seunolanikeajayi@gmail.com | oluwaseun.ajayi@uga.edu
- ORCID: [0000-0003-0040-7217](https://orcid.org/0000-0003-0040-7217)
- LinkedIn: [linkedin.com/in/oluwaseun-o-ajayi-b-sc-mrsc](https://www.linkedin.com/in/oluwaseun-o-ajayi-b-sc-mrsc/)

---

## Acknowledgments

- University of Georgia Chemistry Department for research infrastructure
- Laboratory automation community for best practices
- Open-source scientific computing community (NumPy, SciPy, scikit-learn)

---

## Project Statistics

![GitHub stars](https://img.shields.io/github/stars/Oluwaseun-O-Ajayi/sdl-framework?style=social)
![GitHub forks](https://img.shields.io/github/forks/Oluwaseun-O-Ajayi/sdl-framework?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/Oluwaseun-O-Ajayi/sdl-framework?style=social)

---

## Roadmap

### Version 1.0 (Current)
-  Core Bayesian optimization engine
-  Basic instrument integration framework
-  Example workflows and documentation
-  Publication-ready protocols

### Version 1.1 (Q1 2025)
-  Multi-objective optimization
-  Advanced constraint handling
-  Real-time experiment monitoring dashboard
-  Cloud deployment support

### Version 2.0 (Q2 2025)
-  Distributed SDL coordination
-  Active learning with neural networks
-  Automated literature integration
-  Transfer learning across campaigns

---

## Quick Links

- [ Full Documentation](docs/)
- [ Example Notebooks](examples/notebooks/)
- [ Case Studies](docs/case_studies/)
- [ Report Issues](https://github.com/Oluwaseun-O-Ajayi/sdl-framework/issues)
- [ Discussions](https://github.com/Oluwaseun-O-Ajayi/sdl-framework/discussions)

---

<div align="center">

</div>

**Advancing reproducible experimental optimization through self-driving laboratory workflows**
