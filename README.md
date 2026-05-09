# EE209AS Fertilizer Recommendation Evaluation

This project supports an EE209AS AgriGuide AI workflow for evaluating fertilizer recommendations. It includes the fertilizer dataset, reproducible train/test splits, plotting scripts, prompt/output instructions, and a PySide6 grading GUI for comparing model recommendations against reference fertilizer labels.

## Project Layout

- `datasets/`: source fertilizer dataset and generated split datasets.
- `datasets/split-80-20/`, `datasets/split-70-30/`, `datasets/split-60-40/`: train, test, and model-facing test CSVs for each split.
- `python/`: Python tools for dataset splitting, plotting, and the grader GUI.
- `python/fertilizer_grader_gui/`: desktop GUI used for human grading.
- `scripts/`: Windows batch entry points for setup and runnable project tasks.
- `project-docs/`: grading rubrics, model output instructions, dataset notes, and proposal material.
- `plotting/`: generated charts for dataset distribution and split coverage.
- `grading-results/`: intended output location for grader result CSVs.
- `deps/requirements.txt`: pinned Python dependencies.

## Setup

Run the dependency installer from the repository root:

```bat
scripts\install-deps.bat
```

The script creates `.venv` if needed, upgrades `pip`, and installs the packages from `deps\requirements.txt`.

## Common Commands

Run the fertilizer grading GUI:

```bat
scripts\run_fertilizer_grader_gui.bat
```

Regenerate all dataset splits:

```bat
scripts\split_fertilizer_dataset.bat
```

Generate category distribution plots:

```bat
scripts\generate_category_distribution_plots.bat
```

Generate train/test category coverage plots for all splits:

```bat
scripts\generate_train_test_category_coverage_plot.bat
```

Generate train/test category coverage for specific splits:

```bat
scripts\generate_train_test_category_coverage_plot.bat 80-20
scripts\generate_train_test_category_coverage_plot.bat split-70-30
```

## Dataset Splits

The source dataset is `datasets/fertilizer-prediction-dataset.csv`.

Each generated split directory contains:

- `fertilizer-prediction-train.csv`: training data with reference `Fertilizer Name`.
- `fertilizer-prediction-test.csv`: test data with reference `Fertilizer Name`.
- `fertilizer-prediction-test-model.csv`: model-facing test data with `Fertilizer Name` removed.

The split script preserves category coverage for `Crop Type`, `Soil Type`, and `Fertilizer Name` when possible, adds `split_name`, and expects stable `item_id` values.

## Model Output and Grading Workflow

Use `project-docs/model-output-instructions.md` when asking a model to recommend fertilizers for a model-facing test file. The instructions define both the required CSV columns and the expected decision-support content for explanation, confidence, uncertainty/caution, and practical notes.

Use `project-docs/cohen-kappa-grading.md` for the human grading rubric. The grader GUI is intended to produce grading CSVs that can be compared between graders for Cohen's kappa calculations.

Recommended grading outputs belong in `grading-results/`.

## Development Rules

Project-specific agent rules live in `.agents/rules/`. Read those rules before changing the project.

When project behavior, setup, scripts, dependencies, file layout, or user workflow changes, update this README in the same change so it remains accurate.
