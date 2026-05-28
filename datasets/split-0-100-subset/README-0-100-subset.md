# Split-0-100 Subset

This split is a 15-row subset for smaller model evaluation runs.

Generated files:

- `fertilizer-prediction-test.csv`: selected rows with reference `Fertilizer Name`.
- `fertilizer-prediction-test-model.csv`: selected rows with `Fertilizer Name` removed for model evaluation.

The selected rows cover every crop type, soil type, and fertilizer label in the source dataset. Give the model `fertilizer-prediction-test-model.csv`. Keep `fertilizer-prediction-test.csv` for the GUI and merge scripts so outputs can be checked against the reference labels.
