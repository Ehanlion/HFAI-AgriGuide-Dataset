# Final Output Results Format

The final combined result files are created by:

```bat
scripts\merge_final_fertilizer_results.bat
```

The script lists available dataset splits and can create one split file or all split files.

## Output Location

Final CSV files are written to `results-final/` with this name pattern:

`fertilizer-result-final-graded-split-XX-XX.csv`

Example:

`results-final/fertilizer-result-final-graded-split-80-20.csv`

## Row Shape

The final CSV uses one row per model response.

Rows are matched by:

- `split_name`
- `item_id`
- `model_name`
- `prompt_version`

The merge tool only combines model, grader, and reference rows for the same split. Results from different splits are never merged into the same final file.

## Included Columns

Each final CSV contains:

- All columns from the model result CSV, including the model response fields.
- `actual_fertilizer`: the correct fertilizer copied from `Fertilizer Name` in the matching split's `fertilizer-prediction-test.csv`.
- `is_model_fertilizer_exact_match`: `true` when `model_fertilizer` exactly matches `actual_fertilizer` after trimming/case normalization, otherwise `false`.
- One set of grader rubric columns per grader.

Grader columns use this pattern:

`grader_<grader_id>_<rubric_column>`

Example columns for grader `ethan`:

- `grader_ethan_recommendation_correctness`
- `grader_ethan_explanation_relevance`
- `grader_ethan_clarity`
- `grader_ethan_uncertainty_calibration`
- `grader_ethan_decision_support_usefulness`

## Required Inputs

For a selected split, the merge tool requires:

- At least one model result CSV in `results-model/`.
- At least one grader result CSV in `results-grading/`.
- A matching reference test CSV at `datasets/split-XX-XX/fertilizer-prediction-test.csv`.

The tool prints a clear error if any required input is missing, if a file contains rows from the wrong split, or if rows cannot be matched.

## Cohen's Kappa Reports

Cohen's kappa reports are created by:

```bat
scripts\calculate_final_cohen_kappa.bat
```

The script lists available final CSV files and can calculate one file or all files.

Reports are printed to the console and saved to `results-final/` as text files named like:

`cohen-kappa-fertilizer-result-final-graded-split-80-20.txt`

The report calculates unweighted kappa for `recommendation_correctness` and linear weighted kappa for the 1-to-5 rubric columns.
