from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL_RESULTS_DIR = PROJECT_ROOT / "results-final"
FINAL_RESULT_PATTERN = "fertilizer-result-final-graded-split-*.csv"
GRADER_FIELDS_SUFFIX = "-grader-fields"
ITEM_ID_COLUMN = "item_id"
MODEL_NAME_COLUMN = "model_name"
PROMPT_VERSION_COLUMN = "prompt_version"
RESULT_MODEL_ID_COLUMN = "result_model_id"
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


def select_final_files(paths: list[Path]) -> list[Path]:
    if not paths:
        raise ExtractError(f"No final result CSVs found in {FINAL_RESULTS_DIR}.")

    print("Select final result file to extract grader fields from:")
    for index, path in enumerate(paths, start=1):
        print(f"{index}. {path.name}")
    all_option = len(paths) + 1
    print(f"{all_option}. All files")

    choice = input("Enter number: ").strip()
    if not choice.isdigit():
        raise ExtractError("Selection must be a number.")
    choice_index = int(choice)
    if choice_index == all_option:
        return paths
    if 1 <= choice_index <= len(paths):
        return [paths[choice_index - 1]]
    raise ExtractError(f"Selection must be between 1 and {all_option}.")


def safe_filename_token(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    return cleaned.strip("-._") or "unknown-model"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def default_output_path(input_path: Path, model_id: str) -> Path:
    model_token = safe_filename_token(model_id)
    return input_path.with_name(f"{input_path.stem}-{model_token}{GRADER_FIELDS_SUFFIX}.csv")


def model_group_label(row: dict[str, str]) -> str:
    result_model_id = row.get(RESULT_MODEL_ID_COLUMN, "").strip()
    if result_model_id:
        return result_model_id

    model_name = row.get(MODEL_NAME_COLUMN, "").strip() or "unknown_model"
    prompt_version = row.get(PROMPT_VERSION_COLUMN, "").strip()
    if prompt_version:
        return f"{model_name}-{prompt_version}"
    return model_name


def extract_fields(input_path: Path, output_dir: Path | None) -> list[Path]:
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

        rows_by_model: dict[str, list[dict[str, str]]] = {}
        for row in reader:
            rows_by_model.setdefault(model_group_label(row), []).append(row)
        if not rows_by_model:
            raise ExtractError(f"{input_path} has no data rows.")

        output_columns = [short_column_name(column) for column in source_columns]
        written_paths: list[Path] = []
        for model_id, rows in sorted(rows_by_model.items()):
            output_path = (
                output_dir / default_output_path(input_path, model_id).name
                if output_dir is not None
                else default_output_path(input_path, model_id)
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", newline="", encoding="utf-8") as output_file:
                writer = csv.DictWriter(output_file, fieldnames=output_columns)
                writer.writeheader()
                for row in rows:
                    writer.writerow(
                        {
                            short_column_name(column): row.get(column, "")
                            for column in source_columns
                        }
                    )
            written_paths.append(output_path)
        return written_paths


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
            "Output directory. Defaults to writing per-model "
            "'<input-stem>-<model-id>-grader-fields.csv' files beside the input."
        ),
    )
    return parser.parse_args()


def resolve_input_paths(path: Path | None) -> list[Path]:
    if path is None:
        return select_final_files(discover_final_files())
    if path.is_absolute():
        return [path]

    project_path = PROJECT_ROOT / path
    if project_path.exists():
        return [project_path]

    final_results_path = FINAL_RESULTS_DIR / path
    if final_results_path.exists():
        return [final_results_path]

    return [project_path]


def resolve_output_dir(path: Path | None) -> Path | None:
    if path is None:
        return None
    return path if path.is_absolute() else PROJECT_ROOT / path


def main() -> int:
    args = parse_args()
    input_paths = resolve_input_paths(args.input)
    output_dir = resolve_output_dir(args.output)

    try:
        written_paths: list[Path] = []
        for input_path in input_paths:
            if output_dir is not None and output_dir.suffix.casefold() == ".csv":
                raise ExtractError(
                    "The output argument must be a directory because extraction writes "
                    "one grader-field CSV per model."
                )
            written_paths.extend(extract_fields(input_path, output_dir))
    except OSError as exc:
        print(f"Error: {exc}")
        return 1
    except ExtractError as exc:
        print(f"Error: {exc}")
        return 1

    for output_path in written_paths:
        print(f"Wrote grader field CSV to {display_path(output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
