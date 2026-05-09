# Fertilizer Model Input Instructions

Use these instructions with one split's training file and matching model test file.

The training file contains examples with correct fertilizer recommendations. The model test file contains rows from the same split with the correct `Fertilizer Name` removed. Your job is to learn the pattern from the training file and apply it to each row in the model test file.

## Files to Use

- Training file: `datasets/split-XX-XX/fertilizer-prediction-train.csv`
- Model test file: `datasets/split-XX-XX/fertilizer-prediction-test-model.csv`
- Output format instructions: `project-docs/model-output-instructions.md`

Use files from the same split only. For example, if the test file is from `split-80-20`, use the `split-80-20` training file.

## How to Use the Training Dataset

- Treat the training CSV as labeled examples of fertilizer recommendations for different crop, soil, environmental, and nutrient conditions.
- Use `Fertilizer Name` in the training file as the reference label to learn from.
- Pay attention to the relationship between `Crop Type`, `Soil Type`, `Moisture`, `Temparature`, `Humidity `, `Nitrogen`, `Potassium`, `Phosphorous`, and `Fertilizer Name`.
- Use the training rows to infer which fertilizer labels are plausible for similar test rows.
- Do not copy a training row unless the test row genuinely matches the same pattern.
- Do not invent fertilizer labels outside the fertilizer names represented in the training file unless the output instructions explicitly allow it.
- Preserve `item_id` and `split_name` from the model test file so outputs can be matched during grading.

## How to Handle the Model Test Dataset

- Predict one fertilizer recommendation for every row in `fertilizer-prediction-test-model.csv`.
- Do not skip, merge, reorder, or duplicate rows.
- Do not add the hidden `Fertilizer Name` column to your output.
- Use the model test row's input fields exactly as given.
- If a row is ambiguous, still provide the best fertilizer recommendation, but explain the uncertainty in the required output fields.

## Important Evaluation Context

This benchmark evaluates more than exact fertilizer label accuracy. It also evaluates whether the recommendation is interpretable, appropriately cautious, and useful as human decision support.

Your output should help a human understand the likely fertilizer choice without implying that the model's answer is guaranteed or a substitute for expert agricultural advice.

## Tooling Usages

You may not search dataset sites such as Hugging Face or Kaggle to find this dataset or similar datasets when developing your answers. You may use general scientific or agricultural sources if needed, but do not search dataset repositories in a way that could reveal hidden test answers.
