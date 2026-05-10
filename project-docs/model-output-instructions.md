# Fertilizer Model Output Instructions

Use these instructions with one split's model test file. Some splits also provide a training file; no-training splits such as `split-0-100` and `split-0-100-subset` do not.

The model test file omits the correct `Fertilizer Name`. Your task is to recommend a fertilizer for every row in the model test file and return one CSV file.

## Expected Decision-Support Fields

- `explanation`: Explain why the recommended fertilizer fits the specific row. Refer to the actual crop type, soil type, moisture, temperature/humidity, and nitrogen, potassium, and phosphorous values when they matter. Avoid generic fertilizer advice that could apply to any row.
- `confidence_statement`: State the confidence level in the recommendation in a calibrated way, with a row-specific reason for that confidence level. The statement should reflect that this is a benchmark prediction from limited tabular data, not a guaranteed agronomic prescription.
- `uncertainty_or_caution`: Identify relevant row-specific limits, ambiguity, or real-world checks. Mention that actual fertilizer decisions should be verified with soil testing, local agronomic guidance, crop conditions, or regional recommendations when appropriate.
- `decision_support_notes`: Add concise practical notes that help a human decision-maker interpret the recommendation responsibly for that row. Focus on usefulness, safety, and avoiding over-trust; do not present the model output as a substitute for expert agricultural advice.

## Required Output Filename

Name the file using the model name and split like this: `fertilizer-result-modelname-split-name.csv` and use the actual `split_name` value from the input file, such as `split-80-20` or `split-0-100-subset`.

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
- Set `prompt_version` to the prompt or instruction version used for the run, such as `model-instructions-v2` for outputs produced with the current short model instructions.
- Do not add `Fertilizer Name`; that is the hidden reference answer.
- Put your fertilizer recommendation in `model_fertilizer`.
- Use `explanation` to connect the crop, soil, moisture, temperature/humidity, and nutrient values to the recommendation.
- Use `confidence_statement` to state how confident the model is.
- Use `uncertainty_or_caution` to explain limitations and note that real fertilizer decisions should be verified with soil testing, local expertise, or agronomic guidance.
- Use `decision_support_notes` for concise practical notes that would help a human interpret the recommendation responsibly.
- Treat every row independently. Do not blindly copy a prior row's narrative fields or repeat identical boilerplate across rows for `confidence_statement`, `uncertainty_or_caution`, or `decision_support_notes`.
- Before finalizing the CSV, check whether multiple rows reuse the same generic sentence in the narrative fields. If they do, rewrite those fields so they reflect each row's crop, soil, moisture, temperature/humidity, and N/K/P values.

## Tooling Usages

You may not search dataset sites such as HuggingFace or Kaggle to find the datasets or similar datasets when developing your answers. You are free to search the internet and scientific sources, but refrain from searching on dataset sites in order to not directly examine potential matching datasets with answers in them please.
