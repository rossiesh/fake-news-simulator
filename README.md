# Fake News Simulator

## Overview

This project was developed as part of the "Informatik und Gesellschaft" module.
It provides an abstract simulation of a social network, such as Instagram. In particular, it examines the spread of
disinformation ("fake news") based on various assumptions regarding the network. These assumptions also cover moderation
and the manner or extent of its implementation.

## Model Idea

The social network is simulated as a directed graph, where each node represents an account. An account can be either an
influencer or a regular user. Directed edges connect the nodes, representing the relationships between them. A directed
edge from account A to account B indicates that A follows B. If B shares a piece of disinformation, A can receive it.
Influencers are less common in this network but have a wider reach due to their larger number of followers.

## Model Assumptions

The aim of this project is not to replicate a real-world social network on platforms like Instagram in detail. The same
applies to recommendation algorithms and moderation strategies. Downranking and labeling, as moderation strategies, are
modeled solely in terms of their assumed effects on visibility and sharing behavior.

## Installation

The project requires Python 3.12 or newer. The required dependencies are defined in `pyproject.toml`.
Install the dependencies using `uv sync` (run in the project folder).
`uv` must be installed on the system.

## CLI Usage

Commands:

- `simulator init <experiment_name>`: Initializes a new experiment JSON file with default values.
- `simulator list`: Lists all generated experiments.
- `simulator validate <experiment_name>`: Validates an existing experiment based on rules defined in
  `experiment_schema.py`.
- `simulator start <experiment_name>`: Validates an experiment, creates scenarios, and simulates them. Subsequently,
  results and graphs are output to `results/`.

## Experiment Files

Experiment configurations are stored in `experiments/`. A file named `experiments/<experiment_name>.json` is
simulated using the command `simulator start <experiment_name>`. The following rules apply when specifying parameter
values:

- A maximum of two varying parameters is permitted. A varying parameter is identified by the fact that a list of values
  is assigned to it.
- Between two and three values may be assigned to each varying parameter.

## Simulation Process

When an experiment starts, the specified JSON file from `experiments/` is first loaded and validated against the
Pydantic schema in `experiment_schema`. Then, `scenario_generator` generates concrete scenarios from all varying
parameters. Up to 9 scenarios are possible per experiment. A scenario is repeated a certain number of times to allow for
average calculations. A new random graph is generated for each run. The same graph and the same starting node are used
for all scenarios within that run. This makes the scenarios within a run more comparable. Each scenario is then
simulated with the disinformation spreading stepwise through the follower relationships. After all runs, means and
standard deviations are calculated.
Finally, CSV files, a copy of the experiment configuration and PNG graphs are saved in the `results/` folder.

## Parameters

- `number_of_nodes`: Number of nodes in the graph. [500, 7000].
- `influencer_ratio`: Proportion of influencer nodes among all nodes. 0.05 corresponds to 5% influencers. [0, 1]
- `share_probability`: Probability that an account will share disinformation. [0, 1]
- `recipient_ratio`: Indicates the proportion of followers an account sends disinformation to when it shares it.
  0.3 means an account shares with 30% of its followers. `share_probability` determines whether an account will share at
  all. [0, 1]
- `check_probability`: Probability that an account will check potential disinformation and then refrain from sharing
  it. [0, 1]
- `moderation.type`: Choice of moderation strategy:
    - `none`: No moderation.
    - `label`: A contacted account is notified that the post contains disinformation. When active, a node's
      `share_probability` is reduced by `moderation.label_reduction_factor`.
    - `downrank`: Certain accounts are prevented from seeing disinformation. In the model this is abstracted by
      reducing a node's `recipient_ratio` by `moderation.downrank_reduction_factor` when moderation is active. This
      results in fewer other accounts seeing this disinformation.
    - `delete`: When active, disinformation is deleted. Its spread is stopped.
- `moderation.threshold_activation_ratio`: Moderation becomes active when
  `reached_accounts >= number_of_nodes * moderation.threshold_activation_ratio`. [0, 1]
- `runs_per_scenario`: Specifies how many times a scenario should be repeated. [30, 50].
- `max_steps_per_run`: Specifies how many steps are executed in a simulation before it terminates.
  Prevents excessively long simulations. [30, 100].

The following parameters are allowed as variable parameters:

- `share_probability`
- `recipient_ratio`
- `check_probability`
- `moderation.type`
- `moderation.threshold_activation_ratio`
- `moderation.label_reduction_factor`
- `moderation.downrank_reduction_factor`

All other parameters are not allowed as variable parameters because they significantly influence the structure of the
graph and would complicate the described simulation process.

## Storage of Results

Results are stored under `results/`. A subfolder is created for each simulated experiment, named as follows:
`<experiment_name>__<YYYY-MM-DD>_<HH-MM-SS>`.
The results are stored in each subfolder as follows:

- `00_experiment_config.json`: Copy of the validated experiment configuration.
- `01_scenario_table.csv`: All scenarios generated from the experiment with specific parameter values.
- `02_simulation_results.csv`: Results of all scenarios and runs.
- `03_scenario_summaries.csv`: Summaries of all scenarios including average values and standard deviations.
- `04_spread_summaries.csv`: For each scenario and each step, the average number of accounts reached up to that point is
  recorded.
- `05_reached_accounts.png`: Graph showing the average number of accounts reached per scenario. Also shows error ranges
  based on the standard deviation of reached accounts.
- `06_total_shares.png`: Graph showing the average number of shares of a piece of disinformation per scenario. Also
  shows error ranges based on the standard deviation of shares.
- `07_spread_over_steps.png`: Graph showing the time progression of average number of reached accounts per scenario.

## Example Experiments

The project includes six pre-configured experiments:

- `downrank_strength`: Varies `moderation.threshold_activation_ratio` and `moderation.downrank_reduction_factor`.
  Investigates the extent to which downranking must reduce reach in order to influence the spread.
- `label_strength`: Varies `moderation.threshold_activation_ratio` and `moderation.label_reduction_factor`.
  Investigates the extent to which a warning label must reduce sharing behavior in order to influence the spread.
- `moderation_type_and_threshold`: Varies `moderation.type` and `moderation.threshold_activation_ratio`. Investigates
  whether the type of moderation or the timing of its activation has a greater impact on the extent to which
  disinformation spreads.
- `moderation_under_high_spread`: Varies `moderation.type` and `moderation.threshold_activation_ratio` in a setup
  characterized by high `share_probability`, high `recipient_ratio`, and low `check_probability`. Tests moderation
  strategies under conditions of more intense spread dynamics.
- `share_and_check`: Varies `share_probability` and `check_probability`. Investigates how sharing and fact-checking
  behaviors influence the spread of disinformation in the absence of active moderation.
- `share_and_recipient_ratio`: Varies `share_probability` and `recipient_ratio`. Investigates whether the spread
  is influenced more by the probability of sharing or by the proportion of followers reached when sharing.

## Example Experiments - Main Findings/Results

- A high `check_probability` can slow the spread. This effect is particularly noticeable with low and medium
  partial probability. However, with very high partial probability, checking behavior alone is not always sufficient
  to prevent widespread reach.
- Labeling primarily reduces sharing. Since the disinformation remains visible, the number of shares decreases more than
  the reach achieved. Fewer shares do not automatically mean that fewer accounts come into contact with the
  disinformation.
- Early moderation is more effective than later moderation, especially if the measures are strong enough. With weak
  labels or weak downranking, the difference between early/late activation is sometimes small. If a moderation strategy
  is only activated after widespread dissemination, the disinformation has already reached many accounts.
- Whether a moderation measure is considered effective depends on the chosen metric. A measure can significantly reduce
  the number of shares without correspondingly reducing the reach achieved.
- High standard deviations indicate that random network structure and starting node (influencer or normal user) have a
  significant impact on individual runs.
