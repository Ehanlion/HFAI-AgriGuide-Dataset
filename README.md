# EE209AS Fertilizer Recommendation Evaluation

This project supports an EE209AS AgriGuide AI workflow for evaluating fertilizer recommendations. It includes the fertilizer dataset, reproducible evaluation test sets, plotting scripts, model instructions, and a PySide6 grading GUI for comparing model recommendations against reference fertilizer labels.

## Pulling the Dataset Submodule

This repository uses `agriguide-final-set/` as a Git submodule for the standalone final dataset repository.

For a fresh clone, pull the project and dataset submodule together:

```bat
git clone --recurse-submodules <repo-url>
```

If you already cloned the project, initialize or update the dataset submodule from the repository root:

```bat
git submodule update --init --recursive
```

After pulling future parent-repo updates, refresh submodules as needed:

```bat
git submodule update --recursive --remote
```

## Project Layout

- `datasets/`: source fertilizer dataset and generated evaluation test sets.
- `datasets/split-0-100/`, `datasets/split-0-100-subset/`, `datasets/split-0-100-subset-no-nutrients/`: reference test CSVs and model-facing test CSVs.
- `python/`: Python tools for test-set generation, plotting, result merging, and the grader GUI.
- `python/fertilizer_grader_gui/`: desktop GUI used for human grading.
- `scripts/`: Windows batch entry points for setup and runnable project tasks.
- `project-docs/`: grading rubrics, model instructions, dataset notes, and proposal material.
- `agriguide-final-set/`: Git submodule for the standalone final dataset repository, including the final dataset README and copied grading rubric.
- `plotting/`: generated charts for dataset distribution and test-set coverage.
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

Regenerate all evaluation test sets:

```bat
scripts\build_fertilizer_test_sets.bat
```

Generate category distribution plots:

```bat
scripts\generate_category_distribution_plots.bat
```

Generate test category coverage plots:

```bat
scripts\generate_test_category_coverage_plot.bat
```

Generate test category coverage for specific test sets:

```bat
scripts\generate_test_category_coverage_plot.bat 0-100
scripts\generate_test_category_coverage_plot.bat split-0-100-subset
scripts\generate_test_category_coverage_plot.bat split-0-100-subset-no-nutrients
```

Merge model results, grader results, and reference answers into final CSVs:

```bat
scripts\merge_final_fertilizer_results.bat
```

Calculate Cohen's kappa for final CSVs:

```bat
scripts\calculate_final_cohen_kappa.bat
```

Extract `item_id` and grader result columns from a final graded CSV. The script lists
available final result CSVs in `results-final/` and writes a matching
`*-grader-fields.csv` file beside the selected input:

```bat
scripts\extract_final_grader_fields.bat
```

## Evaluation Test Sets

The source dataset is `datasets/fertilizer-prediction-dataset.csv`.

Evaluation directories contain:

- `fertilizer-prediction-test.csv`: test data with reference `Fertilizer Name`.
- `fertilizer-prediction-test-model.csv`: model-facing test data with `Fertilizer Name` removed.

`split-0-100` uses all source rows as test rows. `split-0-100-subset` uses 15 deterministic rows selected to cover every crop type, soil type, and fertilizer label. `split-0-100-subset-no-nutrients` uses the same 15 rows as `split-0-100-subset`, but replaces `Nitrogen`, `Potassium`, and `Phosphorous` values with `?` to test model behavior when nutrient measurements are withheld.

The test-set script adds `split_name`, preserves stable `item_id` values, and makes the reference CSV available only for grading and merging. Give the model the matching `fertilizer-prediction-test-model.csv`; the model writes recommendations; the GUI and merge scripts verify those outputs against `fertilizer-prediction-test.csv`.

## Model Output and Grading Workflow

Use `project-docs/model-instructions.md` for the standard prompt context listing allowed fertilizers, crop scope, required output columns, the current `prompt_version`, and minimal row-by-row response requirements.

Use `project-docs/model-instructions-no-nutrients.md` with `split-0-100-subset-no-nutrients`. These instructions tell the model that nutrient values are withheld as `?`, ask it to preserve those placeholders, and ask it to include both the visible row information and the crop's basic survival needs in the recommendation notes.

Use `project-docs/grading-rubric.md` for the evidence-based human grading rubric. The grader GUI loads the matching rubric options from `python/fertilizer_grader_gui/grading-rubric.json` and uses text labels for recommendation correctness plus 1-to-5 numeric ratings for explanation relevance, clarity, uncertainty calibration, and decision-support usefulness. Its grading CSVs can be compared between graders for Cohen's kappa calculations.

Use `project-docs/fertilizer-reference.md` for the focused fertilizer notes shown while grading `recommendation_correctness`. The grader GUI loads the matching reference data from `python/fertilizer_grader_gui/fertilizer-reference.json` and displays notes for both the reference fertilizer and the model-predicted fertilizer.

Recommended grading outputs belong in `results-grading/`.

Recommended model outputs belong in `results-model/`.

Use `scripts\merge_final_fertilizer_results.bat` after model outputs and human grading outputs exist for a split. The merge tool only lists splits that have model results, grader results, and reference test data available, such as `split-0-100`, `split-0-100-subset`, and `split-0-100-subset-no-nutrients`. It recognizes the filename model id before the split name and grader filename suffixes after the split name, so files such as `fertilizer-result-gpt-5.5-thinking-rev2-split-0-100-subset.csv` and matching grader files are kept separate even if their internal `model_name` column is unchanged. It shows the models and graders found for each split, requires every listed grader to grade every listed model response, then writes final wide-format CSVs to `results-final/` using the name pattern `fertilizer-result-final-graded-split-name.csv`.

Use `scripts\calculate_final_cohen_kappa.bat` after final CSVs exist. The kappa tool prints grader-pair agreement results, includes separate agreement sections for each model in a combined final CSV, and saves matching text reports in `results-final/`.

Use `scripts\extract_final_grader_fields.bat` after final CSVs exist to choose
one final graded CSV, such as `fertilizer-result-final-graded-split-0-100.csv`
or `fertilizer-result-final-graded-split-0-100-subset.csv`, and write a compact
grader-fields CSV with `item_id` plus shortened grader rubric columns.

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
