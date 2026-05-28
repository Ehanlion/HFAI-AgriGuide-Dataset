from collections import Counter
import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "datasets"
OUTPUT_DIR = PROJECT_ROOT / "plotting"

TEST_SETS = ["0-100", "0-100-subset"]

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


def test_set_dir(test_set_name: str) -> Path:
    return DATASET_DIR / f"split-{test_set_name}"


def reference_test_path(test_set_name: str) -> Path:
    return test_set_dir(test_set_name) / "fertilizer-prediction-test.csv"


def output_path(test_set_name: str) -> Path:
    return OUTPUT_DIR / f"test_category_coverage_{test_set_name}.png"


def requested_test_sets() -> list[str]:
    if len(sys.argv) == 1:
        return TEST_SETS

    test_set_names = []
    for argument in sys.argv[1:]:
        test_set_name = argument.removeprefix("split-")
        if test_set_name not in TEST_SETS:
            valid = ", ".join(TEST_SETS)
            raise ValueError(f"Unknown test set '{argument}'. Valid test sets: {valid}")
        test_set_names.append(test_set_name)

    return test_set_names


def plot_test_set(test_set_name: str) -> None:
    test_rows = read_rows(reference_test_path(test_set_name))
    fig, axes = plt.subplots(3, 1, figsize=(9, 13), constrained_layout=True)

    for axis, (column_name, label) in zip(axes, CATEGORIES):
        plot_counts(axis, count_values(test_rows, column_name), f"Test {label}")

    fig.suptitle(f"Test Category Coverage ({test_set_name})", fontsize=18)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = output_path(test_set_name)
    fig.savefig(path, dpi=200)
    plt.close(fig)

    print(f"Wrote {path}")


def main() -> None:
    for test_set_name in requested_test_sets():
        plot_test_set(test_set_name)


if __name__ == "__main__":
    main()
