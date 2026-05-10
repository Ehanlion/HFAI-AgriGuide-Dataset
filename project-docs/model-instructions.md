# Fertilizer Model Instructions

Recommend exactly one fertilizer for each input row.

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
