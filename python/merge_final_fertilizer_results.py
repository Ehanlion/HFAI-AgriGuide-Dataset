from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_RESULTS_DIR = PROJECT_ROOT / "results-model"
GRADING_RESULTS_DIR = PROJECT_ROOT / "results-grading"
DATASETS_DIR = PROJECT_ROOT / "datasets"
FINAL_RESULTS_DIR = PROJECT_ROOT / "results-final"

REFERENCE_FERTILIZER_COLUMN = "Fertilizer Name"
ACTUAL_FERTILIZER_COLUMN = "actual_fertilizer"
EXACT_MATCH_COLUMN = "is_model_fertilizer_exact_match"
ITEM_ID_COLUMN = "item_id"
SPLIT_NAME_COLUMN = "split_name"
MODEL_NAME_COLUMN = "model_name"
PROMPT_VERSION_COLUMN = "prompt_version"
RESULT_MODEL_ID_COLUMN = "result_model_id"
GRADER_ID_COLUMN = "grader_id"
MODEL_FERTILIZER_COLUMN = "model_fertilizer"

RUBRIC_COLUMNS = [
    "recommendation_correctness",
    "explanation_relevance",
    "clarity",
    "uncertainty_calibration",
    "decision_support_usefulness",
]

MODEL_REQUIRED_COLUMNS = [
    ITEM_ID_COLUMN,
    SPLIT_NAME_COLUMN,
    MODEL_NAME_COLUMN,
    PROMPT_VERSION_COLUMN,
    MODEL_FERTILIZER_COLUMN,
]
GRADER_REQUIRED_COLUMNS = [
    ITEM_ID_COLUMN,
    SPLIT_NAME_COLUMN,
    MODEL_NAME_COLUMN,
    PROMPT_VERSION_COLUMN,
    GRADER_ID_COLUMN,
    MODEL_FERTILIZER_COLUMN,
] + RUBRIC_COLUMNS
REFERENCE_REQUIRED_COLUMNS = [
    ITEM_ID_COLUMN,
    SPLIT_NAME_COLUMN,
    REFERENCE_FERTILIZER_COLUMN,
]


class MergeError(Exception):
    pass


class SplitSummary:
    def __init__(
        self,
        token: str,
        models: list[str],
        graders: list[str],
        missing_grader_files: list[str],
    ) -> None:
        self.token = token
        self.models = models
        self.graders = graders
        self.missing_grader_files = missing_grader_files


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise MergeError(f"{path} does not contain a header row.")
        return list(reader.fieldnames), list(reader)


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def split_token(value: str) -> str | None:
    normalized = value.replace("\\", "/")
    dataset_tokens = sorted(
        (
            path.name.removeprefix("split-")
            for path in DATASETS_DIR.glob("split-*")
            if path.is_dir()
        ),
        key=len,
        reverse=True,
    )
    for token in dataset_tokens:
        if re.search(rf"split-{re.escape(token)}(?=\.csv|/|-|$)", normalized):
            return token

    match = re.search(r"split-([a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*)(?=\.csv|/|$)", normalized)
    return match.group(1) if match else None


def split_name(token: str) -> str:
    return f"split-{token}"


def output_path_for_split(token: str) -> Path:
    return FINAL_RESULTS_DIR / f"fertilizer-result-final-graded-split-{token}.csv"


def normalize_label(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def safe_column_token(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    return cleaned.strip("_") or "grader"


def row_key(row: dict[str, str]) -> tuple[str, str, str]:
    result_model_id = row.get(RESULT_MODEL_ID_COLUMN, "").strip()
    if not result_model_id:
        result_model_id = model_label(row)
    return (
        row.get(SPLIT_NAME_COLUMN, "").strip(),
        row.get(ITEM_ID_COLUMN, "").strip(),
        result_model_id,
    )


def reference_key(row: dict[str, str]) -> tuple[str, str]:
    return (
        row.get(SPLIT_NAME_COLUMN, "").strip(),
        row.get(ITEM_ID_COLUMN, "").strip(),
    )


def require_columns(path: Path, fieldnames: list[str], required: list[str]) -> None:
    missing = [column for column in required if column not in fieldnames]
    if missing:
        raise MergeError(f"{path} is missing required columns: {', '.join(missing)}")


def validate_single_split(path: Path, rows: list[dict[str, str]], expected_split: str) -> None:
    found = sorted({row.get(SPLIT_NAME_COLUMN, "").strip() for row in rows})
    if not found:
        raise MergeError(f"{path} has no data rows.")
    if found != [expected_split]:
        raise MergeError(
            f"{path} contains split_name values {found}; expected only {expected_split}."
        )


def discover_split_tokens() -> list[str]:
    model_tokens: set[str] = set()
    for path in MODEL_RESULTS_DIR.glob("*.csv"):
        token = split_token(path.name)
        if token:
            model_tokens.add(token)

    grading_tokens: set[str] = set()
    for path in GRADING_RESULTS_DIR.glob("*.csv"):
        token = split_token(path.name)
        if token:
            grading_tokens.add(token)

    reference_tokens: set[str] = set()
    for path in DATASETS_DIR.glob("split-*/fertilizer-prediction-test.csv"):
        token = split_token(str(path))
        if token:
            reference_tokens.add(token)

    return sorted((model_tokens | grading_tokens) & reference_tokens)


def files_for_split(directory: Path, token: str) -> list[Path]:
    return sorted(path for path in directory.glob("*.csv") if split_token(path.name) == token)


def filename_model_id(path: Path, token: str) -> str | None:
    match = re.match(
        rf"^fertilizer-result-(?P<model>.+)-split-{re.escape(token)}(?:-.+)?$",
        path.stem,
    )
    if not match:
        return None
    return match.group("model").strip() or None


def expected_grader_path(model_path: Path, token: str, grader_id: str) -> Path:
    model_id = filename_model_id(model_path, token)
    if not model_id:
        return GRADING_RESULTS_DIR / f"{model_path.stem}-{grader_id}.csv"
    return GRADING_RESULTS_DIR / f"fertilizer-result-{model_id}-split-{token}-{grader_id}.csv"


def reference_path_for_split(token: str) -> Path:
    return DATASETS_DIR / split_name(token) / "fertilizer-prediction-test.csv"


def model_label(row: dict[str, str]) -> str:
    model_name = row.get(MODEL_NAME_COLUMN, "").strip() or "unknown_model"
    prompt_version = row.get(PROMPT_VERSION_COLUMN, "").strip()
    if prompt_version:
        return f"{model_name} / {prompt_version}"
    return model_name


def model_identity(path: Path, token: str, row: dict[str, str]) -> str:
    return filename_model_id(path, token) or model_label(row)


def model_summary_label(path: Path, token: str, row: dict[str, str]) -> str:
    identity = model_identity(path, token, row)
    label = model_label(row)
    if identity and identity != label:
        return f"{identity} ({label})"
    return identity


def summarize_split(token: str) -> SplitSummary:
    model_paths = files_for_split(MODEL_RESULTS_DIR, token)
    grading_paths = files_for_split(GRADING_RESULTS_DIR, token)

    models: set[str] = set()
    model_ids_by_path: dict[Path, str] = {}
    for path in model_paths:
        fieldnames, rows = read_csv_rows(path)
        require_columns(path, fieldnames, MODEL_REQUIRED_COLUMNS)
        validate_single_split(path, rows, split_name(token))
        model_ids_by_path[path] = filename_model_id(path, token) or model_label(rows[0])
        models.update(model_summary_label(path, token, row) for row in rows)

    graders: set[str] = set()
    graded_pairs: set[tuple[str, str]] = set()
    for path in grading_paths:
        fieldnames, rows = read_csv_rows(path)
        require_columns(path, fieldnames, GRADER_REQUIRED_COLUMNS)
        validate_single_split(path, rows, split_name(token))
        path_model_id = filename_model_id(path, token)
        for row in rows:
            grader_id = row.get(GRADER_ID_COLUMN, "").strip()
            model_id = path_model_id or model_label(row)
            if grader_id:
                graders.add(grader_id)
                graded_pairs.add((model_id, grader_id))

    missing_grader_files: list[str] = []
    if model_paths and not grading_paths:
        missing_grader_files.append(
            f"No grader result CSVs found in {GRADING_RESULTS_DIR.relative_to(PROJECT_ROOT)} "
            f"for {split_name(token)}."
        )
    elif graders:
        for model_path, model_id in sorted(model_ids_by_path.items()):
            for grader_id in sorted(grader for grader in graders if grader):
                if (model_id, grader_id) not in graded_pairs:
                    missing_grader_files.append(
                        str(
                            expected_grader_path(
                                model_path,
                                token,
                                grader_id,
                            ).relative_to(PROJECT_ROOT)
                        )
                    )

    return SplitSummary(
        token=token,
        models=sorted(model for model in models if model),
        graders=sorted(grader for grader in graders if grader),
        missing_grader_files=missing_grader_files,
    )


def discover_split_summaries() -> list[SplitSummary]:
    return [summarize_split(token) for token in discover_split_tokens()]


def select_splits(summaries: list[SplitSummary]) -> list[str]:
    if not summaries:
        raise MergeError(
            "No complete splits are available. A split needs at least one model result CSV "
            "in results-model, at least one grader result CSV in results-grading, and a "
            "matching fertilizer-prediction-test.csv in datasets."
        )

    print("Select split to create final results for:")
    for index, summary in enumerate(summaries, start=1):
        print(f"{index}. {split_name(summary.token)}")
        print(f"   Models: {', '.join(summary.models) if summary.models else 'none'}")
        print(f"   Graders: {', '.join(summary.graders) if summary.graders else 'none'}")
        if summary.missing_grader_files:
            print("   Missing expected grader files:")
            for missing_path in summary.missing_grader_files:
                print(f"     {missing_path}")
    all_option = len(summaries) + 1
    print(f"{all_option}. All splits")

    choice = input("Enter number: ").strip()
    if not choice.isdigit():
        raise MergeError("Selection must be a number.")
    choice_index = int(choice)
    if choice_index == all_option:
        return [summary.token for summary in summaries]
    if 1 <= choice_index <= len(summaries):
        return [summaries[choice_index - 1].token]
    raise MergeError(f"Selection must be between 1 and {all_option}.")


def load_references(token: str) -> dict[tuple[str, str], dict[str, str]]:
    path = reference_path_for_split(token)
    if not path.is_file():
        raise MergeError(f"Missing reference test file: {path}")
    fieldnames, rows = read_csv_rows(path)
    require_columns(path, fieldnames, REFERENCE_REQUIRED_COLUMNS)
    validate_single_split(path, rows, split_name(token))

    references: dict[tuple[str, str], dict[str, str]] = {}
    duplicates: list[tuple[str, str]] = []
    for row in rows:
        key = reference_key(row)
        if key in references:
            duplicates.append(key)
        references[key] = row
    if duplicates:
        raise MergeError(f"{path} contains duplicate reference rows, including {duplicates[0]}.")
    return references


def load_models(token: str) -> tuple[list[str], list[dict[str, str]]]:
    paths = files_for_split(MODEL_RESULTS_DIR, token)
    if not paths:
        raise MergeError(f"Missing model result CSVs in {MODEL_RESULTS_DIR} for {split_name(token)}.")

    output_fields: list[str] = []
    rows: list[dict[str, str]] = []
    seen_keys: set[tuple[str, str, str]] = set()
    for path in paths:
        fieldnames, file_rows = read_csv_rows(path)
        require_columns(path, fieldnames, MODEL_REQUIRED_COLUMNS)
        validate_single_split(path, file_rows, split_name(token))
        for field in fieldnames:
            if field not in output_fields:
                output_fields.append(field)
        if RESULT_MODEL_ID_COLUMN not in output_fields:
            output_fields.append(RESULT_MODEL_ID_COLUMN)
        for source_row in file_rows:
            row = dict(source_row)
            row[RESULT_MODEL_ID_COLUMN] = model_identity(path, token, row)
            key = row_key(row)
            if key in seen_keys:
                raise MergeError(f"Duplicate model row key in {path}: {key}")
            seen_keys.add(key)
            rows.append(row)
    return output_fields, rows


def load_grades(token: str) -> dict[tuple[str, str, str], dict[str, dict[str, str]]]:
    paths = files_for_split(GRADING_RESULTS_DIR, token)
    if not paths:
        raise MergeError(f"Missing grader result CSVs in {GRADING_RESULTS_DIR} for {split_name(token)}.")

    grades_by_key: dict[tuple[str, str, str], dict[str, dict[str, str]]] = defaultdict(dict)
    for path in paths:
        fieldnames, rows = read_csv_rows(path)
        require_columns(path, fieldnames, GRADER_REQUIRED_COLUMNS)
        validate_single_split(path, rows, split_name(token))
        path_model_id = filename_model_id(path, token)
        for source_row in rows:
            row = dict(source_row)
            row[RESULT_MODEL_ID_COLUMN] = path_model_id or model_identity(path, token, row)
            grader_id = row.get(GRADER_ID_COLUMN, "").strip()
            if not grader_id:
                raise MergeError(f"{path} contains a row with blank grader_id.")
            key = row_key(row)
            if grader_id in grades_by_key[key]:
                raise MergeError(f"Duplicate grade for grader {grader_id} and row key {key} in {path}.")
            grades_by_key[key][grader_id] = row
    return dict(grades_by_key)


def merge_split(token: str) -> Path:
    references = load_references(token)
    model_fields, model_rows = load_models(token)
    grades_by_key = load_grades(token)

    model_keys = {row_key(row) for row in model_rows}
    unmatched_grade_keys = sorted(key for key in grades_by_key if key not in model_keys)
    if unmatched_grade_keys:
        raise MergeError(
            "Grader rows do not match model results. "
            f"First unmatched row key: {unmatched_grade_keys[0]}. "
            "Check that each grading filename uses the same model id as its model CSV, "
            "for example fertilizer-result-<model-id>-split-<split-name>-<grader-id>.csv."
        )

    grader_ids = sorted({grader_id for grades in grades_by_key.values() for grader_id in grades})
    missing_grade_sets = [
        (key, grader_id)
        for key in sorted(model_keys)
        for grader_id in grader_ids
        if grader_id not in grades_by_key.get(key, {})
    ]
    if missing_grade_sets:
        missing_key, missing_grader = missing_grade_sets[0]
        model_path_by_id: dict[str, Path] = {}
        for model_path in files_for_split(MODEL_RESULTS_DIR, token):
            fieldnames, file_rows = read_csv_rows(model_path)
            require_columns(model_path, fieldnames, MODEL_REQUIRED_COLUMNS)
            if file_rows:
                model_path_by_id[model_identity(model_path, token, file_rows[0])] = model_path
        expected_path = expected_grader_path(
            model_path_by_id.get(
                missing_key[2],
                MODEL_RESULTS_DIR / f"fertilizer-result-{missing_key[2]}-split-{token}.csv",
            ),
            token,
            missing_grader,
        )
        raise MergeError(
            f"Cannot merge incomplete grading results. Grader {missing_grader} is missing "
            f"a grade for row key {missing_key}. Expected grading file: "
            f"{expected_path.relative_to(PROJECT_ROOT)}"
        )

    grader_fields = [
        f"grader_{safe_column_token(grader_id)}_{rubric}"
        for grader_id in grader_ids
        for rubric in RUBRIC_COLUMNS
    ]
    final_fields = model_fields + [ACTUAL_FERTILIZER_COLUMN, EXACT_MATCH_COLUMN] + grader_fields

    final_rows: list[dict[str, str]] = []
    for model_row in model_rows:
        key = row_key(model_row)
        ref_key = reference_key(model_row)
        if ref_key not in references:
            raise MergeError(f"Model row {key} is missing from reference test results.")

        final_row = {field: model_row.get(field, "") for field in model_fields}
        actual_fertilizer = references[ref_key].get(REFERENCE_FERTILIZER_COLUMN, "")
        model_fertilizer = model_row.get(MODEL_FERTILIZER_COLUMN, "")
        final_row[ACTUAL_FERTILIZER_COLUMN] = actual_fertilizer
        final_row[EXACT_MATCH_COLUMN] = str(
            normalize_label(model_fertilizer) == normalize_label(actual_fertilizer)
        ).lower()

        for grader_id in grader_ids:
            grade_row = grades_by_key.get(key, {}).get(grader_id)
            for rubric in RUBRIC_COLUMNS:
                final_row[f"grader_{safe_column_token(grader_id)}_{rubric}"] = (
                    grade_row.get(rubric, "") if grade_row else ""
                )
        final_rows.append(final_row)

    path = output_path_for_split(token)
    write_csv_rows(path, final_fields, final_rows)
    print(f"Wrote {path} ({len(final_rows)} rows, {len(grader_ids)} graders).")
    return path


def main() -> int:
    try:
        summaries = discover_split_summaries()
        selected_tokens = select_splits(summaries)
        failures: list[str] = []
        for token in selected_tokens:
            try:
                merge_split(token)
            except MergeError as exc:
                failures.append(f"{split_name(token)}: {exc}")
                print(f"ERROR: {split_name(token)}: {exc}", file=sys.stderr)
        return 1 if failures and len(failures) == len(selected_tokens) else 0
    except MergeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
