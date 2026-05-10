# Cohen's Kappa Grading Rubric

This document defines the human grading rubric for AgriGuide AI fertilizer recommendation responses and explains how to structure the grades so Cohen's kappa can be calculated cleanly.

The evidence-based grading anchors are maintained in `project-docs/grading-rubric.md`, and the GUI loads the matching machine-readable options from `python/fertilizer_grader_gui/grading-rubric.json`. Keep the column names and allowed labels in those files aligned with the columns below.

## Core Rule

It is okay to mix label styles across different rubric categories.

For example, `recommendation_correctness` can use text labels like `correct`, `partially_correct`, and `incorrect`, while `explanation_relevance`, `clarity`, `uncertainty_calibration`, and `decision_support_usefulness` can use a `1-5` scale.

The important rule is that each individual rubric column must have one fixed set of allowed labels, and both graders must use that same set.

## Recommended Grading Unit

Each grade should apply to one AI response for one dataset item.

Use one row per grader per response. The same AI response should be graded independently by both team members before comparing scores.

Recommended identifier columns:

- `item_id`
- `split_name`
- `model_name`
- `prompt_version`
- `grader_id`
- `reference_fertilizer`
- `model_fertilizer`

The fields `item_id`, `split_name`, `model_name`, and `prompt_version` are what let us match Ethan's grade to Rachel's grade for the same response.

`split_name` is required because the same source item can appear in different test sets across evaluations such as `split-80-20`, `split-70-30`, `split-60-40`, `split-0-100`, and `split-0-100-subset`. Grades from different splits should not be paired with each other.

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

- `1`
- `2`
- `3`
- `4`
- `5`

Breakdown:

- `1`: The explanation is missing, unrelated to the given case, or almost entirely generic.
- `2`: The explanation barely connects to the input or mentions one relevant input with weak reasoning.
- `3`: The explanation uses some relevant input values, but misses important factors or does not clearly connect them to the fertilizer.
- `4`: The explanation uses most important inputs and gives a reasonable fertilizer-specific justification.
- `5`: The explanation clearly connects the crop, soil, moisture, temperature/humidity, and nutrient levels to the fertilizer recommendation.

Use this category to evaluate whether the model explains the recommendation using the actual dataset fields instead of giving generic fertilizer advice.

### Interpretability and Clarity

Column name:

`clarity`

Allowed labels:

- `1`
- `2`
- `3`
- `4`
- `5`

Breakdown:

- `1`: The response is confusing, contradictory, impossible to use, or lacks a clear recommendation.
- `2`: The response has a recommendation, but it is hard to follow or poorly organized.
- `3`: The response is understandable but has some unclear reasoning, vague wording, or unnecessary complexity.
- `4`: The response is clear, organized, and understandable for a non-expert.
- `5`: The response is very clear, concise, and easy for a non-expert to act on responsibly.

Use this category to evaluate whether the response is understandable to a human decision-maker.

### Uncertainty Calibration

Column name:

`uncertainty_calibration`

Allowed labels:

- `1`
- `2`
- `3`
- `4`
- `5`

Breakdown:

- `1`: The AI is dangerously overconfident, presents the recommendation as guaranteed, or gives little to no caution for real-world use.
- `2`: The AI gives a recommendation with weak caution, but still sounds more certain than the dataset supports.
- `3`: The AI gives a usable recommendation and includes some uncertainty or verification language, but the caution is limited or generic.
- `4`: The AI gives a clear recommendation while appropriately noting that real fertilizer decisions should be verified with soil testing, local expertise, or agronomic guidance.
- `5`: The AI balances recommendation and caution very well, explains limits of the data, and avoids implying that the benchmark answer is a substitute for expert agronomic advice.

Use this category to evaluate whether the model's confidence level is responsible for a decision-support setting.

### Decision-Support Usefulness

Column name:

`decision_support_usefulness`

Allowed labels:

- `1`
- `2`
- `3`
- `4`
- `5`

Breakdown:

- `1`: The response is unusable, actively misleading, or gives very little help.
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
   Include `split_name` in this match so separate split evaluations remain distinct.
2. Pair Ethan's label and Rachel's label for that rubric column.
3. Calculate observed agreement, which is how often the two graders chose the same label.
4. Calculate expected agreement, which is how often they would be expected to agree by chance based on their label distributions.
5. Apply Cohen's kappa:

`kappa = (observed agreement - expected agreement) / (1 - expected agreement)`

For the text-label category `recommendation_correctness`, use standard unweighted Cohen's kappa.

For `1-5` scale categories, there are two valid options:

- Use unweighted Cohen's kappa if we only care whether the graders selected exactly the same score.
- Use weighted Cohen's kappa if we want near-agreements to count better than far-apart disagreements, such as `4` vs `5` being less severe than `1` vs `5`.

For this project, weighted Cohen's kappa is recommended for the `1-5` rubric columns because those scores are ordered.
