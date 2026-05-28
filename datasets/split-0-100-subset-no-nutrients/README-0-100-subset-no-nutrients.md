# Split-0-100 Subset No Nutrients

This split is a 15-row subset for testing model behavior when nutrient measurements are withheld.

Generated files:

- `fertilizer-prediction-test.csv`: selected rows with reference `Fertilizer Name`; `Nitrogen`, `Potassium`, and `Phosphorous` are replaced with `?`.
- `fertilizer-prediction-test-model.csv`: selected rows with `Fertilizer Name` removed and `Nitrogen`, `Potassium`, and `Phosphorous` replaced with `?` for model evaluation.

The selected `item_id` values match `datasets/split-0-100-subset/`. Give the model `fertilizer-prediction-test-model.csv` with `project-docs/model-instructions-no-nutrients.md`. Keep `fertilizer-prediction-test.csv` for the GUI and merge scripts so outputs can be checked against the reference labels.
