# Fertilizer Dataset Breakdown

This document explains the fertilizer types used in `datasets/fertilizer-prediction-dataset.csv`.

Fertilizer labels with numbers are usually written as nutrient grades. The numbers represent the percentage of major nutrients in this order:

`Nitrogen - Phosphorus - Potassium`

These are often abbreviated as `N-P-K`.

## Urea

Urea is a nitrogen fertilizer. It is commonly used when crops need more nitrogen for leaf and stem growth.

Typical urea fertilizer is often labeled around `46-0-0`, meaning it contains a high percentage of nitrogen and little to no phosphorus or potassium. In this dataset, urea appears when the recommended fertilizer is mainly meant to correct nitrogen needs.

## DAP

DAP stands for diammonium phosphate. It supplies both nitrogen and phosphorus.

DAP is commonly used when a crop needs phosphorus for root development, early plant growth, flowering, or seed formation, while also receiving some nitrogen. A common DAP grade is `18-46-0`, meaning it is especially rich in phosphorus and does not supply potassium.

## 14-35-14

`14-35-14` is a mixed N-P-K fertilizer containing nitrogen, phosphorus, and potassium.

The grade means it contains:

- `14%` nitrogen
- `35%` phosphorus
- `14%` potassium

This fertilizer is phosphorus-heavy compared with its nitrogen and potassium levels. It is useful when the crop needs strong phosphorus support but still benefits from some nitrogen and potassium.

## 28-28

`28-28` is a two-nutrient fertilizer grade. In this dataset, it represents a fertilizer with nitrogen and phosphorus but little or no potassium.

The grade means it contains about:

- `28%` nitrogen
- `28%` phosphorus

This type of fertilizer is useful when both nitrogen and phosphorus are needed, especially for growth and root development, but potassium is not the main concern.

## 17-17-17

`17-17-17` is a balanced N-P-K fertilizer.

The grade means it contains:

- `17%` nitrogen
- `17%` phosphorus
- `17%` potassium

Because all three nutrients are present in equal amounts, this is a general-purpose fertilizer. It can support overall plant growth, root development, flowering, and plant strength when the soil needs a balanced nutrient addition.

## 20-20

`20-20` is another two-nutrient fertilizer grade. In this dataset, it represents a fertilizer with nitrogen and phosphorus but little or no potassium.

The grade means it contains about:

- `20%` nitrogen
- `20%` phosphorus

This fertilizer is less concentrated than `28-28`, but it serves a similar purpose: supplying both nitrogen and phosphorus when potassium is not the priority.

## 10-26-26

`10-26-26` is a mixed N-P-K fertilizer containing nitrogen, phosphorus, and potassium.

The grade means it contains:

- `10%` nitrogen
- `26%` phosphorus
- `26%` potassium

This fertilizer is higher in phosphorus and potassium than nitrogen. It is useful when crops need root, flowering, fruiting, or overall plant-strength support without adding a very large amount of nitrogen.

