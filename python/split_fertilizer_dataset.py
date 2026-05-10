import csv
import random
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "datasets"
SOURCE_DATASET_PATH = DATASET_DIR / "fertilizer-prediction-dataset.csv"

ITEM_ID_COLUMN = "item_id"
SPLIT_NAME_COLUMN = "split_name"
FERTILIZER_COLUMN = "Fertilizer Name"
CATEGORY_COLUMNS = ["Crop Type", "Soil Type", "Fertilizer Name"]


@dataclass(frozen=True)
class SplitSpec:
    name: str
    test_ratio: float | None
    subset_size: int | None = None
    write_train: bool = True


SPLITS = {
    "80-20": SplitSpec("80-20", 0.20),
    "70-30": SplitSpec("70-30", 0.30),
    "60-40": SplitSpec("60-40", 0.40),
    "0-100": SplitSpec("0-100", None, write_train=False),
    "0-100-subset": SplitSpec("0-100-subset", None, subset_size=15, write_train=False),
}
RANDOM_SEED = 209


def read_dataset() -> tuple[list[str], list[dict[str, str]]]:
    with SOURCE_DATASET_PATH.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"{SOURCE_DATASET_PATH} does not contain a header row.")

        if ITEM_ID_COLUMN not in reader.fieldnames:
            raise ValueError(
                f"{SOURCE_DATASET_PATH} must include an '{ITEM_ID_COLUMN}' column. "
                "Add stable item IDs before generating splits."
            )

        missing_columns = [
            column for column in CATEGORY_COLUMNS if column not in reader.fieldnames
        ]
        if missing_columns:
            raise ValueError(f"Missing category columns: {', '.join(missing_columns)}")

        return reader.fieldnames, list(reader)


def validate_item_ids(rows: list[dict[str, str]]) -> None:
    item_ids = [(row.get(ITEM_ID_COLUMN) or "").strip() for row in rows]
    missing_count = sum(1 for item_id in item_ids if not item_id)
    if missing_count:
        raise ValueError(f"{missing_count} rows are missing '{ITEM_ID_COLUMN}' values.")

    duplicate_ids = sorted(
        item_id for item_id, count in Counter(item_ids).items() if count > 1
    )
    if duplicate_ids:
        raise ValueError(f"Duplicate item IDs found: {', '.join(duplicate_ids)}")


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


def model_test_dataset_path(split_name: str) -> Path:
    return split_dir(split_name) / "fertilizer-prediction-test-model.csv"


def split_fieldnames(fieldnames: list[str]) -> list[str]:
    return [ITEM_ID_COLUMN, SPLIT_NAME_COLUMN] + [
        fieldname
        for fieldname in fieldnames
        if fieldname not in {ITEM_ID_COLUMN, SPLIT_NAME_COLUMN}
    ]


def model_test_fieldnames(fieldnames: list[str]) -> list[str]:
    return [
        fieldname
        for fieldname in split_fieldnames(fieldnames)
        if fieldname != FERTILIZER_COLUMN
    ]


def add_split_name(rows: list[dict[str, str]], split_name: str) -> list[dict[str, str]]:
    return [
        {
            **row,
            SPLIT_NAME_COLUMN: f"split-{split_name}",
        }
        for row in rows
    ]


def remove_fertilizer_name(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            fieldname: value
            for fieldname, value in row.items()
            if fieldname != FERTILIZER_COLUMN
        }
        for row in rows
    ]


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


def select_coverage_subset(
    rows: list[dict[str, str]],
    subset_size: int,
) -> list[dict[str, str]]:
    all_categories = set().union(*(category_values(row) for row in rows))
    covered_categories: set[tuple[str, str]] = set()
    selected_rows: list[dict[str, str]] = []

    if subset_size < len(all_categories):
        # Each row can cover at most one value per category column, so this is a
        # quick impossible-case check before the greedy selector runs.
        minimum_possible = max(
            len({(row.get(column) or "").strip() for row in rows})
            for column in CATEGORY_COLUMNS
        )
        if subset_size < minimum_possible:
            raise ValueError(
                f"Subset size {subset_size} is too small to cover all category values."
            )

    def current_count_sum(row: dict[str, str]) -> int:
        return sum(
            sum(
                1
                for selected_row in selected_rows
                if selected_row.get(column) == row.get(column)
            )
            for column in CATEGORY_COLUMNS
        )

    while covered_categories != all_categories:
        candidates = [row for row in rows if row not in selected_rows]
        if not candidates:
            missing = ", ".join(
                f"{column}={value}"
                for column, value in sorted(all_categories - covered_categories)
            )
            raise ValueError(f"Could not cover these categories in subset: {missing}")

        candidates.sort(
            key=lambda row: (
                -len(category_values(row) - covered_categories),
                current_count_sum(row),
                row.get(ITEM_ID_COLUMN, ""),
            )
        )
        selected_rows.append(candidates[0])
        covered_categories.update(category_values(candidates[0]))

    while len(selected_rows) < subset_size:
        candidates = [row for row in rows if row not in selected_rows]
        if not candidates:
            break
        candidates.sort(
            key=lambda row: (
                current_count_sum(row),
                row.get(ITEM_ID_COLUMN, ""),
            )
        )
        selected_rows.append(candidates[0])

    if len(selected_rows) > subset_size:
        raise ValueError(
            f"Needed {len(selected_rows)} rows to cover all category values; "
            f"subset limit is {subset_size}."
        )

    return selected_rows


def requested_splits() -> list[SplitSpec]:
    if len(sys.argv) == 1:
        return list(SPLITS.values())

    split_specs = []
    for argument in sys.argv[1:]:
        split_name = argument.removeprefix("split-")
        if split_name not in SPLITS:
            valid = ", ".join(SPLITS)
            raise ValueError(f"Unknown split '{argument}'. Valid splits: {valid}")
        split_specs.append(SPLITS[split_name])

    return split_specs


def write_ratio_split(
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
    output_fieldnames = split_fieldnames(fieldnames)
    train_rows_with_split = add_split_name(train_rows, split_name)
    test_rows_with_split = add_split_name(test_rows, split_name)
    write_dataset(train_dataset_path(split_name), output_fieldnames, train_rows_with_split)
    write_dataset(test_dataset_path(split_name), output_fieldnames, test_rows_with_split)
    write_dataset(
        model_test_dataset_path(split_name),
        model_test_fieldnames(fieldnames),
        remove_fertilizer_name(test_rows_with_split),
    )

    print(
        f"Wrote split-{split_name}: {len(train_rows)} train rows, "
        f"{len(test_rows)} test rows, {len(test_rows)} model test rows"
    )


def write_test_only_split(
    split_name: str,
    fieldnames: list[str],
    rows: list[dict[str, str]],
    subset_size: int | None = None,
) -> None:
    test_rows = select_coverage_subset(rows, subset_size) if subset_size else rows

    output_dir = split_dir(split_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    train_path = train_dataset_path(split_name)
    if train_path.exists():
        train_path.unlink()

    output_fieldnames = split_fieldnames(fieldnames)
    test_rows_with_split = add_split_name(test_rows, split_name)
    write_dataset(test_dataset_path(split_name), output_fieldnames, test_rows_with_split)
    write_dataset(
        model_test_dataset_path(split_name),
        model_test_fieldnames(fieldnames),
        remove_fertilizer_name(test_rows_with_split),
    )

    print(
        f"Wrote split-{split_name}: no train rows, {len(test_rows)} test rows, "
        f"{len(test_rows)} model test rows"
    )


def write_split(
    spec: SplitSpec,
    fieldnames: list[str],
    rows: list[dict[str, str]],
) -> None:
    if spec.write_train:
        if spec.test_ratio is None:
            raise ValueError(f"Split {spec.name} is missing a test ratio.")
        write_ratio_split(spec.name, spec.test_ratio, fieldnames, rows)
        return

    write_test_only_split(spec.name, fieldnames, rows, spec.subset_size)


def main() -> None:
    fieldnames, rows = read_dataset()
    validate_item_ids(rows)
    validate_all_categories_can_be_split(rows)

    for spec in requested_splits():
        write_split(spec, fieldnames, rows)


if __name__ == "__main__":
    main()
