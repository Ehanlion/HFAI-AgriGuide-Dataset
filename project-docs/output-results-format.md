# Final Output Results Format

The final combined result files are created by:

```bat
scripts\merge_final_fertilizer_results.bat
```

The script lists only complete dataset splits that can be generated from the available files. A split is complete when it has at least one model result CSV, at least one grader result CSV, and the matching reference test CSV. The menu also shows the models and graders found for each split. The script can create one split file or all complete split files.

## Output Location

Final CSV files are written to `results-final/` with this name pattern:

`fertilizer-result-final-graded-split-name.csv`

Example:

`results-final/fertilizer-result-final-graded-split-80-20.csv`

`results-final/fertilizer-result-final-graded-split-0-100-subset.csv`

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

## Example Columns for Two Models and Two Graders

If two model result files exist for the same split, and two graders each grade both models, the grader folder can contain four grader CSV files:

- `fertilizer-result-model-a-split-80-20-ethan.csv`
- `fertilizer-result-model-a-split-80-20-rachel.csv`
- `fertilizer-result-model-b-split-80-20-ethan.csv`
- `fertilizer-result-model-b-split-80-20-rachel.csv`

The final CSV still has one row per model response. It does not create separate grader columns for each model, because the model identity is already stored on each row in `model_name` and `prompt_version`.

A typical final CSV header for two graders would contain columns like:

- `item_id`
- `split_name`
- `Temparature`
- `Humidity `
- `Moisture`
- `Soil Type`
- `Crop Type`
- `Nitrogen`
- `Potassium`
- `Phosphorous`
- `model_name`
- `prompt_version`
- `model_fertilizer`
- `explanation`
- `confidence_statement`
- `uncertainty_or_caution`
- `decision_support_notes`
- `actual_fertilizer`
- `is_model_fertilizer_exact_match`
- `grader_ethan_recommendation_correctness`
- `grader_ethan_explanation_relevance`
- `grader_ethan_clarity`
- `grader_ethan_uncertainty_calibration`
- `grader_ethan_decision_support_usefulness`
- `grader_rachel_recommendation_correctness`
- `grader_rachel_explanation_relevance`
- `grader_rachel_clarity`
- `grader_rachel_uncertainty_calibration`
- `grader_rachel_decision_support_usefulness`

For each `item_id`, there would usually be two rows: one for Model A and one for Model B. Ethan and Rachel's grades for Model A are stored on the Model A row, and their grades for Model B are stored on the Model B row.

The merge tool requires complete grader coverage. If Ethan and Rachel are both present for a split, then both graders must have graded every model response included in that split. For example, if Rachel graded Model A but did not grade Model B, the merge fails instead of creating a final CSV with blank Rachel columns for Model B.

## Required Inputs

For a selected split, the merge tool requires:

- At least one model result CSV in `results-model/`.
- At least one grader result CSV in `results-grading/`.
- A matching reference test CSV at `datasets/split-name/fertilizer-prediction-test.csv`.

The tool prints a clear error if any required input is missing, if a file contains rows from the wrong split, if rows cannot be matched, or if any grader is missing grades for a model response in the selected split.

Splits that do not have all required input categories are not shown in the selection menu.

## Cohen's Kappa Reports

Cohen's kappa reports are created by:

```bat
scripts\calculate_final_cohen_kappa.bat
```

The script lists available final CSV files and can calculate one file or all files.

Reports are printed to the console and saved to `results-final/` as text files named like:

`cohen-kappa-fertilizer-result-final-graded-split-80-20.txt`

`cohen-kappa-fertilizer-result-final-graded-split-0-100-subset.txt`

The report calculates unweighted kappa for `recommendation_correctness` and linear weighted kappa for the 1-to-5 rubric columns.

When a final CSV contains multiple models, the kappa report includes:

- Overall agreement across all model rows.
- Separate agreement sections for each `model_name` and `prompt_version`.

This means a final CSV containing two models and two graders will produce distinct Cohen's kappa scores for each model's graded responses, plus an overall score across both models.
