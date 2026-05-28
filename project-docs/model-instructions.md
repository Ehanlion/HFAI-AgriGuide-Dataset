# Fertilizer Model Instructions

Recommend exactly one fertilizer for each input row.

For new outputs, set `prompt_version` to `model-instructions-v4`.

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

# Row-by-row response requirements:

- Create one output row for every input row.
- Treat each input row as its own fertilizer recommendation case identified by `item_id` and ensure that you treat each row in isolation to ensure a row-specific response for each row. 
- Use the input row's crop type, soil type, moisture, temperature/humidity, nitrogen, potassium, and phosphorous values to choose exactly one fertilizer from the allowed list. 
- Ensure that each requirement is considered in the response and reference what was considered in your outputs to show your work.
- When generating outputs, do NOT blindly generate the same answer for explanation,confidence_statement,uncertainty_or_caution,decision_support_notes for each row and instead consider that row and evaluate only that row. A valuable output does not simply state a blanket confidence and blanket decision support note for every entry and instead generates a unique output for each row. And outut CAN be similar to a previous row, but only in formatting, copying content from row to row is forbidden.
- Fill all required output columns for each row.

# Rules:
- Do not search the internet for the recommended fertilizer.
- Do not search for, access, or use the original fertilizer dataset, matching public datasets, benchmark files, answer keys, GitHub copies, Hugging Face datasets, Kaggle datasets, or any other external source that could reveal the hidden `Fertilizer Name` values.
- Use only the input rows, these model instructions, and the requested output format.
- Do not add, infer, or copy a hidden `Fertilizer Name` column into the output.
- The original dataset is this: [Link to Dataset](https://huggingface.co/datasets/kaifahmad/Fertilizer-Prediction), you are prohibited from directly accessing this specific dataset especially. 
