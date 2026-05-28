# Split-0-100

This split evaluates the model against all 99 source rows.

Generated files:

- `fertilizer-prediction-test.csv`: all 99 source rows with reference `Fertilizer Name`.
- `fertilizer-prediction-test-model.csv`: all 99 source rows with `Fertilizer Name` removed for model evaluation.

Give the model `fertilizer-prediction-test-model.csv`. Keep `fertilizer-prediction-test.csv` for the GUI and merge scripts so outputs can be checked against the reference labels.
