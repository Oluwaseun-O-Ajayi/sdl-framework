# Changelog

## 1.1.0 (2026-10)

### Fixed
- The orchestrator now honors `acquisition_function` (EI, UCB or PI); previously it always used expected improvement.
- Initial designs now use true Latin hypercube sampling; the orchestrator previously drew uniform random points.
- Convergence: a campaign now stops only after `patience` consecutive experiments without improvement, instead of after the first experiment that did not improve on the best value.
- Parameter importance is now computed from an anisotropic kernel on rescaled inputs; previously a single length scale was fitted, so importance could not distinguish parameters.

### Changed
- The orchestrator uses `ExperimentDesigner` from `experiment_designer.py`; the duplicate designer class in `orchestrator.py` was removed.
- Inputs are rescaled to the unit hypercube before Gaussian-process modeling, and the kernel includes a learned noise term.
- New `random_state` option for reproducible campaigns; new `patience` option.
- Packaging moved from `setup.py` to `pyproject.toml`; unused dependencies removed.
- The enzyme example compares the campaign with random sampling at the same budget instead of with an exhaustive grid.
- Unsupported performance statements were removed from the tutorial and protocol documents.

### Added
- Test suite (`tests/`) and continuous integration on Linux, macOS and Windows.
- `CONTRIBUTING.md` and this changelog.

## 1.0.0 (2026-07)
- Initial archived release.
