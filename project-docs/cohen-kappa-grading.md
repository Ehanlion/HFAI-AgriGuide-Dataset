# Cohen's Kappa Grading Rubric

This document defines the human grading rubric for AgriGuide AI fertilizer recommendation responses and explains how to structure the grades so Cohen's kappa can be calculated cleanly.

## Core Rule

It is okay to mix label styles across different rubric categories.

For example, `recommendation_correctness` can use text labels like `correct`, `partially_correct`, and `incorrect`, while `explanation_relevance`, `clarity`, `uncertainty_calibration`, and `decision_support_usefulness` can use a `0-5` scale.

The important rule is that each individual rubric column must have one fixed set of allowed labels, and both graders must use that same set.

## Recommended Grading Unit

Each grade should apply to one AI response for one dataset item.

Use one row per grader per response. The same AI response should be graded independently by both team members before comparing scores.

Recommended identifier columns:

- `item_id`
- `model_name`
- `prompt_version`
- `grader_id`
- `reference_fertilizer`
- `model_fertilizer`

The fields `item_id`, `model_name`, and `prompt_version` are what let us match Ethan's grade to Rachel's grade for the same response.

## Rubric Columns

### Recommendation Correctness

Column name:

`recommendation_correctness`

Allowed labels:

- `correct`
- `partially_correct`
- `incorrect`

Breakdown:

- `correct`: The AI recommends the same fertilizer as the dataset label.
- `partially_correct`: The AI does not give the exact dataset label, but the recommendation has meaningful nutrient overlap or gives the correct fertilizer as one of multiple options.
- `incorrect`: The AI recommends a different fertilizer, gives no usable fertilizer, or gives advice that conflicts with the dataset label.

Use this category to evaluate whether the model got the main fertilizer recommendation right.

### Explanation Relevance

Column name:

`explanation_relevance`

Allowed labels:

- `0`
- `1`
- `2`
- `3`
- `4`
- `5`

Breakdown:

- `0`: The explanation is missing or unrelated to the given case.
- `1`: The explanation is mostly generic and barely connects to the input.
- `2`: The explanation mentions one relevant input, but the reasoning is weak or mostly incomplete.
- `3`: The explanation uses some relevant input values, but misses important factors or does not clearly connect them to the fertilizer.
- `4`: The explanation uses most important inputs and gives a reasonable fertilizer-specific justification.
- `5`: The explanation clearly connects the crop, soil, moisture, temperature/humidity, and nutrient levels to the fertilizer recommendation.

Use this category to evaluate whether the model explains the recommendation using the actual dataset fields instead of giving generic fertilizer advice.

### Interpretability and Clarity

Column name:

`clarity`

Allowed labels:

- `0`
- `1`
- `2`
- `3`
- `4`
- `5`

Breakdown:

- `0`: The response is confusing, contradictory, or impossible to use.
- `1`: The response is very hard to follow and lacks a clear recommendation.
- `2`: The response has a recommendation, but the wording is vague, cluttered, or poorly organized.
- `3`: The response is understandable but has some unclear reasoning or unnecessary complexity.
- `4`: The response is clear, organized, and understandable for a non-expert.
- `5`: The response is very clear, concise, and easy for a non-expert to act on responsibly.

Use this category to evaluate whether the response is understandable to a human decision-maker.

### Uncertainty Calibration

Column name:

`uncertainty_calibration`

Allowed labels:

- `0`
- `1`
- `2`
- `3`
- `4`
- `5`

Breakdown:

- `0`: The AI is dangerously overconfident, presents the recommendation as guaranteed, or gives no caution for real-world use.
- `1`: The AI is strongly overconfident and gives little or no indication that the recommendation should be verified.
- `2`: The AI gives a recommendation with weak caution, but still sounds more certain than the dataset supports.
- `3`: The AI gives a usable recommendation and includes some uncertainty or verification language, but the caution is limited or generic.
- `4`: The AI gives a clear recommendation while appropriately noting that real fertilizer decisions should be verified with soil testing, local expertise, or agronomic guidance.
- `5`: The AI balances recommendation and caution very well, explains limits of the data, and avoids implying that the benchmark answer is a substitute for expert agronomic advice.

Use this category to evaluate whether the model's confidence level is responsible for a decision-support setting.

### Decision-Support Usefulness

Column name:

`decision_support_usefulness`

Allowed labels:

- `0`
- `1`
- `2`
- `3`
- `4`
- `5`

Breakdown:

- `0`: The response is unusable or actively misleading.
- `1`: The response gives very little help and may cause poor decision-making.
- `2`: The response has one useful piece of information, but major parts are missing or flawed.
- `3`: The response is somewhat useful, but would still require significant outside interpretation.
- `4`: The response is useful and would help a human understand the likely fertilizer choice.
- `5`: The response is highly useful, gives a clear recommendation, explains the reasoning, and includes appropriate caution.

Use this category to evaluate the overall value of the response as human decision support, not just whether the fertilizer label is correct.

## How We Will Calculate Cohen's Kappa

Calculate Cohen's kappa separately for each rubric column:

- `recommendation_correctness`
- `explanation_relevance`
- `clarity`
- `uncertainty_calibration`
- `decision_support_usefulness`

For each calculation:

1. Filter to the same `item_id`, `model_name`, and `prompt_version` rows for both graders.
2. Pair Ethan's label and Rachel's label for that rubric column.
3. Calculate observed agreement, which is how often the two graders chose the same label.
4. Calculate expected agreement, which is how often they would be expected to agree by chance based on their label distributions.
5. Apply Cohen's kappa:

`kappa = (observed agreement - expected agreement) / (1 - expected agreement)`

For the text-label category `recommendation_correctness`, use standard unweighted Cohen's kappa.

For `0-5` scale categories, there are two valid options:

- Use unweighted Cohen's kappa if we only care whether the graders selected exactly the same score.
- Use weighted Cohen's kappa if we want near-agreements to count better than far-apart disagreements, such as `4` vs `5` being less severe than `0` vs `5`.

For this project, weighted Cohen's kappa is recommended for the `0-5` rubric columns because those scores are ordered.
