# Evidence-Based Fertilizer Grading Rubric

Use this rubric to grade one model response for one dataset row. The GUI loads the matching machine-readable rubric from `python/fertilizer_grader_gui/grading-rubric.json`; keep the column names and labels below unchanged so grading CSVs remain compatible with merge and Cohen's kappa scripts.

## Evidence Base

This rubric combines agronomic fertilizer-selection guidance with human-AI decision-support evidence:

- USDA NRCS nutrient management guidance emphasizes site-specific conditions, soil and plant testing, crop nutrient needs, realistic rates, and the 4R principles: right source, right rate, right time, and right place.
- The 4R Nutrient Stewardship framework says source selection should match crop and soil needs, rate decisions should reflect soil nutrient supply and plant demand, timing should reflect crop uptake and loss risk, and placement should keep nutrients where roots can use them.
- University extension fertilizer guidance explains that N-P-K labels identify nitrogen, phosphorus, and potassium concentrations; fertilizer selection should follow soil-test needs and avoid adding nutrients the soil does not need.
- Human-AI decision-support research shows that explanations and confidence statements should support appropriate reliance. Explanations can help, but persuasive explanations can also increase overreliance when the AI is wrong, so graders should reward clear limits, verification advice, and calibrated confidence.
- NIST AI RMF frames trustworthy AI around validity, reliability, safety, transparency, accountability, and management of harmful overreliance in real use contexts.

Sources:

- USDA NRCS, Nutrient Management: https://www.nrcs.usda.gov/getting-assistance/other-topics/nutrient-management
- 4R Nutrient Stewardship, What are the 4Rs?: https://4rcertified.org/what-are-the-4rs/
- University of Minnesota Extension, Interpreting soil tests for fruit and vegetable crops: https://extension.umn.edu/nutrient-management-specialty-crops/interpreting-soil-tests-fruit-and-vegetable-crops
- University of Minnesota Extension, What is the right fertilizer for your lawn and garden?: https://extension.umn.edu/managing-soil-and-nutrients/what-right-fertilizer-your-lawn-and-garden
- Utah State University Extension, Soil: https://extension.usu.edu/vegetableguide/management/soil.php
- NIST, AI Risk Management Framework 1.0: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
- Chen et al., Understanding the Role of Human Intuition on Reliance in Human-AI Decision-Making with Explanations: https://www.microsoft.com/en-us/research/publication/understanding-the-role-of-human-intuition-on-reliance-in-human-ai-decision-making-with-explanations/
- Vasconcelos et al., Explanations can reduce overreliance on AI systems during decision-making: https://cicl.stanford.edu/publication/vasconcelos2022explanations/

## Grading Rules

- Grade only what appears in the model response for the current row.
- Compare `model_fertilizer` against the hidden/reference `Fertilizer Name` shown in the GUI.
- For explanation categories, look for concrete use of row fields: crop type, soil type, moisture, temperature, humidity, nitrogen, potassium, and phosphorous.
- Reward fertilizer reasoning that uses N-P-K source fit, not generic plant-growth statements alone.
- Reward caution that treats the output as benchmark decision support, not a field-ready prescription.
- Do not give high scores for polished language if the answer ignores the row evidence or encourages overtrust.

## Category 1: Recommendation Correctness

Column: `recommendation_correctness`

Allowed labels: `correct`, `partially_correct`, `incorrect`

- `correct`: The model's primary fertilizer exactly matches the reference label for this row.
- `partially_correct`: The model misses the exact label but has meaningful N-P-K overlap with the reference source, or includes the reference fertilizer among multiple usable choices.
- `incorrect`: The model recommends a different fertilizer class, gives no usable fertilizer, invents a fertilizer outside the allowed set, or contradicts the reference label.

Use this category for the fertilizer label only. Do not raise or lower this score because the explanation is good or bad; explanation quality is graded separately.

## Category 2: Explanation Relevance

Column: `explanation_relevance`

Allowed labels: `1`, `2`, `3`, `4`, `5`

- `1`: Missing, unrelated, or generic explanation; does not use the row's crop, soil, environmental, or nutrient values.
- `2`: Mentions one relevant input but gives weak or mostly generic reasoning that could fit many rows.
- `3`: Uses some row inputs, usually N-P-K or crop, but misses important available evidence or leaves the fertilizer link vague.
- `4`: Uses most important row inputs and gives a fertilizer-specific justification grounded in nutrient source fit and crop or soil context.
- `5`: Clearly connects crop, soil type, moisture/temperature/humidity, and N-P-K values to the selected fertilizer using source-fit reasoning.

Evidence to look for:

- The response refers to the actual row values instead of generic fertilizer advice.
- N-P-K reasoning matches the fertilizer source. For example, urea is nitrogen-focused, DAP supplies nitrogen and phosphorus, and numeric blends should be interpreted as N-P-K grades.
- The explanation notices whether potassium or phosphorus appears absent, low, moderate, or high relative to the row pattern.

## Category 3: Interpretability and Clarity

Column: `clarity`

Allowed labels: `1`, `2`, `3`, `4`, `5`

- `1`: Confusing, contradictory, or missing a clear recommendation; a grader cannot tell what action is being suggested.
- `2`: Contains a recommendation but is hard to follow, poorly organized, or obscured by jargon.
- `3`: Understandable overall, but includes vague wording, unnecessary complexity, or minor internal inconsistency.
- `4`: Clear, organized, concise, and understandable to a non-expert grader.
- `5`: Very clear and concise; separates recommendation, evidence, confidence, and caution so a human can interpret it responsibly.

Evidence to look for:

- The fertilizer choice is easy to identify.
- The response does not contradict itself across the explanation, confidence statement, caution, and decision-support notes.
- Technical terms are either simple enough for the benchmark context or explained through the row evidence.

## Category 4: Uncertainty Calibration

Column: `uncertainty_calibration`

Allowed labels: `1`, `2`, `3`, `4`, `5`

- `1`: Dangerously overconfident; presents the output as guaranteed agronomic advice or omits caution for field use.
- `2`: Adds weak caution but still implies more certainty than the limited benchmark row supports.
- `3`: Includes some uncertainty or verification language, but it is generic or not tied to missing field evidence.
- `4`: Gives a clear recommendation while noting that real fertilizer decisions should be checked with soil testing, local guidance, crop stage, or field conditions.
- `5`: Balances recommendation and caution very well; explains limits of the dataset and avoids encouraging overreliance on the AI answer.

Evidence to look for:

- The model treats the answer as a benchmark prediction from limited tabular data.
- The response mentions soil testing, local extension/agronomic guidance, crop stage, yield target, weather, prior fertilizer history, or regional conditions when warning about field use.
- The confidence level is not inflated simply because the text sounds plausible.

## Category 5: Decision-Support Usefulness

Column: `decision_support_usefulness`

Allowed labels: `1`, `2`, `3`, `4`, `5`

- `1`: Unusable or actively misleading for human decision support.
- `2`: Contains one useful detail but major evidence, caution, or recommendation quality is missing or flawed.
- `3`: Somewhat useful, but a human would need substantial outside interpretation to understand or safely use the answer.
- `4`: Useful decision support: the answer states the fertilizer, gives relevant row-based reasoning, and includes appropriate verification cautions.
- `5`: Highly useful decision support: integrates label correctness, N-P-K source fit, case-specific reasoning, clear wording, and calibrated caution.

Evidence to look for:

- The answer helps a human understand why the fertilizer was selected.
- The answer avoids pretending to determine application rate, timing, or placement when the row does not contain enough information.
- The answer would reduce, not increase, the risk of blind trust in a wrong fertilizer recommendation.

## Quick Grader Checklist

Before assigning scores, ask:

1. Does the fertilizer label match the reference answer?
2. Does the explanation use actual row evidence, especially N-P-K values?
3. Does the response clearly connect fertilizer source to nutrient need?
4. Is the answer readable and internally consistent?
5. Does it communicate that real application decisions require soil testing or local agronomic guidance?
6. Would this help a human make a responsible decision without overtrusting the model?
