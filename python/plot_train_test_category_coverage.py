from collections import Counter
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "datasets"
OUTPUT_DIR = PROJECT_ROOT / "plotting"

SPLITS = ["80-20", "70-30", "60-40"]

CATEGORIES = [
    ("Crop Type", "Crop Type"),
    ("Soil Type", "Soil Type"),
    ("Fertilizer Name", "Fertilizer Name"),
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        return list(csv.DictReader(csv_file))


def count_values(rows: list[dict[str, str]], column_name: str) -> Counter[str]:
    return Counter(
        value
        for row in rows
        if (value := (row.get(column_name) or "").strip())
    )


def plot_counts(ax, counts: Counter[str], title: str) -> None:
    labels = sorted(counts)
    values = [counts[label] for label in labels]
    bars = ax.barh(labels, values, color="#3f7cac")

    ax.set_title(title, fontsize=12, pad=8)
    ax.set_xlabel("Rows")
    ax.grid(axis="x", alpha=0.25)
    ax.bar_label(bars, padding=3, fontsize=8)
    ax.set_xlim(0, max(values) + 2 if values else 1)


def split_dir(split_name: str) -> Path:
    return DATASET_DIR / f"split-{split_name}"


def train_dataset_path(split_name: str) -> Path:
    return split_dir(split_name) / "fertilizer-prediction-train.csv"


def test_dataset_path(split_name: str) -> Path:
    return split_dir(split_name) / "fertilizer-prediction-test.csv"


def output_path(split_name: str) -> Path:
    return OUTPUT_DIR / f"train_test_category_coverage_{split_name}.png"


def requested_splits() -> list[str]:
    if len(sys.argv) == 1:
        return SPLITS

    split_names = []
    for argument in sys.argv[1:]:
        split_name = argument.removeprefix("split-")
        if split_name not in SPLITS:
            valid = ", ".join(SPLITS)
            raise ValueError(f"Unknown split '{argument}'. Valid splits: {valid}")
        split_names.append(split_name)

    return split_names


def plot_split(split_name: str) -> None:
    train_rows = read_rows(train_dataset_path(split_name))
    test_rows = read_rows(test_dataset_path(split_name))

    fig, axes = plt.subplots(3, 2, figsize=(15, 13), constrained_layout=True)

    for row_index, (column_name, label) in enumerate(CATEGORIES):
        plot_counts(
            axes[row_index][0],
            count_values(train_rows, column_name),
            f"Train {label}",
        )
        plot_counts(
            axes[row_index][1],
            count_values(test_rows, column_name),
            f"Test {label}",
        )

    fig.suptitle(f"Train/Test Category Coverage ({split_name})", fontsize=18)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = output_path(split_name)
    fig.savefig(path, dpi=200)
    plt.close(fig)

    print(f"Wrote {path}")


def main() -> None:
    for split_name in requested_splits():
        plot_split(split_name)


if __name__ == "__main__":
    main()
