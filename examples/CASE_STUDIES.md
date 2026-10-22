# Case studies

Four worked examples that measure what a closed-loop campaign achieves on problems
whose optimum is known. All campaigns are simulated, use fixed random seeds and
are repeated ten times, so the spread between runs is reported along with the
typical result. Results are written to `examples/case_study_results/`. Reproduce
them with:

```bash
python examples/case_study_1_bo_vs_random.py
python examples/case_study_2_acquisition_functions.py
python examples/case_study_3_noisy_enzyme_assay.py
python examples/case_study_4_initial_design_size.py
```

The full set takes roughly ten minutes on a laptop. Setting the environment
variable `SDL_CASE_STUDY_SEEDS=1` runs a single repeat for a quick check; quick
runs write to a temporary folder and leave the saved results unchanged. The
numbers below were produced with version 1.1.1.

| Case | Application | Objective |
|---|---|---|
| 1 | Bayesian optimization against random search | Branin function, budget 30 |
| 2 | Choosing an acquisition function | Branin function, EI, UCB and PI |
| 3 | Optimizing a noisy simulated enzyme assay | Three parameters, 5% measurement noise |
| 4 | Choosing the size of the initial design | Branin function, 3 to 20 initial points |

The Branin function is a standard optimization benchmark on x1 in [-5, 10] and
x2 in [0, 15] with three global minima of value 0.397887. "Gap" is the best value
found minus this minimum, so 0 means the optimum was found.

## Case 1: Bayesian optimization against random search

**Question.** With the same budget of 30 experiments, how much closer to the
optimum does a model-guided campaign get than random sampling?

**Result.** Median gap over ten runs:

| After experiment | 5 | 10 | 15 | 20 | 30 |
|---|---|---|---|---|---|
| Bayesian optimization (EI) | 5.56 | 2.11 | 0.794 | 0.303 | 0.00563 |
| Random search | 10.4 | 6.15 | 2.98 | 1.77 | 1.70 |

All ten Bayesian optimization runs ended within 0.1 of the minimum, against none
of the ten random-search runs.

**What it shows.** The first five experiments are a space-filling design in both
cases, so the methods start similarly. Once the model guides the choice, the gap
closes quickly, while random sampling stalls. On this benchmark, random search
after 30 experiments is still further from the optimum than Bayesian
optimization after 15.

## Case 2: Comparing acquisition functions

**Question.** How do expected improvement (EI), upper confidence bound (UCB) and
probability of improvement (PI) compare on the same problem and budget?

**Result.**

| Acquisition | Median gap after 15 | Median gap after 30 | Runs within 0.01 | Median experiments to reach 0.01 |
|---|---|---|---|---|
| EI | 0.794 | 0.00563 | 8 of 10 | 24 |
| UCB | 2.16 | 0.000332 | 8 of 10 | 26.5 |
| PI | 0.164 | 0.000426 | 10 of 10 | 22 |

**What it shows.** All three reach the optimum in most runs. UCB explores more
early on and is slowest at 15 experiments, but its final values are among the
best. PI, with the package's default settings, was fastest on this smooth,
two-dimensional problem. These rankings are specific to the benchmark and should
be rechecked in simulation for a new problem before instrument time is committed,
which is what this framework is for.

## Case 3: A noisy simulated enzyme assay

**Question.** When every measurement carries 5% noise, how good are the
conditions a campaign recommends, and how far does the best observed value
overstate the truth?

**Objective.** Reaction velocity as a function of temperature (20 to 60 C), pH
(5 to 9) and substrate concentration (10 to 300 uM), with a temperature optimum at
37 C, a pH optimum at 7.4, Michaelis-Menten behaviour (Km 45 uM) and substrate
inhibition above 150 uM. The true optimum is 92.31 at 37 C, pH 7.4 and 150 uM.

**Result.** Over ten runs of 30 experiments, the recommended conditions reach a
median of 94.5% of the true optimum (range 83.5 to 98.8%). Temperature and pH are
found closely (34.6 to 38.6 C, pH 7.22 to 7.52). Substrate is less well
determined (97 to 145 uM, against a true 150 uM). The best observed value
overstates the true value at the recommended conditions by a median of 5.5.

**What it shows.** Velocity changes slowly with substrate near the optimum, so
noise hides the difference between 120 and 150 uM, while the sharp temperature
and pH optima are located well. Because the recommended point is the one with the
best noisy reading, its measured value is biased upwards; confirming the
recommended conditions with replicate measurements is the practical safeguard.

## Case 4: Size of the initial design

**Question.** With a fixed budget of 30 experiments, how many should be spent on
the initial Latin hypercube design?

**Result.**

| Initial points | Median gap after 30 | Worst gap after 30 |
|---|---|---|
| 3 | 0.00908 | 0.0416 |
| 5 | 0.00563 | 0.0228 |
| 10 | 0.0161 | 0.0574 |
| 20 | 0.0131 | 0.0437 |

**What it shows.** Every design size reached the optimum to within 0.06 in all
runs, and the default of five gave the smallest median and worst-case gaps. On a
smooth two-dimensional problem the result is not very sensitive to this choice;
problems with more parameters usually need more initial points, which can be
tested the same way before a real campaign.
