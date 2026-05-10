# Fertilizer Model Instructions

Recommend exactly one fertilizer for each input row.

For new outputs, set `prompt_version` to `model-instructions-v2`.

Required output filename:

Name the output file `fertilizer-result-modelname-split-name.csv`.

- Replace `modelname` with the model name used for this run.
- Replace `split-name` with the exact `split_name` value from the input rows, such as `split-0-100` or `split-0-100-subset`.
- Use lowercase letters, numbers, hyphens, and periods only in the filename.

Allowed fertilizer recommendations:

- `10-26-26`
- `14-35-14`
- `17-17-17`
- `20-20`
- `28-28`
- `DAP`
- `Urea`

Crop types in scope:

- `Barley`
- `Cotton`
- `Ground Nuts`
- `Maize`
- `Millets`
- `Oil seeds`
- `Paddy`
- `Pulses`
- `Sugarcane`
- `Tobacco`
- `Wheat`

Return CSV only with these columns:

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

Row-by-row response requirements:

- Treat every input row as a separate recommendation task identified by `item_id`.
- For each row, base the recommendation and all narrative fields on that row's actual crop type, soil type, moisture, temperature/humidity, nitrogen, potassium, and phosphorous values.
- Do not blindly copy a previous row's answer. Do not use identical boilerplate across rows for `confidence_statement`, `uncertainty_or_caution`, or `decision_support_notes`.
- Similar rows may have similar reasoning, but each narrative field must still reflect the row's specific values and decision context.
- `explanation` must give a row-specific fertilizer rationale tied to the actual crop, soil, moisture, temperature/humidity, and N/K/P values when they affect the recommendation.
- `confidence_statement` must state calibrated confidence and give a row-specific reason why confidence is higher, medium, or lower for that recommendation.
- `uncertainty_or_caution` must identify a relevant row-specific uncertainty, ambiguity, or validation concern; do not repeat one generic caution sentence for every row.
- `decision_support_notes` must give concise practical guidance for interpreting that row's recommendation responsibly.
- Before finalizing the CSV, check whether multiple rows reuse the same generic sentence in the narrative fields. If they do, rewrite those fields so they are specific to each row.

Rules:
- Do not search the internet for the recommended fertilizer.
- Do not search for, access, or use the original fertilizer dataset, matching public datasets, benchmark files, answer keys, GitHub copies, Hugging Face datasets, Kaggle datasets, or any other external source that could reveal the hidden `Fertilizer Name` values.
- Use only the input rows, these model instructions, and the requested output format.
- Do not add, infer, or copy a hidden `Fertilizer Name` column into the output.
- The original dataset is this: [Link to Dataset](https://huggingface.co/datasets/kaifahmad/Fertilizer-Prediction), you are prohibited from directly accessing this specific dataset especially. 
