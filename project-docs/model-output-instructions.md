# Fertilizer Model Output Instructions

Use these instructions with one split's training file and matching model test file.

The training file contains correct fertilizer recommendations. The model test file omits the correct `Fertilizer Name`. Your task is to recommend a fertilizer for every row in the model test file and return one CSV file.

## Expected Decision-Support Fields

- `explanation`: Explain why the recommended fertilizer fits the specific row. Refer to the actual crop type, soil type, moisture, temperature/humidity, and nitrogen, potassium, and phosphorous values when they matter. Avoid generic fertilizer advice that could apply to any row.
- `confidence_statement`: State the confidence level in the recommendation in a calibrated way. The statement should reflect that this is a benchmark prediction from limited tabular data, not a guaranteed agronomic prescription.
- `uncertainty_or_caution`: Identify relevant limits, ambiguity, or real-world checks. Mention that actual fertilizer decisions should be verified with soil testing, local agronomic guidance, crop conditions, or regional recommendations when appropriate.
- `decision_support_notes`: Add concise practical notes that help a human decision-maker interpret the recommendation responsibly. Focus on usefulness, safety, and avoiding over-trust; do not present the model output as a substitute for expert agricultural advice.

## Required Output Filename

Name the file using the model name and split like this: `fertilizer-result-modelname-split-XX-XX.csv` and use the actual model name and the `split-XX-XX` value from the input file.

## Required Output Format

Return CSV only. Do not include Markdown fences, comments, explanations outside the CSV, or extra summary text.

Keep one output row for every input row. Do not skip rows and do not reorder rows.

Required columns:

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

## Field Rules

- Copy `item_id`, `split_name`, and all input condition fields exactly from the model test file.
- Do not add `Fertilizer Name`; that is the hidden reference answer.
- Put your fertilizer recommendation in `model_fertilizer`.
- Use `explanation` to connect the crop, soil, moisture, temperature/humidity, and nutrient values to the recommendation.
- Use `confidence_statement` to state how confident the model is.
- Use `uncertainty_or_caution` to explain limitations and note that real fertilizer decisions should be verified with soil testing, local expertise, or agronomic guidance.
- Use `decision_support_notes` for concise practical notes that would help a human interpret the recommendation responsibly.
