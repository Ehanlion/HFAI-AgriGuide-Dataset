from collections import Counter
import csv
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "datasets" / "fertilizer-prediction-dataset.csv"
OUTPUT_DIR = PROJECT_ROOT / "plotting"

CATEGORIES = [
    ("Fertilizer Name", "fertilizer_name_distribution.png", "Fertilizer Name Distribution"),
    ("Soil Type", "soil_type_distribution.png", "Soil Type Distribution"),
    ("Crop Type", "crop_type_distribution.png", "Crop Type Distribution"),
]


def read_category_counts(column_name: str) -> Counter[str]:
    with DATASET_PATH.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None or column_name not in reader.fieldnames:
            available_columns = ", ".join(reader.fieldnames or [])
            raise ValueError(
                f"Column '{column_name}' was not found. Available columns: {available_columns}"
            )

        values = (
            (row.get(column_name) or "").strip()
            for row in reader
        )
        return Counter(value for value in values if value)


def autopct_for_counts(values: Iterable[int]):
    total = sum(values)

    def format_label(percent: float) -> str:
        count = round(percent * total / 100)
        return f"{percent:.1f}%\n({count})"

    return format_label


def plot_pie_chart(ax, counts: Counter[str], title: str) -> None:
    labels = list(counts.keys())
    values = list(counts.values())

    wedges, _, autotexts = ax.pie(
        values,
        labels=None,
        autopct=autopct_for_counts(values),
        startangle=90,
        pctdistance=0.72,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    ax.set_title(title, fontsize=13, pad=12)
    ax.axis("equal")
    ax.legend(
        wedges,
        labels,
        title="Categories",
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        fontsize=8,
    )

    for text in autotexts:
        text.set_fontsize(8)
        text.set_color("black")


def save_individual_chart(column_name: str, filename: str, title: str) -> Counter[str]:
    counts = read_category_counts(column_name)

    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)
    plot_pie_chart(ax, counts, title)
    fig.savefig(OUTPUT_DIR / filename, dpi=200)
    plt.close(fig)

    return counts


def save_combined_chart(all_counts: list[tuple[str, Counter[str]]]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(21, 7), constrained_layout=True)

    for ax, (title, counts) in zip(axes, all_counts):
        plot_pie_chart(ax, counts, title)

    fig.suptitle("Dataset Category Distributions", fontsize=18)
    fig.savefig(OUTPUT_DIR / "combined_category_distributions.png", dpi=200)
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_counts = []
    for column_name, filename, title in CATEGORIES:
        counts = save_individual_chart(column_name, filename, title)
        all_counts.append((title, counts))

    save_combined_chart(all_counts)


if __name__ == "__main__":
    main()
