from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "grading-results"
REFERENCE_FERTILIZER_COLUMN = "Fertilizer Name"
MODEL_FERTILIZER_COLUMN = "model_fertilizer"
ITEM_ID_COLUMN = "item_id"
SPLIT_NAME_COLUMN = "split_name"

RUBRICS = [
    (
        "recommendation_correctness",
        "Recommendation Correctness",
        [
            ("correct", "The AI recommends the same fertilizer as the dataset label."),
            (
                "partially_correct",
                "The recommendation has meaningful nutrient overlap or includes the correct fertilizer among multiple options.",
            ),
            (
                "incorrect",
                "The AI recommends a different fertilizer, gives no usable fertilizer, or conflicts with the dataset label.",
            ),
        ],
    ),
    (
        "explanation_relevance",
        "Explanation Relevance",
        [
            ("0", "The explanation is missing or unrelated to the given case."),
            ("1", "The explanation is mostly generic and barely connects to the input."),
            ("2", "The explanation mentions one relevant input, but the reasoning is weak or incomplete."),
            ("3", "The explanation uses some relevant inputs, but misses important factors."),
            ("4", "The explanation uses most important inputs and gives a reasonable fertilizer-specific justification."),
            ("5", "The explanation clearly connects crop, soil, moisture, temperature/humidity, and nutrients to the recommendation."),
        ],
    ),
    (
        "clarity",
        "Interpretability and Clarity",
        [
            ("0", "The response is confusing, contradictory, or impossible to use."),
            ("1", "The response is very hard to follow and lacks a clear recommendation."),
            ("2", "The response has a recommendation, but wording is vague, cluttered, or poorly organized."),
            ("3", "The response is understandable but has some unclear reasoning or unnecessary complexity."),
            ("4", "The response is clear, organized, and understandable for a non-expert."),
            ("5", "The response is very clear, concise, and easy for a non-expert to act on responsibly."),
        ],
    ),
    (
        "uncertainty_calibration",
        "Uncertainty Calibration",
        [
            ("0", "The AI is dangerously overconfident, presents the recommendation as guaranteed, or gives no caution."),
            ("1", "The AI is strongly overconfident and gives little or no verification language."),
            ("2", "The AI gives weak caution, but still sounds more certain than the dataset supports."),
            ("3", "The AI includes some uncertainty or verification language, but the caution is limited or generic."),
            ("4", "The AI recommends clearly while noting that decisions should be verified with soil testing or expertise."),
            ("5", "The AI balances recommendation and caution very well and explains limits of the data."),
        ],
    ),
    (
        "decision_support_usefulness",
        "Decision-Support Usefulness",
        [
            ("0", "The response is unusable or actively misleading."),
            ("1", "The response gives very little help and may cause poor decision-making."),
            ("2", "The response has one useful piece of information, but major parts are missing or flawed."),
            ("3", "The response is somewhat useful, but would require significant outside interpretation."),
            ("4", "The response is useful and would help a human understand the likely fertilizer choice."),
            ("5", "The response is highly useful, gives clear reasoning, and includes appropriate caution."),
        ],
    ),
]

REASONING_FIELDS = [
    "explanation",
    "confidence_statement",
    "uncertainty_or_caution",
    "decision_support_notes",
]


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"{path} does not contain a header row.")
        return reader.fieldnames, list(reader)


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower())
    return cleaned.strip("-") or "grader"


class KeyValueTable(QTableWidget):
    def __init__(self) -> None:
        super().__init__(0, 2)
        self.setHorizontalHeaderLabels(["Field", "Value"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.setWordWrap(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def set_mapping(self, values: dict[str, str], fields: list[str] | None = None) -> None:
        names = fields or list(values.keys())
        self.setRowCount(len(names))
        for row_index, field in enumerate(names):
            self.setItem(row_index, 0, QTableWidgetItem(field))
            self.setItem(row_index, 1, QTableWidgetItem(values.get(field, "")))
        self.resizeRowsToContents()


class GraderWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AgriGuide Fertilizer Grader")
        self.resize(1300, 820)

        self.model_path: Path | None = None
        self.reference_path: Path | None = None
        self.output_path: Path | None = None
        self.model_fields: list[str] = []
        self.reference_fields: list[str] = []
        self.model_rows: list[dict[str, str]] = []
        self.reference_rows_by_key: dict[tuple[str, str], dict[str, str]] = {}
        self.completed_rows: list[dict[str, str]] = []
        self.current_index = 0
        self.current_rubric_index = 0
        self.current_grades: dict[str, str] = {}
        self.editing_existing_grade = False

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top = QGridLayout()
        self.grader_input = QLineEdit()
        self.output_input = QLineEdit(str(DEFAULT_OUTPUT_DIR))
        self.model_input = QLineEdit()
        self.reference_input = QLineEdit()

        top.addWidget(QLabel("Grader"), 0, 0)
        top.addWidget(self.grader_input, 0, 1)
        top.addWidget(QLabel("Output directory"), 0, 2)
        top.addWidget(self.output_input, 0, 3)
        output_button = QPushButton("Browse")
        output_button.clicked.connect(self.choose_output_dir)
        top.addWidget(output_button, 0, 4)

        top.addWidget(QLabel("Model result CSV"), 1, 0)
        top.addWidget(self.model_input, 1, 1, 1, 3)
        model_button = QPushButton("Browse")
        model_button.clicked.connect(self.choose_model_file)
        top.addWidget(model_button, 1, 4)

        top.addWidget(QLabel("Reference test CSV"), 2, 0)
        top.addWidget(self.reference_input, 2, 1, 1, 3)
        reference_button = QPushButton("Browse")
        reference_button.clicked.connect(self.choose_reference_file)
        top.addWidget(reference_button, 2, 4)

        load_button = QPushButton("Load Grading Session")
        load_button.clicked.connect(self.load_session)
        top.addWidget(load_button, 3, 3, 1, 2)
        layout.addLayout(top)

        splitter = QSplitter(Qt.Horizontal)
        self.model_table = KeyValueTable()
        self.reference_table = KeyValueTable()
        self.reasoning_view = QTextEdit()
        self.reasoning_view.setReadOnly(True)
        splitter.addWidget(self.wrap("Model Result", self.model_table))
        splitter.addWidget(self.wrap("Reference Answer", self.reference_table))
        splitter.addWidget(self.wrap("Model Reasoning", self.reasoning_view))
        splitter.setSizes([430, 430, 440])
        layout.addWidget(splitter, stretch=1)

        self.progress_label = QLabel("Load a grading session to begin.")
        layout.addWidget(self.progress_label)

        self.grading_box = QGroupBox("Grade")
        self.grading_layout = QVBoxLayout(self.grading_box)
        self.prompt_label = QLabel("")
        self.prompt_label.setWordWrap(True)
        self.button_row = QHBoxLayout()
        self.review_table = KeyValueTable()
        self.review_table.hide()
        self.confirm_row = QHBoxLayout()
        self.grading_layout.addWidget(self.prompt_label)
        self.grading_layout.addLayout(self.button_row)
        self.grading_layout.addWidget(self.review_table)
        self.grading_layout.addLayout(self.confirm_row)
        layout.addWidget(self.grading_box)

    def wrap(self, title: str, widget: QWidget) -> QGroupBox:
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        layout.addWidget(widget)
        return box

    def choose_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select output directory", self.output_input.text())
        if path:
            self.output_input.setText(path)

    def choose_model_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select model result CSV", str(PROJECT_ROOT), "CSV files (*.csv)")
        if path:
            self.model_input.setText(path)

    def choose_reference_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select reference test CSV", str(PROJECT_ROOT / "datasets"), "CSV files (*.csv)")
        if path:
            self.reference_input.setText(path)

    def load_session(self) -> None:
        try:
            grader = safe_name(self.grader_input.text())
            if not self.grader_input.text().strip():
                raise ValueError("Enter a grader name before loading a session.")
            self.model_path = Path(self.model_input.text())
            self.reference_path = Path(self.reference_input.text())
            if not self.model_path.is_file():
                raise ValueError("Select an existing model result CSV.")
            if not self.reference_path.is_file():
                raise ValueError("Select an existing reference test CSV.")

            self.model_fields, self.model_rows = read_csv_rows(self.model_path)
            self.reference_fields, reference_rows = read_csv_rows(self.reference_path)
            self.validate_required_fields()
            self.reference_rows_by_key = {
                self.row_key(row): row for row in reference_rows
            }
            self.validate_model_rows_have_references()

            output_dir = Path(self.output_input.text())
            self.output_path = output_dir / f"{self.model_path.stem}-{grader}.csv"
            self.completed_rows = []
            if self.output_path.exists():
                _, existing_rows = read_csv_rows(self.output_path)
                if existing_rows:
                    answer = QMessageBox.question(
                        self,
                        "Resume grading?",
                        f"Found {len(existing_rows)} completed rows in {self.output_path.name}. Resume from the next item?",
                    )
                    if answer == QMessageBox.Yes:
                        self.completed_rows = existing_rows

            completed_keys = {self.row_key(row) for row in self.completed_rows}
            self.current_index = next(
                (index for index, row in enumerate(self.model_rows) if self.row_key(row) not in completed_keys),
                len(self.model_rows),
            )
            self.show_current_item()
        except Exception as exc:
            QMessageBox.critical(self, "Could not load session", str(exc))

    def validate_required_fields(self) -> None:
        required_model = {ITEM_ID_COLUMN, SPLIT_NAME_COLUMN, MODEL_FERTILIZER_COLUMN}
        required_reference = {ITEM_ID_COLUMN, SPLIT_NAME_COLUMN, REFERENCE_FERTILIZER_COLUMN}
        missing_model = sorted(required_model - set(self.model_fields))
        missing_reference = sorted(required_reference - set(self.reference_fields))
        if missing_model:
            raise ValueError(f"Model result CSV is missing columns: {', '.join(missing_model)}")
        if missing_reference:
            raise ValueError(f"Reference test CSV is missing columns: {', '.join(missing_reference)}")

    def validate_model_rows_have_references(self) -> None:
        missing = [
            self.row_key(row)
            for row in self.model_rows
            if self.row_key(row) not in self.reference_rows_by_key
        ]
        if missing:
            sample = ", ".join(f"{split}/{item}" for split, item in missing[:5])
            raise ValueError(f"Model rows missing from reference CSV: {sample}")

    def row_key(self, row: dict[str, str]) -> tuple[str, str]:
        return (
            (row.get(SPLIT_NAME_COLUMN) or "").strip(),
            (row.get(ITEM_ID_COLUMN) or "").strip(),
        )

    def show_current_item(self) -> None:
        if self.current_index >= len(self.model_rows):
            self.clear_grading_controls()
            self.progress_label.setText(f"Complete. Wrote {self.output_path}")
            QMessageBox.information(self, "Grading complete", f"All rows are graded.\n\n{self.output_path}")
            return

        self.current_grades = {}
        self.editing_existing_grade = False
        self.current_rubric_index = 0
        model_row = self.model_rows[self.current_index]
        reference_row = self.reference_rows_by_key[self.row_key(model_row)]
        self.model_table.set_mapping(model_row)
        self.reference_table.set_mapping(reference_row)
        self.reasoning_view.setPlainText(
            "\n\n".join(
                f"{field}:\n{model_row.get(field, '')}"
                for field in REASONING_FIELDS
                if field in model_row
            )
        )
        self.progress_label.setText(
            f"Item {self.current_index + 1} of {len(self.model_rows)} "
            f"({model_row.get(SPLIT_NAME_COLUMN)} / {model_row.get(ITEM_ID_COLUMN)})"
        )
        self.show_rubric_prompt()

    def clear_layout(self, layout: QHBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def clear_grading_controls(self) -> None:
        self.prompt_label.setText("")
        self.clear_layout(self.button_row)
        self.clear_layout(self.confirm_row)
        self.review_table.hide()

    def show_rubric_prompt(self) -> None:
        self.review_table.hide()
        self.clear_layout(self.button_row)
        self.clear_layout(self.confirm_row)
        column, title, options = RUBRICS[self.current_rubric_index]
        self.prompt_label.setText(f"{title}: choose a grade for `{column}`.")
        for label, tooltip in options:
            button = QPushButton(label)
            button.setToolTip(tooltip)
            button.clicked.connect(lambda _checked=False, value=label: self.record_grade(value))
            self.button_row.addWidget(button)
        self.button_row.addStretch()

    def record_grade(self, value: str) -> None:
        column = RUBRICS[self.current_rubric_index][0]
        self.current_grades[column] = value
        if self.editing_existing_grade:
            self.editing_existing_grade = False
            self.show_confirmation()
            return

        self.current_rubric_index += 1
        if self.current_rubric_index >= len(RUBRICS):
            self.show_confirmation()
        else:
            self.show_rubric_prompt()

    def show_confirmation(self) -> None:
        self.clear_layout(self.button_row)
        self.clear_layout(self.confirm_row)
        self.prompt_label.setText("Review grades before confirming this item.")
        self.review_table.set_mapping(self.current_grades, [rubric[0] for rubric in RUBRICS])
        self.review_table.show()

        for index, (column, title, _options) in enumerate(RUBRICS):
            button = QPushButton(f"Edit {title}")
            button.clicked.connect(lambda _checked=False, rubric_index=index: self.edit_rubric(rubric_index))
            self.confirm_row.addWidget(button)

        confirm = QPushButton("Confirm and Save")
        confirm.clicked.connect(self.confirm_current_item)
        self.confirm_row.addWidget(confirm)

    def edit_rubric(self, rubric_index: int) -> None:
        self.editing_existing_grade = True
        self.current_rubric_index = rubric_index
        self.show_rubric_prompt()

    def confirm_current_item(self) -> None:
        if self.output_path is None:
            return
        model_row = self.model_rows[self.current_index]
        reference_row = self.reference_rows_by_key[self.row_key(model_row)]
        graded_row = {
            ITEM_ID_COLUMN: model_row.get(ITEM_ID_COLUMN, ""),
            SPLIT_NAME_COLUMN: model_row.get(SPLIT_NAME_COLUMN, ""),
            "model_name": model_row.get("model_name", ""),
            "prompt_version": model_row.get("prompt_version", ""),
            "grader_id": safe_name(self.grader_input.text()),
            "reference_fertilizer": reference_row.get(REFERENCE_FERTILIZER_COLUMN, ""),
            "model_fertilizer": model_row.get(MODEL_FERTILIZER_COLUMN, ""),
        }
        graded_row.update(self.current_grades)
        self.completed_rows.append(graded_row)
        output_fields = [
            ITEM_ID_COLUMN,
            SPLIT_NAME_COLUMN,
            "model_name",
            "prompt_version",
            "grader_id",
            "reference_fertilizer",
            "model_fertilizer",
        ] + [rubric[0] for rubric in RUBRICS]
        write_csv_rows(self.output_path, output_fields, self.completed_rows)
        self.current_index += 1
        self.show_current_item()


def main() -> None:
    app = QApplication(sys.argv)
    window = GraderWindow()
    window.show()
    sys.exit(app.exec())
