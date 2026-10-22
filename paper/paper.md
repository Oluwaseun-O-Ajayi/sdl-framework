---
title: 'SDL Framework: a compact Python implementation of closed-loop Bayesian optimization for self-driving laboratory workflows'
tags:
  - Python
  - Bayesian optimization
  - self-driving laboratories
  - experimental design
  - laboratory automation
authors:
  - name: Oluwaseun O. Ajayi
    orcid: 0000-0003-0040-7217
    affiliation: 1
affiliations:
  - name: Department of Chemistry, University of Georgia, Athens, Georgia, United States
    index: 1
date: 15 October 2026
bibliography: paper.bib
---

# Summary

Many laboratory experiments are tuned by adjusting several conditions at once, such as temperature, pH and reagent concentrations, where each experiment costs time and material. A self-driving laboratory replaces manual choice of the next experiment with a loop: a statistical model of the results so far proposes the next conditions, the experiment is run and analyzed, and the model is updated [@Abolhasani2023]. SDL Framework is a Python package that implements this loop in a small, readable code base. The user supplies two functions, one that runs an experiment for a given set of conditions and one that turns the raw output into an objective value, and the framework handles the initial experimental design, the surrogate model, the choice of the next experiment, stopping, and a complete record of the campaign.

# Statement of need

Bayesian optimization [@Jones1998; @Shahriari2016] is now a standard way to choose experiments when each one is expensive, and it is the decision engine of most self-driving laboratories. Researchers who want to adopt it in an ordinary laboratory, or to teach it, face two practical gaps. General-purpose optimization libraries expose the mathematics but leave the experimental loop (execution, failure handling, record keeping and stopping) to the user, while integrated platforms are tied to specific hardware. SDL Framework fills the space between them: it provides the full closed loop, with experiment execution delegated to a user function, in about 700 lines of documented Python that a student or bench scientist can read end to end.

The intended users are experimental chemists and biochemists who want to prototype an optimization campaign in simulation before connecting instruments, instructors teaching experimental design, and developers who need a minimal, inspectable reference implementation. Because the executor is an ordinary Python function, the same campaign code runs against a simulator, a script that reads instrument files, or an instrument-control interface.

# State of the field

Mature open-source tools exist for Bayesian optimization. BoTorch [@Balandat2020] provides state-of-the-art Monte-Carlo acquisition functions on PyTorch and is aimed at users comfortable with its probabilistic modeling stack. Summit [@Felton2021] benchmarks optimization strategies for chemical reactions on simulated reaction benchmarks. General machine-learning libraries such as scikit-learn [@Pedregosa2011] provide Gaussian-process regression but no experimental loop.

SDL Framework does not compete with these tools on algorithmic breadth. It was built as a separate package, rather than as a contribution to an existing one, because its purpose is different: to keep the complete loop, including execution, failure handling, stopping rules and campaign records, in a code base small enough to audit and teach from, with dependencies limited to NumPy, SciPy, pandas, scikit-learn [@Virtanen2020; @Pedregosa2011] and Matplotlib. Users who outgrow it can move the same executor and analyzer functions to a larger library.

# Software design

The package has two layers. `ExperimentDesigner` holds the surrogate model and the acquisition logic. Inputs are rescaled to the unit hypercube, and a Gaussian process [@Rasmussen2006] with one length scale per parameter and a learned noise term is fitted to the observations. Expected improvement, upper confidence bound and probability of improvement are available, and the acquisition function is maximized by bounded quasi-Newton optimization from random restarts. Initial designs use Latin hypercube [@McKay1979], random or factorial sampling, and user constraints are applied to both initial and proposed points.

`SDLOrchestrator` runs the campaign. It executes the initial design, fits the model, then alternates between proposing, executing and refitting until a budget is spent or no improvement larger than a set tolerance has occurred for a set number of consecutive experiments. Experiments that raise an exception are recorded as failed and excluded from the model rather than stopping the campaign. Every experiment, its parameters, results, status and timestamp are kept, and the campaign is exported as a JSON report and a CSV table. A single `random_state` makes the design and proposal sequence reproducible.

The main trade-offs follow from the goal of readability. Proposals are sequential, one experiment at a time; parameters are continuous; and the Gaussian process scales to the tens to hundreds of experiments typical of bench campaigns, not to thousands. Parameter importance is reported as normalized inverse length scales, which is a heuristic description of the fitted model and not a sensitivity analysis.

![Best value found against the number of experiments on the simulated enzyme example included in the repository. The SDL Framework campaign (expected improvement, 12 initial Latin hypercube experiments, 10 seeds) is compared with random sampling at the same budget (20 runs). Lines are medians and bands interquartile ranges. The two strategies are indistinguishable during the initial design and separate once model-guided experiments begin. The figure is regenerated by `paper/make_figure.py`.\label{fig:campaign}](figure.png)

The repository includes a simulated enzymatic reaction with a known optimum, used in the example, the tutorial notebook and \autoref{fig:campaign}, and a test suite that checks the acquisition functions against their closed forms, bounds and constraint handling, reproducibility under a fixed seed, and convergence on a test function with a known optimum. Tests run on Linux, macOS and Windows through continuous integration.

# Research impact statement

SDL Framework provides a working, tested reference for closed-loop experimental optimization that can be used to plan campaigns in simulation before instrument time is committed, to teach Bayesian experimental design with a code base students can read in one sitting, and to connect existing analysis code to an optimization loop through two functions. The bundled example and \autoref{fig:campaign} show the expected behavior on a problem with a known answer. Four reproducible case studies (`examples/CASE_STUDIES.md`) compare Bayesian optimization with random search, compare acquisition functions, optimize a noisy simulated enzyme assay and test the size of the initial design, each against a known optimum. The framework has not yet been validated on a physical instrument, and claims about experimental savings in any specific application require that validation.

# AI usage disclosure

The author designed and wrote the original version of this software in January 2026, and wrote this paper. In October 2026, Claude Opus 5.5 (Anthropic) was used for code review, refactoring, and testing. The author directed and verified all changes and takes full responsibility for the work.

# Acknowledgements

This work was conducted independently and received no specific funding from any agency in the public, commercial, or not-for-profit sectors.

# References
