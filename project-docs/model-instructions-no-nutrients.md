# Fertilizer Model Instructions: No Nutrient Values

Recommend exactly one fertilizer for each input row.

For new outputs, set `prompt_version` to `model-instructions-no-nutrients-v1`.

Required output filename:

Name the output file `fertilizer-result-modelname-split-name.csv`.

- Replace `modelname` with the model name used for this run.
- Replace `split-name` with the exact `split_name` value from the input rows, such as `split-0-100-subset-no-nutrients`.
- Use lowercase letters, numbers, hyphens, and periods only in the filename.

Important input note:

- The `Nitrogen`, `Potassium`, and `Phosphorous` values have been withheld.
- Withheld nutrient values are shown as `?` to preserve the normal CSV shape.
- Do not treat `?` as zero. Treat it as unknown/missing nutrient information.

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

- Create one output row for every input row.
- Treat each input row as its own fertilizer recommendation case identified by `item_id`.
- Preserve the input row's `?` values in the `Nitrogen`, `Potassium`, and `Phosphorous` output columns.
- Use the visible crop type, soil type, moisture, temperature, and humidity values to choose exactly one fertilizer from the allowed list.
- In `explanation`, in addition to the normal output, additionally state the normal visible information used for the recommendation: crop type, soil type, moisture, temperature, and humidity.
- In `decision_support_notes`, include what the crop generally needs to survive and stay healthy, especially basic water, root-zone conditions, and likely macro-nutrient needs, while acknowledging that the actual nutrient measurements are withheld.
- Fill all required output columns for each row.

Rules:

- Do not search the internet for the recommended fertilizer.
- Do not search for, access, or use the original fertilizer dataset, matching public datasets, benchmark files, answer keys, GitHub copies, Hugging Face datasets, Kaggle datasets, or any other external source that could reveal the hidden `Fertilizer Name` values.
- Use only the input rows, these model instructions, and the requested output format.
- Do not add, infer, or copy a hidden `Fertilizer Name` column into the output.
- The original dataset is this: [Link to Dataset](https://huggingface.co/datasets/kaifahmad/Fertilizer-Prediction), you are prohibited from directly accessing this specific dataset especially.
