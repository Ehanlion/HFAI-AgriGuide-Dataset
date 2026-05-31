from __future__ import annotations

import argparse
import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL_RESULTS_DIR = PROJECT_ROOT / "results-final"
FINAL_RESULT_PATTERN = "fertilizer-result-final-graded-split-*.csv"
GRADER_FIELDS_SUFFIX = "-grader-fields"
ITEM_ID_COLUMN = "item_id"
GRADER_COLUMN_PREFIX = "grader_"
RUBRIC_COLUMN_SHORT_NAMES = {
    "recommendation_correctness": "correctness",
    "explanation_relevance": "explanation",
    "clarity": "clarity",
    "uncertainty_calibration": "uncertainty",
    "decision_support_usefulness": "support",
}


class ExtractError(Exception):
    pass


def is_source_final_result(path: Path) -> bool:
    return path.suffix.casefold() == ".csv" and not path.stem.endswith(GRADER_FIELDS_SUFFIX)


def discover_final_files() -> list[Path]:
    return sorted(
        path
        for path in FINAL_RESULTS_DIR.glob(FINAL_RESULT_PATTERN)
        if is_source_final_result(path)
    )


def select_final_file(paths: list[Path]) -> Path:
    if not paths:
        raise ExtractError(f"No final result CSVs found in {FINAL_RESULTS_DIR}.")

    print("Select final result file to extract grader fields from:")
    for index, path in enumerate(paths, start=1):
        print(f"{index}. {path.name}")

    choice = input("Enter number: ").strip()
    if not choice.isdigit():
        raise ExtractError("Selection must be a number.")
    choice_index = int(choice)
    if 1 <= choice_index <= len(paths):
        return paths[choice_index - 1]
    raise ExtractError(f"Selection must be between 1 and {len(paths)}.")


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}{GRADER_FIELDS_SUFFIX}.csv")


def extract_fields(input_path: Path, output_path: Path) -> None:
    with input_path.open(newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ExtractError(f"{input_path} does not contain a header row.")

        fieldnames = list(reader.fieldnames)
        if ITEM_ID_COLUMN not in fieldnames:
            raise ExtractError(f"{input_path} is missing required column: {ITEM_ID_COLUMN}")

        source_columns = [
            ITEM_ID_COLUMN,
            *[field for field in fieldnames if field.startswith(GRADER_COLUMN_PREFIX)],
        ]
        if len(source_columns) == 1:
            raise ExtractError(f"{input_path} does not contain any grader columns.")

        output_columns = [short_column_name(column) for column in source_columns]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=output_columns)
            writer.writeheader()
            for row in reader:
                writer.writerow(
                    {
                        short_column_name(column): row.get(column, "")
                        for column in source_columns
                    }
                )


def short_column_name(column: str) -> str:
    if column == ITEM_ID_COLUMN:
        return column

    if not column.startswith(GRADER_COLUMN_PREFIX):
        return column

    grader_and_rubric = column[len(GRADER_COLUMN_PREFIX) :]
    for rubric, short_name in RUBRIC_COLUMN_SHORT_NAMES.items():
        suffix = f"_{rubric}"
        if grader_and_rubric.endswith(suffix):
            grader_id = grader_and_rubric[: -len(suffix)]
            return f"{grader_id}_{short_name}"

    return grader_and_rubric


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract item_id and grader result columns from a final fertilizer CSV."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help=(
            "Input final CSV. If omitted, choose from final result CSVs in "
            f"{FINAL_RESULTS_DIR.relative_to(PROJECT_ROOT)}."
        ),
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        help=(
            "Output CSV. Defaults to '<input-stem>-grader-fields.csv' "
            "beside the input."
        ),
    )
    return parser.parse_args()


def resolve_input_path(path: Path | None) -> Path:
    if path is None:
        return select_final_file(discover_final_files())
    if path.is_absolute():
        return path

    project_path = PROJECT_ROOT / path
    if project_path.exists():
        return project_path

    final_results_path = FINAL_RESULTS_DIR / path
    if final_results_path.exists():
        return final_results_path

    return project_path


def resolve_output_path(path: Path | None, input_path: Path) -> Path:
    if path is None:
        return default_output_path(input_path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def main() -> int:
    args = parse_args()
    input_path = resolve_input_path(args.input)
    output_path = resolve_output_path(args.output, input_path)

    try:
        extract_fields(input_path, output_path)
    except OSError as exc:
        print(f"Error: {exc}")
        return 1
    except ExtractError as exc:
        print(f"Error: {exc}")
        return 1

    print(f"Wrote grader field CSV to {output_path.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
