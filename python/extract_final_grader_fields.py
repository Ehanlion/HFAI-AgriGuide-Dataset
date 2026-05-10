from __future__ import annotations

import argparse
import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    PROJECT_ROOT
    / "results-final"
    / "fertilizer-result-final-graded-split-0-100-subset.csv"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "results-final"
    / "fertilizer-result-final-graded-split-0-100-subset-grader-fields.csv"
)
ITEM_ID_COLUMN = "item_id"
GRADER_COLUMN_PREFIX = "grader_"


class ExtractError(Exception):
    pass


def extract_fields(input_path: Path, output_path: Path) -> None:
    with input_path.open(newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ExtractError(f"{input_path} does not contain a header row.")

        fieldnames = list(reader.fieldnames)
        if ITEM_ID_COLUMN not in fieldnames:
            raise ExtractError(f"{input_path} is missing required column: {ITEM_ID_COLUMN}")

        output_columns = [
            ITEM_ID_COLUMN,
            *[field for field in fieldnames if field.startswith(GRADER_COLUMN_PREFIX)],
        ]
        if len(output_columns) == 1:
            raise ExtractError(f"{input_path} does not contain any grader columns.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=output_columns)
            writer.writeheader()
            for row in reader:
                writer.writerow({column: row.get(column, "") for column in output_columns})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract item_id and grader result columns from a final fertilizer CSV."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input final CSV. Defaults to {DEFAULT_INPUT.relative_to(PROJECT_ROOT)}.",
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output CSV. Defaults to {DEFAULT_OUTPUT.relative_to(PROJECT_ROOT)}.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = args.input if args.input.is_absolute() else PROJECT_ROOT / args.input
    output_path = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output

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
