import csv
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
NUTRIENT_COLUMNS = ["Nitrogen", "Potassium", "Phosphorous"]
WITHHELD_VALUE = "?"


@dataclass(frozen=True)
class TestSetSpec:
    name: str
    subset_size: int | None = None
    withhold_nutrients: bool = False


TEST_SETS = {
    "0-100": TestSetSpec("0-100"),
    "0-100-subset": TestSetSpec("0-100-subset", subset_size=15),
    "0-100-subset-no-nutrients": TestSetSpec(
        "0-100-subset-no-nutrients",
        subset_size=15,
        withhold_nutrients=True,
    ),
}


def read_dataset() -> tuple[list[str], list[dict[str, str]]]:
    with SOURCE_DATASET_PATH.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"{SOURCE_DATASET_PATH} does not contain a header row.")

        if ITEM_ID_COLUMN not in reader.fieldnames:
            raise ValueError(
                f"{SOURCE_DATASET_PATH} must include an '{ITEM_ID_COLUMN}' column. "
                "Add stable item IDs before generating test sets."
            )

        missing_columns = [
            column
            for column in CATEGORY_COLUMNS + NUTRIENT_COLUMNS
            if column not in reader.fieldnames
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


def test_set_dir(test_set_name: str) -> Path:
    return DATASET_DIR / f"split-{test_set_name}"


def reference_test_path(test_set_name: str) -> Path:
    return test_set_dir(test_set_name) / "fertilizer-prediction-test.csv"


def model_test_path(test_set_name: str) -> Path:
    return test_set_dir(test_set_name) / "fertilizer-prediction-test-model.csv"


def output_fieldnames(fieldnames: list[str]) -> list[str]:
    return [ITEM_ID_COLUMN, SPLIT_NAME_COLUMN] + [
        fieldname
        for fieldname in fieldnames
        if fieldname not in {ITEM_ID_COLUMN, SPLIT_NAME_COLUMN}
    ]


def model_fieldnames(fieldnames: list[str]) -> list[str]:
    return [
        fieldname
        for fieldname in output_fieldnames(fieldnames)
        if fieldname != FERTILIZER_COLUMN
    ]


def add_split_name(
    rows: list[dict[str, str]],
    test_set_name: str,
) -> list[dict[str, str]]:
    return [
        {
            **row,
            SPLIT_NAME_COLUMN: f"split-{test_set_name}",
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


def withhold_nutrients(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            fieldname: WITHHELD_VALUE if fieldname in NUTRIENT_COLUMNS else value
            for fieldname, value in row.items()
        }
        for row in rows
    ]


def select_coverage_subset(
    rows: list[dict[str, str]],
    subset_size: int,
) -> list[dict[str, str]]:
    all_categories = set().union(*(category_values(row) for row in rows))
    covered_categories: set[tuple[str, str]] = set()
    selected_rows: list[dict[str, str]] = []

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


def write_dataset(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def requested_test_sets() -> list[TestSetSpec]:
    if len(sys.argv) == 1:
        return list(TEST_SETS.values())

    test_sets = []
    for argument in sys.argv[1:]:
        test_set_name = argument.removeprefix("split-")
        if test_set_name not in TEST_SETS:
            valid = ", ".join(TEST_SETS)
            raise ValueError(f"Unknown test set '{argument}'. Valid test sets: {valid}")
        test_sets.append(TEST_SETS[test_set_name])

    return test_sets


def write_test_set(
    spec: TestSetSpec,
    fieldnames: list[str],
    rows: list[dict[str, str]],
) -> None:
    test_rows = select_coverage_subset(rows, spec.subset_size) if spec.subset_size else rows
    test_rows_with_split = add_split_name(test_rows, spec.name)
    if spec.withhold_nutrients:
        test_rows_with_split = withhold_nutrients(test_rows_with_split)
    output_dir = test_set_dir(spec.name)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_dataset(
        reference_test_path(spec.name),
        output_fieldnames(fieldnames),
        test_rows_with_split,
    )
    write_dataset(
        model_test_path(spec.name),
        model_fieldnames(fieldnames),
        remove_fertilizer_name(test_rows_with_split),
    )

    print(
        f"Wrote split-{spec.name}: {len(test_rows)} reference rows, "
        f"{len(test_rows)} model rows"
    )


def main() -> None:
    fieldnames, rows = read_dataset()
    validate_item_ids(rows)

    for spec in requested_test_sets():
        write_test_set(spec, fieldnames, rows)


if __name__ == "__main__":
    main()
