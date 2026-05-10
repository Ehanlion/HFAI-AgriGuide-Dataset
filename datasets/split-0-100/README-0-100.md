# Split-0-100

This split is used when we do not want to give the model a training set ahead of time. This is used to fully test the model with a raw, not-seen-before data set, to evaluate its performance.

Generated files:

- `fertilizer-prediction-test.csv`: all 99 source rows with reference `Fertilizer Name`.
- `fertilizer-prediction-test-model.csv`: all 99 source rows with `Fertilizer Name` removed for model evaluation.

This directory intentionally does not contain `fertilizer-prediction-train.csv`.
