from __future__ import annotations

import csv
import itertools
import re
import sys
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL_RESULTS_DIR = PROJECT_ROOT / "results-final"
FINAL_RESULT_PATTERN = "fertilizer-result-final-graded-split-*.csv"

RUBRIC_COLUMNS = [
    "recommendation_correctness",
    "explanation_relevance",
    "clarity",
    "uncertainty_calibration",
    "decision_support_usefulness",
]
MODEL_NAME_COLUMN = "model_name"
PROMPT_VERSION_COLUMN = "prompt_version"
RESULT_MODEL_ID_COLUMN = "result_model_id"
WEIGHTED_RUBRICS = {
    "explanation_relevance",
    "clarity",
    "uncertainty_calibration",
    "decision_support_usefulness",
}


class KappaError(Exception):
    pass


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise KappaError(f"{path} does not contain a header row.")
        return list(reader.fieldnames), list(reader)


def discover_final_files() -> list[Path]:
    return sorted(FINAL_RESULTS_DIR.glob(FINAL_RESULT_PATTERN))


def select_final_files(paths: list[Path]) -> list[Path]:
    if not paths:
        raise KappaError(f"No final result CSVs found in {FINAL_RESULTS_DIR}.")

    print("Select final result file to calculate Cohen's kappa for:")
    for index, path in enumerate(paths, start=1):
        print(f"{index}. {path.name}")
    all_option = len(paths) + 1
    print(f"{all_option}. All files")

    choice = input("Enter number: ").strip()
    if not choice.isdigit():
        raise KappaError("Selection must be a number.")
    choice_index = int(choice)
    if choice_index == all_option:
        return paths
    if 1 <= choice_index <= len(paths):
        return [paths[choice_index - 1]]
    raise KappaError(f"Selection must be between 1 and {all_option}.")


def grader_ids_from_fields(fieldnames: list[str]) -> list[str]:
    grader_ids: set[str] = set()
    for field in fieldnames:
        for rubric in RUBRIC_COLUMNS:
            suffix = f"_{rubric}"
            if field.startswith("grader_") and field.endswith(suffix):
                grader_ids.add(field[len("grader_") : -len(suffix)])
    return sorted(grader_ids)


def column_for(grader_id: str, rubric: str) -> str:
    return f"grader_{grader_id}_{rubric}"


def unweighted_kappa(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    total = len(pairs)
    observed = sum(1 for left, right in pairs if left == right) / total
    left_counts = Counter(left for left, _right in pairs)
    right_counts = Counter(right for _left, right in pairs)
    labels = set(left_counts) | set(right_counts)
    expected = sum((left_counts[label] / total) * (right_counts[label] / total) for label in labels)
    if expected == 1:
        return 1.0 if observed == 1 else None
    return (observed - expected) / (1 - expected)


def linear_weighted_kappa(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    labels = ["1", "2", "3", "4", "5"]
    label_to_index = {label: index for index, label in enumerate(labels)}
    if any(left not in label_to_index or right not in label_to_index for left, right in pairs):
        return unweighted_kappa(pairs)

    total = len(pairs)
    max_distance = len(labels) - 1
    observed_disagreement = sum(
        abs(label_to_index[left] - label_to_index[right]) / max_distance
        for left, right in pairs
    ) / total
    left_counts = Counter(left for left, _right in pairs)
    right_counts = Counter(right for _left, right in pairs)
    expected_disagreement = 0.0
    for left in labels:
        for right in labels:
            expected_disagreement += (
                (left_counts[left] / total)
                * (right_counts[right] / total)
                * (abs(label_to_index[left] - label_to_index[right]) / max_distance)
            )
    if expected_disagreement == 0:
        return 1.0 if observed_disagreement == 0 else None
    return 1 - (observed_disagreement / expected_disagreement)


def format_kappa(value: float | None) -> str:
    return "undefined" if value is None else f"{value:.4f}"


def model_group_label(row: dict[str, str]) -> str:
    result_model_id = row.get(RESULT_MODEL_ID_COLUMN, "").strip()
    model_name = row.get(MODEL_NAME_COLUMN, "").strip() or "unknown_model"
    prompt_version = row.get(PROMPT_VERSION_COLUMN, "").strip()
    label = model_name
    if prompt_version:
        label = f"{model_name} / {prompt_version}"
    if result_model_id and result_model_id != label:
        return f"{result_model_id} ({label})"
    return result_model_id or label


def append_kappa_section(
    lines: list[str],
    section_title: str,
    rows: list[dict[str, str]],
    fieldnames: list[str],
    grader_ids: list[str],
) -> None:
    lines.append(section_title)
    lines.append(f"Rows: {len(rows)}")
    for left_grader, right_grader in itertools.combinations(grader_ids, 2):
        lines.append(f"{left_grader} vs {right_grader}")
        for rubric in RUBRIC_COLUMNS:
            left_column = column_for(left_grader, rubric)
            right_column = column_for(right_grader, rubric)
            if left_column not in fieldnames or right_column not in fieldnames:
                raise KappaError(
                    f"Missing columns for {left_grader}/{right_grader} {rubric}."
                )
            pairs = [
                (row.get(left_column, "").strip(), row.get(right_column, "").strip())
                for row in rows
                if row.get(left_column, "").strip() and row.get(right_column, "").strip()
            ]
            kappa = linear_weighted_kappa(pairs) if rubric in WEIGHTED_RUBRICS else unweighted_kappa(pairs)
            weighting = "linear weighted" if rubric in WEIGHTED_RUBRICS else "unweighted"
            lines.append(f"  {rubric}: {format_kappa(kappa)} ({weighting}, n={len(pairs)})")
        lines.append("")


def report_path_for(path: Path) -> Path:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", path.stem).strip("-") or path.stem
    return FINAL_RESULTS_DIR / f"cohen-kappa-{cleaned}.txt"


def calculate_for_file(path: Path) -> str:
    fieldnames, rows = read_csv_rows(path)
    grader_ids = grader_ids_from_fields(fieldnames)
    if len(grader_ids) < 2:
        raise KappaError(f"{path.name} has fewer than two graders.")
    if MODEL_NAME_COLUMN not in fieldnames:
        raise KappaError(f"{path.name} is missing required column: {MODEL_NAME_COLUMN}")

    lines = [
        f"Cohen's kappa report for {path.name}",
        f"Graders: {', '.join(grader_ids)}",
        "",
    ]
    append_kappa_section(lines, "Overall agreement across all models", rows, fieldnames, grader_ids)

    rows_by_model: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        rows_by_model.setdefault(model_group_label(row), []).append(row)

    for label in sorted(rows_by_model):
        append_kappa_section(
            lines,
            f"Agreement for model: {label}",
            rows_by_model[label],
            fieldnames,
            grader_ids,
        )

    report = "\n".join(lines).rstrip() + "\n"
    report_path = report_path_for(path)
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote {report_path}")
    return report


def main() -> int:
    try:
        selected_paths = select_final_files(discover_final_files())
        failures: list[str] = []
        for path in selected_paths:
            try:
                calculate_for_file(path)
            except KappaError as exc:
                failures.append(f"{path.name}: {exc}")
                print(f"ERROR: {path.name}: {exc}", file=sys.stderr)
        return 1 if failures and len(failures) == len(selected_paths) else 0
    except KappaError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
