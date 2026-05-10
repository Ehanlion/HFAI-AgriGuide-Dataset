# EE209AS Fertilizer Recommendation Evaluation

This project supports an EE209AS AgriGuide AI workflow for evaluating fertilizer recommendations. It includes the fertilizer dataset, reproducible train/test splits, plotting scripts, prompt/output instructions, and a PySide6 grading GUI for comparing model recommendations against reference fertilizer labels.

## Project Layout

- `datasets/`: source fertilizer dataset and generated split datasets.
- `datasets/split-80-20/`, `datasets/split-70-30/`, `datasets/split-60-40/`: train, test, and model-facing test CSVs for each training split.
- `datasets/split-0-100/`, `datasets/split-0-100-subset/`: no-training test and model-facing test CSVs.
- `python/`: Python tools for dataset splitting, plotting, and the grader GUI.
- `python/fertilizer_grader_gui/`: desktop GUI used for human grading.
- `scripts/`: Windows batch entry points for setup and runnable project tasks.
- `project-docs/`: grading rubrics, model output instructions, dataset notes, and proposal material.
- `plotting/`: generated charts for dataset distribution and split coverage.
- `results-model/`: model output CSVs for each evaluated split.
- `results-grading/`: intended output location for grader result CSVs.
- `results-final/`: merged model, reference-answer, grader, and kappa report outputs.
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

The grader GUI uses a larger interface with emphasized field labels, bold model-reasoning sections, large bottom grading buttons, and a light/dark theme toggle.

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
scripts\generate_train_test_category_coverage_plot.bat split-0-100-subset
```

Merge model results, grader results, and reference answers into final CSVs:

```bat
scripts\merge_final_fertilizer_results.bat
```

Calculate Cohen's kappa for final CSVs:

```bat
scripts\calculate_final_cohen_kappa.bat
```

Extract `item_id` and grader result columns from the final graded subset CSV:

```bat
scripts\extract_final_grader_fields.bat
```

## Dataset Splits

The source dataset is `datasets/fertilizer-prediction-dataset.csv`.

Training split directories contain:

- `fertilizer-prediction-train.csv`: training data with reference `Fertilizer Name`.
- `fertilizer-prediction-test.csv`: test data with reference `Fertilizer Name`.
- `fertilizer-prediction-test-model.csv`: model-facing test data with `Fertilizer Name` removed.

No-training split directories contain only:

- `fertilizer-prediction-test.csv`: test data with reference `Fertilizer Name`.
- `fertilizer-prediction-test-model.csv`: model-facing test data with `Fertilizer Name` removed.

`split-0-100` uses all source rows as test rows. `split-0-100-subset` uses 15 deterministic rows selected to cover every crop type, soil type, and fertilizer label.

The split script preserves category coverage for `Crop Type`, `Soil Type`, and `Fertilizer Name` when possible, adds `split_name`, and expects stable `item_id` values.

## Model Output and Grading Workflow

Use `project-docs/model-input-instructions.md` to tell a model how to use a training split, or how to handle no-training splits that provide only the model-facing test file.

Use `project-docs/model-instructions.md` for the short no-clue prompt context listing allowed fertilizers, crop scope, required output columns, the current `prompt_version`, and row-specific response requirements.

Use `project-docs/model-output-instructions.md` when asking a model to return fertilizer recommendations. The instructions define both the required CSV columns and the expected decision-support content for explanation, confidence, uncertainty/caution, and practical notes. These narrative fields should be specific to each input row and should not reuse generic boilerplate across rows.

Use `project-docs/grading-rubric.md` for the evidence-based human grading rubric. The grader GUI loads the matching rubric options from `python/fertilizer_grader_gui/grading-rubric.json` and uses text labels for recommendation correctness plus 1-to-5 numeric ratings for explanation relevance, clarity, uncertainty calibration, and decision-support usefulness. Its grading CSVs can be compared between graders for Cohen's kappa calculations.

Use `project-docs/fertilizer-reference.md` for the focused fertilizer notes shown while grading `recommendation_correctness`. The grader GUI loads the matching reference data from `python/fertilizer_grader_gui/fertilizer-reference.json` and displays notes for both the reference fertilizer and the model-predicted fertilizer.

Recommended grading outputs belong in `results-grading/`.

Recommended model outputs belong in `results-model/`.

Use `scripts\merge_final_fertilizer_results.bat` after model outputs and human grading outputs exist for a split. The merge tool only lists splits that have model results, grader results, and reference test data available, including no-training splits such as `split-0-100` and `split-0-100-subset`. It recognizes the filename model id before the split name and grader filename suffixes after the split name, so files such as `fertilizer-result-gpt-5.5-thinking-rev2-split-0-100-subset.csv` and matching grader files are kept separate even if their internal `model_name` column is unchanged. It shows the models and graders found for each split, requires every listed grader to grade every listed model response, then writes final wide-format CSVs to `results-final/` using the name pattern `fertilizer-result-final-graded-split-name.csv`.

Use `scripts\calculate_final_cohen_kappa.bat` after final CSVs exist. The kappa tool prints grader-pair agreement results, includes separate agreement sections for each model in a combined final CSV, and saves matching text reports in `results-final/`.

The final CSV format is documented in `project-docs/output-results-format.md`.

## Development Rules

Project-specific agent rules live in `.agents/rules/`. Read those rules before changing the project.

When project behavior, setup, scripts, dependencies, file layout, or user workflow changes, update this README in the same change so it remains accurate.

# Grader Jump-Start

Steps to do:
1. Clone the project repository
2. Run the install script to setup the virtual environment, `.\scripts\install-deps.bat`
3. Run the grader-gui, `.\scripts\run_fertilizer_grader_gui.bat`
4. Specify grader name in the GUI and the output directory must be set to `results-grading`
