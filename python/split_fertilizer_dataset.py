import csv
import random
import sys
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "datasets"
SOURCE_DATASET_PATH = DATASET_DIR / "fertilizer-prediction-dataset.csv"

CATEGORY_COLUMNS = ["Crop Type", "Soil Type", "Fertilizer Name"]
SPLITS = {
    "80-20": 0.20,
    "70-30": 0.30,
    "60-40": 0.40,
}
RANDOM_SEED = 209


def read_dataset() -> tuple[list[str], list[dict[str, str]]]:
    with SOURCE_DATASET_PATH.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"{SOURCE_DATASET_PATH} does not contain a header row.")

        missing_columns = [
            column for column in CATEGORY_COLUMNS if column not in reader.fieldnames
        ]
        if missing_columns:
            raise ValueError(f"Missing category columns: {', '.join(missing_columns)}")

        return reader.fieldnames, list(reader)


def category_values(row: dict[str, str]) -> set[tuple[str, str]]:
    return {
        (column, (row.get(column) or "").strip())
        for column in CATEGORY_COLUMNS
        if (row.get(column) or "").strip()
    }


def validate_all_categories_can_be_split(rows: list[dict[str, str]]) -> None:
    for column in CATEGORY_COLUMNS:
        counts = Counter((row.get(column) or "").strip() for row in rows)
        rare_values = [value for value, count in counts.items() if value and count < 2]
        if rare_values:
            raise ValueError(
                f"Cannot split column '{column}' while preserving train/test coverage. "
                f"These values appear fewer than 2 times: {', '.join(rare_values)}"
            )


def split_dir(split_name: str) -> Path:
    return DATASET_DIR / f"split-{split_name}"


def train_dataset_path(split_name: str) -> Path:
    return split_dir(split_name) / "fertilizer-prediction-train.csv"


def test_dataset_path(split_name: str) -> Path:
    return split_dir(split_name) / "fertilizer-prediction-test.csv"


def build_test_indices(
    rows: list[dict[str, str]],
    target_test_size: int,
    split_name: str,
) -> set[int]:
    rng = random.Random(f"{RANDOM_SEED}-{split_name}")
    remaining_train_counts = {
        column: Counter((row.get(column) or "").strip() for row in rows)
        for column in CATEGORY_COLUMNS
    }
    all_categories = set().union(*(category_values(row) for row in rows))
    covered_categories: set[tuple[str, str]] = set()
    test_indices: set[int] = set()

    def can_move_to_test(index: int) -> bool:
        row = rows[index]
        return all(
            remaining_train_counts[column][value] > 1
            for column, value in category_values(row)
        )

    def move_to_test(index: int) -> None:
        test_indices.add(index)
        for column, value in category_values(rows[index]):
            remaining_train_counts[column][value] -= 1
        covered_categories.update(category_values(rows[index]))

    while covered_categories != all_categories:
        uncovered = all_categories - covered_categories
        candidates = [
            index
            for index, row in enumerate(rows)
            if index not in test_indices
            and can_move_to_test(index)
            and category_values(row) & uncovered
        ]
        if not candidates:
            missing = ", ".join(f"{column}={value}" for column, value in sorted(uncovered))
            raise ValueError(f"Could not cover these categories in test: {missing}")

        candidates.sort(
            key=lambda index: (
                -len(category_values(rows[index]) & uncovered),
                rng.random(),
            )
        )
        move_to_test(candidates[0])

    while len(test_indices) < target_test_size:
        candidates = [
            index
            for index in range(len(rows))
            if index not in test_indices and can_move_to_test(index)
        ]
        if not candidates:
            break
        move_to_test(rng.choice(candidates))

    return test_indices


def write_dataset(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def validate_split(
    train_rows: list[dict[str, str]],
    test_rows: list[dict[str, str]],
) -> None:
    for column in CATEGORY_COLUMNS:
        train_values = {(row.get(column) or "").strip() for row in train_rows}
        test_values = {(row.get(column) or "").strip() for row in test_rows}
        missing_from_train = sorted(test_values - train_values)
        if missing_from_train:
            raise ValueError(
                f"Test contains {column} values absent from train: "
                f"{', '.join(missing_from_train)}"
            )


def requested_splits() -> list[tuple[str, float]]:
    if len(sys.argv) == 1:
        return list(SPLITS.items())

    split_names = []
    for argument in sys.argv[1:]:
        split_name = argument.removeprefix("split-")
        if split_name not in SPLITS:
            valid = ", ".join(SPLITS)
            raise ValueError(f"Unknown split '{argument}'. Valid splits: {valid}")
        split_names.append(split_name)

    return [(split_name, SPLITS[split_name]) for split_name in split_names]


def write_split(
    split_name: str,
    test_ratio: float,
    fieldnames: list[str],
    rows: list[dict[str, str]],
) -> None:
    target_test_size = round(len(rows) * test_ratio)
    test_indices = build_test_indices(rows, target_test_size, split_name)

    train_rows = [row for index, row in enumerate(rows) if index not in test_indices]
    test_rows = [row for index, row in enumerate(rows) if index in test_indices]
    validate_split(train_rows, test_rows)

    output_dir = split_dir(split_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_dataset(train_dataset_path(split_name), fieldnames, train_rows)
    write_dataset(test_dataset_path(split_name), fieldnames, test_rows)

    print(f"Wrote split-{split_name}: {len(train_rows)} train rows, {len(test_rows)} test rows")


def main() -> None:
    fieldnames, rows = read_dataset()
    validate_all_categories_can_be_split(rows)

    for split_name, test_ratio in requested_splits():
        write_split(split_name, test_ratio, fieldnames, rows)


if __name__ == "__main__":
    main()
