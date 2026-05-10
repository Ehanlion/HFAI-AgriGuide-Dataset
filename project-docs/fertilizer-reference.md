# Fertilizer Reference Notes

Use these short notes while grading `recommendation_correctness`. The GUI loads the matching machine-readable version from `python/fertilizer_grader_gui/fertilizer-reference.json`.

## Urea

- Grade: commonly around `46-0-0`.
- Nutrients: high nitrogen; little to no phosphorus or potassium.
- Used for: nitrogen-focused correction when crops need leaf and stem growth support.
- Grading cues: compare against recommendations that primarily address nitrogen; weak overlap with fertilizers selected for phosphorus or potassium support.

## DAP

- Grade: commonly around `18-46-0`.
- Nutrients: nitrogen plus high phosphorus; no potassium.
- Used for: phosphorus support for root development, early growth, flowering, or seed formation while adding some nitrogen.
- Grading cues: meaningful overlap with recommendations that supply nitrogen and phosphorus; weak overlap with potassium-containing blends when potassium is central.

## 14-35-14

- Grade: `14-35-14`.
- Nutrients: nitrogen, phosphorus, and potassium, with phosphorus highest.
- Used for: strong phosphorus support when some nitrogen and potassium are also useful.
- Grading cues: overlaps with phosphorus-heavy fertilizers and mixed N-P-K blends; stronger match when the explanation calls for phosphorus plus some potassium.

## 28-28

- Grade: `28-28`.
- Nutrients: nitrogen and phosphorus; little or no potassium in this dataset context.
- Used for: higher nitrogen-phosphorus support when potassium is not the main concern.
- Grading cues: overlaps with two-nutrient N-P fertilizers such as `20-20`; weaker match when potassium support is needed.

## 17-17-17

- Grade: `17-17-17`.
- Nutrients: balanced nitrogen, phosphorus, and potassium.
- Used for: general-purpose balanced support across growth, root development, flowering, and plant strength.
- Grading cues: overlaps with mixed N-P-K fertilizers; best match when all three major nutrients are relevant rather than one nutrient dominating.

## 20-20

- Grade: `20-20`.
- Nutrients: nitrogen and phosphorus; little or no potassium in this dataset context.
- Used for: moderate nitrogen-phosphorus support when potassium is not the priority.
- Grading cues: overlaps with `28-28`, but is less concentrated; weaker match for cases requiring potassium.

## 10-26-26

- Grade: `10-26-26`.
- Nutrients: lower nitrogen with higher phosphorus and potassium.
- Used for: root, flowering, fruiting, or plant-strength support where phosphorus and potassium matter more than nitrogen.
- Grading cues: overlaps with mixed N-P-K fertilizers and P-K-forward reasoning; weak match when nitrogen-only support is the central need.
