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

### recommendation_correctness

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

### explanation_relevance

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

### clarity

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

### uncertainty_calibration

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

### decision_support_usefulness

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

## How Expected Agreement Is Calculated

Expected agreement is the amount of agreement we would expect by chance if each grader kept their own scoring habits, but their scores were otherwise unrelated.

This is why kappa can be low even when the grades look close. If both graders mostly use the same small part of the rubric, such as mostly `4` and `5`, the expected chance agreement can already be high.

### Expected Agreement for Unweighted Kappa

For unweighted kappa, expected agreement is calculated from each grader's label counts.

For each possible label:

1. Calculate the proportion of rows where Ethan used that label.
2. Calculate the proportion of rows where Rachel used that label.
3. Multiply those two proportions.
4. Add the products across all labels.

Formula:

`expected agreement = sum(P(Ethan label) * P(Rachel label))`

Example for `recommendation_correctness` with 15 rows:

| Label | Ethan count | Ethan proportion | Rachel count | Rachel proportion | Product |
| --- | ---: | ---: | ---: | ---: | ---: |
| `correct` | 11 | `11/15` | 11 | `11/15` | `0.5378` |
| `partially_correct` | 2 | `2/15` | 4 | `4/15` | `0.0356` |
| `incorrect` | 2 | `2/15` | 0 | `0/15` | `0.0000` |

Expected agreement:

`0.5378 + 0.0356 + 0.0000 = 0.5734`

If observed agreement is `13/15 = 0.8667`, then:

`kappa = (0.8667 - 0.5734) / (1 - 0.5734) = 0.6875`

### Expected Agreement for Weighted Kappa

For weighted kappa, the script uses expected weighted disagreement instead of expected agreement. This is mathematically equivalent for the linear weighted version used here.

The script treats the `1-5` labels as ordered positions:

| Score | Position |
| --- | ---: |
| `1` | 0 |
| `2` | 1 |
| `3` | 2 |
| `4` | 3 |
| `5` | 4 |

The disagreement weight between two scores is:

`distance between scores / maximum distance`

Examples:

| Pair | Distance | Disagreement weight |
| --- | ---: | ---: |
| `4` vs `5` | 1 | `1/4 = 0.25` |
| `3` vs `5` | 2 | `2/4 = 0.50` |
| `1` vs `5` | 4 | `4/4 = 1.00` |

To calculate expected weighted disagreement:

1. Take every possible Ethan score from `1` to `5`.
2. Take every possible Rachel score from `1` to `5`.
3. Multiply Ethan's proportion for that score by Rachel's proportion for that score.
4. Multiply by the disagreement weight between the two scores.
5. Add the result across all possible score pairs.

Formula:

`expected weighted disagreement = sum(P(Ethan score) * P(Rachel score) * disagreement weight)`

Then weighted kappa is:

`weighted kappa = 1 - (observed weighted disagreement / expected weighted disagreement)`

For example, if observed weighted disagreement is `0.1667` and expected weighted disagreement is `0.1444`, then:

`weighted kappa = 1 - (0.1667 / 0.1444) = -0.1538`

That negative value does not mean the graders were far apart in absolute terms. It means their observed weighted disagreement was slightly worse than what would be expected from their scoring distributions.

## How to Interpret Kappa Values

Cohen's kappa ranges from `-1` to `1`.

- `1.00`: perfect agreement after accounting for chance.
- `0.00`: agreement is no better than chance based on the graders' label distributions.
- Less than `0.00`: agreement is worse than chance, usually a sign that graders are using the rubric inconsistently or that rows were paired incorrectly.

A common interpretation guide is:

| Kappa value | Typical interpretation |
| --- | --- |
| `< 0.00` | Poor agreement, worse than chance |
| `0.00-0.20` | Slight agreement |
| `0.21-0.40` | Fair agreement |
| `0.41-0.60` | Moderate agreement |
| `0.61-0.80` | Substantial agreement |
| `0.81-1.00` | Almost perfect agreement |

These ranges are only guidelines, not hard rules. Kappa can be lower than expected when one label is very common, even if the raw percent agreement looks high. For this project, review both the kappa value and the actual grading disagreements before deciding whether a rubric category is reliable.

### Unweighted Kappa

Unweighted kappa treats every disagreement as equally wrong.

For `recommendation_correctness`, this means `correct` vs `partially_correct` is counted as a full disagreement, just like `correct` vs `incorrect`. This is appropriate because the category uses named labels rather than an ordered numeric scale.

Use unweighted kappa results to answer:

- Did the graders choose exactly the same category?
- Are graders applying the categorical fertilizer-correctness labels consistently?

### Weighted Kappa

Weighted kappa gives partial credit for near-agreement on ordered scales.

For the `1-5` rubric columns, `4` vs `5` is treated as a smaller disagreement than `1` vs `5`. This is appropriate for:

- `explanation_relevance`
- `clarity`
- `uncertainty_calibration`
- `decision_support_usefulness`

Use weighted kappa results to answer:

- Are graders making similar judgments even when their exact scores differ by one point?
- Are disagreements mostly minor score differences, or are graders interpreting the rubric very differently?

Weighted and unweighted kappa values should not be compared as if they are the same measurement. Weighted kappa will often be higher when graders mostly differ by one adjacent score, because those disagreements are intentionally penalized less. If weighted kappa is still low, the graders likely disagree in more substantial ways or use different parts of the scale.
