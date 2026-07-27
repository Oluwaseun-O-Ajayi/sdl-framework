---
title: 'A Reproducible Python Framework for Closed-Loop Experimental Optimization Using Self-Driving Laboratory Principles'
tags:
  - Python
  - self-driving laboratories
  - Bayesian optimization
  - Gaussian processes
  - active learning
  - enzyme optimization
  - laboratory automation
  - experimental design
  - scientific machine learning
authors:
  - name: Oluwaseun O. Ajayi
    orcid: https://orcid.org/0000-0003-0040-7217
    affiliation: 1
affiliations:
 - name: Department of Chemistry, University of Georgia, Athens, Georgia, USA
   index: 1
date: 2026-XX-XX
bibliography: paper.bib
---

# Summary

Closed-loop experimentation is increasingly important in chemistry, biochemistry, pharmaceutical research, and laboratory automation because experimental systems often involve multidimensional parameter spaces that are costly or time-consuming to explore manually. Self-driving laboratory (SDL) workflows address this challenge by linking experiment design, experiment execution, result analysis, model updating, and next-experiment recommendation within an adaptive optimization loop. However, many researchers and students encounter SDL concepts primarily as high-level descriptions rather than as reusable, inspectable software workflows.

`Autonomous Drug Discovery Lab` is an open-source Python framework for closed-loop experimental optimization using self-driving laboratory principles. For publication purposes, this manuscript frames the repository as a reusable SDL workflow framework rather than as a validated autonomous drug-discovery platform. The software provides core objects for experiment representation, optimization configuration, Gaussian-process-based experimental design, acquisition-function-guided experiment proposal, and campaign-level orchestration. The current implementation supports Expected Improvement, Upper Confidence Bound, and Probability of Improvement acquisition strategies; Latin hypercube, random, and factorial initial design generation; Gaussian Process model updating; next-experiment proposal by acquisition optimization; parameter-importance estimation from Gaussian Process length scales; and example autonomous enzyme optimization workflows.

The repository includes tutorials, quick-start documentation, protocol-style guidance, a simulated enzyme optimization campaign, optimization results, and CSV/JSON campaign outputs. The included campaign artifacts demonstrate the framework workflow: experimental parameters are proposed, simulated experiments are evaluated, results are analyzed, optimization progress is recorded, and summary files are exported. These examples are best interpreted as simulation-based demonstrations and educational workflows unless independent physical experimental validation is added. The framework is intended to support students, academic laboratories, and resource-limited research groups seeking transparent computational infrastructure for learning and prototyping SDL concepts.

# Statement of need

Traditional experimental optimization often follows a sequential pattern: a researcher selects conditions, performs experiments, analyzes the results, and then manually decides what to test next. This approach is intuitive but can become inefficient when four or more experimental parameters must be tuned simultaneously. Exhaustive grid searches scale exponentially with dimensionality, and one-factor-at-a-time strategies may miss interactions among variables. These challenges are common in enzymatic reaction optimization, assay development, formulation studies, analytical method development, and other experimental sciences.

Self-driving laboratories provide a conceptual solution by treating experimentation as an adaptive loop. A model proposes informative experimental conditions, the experiment is executed, the result is analyzed, and the model is updated before proposing the next experiment. In practice, researchers need lightweight software examples that make this loop concrete and modifiable. Many students and small laboratories do not have access to fully integrated robotic platforms, but they can still learn the computational structure of SDL workflows and prototype optimization campaigns using simulated or exported experimental data.

This framework addresses that need by providing a Python-based architecture for defining experimental parameter spaces, executing user-supplied experiment functions, analyzing returned results, updating surrogate models, proposing subsequent experiments, and exporting campaign-level outputs. The contribution is not the invention of Bayesian optimization or a claim of validated autonomous pharmaceutical discovery. Instead, the contribution is an accessible, reproducible implementation of a closed-loop SDL workflow that connects optimization theory with executable scientific software, tutorials, protocol guidance, and example enzyme optimization artifacts.

# Software functionality

The framework currently includes the following functionality:

- Experiment and optimization configuration dataclasses for campaign setup.
- User-defined parameter spaces with continuous bounds and optional constraints.
- Initial design generation using Latin hypercube, random, or factorial sampling.
- Gaussian Process surrogate modeling using scientific Python and scikit-learn components.
- Acquisition functions including Expected Improvement, Upper Confidence Bound, and Probability of Improvement.
- Acquisition-function optimization using bounded numerical optimization.
- Next-experiment proposal based on current observations and surrogate-model uncertainty.
- Parameter-importance estimation from Gaussian Process length scales.
- Objective prediction and acquisition-surface calculation for visualization and inspection.
- Campaign outputs including JSON reports, CSV optimization data, and visualization figures.
- Tutorial and protocol-style documentation for closed-loop optimization workflows.

# Demonstration workflow

The repository includes a simulated autonomous enzyme optimization example. The campaign artifacts include a JSON report describing 14 total experiments, 14 completed experiments, zero failed experiments, two optimization iterations, a maximization objective, and a best observed objective value of 207.15197725491555. The corresponding CSV file records temperature, pH, substrate concentration, enzyme concentration, objective value, specific activity, quality-control status, absorbance, enzyme-stability index, and experiment identifiers for each experiment.

The uploaded optimization figure summarizes the same enzyme optimization demonstration. It includes an optimization trajectory, best-so-far trace, final optimum marker, parameter-importance panel, parameter-evolution plots for temperature, pH, substrate concentration, and enzyme concentration, and a performance metrics panel. Because these artifacts correspond to a simulated example workflow, manuscript claims should describe them as demonstration outputs rather than validated physical laboratory results.

# Research and educational applications

The framework is appropriate for education, prototyping, and methods development in self-driving laboratory workflows. Potential applications include teaching Bayesian experiment design, simulating autonomous enzyme optimization, prototyping closed-loop assay optimization, comparing acquisition strategies, generating reproducible campaign reports, and building bridges between computational optimization and laboratory automation planning. The architecture may also support future integration with instrument-control software, sample tracking systems, LC-MS data processing, enzymatic kinetics analysis, and ADMET prediction tools, but such integrations should be documented as future extensions unless fully implemented and validated.

# Limitations

The current repository should not be presented as a fully validated autonomous drug-discovery platform. The available evidence supports an SDL framework with computational optimization components, tutorial workflows, protocol-style documentation, and simulated enzyme optimization outputs. Claims about operating continuously without human intervention, performance across many validated campaigns, or verified reductions in physical experiment count should be removed or explicitly reframed unless supporting validation data are added. The safest publication framing is a software framework for closed-loop experimental optimization and SDL workflow simulation.

Further work should include unit tests for the orchestrator and experiment designer, documented examples with fixed random seeds, clearer distinction between simulated and physical experiments, improved API documentation, and expanded validation using public benchmark functions or real experimental datasets where available. If physical laboratory validation is later performed, the manuscript can be extended toward a stronger methods paper.

# Acknowledgements

The author acknowledges the scientific Python ecosystem, including NumPy, SciPy, pandas, scikit-learn, Matplotlib, seaborn, and related open-source tools that support numerical computation, Gaussian Process modeling, optimization, and visualization. The development of this framework was motivated by research interests at the intersection of enzymology, analytical chemistry, laboratory automation, and scientific machine learning.

# References
