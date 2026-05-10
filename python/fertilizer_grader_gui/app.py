from __future__ import annotations

import csv
import html
import json
import re
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QCloseEvent, QColor, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
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
GUI_DIR = Path(__file__).resolve().parent
STATE_DIR = GUI_DIR / ".gui-state"
STATE_PATH = STATE_DIR / "state.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results-grading"
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
            ("1", "The explanation is missing, unrelated to the given case, or almost entirely generic."),
            ("2", "The explanation barely connects to the input or mentions one relevant input with weak reasoning."),
            ("3", "The explanation uses some relevant inputs, but misses important factors."),
            ("4", "The explanation uses most important inputs and gives a reasonable fertilizer-specific justification."),
            ("5", "The explanation clearly connects crop, soil, moisture, temperature/humidity, and nutrients to the recommendation."),
        ],
    ),
    (
        "clarity",
        "Interpretability and Clarity",
        [
            ("1", "The response is confusing, contradictory, impossible to use, or lacks a clear recommendation."),
            ("2", "The response has a recommendation, but it is hard to follow or poorly organized."),
            ("3", "The response is understandable but has some unclear reasoning, vague wording, or unnecessary complexity."),
            ("4", "The response is clear, organized, and understandable for a non-expert."),
            ("5", "The response is very clear, concise, and easy for a non-expert to act on responsibly."),
        ],
    ),
    (
        "uncertainty_calibration",
        "Uncertainty Calibration",
        [
            ("1", "The AI is dangerously overconfident, presents the recommendation as guaranteed, or gives little to no caution."),
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
            ("1", "The response is unusable, actively misleading, or gives very little help."),
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

THEMES = {
    "light": {
        "window": "#f7f3e8",
        "text": "#253327",
        "panel": "#fffdf6",
        "panel_alt": "#f1ead8",
        "border": "#c8bfa9",
        "accent": "#2f7d50",
        "accent_hover": "#3c9561",
        "accent_dark": "#1f5c39",
        "field_bg": "#e2efd6",
        "field_text": "#234b34",
        "button_bg": "#fff8df",
        "button_hover": "#ffe8a6",
        "button_pressed": "#e9c45e",
        "button_border": "#cf9f3d",
        "confirm": "#b65d24",
        "confirm_hover": "#cf7030",
        "confirm_border": "#884218",
        "reasoning_heading_bg": "#e2efd6",
        "reasoning_heading_text": "#234b34",
    },
    "dark": {
        "window": "#18231d",
        "text": "#edf4e9",
        "panel": "#223026",
        "panel_alt": "#2b3b30",
        "border": "#60715c",
        "accent": "#65a86f",
        "accent_hover": "#76ba80",
        "accent_dark": "#3f7448",
        "field_bg": "#314734",
        "field_text": "#d8f1d5",
        "button_bg": "#344136",
        "button_hover": "#41513f",
        "button_pressed": "#4d604a",
        "button_border": "#6c805f",
        "confirm": "#c7783e",
        "confirm_hover": "#dc884a",
        "confirm_border": "#9c5729",
        "reasoning_heading_bg": "#314734",
        "reasoning_heading_text": "#d8f1d5",
    },
}

APP_STYLESHEET_TEMPLATE = """
QMainWindow, QWidget {
    background: {window};
    color: {text};
    font-size: 16px;
}

QLineEdit, QTextEdit, QTableWidget {
    background: {panel};
    color: {text};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 8px;
    selection-background-color: {accent};
    selection-color: #ffffff;
}

QLineEdit {
    min-height: 34px;
}

QToolTip {
    background: {panel};
    border: 2px solid {border};
    border-radius: 8px;
    color: {text};
    font-size: 32px;
    font-weight: 700;
    padding: 12px 16px;
}

QTextEdit {
    font-size: 17px;
    line-height: 1.35;
}

QHeaderView::section {
    background: {accent_dark};
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
    padding: 8px;
    border: 0;
}

QGroupBox {
    border: 2px solid {border};
    border-radius: 8px;
    margin-top: 16px;
    padding: 14px 10px 10px 10px;
    font-size: 20px;
    font-weight: 800;
    color: {reasoning_heading_text};
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    background: {window};
}

QLabel {
    font-size: 17px;
    font-weight: 700;
    color: {text};
}

QPushButton {
    background: {button_bg};
    border: 2px solid {button_border};
    border-radius: 8px;
    color: {text};
    font-size: 16px;
    font-weight: 800;
    padding: 9px 16px;
}

QPushButton:hover {
    background: {button_hover};
}

QPushButton:pressed {
    background: {button_pressed};
}

QPushButton#loadButton {
    background: {accent};
    border-color: {accent_dark};
    color: #ffffff;
}

QPushButton#loadButton:hover {
    background: {accent_hover};
}

QPushButton[role="grade"] {
    background: {accent};
    border-color: {accent_dark};
    color: #ffffff;
    font-size: 24px;
    min-height: 76px;
    min-width: 150px;
    padding: 16px 24px;
}

QPushButton[role="grade"]:hover {
    background: {accent_hover};
}

QPushButton[role="confirm"] {
    background: {confirm};
    border-color: {confirm_border};
    color: #ffffff;
    font-size: 22px;
    min-height: 68px;
    padding: 14px 22px;
}

QPushButton[role="confirm"]:hover {
    background: {confirm_hover};
}

QPushButton[role="edit"] {
    min-height: 50px;
}
"""


def build_stylesheet(theme: dict[str, str]) -> str:
    stylesheet = APP_STYLESHEET_TEMPLATE
    for key, value in theme.items():
        stylesheet = stylesheet.replace(f"{{{key}}}", value)
    return stylesheet


def ordered_grade_options(column: str, options: list[tuple[str, str]]) -> list[tuple[str, str]]:
    if column == "recommendation_correctness":
        order = {"incorrect": 0, "partially_correct": 1, "correct": 2}
        return sorted(options, key=lambda option: order.get(option[0], len(order)))
    return options


def grade_button_stylesheet(label: str) -> str:
    colors = {
        "incorrect": ("#b8332f", "#d64a43", "#84201d", "#ffffff"),
        "partially_correct": ("#d9b33f", "#efcc5c", "#9d7c1c", "#1f241f"),
        "correct": ("#2f6fb3", "#3f82ca", "#1f4f82", "#ffffff"),
        "1": ("#b8332f", "#d64a43", "#84201d", "#ffffff"),
        "2": ("#d98534", "#ee9a4c", "#9a5a1b", "#1f241f"),
        "3": ("#d9b33f", "#efcc5c", "#9d7c1c", "#1f241f"),
        "4": ("#4f9f90", "#61b7a6", "#2d6e63", "#ffffff"),
        "5": ("#2f6fb3", "#3f82ca", "#1f4f82", "#ffffff"),
    }
    background, hover, border, text = colors.get(label, ("#2f6fb3", "#3f82ca", "#1f4f82", "#ffffff"))
    return f"""
        QPushButton {{
            background: {background};
            border: 2px solid {border};
            border-radius: 8px;
            color: {text};
            font-size: 24px;
            font-weight: 800;
            min-height: 76px;
            min-width: 150px;
            padding: 16px 24px;
        }}
        QPushButton:hover {{
            background: {hover};
        }}
        QPushButton:pressed {{
            background: {border};
        }}
    """


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"{path} does not contain a header row.")
        return list(reader.fieldnames), list(reader)


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower())
    return cleaned.strip("-") or "grader"


def read_gui_state() -> dict[str, str]:
    if not STATE_PATH.exists():
        return {}

    try:
        with STATE_PATH.open(encoding="utf-8") as state_file:
            state = json.load(state_file)
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(state, dict):
        return {}
    return {str(key): str(value) for key, value in state.items()}


def write_gui_state(state: dict[str, str]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as state_file:
        json.dump(state, state_file, indent=2)


class KeyValueTable(QTableWidget):
    def __init__(self) -> None:
        super().__init__(0, 2)
        self.theme = THEMES["light"]
        self.setHorizontalHeaderLabels(["Field", "Value"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setWordWrap(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.apply_theme(self.theme)

    def apply_theme(self, theme: dict[str, str]) -> None:
        self.theme = theme
        self.setStyleSheet(
            f"QTableWidget {{ alternate-background-color: {theme['panel_alt']}; }}"
            "QTableWidget::item { padding: 6px; }"
        )

    def set_mapping(self, values: dict[str, str], fields: list[str] | None = None) -> None:
        names = fields or list(values.keys())
        self.setRowCount(len(names))
        for row_index, field in enumerate(names):
            field_item = QTableWidgetItem(field)
            field_font = QFont()
            field_font.setBold(True)
            field_item.setFont(field_font)
            field_item.setForeground(QBrush(QColor(self.theme["field_text"])))
            field_item.setBackground(QBrush(QColor(self.theme["field_bg"])))
            self.setItem(row_index, 0, field_item)

            value_item = QTableWidgetItem(values.get(field, ""))
            value_item.setForeground(QBrush(QColor(self.theme["text"])))
            value_item.setBackground(QBrush(QColor(self.theme["panel"])))
            self.setItem(row_index, 1, value_item)
        self.resizeRowsToContents()


class GraderWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AgriGuide Fertilizer Grader")
        self.resize(1300, 820)
        self.theme_name = "light"

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
        top.setHorizontalSpacing(10)
        top.setVerticalSpacing(10)
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
        load_button.setObjectName("loadButton")
        load_button.clicked.connect(self.load_session)
        top.addWidget(load_button, 3, 3, 1, 2)
        self.theme_button = QPushButton("Dark Theme")
        self.theme_button.setCheckable(True)
        self.theme_button.clicked.connect(self.toggle_theme)
        top.addWidget(QLabel("Theme"), 3, 0)
        top.addWidget(self.theme_button, 3, 1)
        layout.addLayout(top)

        splitter = QSplitter(Qt.Orientation.Horizontal)
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
        self.progress_label.setObjectName("progressLabel")
        layout.addWidget(self.progress_label)

        self.grading_box = QGroupBox("Grade")
        self.grading_box.setMinimumHeight(250)
        self.grading_layout = QVBoxLayout(self.grading_box)
        self.grading_layout.setSpacing(14)
        self.prompt_label = QLabel("")
        self.prompt_label.setObjectName("promptLabel")
        self.prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt_label.setWordWrap(True)
        self.button_row = QHBoxLayout()
        self.button_row.setSpacing(14)
        self.review_table = KeyValueTable()
        self.review_table.hide()
        self.confirm_row = QHBoxLayout()
        self.confirm_row.setSpacing(10)
        self.grading_layout.addWidget(self.prompt_label)
        self.grading_layout.addLayout(self.button_row)
        self.grading_layout.addWidget(self.review_table)
        self.grading_layout.addLayout(self.confirm_row)
        layout.addWidget(self.grading_box)
        self.load_gui_state()
        self.apply_theme(self.theme_name)

    def wrap(self, title: str, widget: QWidget) -> QGroupBox:
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 14, 10, 10)
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

    def load_gui_state(self) -> None:
        state = read_gui_state()
        self.grader_input.setText(safe_name(state.get("grader", "")) if state.get("grader") else "")
        self.output_input.setText(state.get("output_dir", str(DEFAULT_OUTPUT_DIR)))
        self.model_input.setText(state.get("model_csv", ""))
        self.reference_input.setText(state.get("reference_csv", ""))
        stored_theme = state.get("theme", "light")
        self.theme_name = stored_theme if stored_theme in THEMES else "light"

        width = state.get("window_width", "")
        height = state.get("window_height", "")
        x_position = state.get("window_x", "")
        y_position = state.get("window_y", "")
        if width.isdigit() and height.isdigit():
            self.resize(int(width), int(height))
        if x_position.lstrip("-").isdigit() and y_position.lstrip("-").isdigit():
            self.move(int(x_position), int(y_position))

    def save_gui_state(self) -> None:
        write_gui_state(
            {
                "grader": safe_name(self.grader_input.text()) if self.grader_input.text().strip() else "",
                "output_dir": self.output_input.text(),
                "model_csv": self.model_input.text(),
                "reference_csv": self.reference_input.text(),
                "window_width": str(self.width()),
                "window_height": str(self.height()),
                "window_x": str(self.x()),
                "window_y": str(self.y()),
                "theme": self.theme_name,
            }
        )

    def apply_theme(self, theme_name: str) -> None:
        self.theme_name = theme_name if theme_name in THEMES else "light"
        theme = THEMES[self.theme_name]
        self.setStyleSheet(build_stylesheet(theme))
        self.theme_button.setChecked(self.theme_name == "dark")
        self.theme_button.setText("Light Theme" if self.theme_name == "dark" else "Dark Theme")
        self.model_table.apply_theme(theme)
        self.reference_table.apply_theme(theme)
        self.review_table.apply_theme(theme)
        self.refresh_reasoning_view()

    def toggle_theme(self) -> None:
        self.apply_theme("dark" if self.theme_name == "light" else "light")
        self.save_gui_state()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.grader_input.setText(safe_name(self.grader_input.text()) if self.grader_input.text().strip() else "")
        self.save_gui_state()
        super().closeEvent(event)

    def load_session(self) -> None:
        try:
            grader = safe_name(self.grader_input.text())
            if not self.grader_input.text().strip():
                raise ValueError("Enter a grader name before loading a session.")
            self.grader_input.setText(grader)
            self.save_gui_state()
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
                    if answer == QMessageBox.StandardButton.Yes:
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
        self.model_table.set_mapping(
            model_row,
            [field for field in model_row if field not in REASONING_FIELDS],
        )
        self.reference_table.set_mapping(reference_row)
        self.refresh_reasoning_view()
        self.progress_label.setText(
            f"Item {self.current_index + 1} of {len(self.model_rows)} "
            f"({model_row.get(SPLIT_NAME_COLUMN)} / {model_row.get(ITEM_ID_COLUMN)})"
        )
        self.show_rubric_prompt()

    def refresh_reasoning_view(self) -> None:
        if not self.model_rows or self.current_index >= len(self.model_rows):
            return

        model_row = self.model_rows[self.current_index]
        theme = THEMES[self.theme_name]
        sections = []
        for field in REASONING_FIELDS:
            if field not in model_row:
                continue
            title = html.escape(field.replace("_", " ").title())
            value = html.escape(model_row.get(field, "")).replace("\n", "<br>")
            sections.append(
                "<section>"
                f"<div class='reasoning-title'>{title}</div>"
                f"<div class='reasoning-body'>{value}</div>"
                "</section>"
            )

        self.reasoning_view.setHtml(
            f"""
            <html>
            <head>
            <style>
                body {{
                    background: {theme["panel"]};
                    color: {theme["text"]};
                    font-family: Segoe UI, Arial, sans-serif;
                    font-size: 17px;
                    line-height: 1.35;
                    margin: 0;
                }}
                section {{
                    margin: 0 0 18px 0;
                }}
                .reasoning-title {{
                    background: {theme["reasoning_heading_bg"]};
                    color: {theme["reasoning_heading_text"]};
                    border: 1px solid {theme["border"]};
                    border-radius: 6px;
                    font-size: 18px;
                    font-weight: 800;
                    padding: 8px 10px;
                    margin-bottom: 8px;
                }}
                .reasoning-body {{
                    padding: 2px 4px 0 4px;
                }}
            </style>
            </head>
            <body>{"".join(sections)}</body>
            </html>
            """
        )

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
        self.prompt_label.setText(f"<b>{title}</b>: choose a grade for <b>{column}</b>.")
        self.button_row.addStretch()
        for label, tooltip in ordered_grade_options(column, options):
            button = QPushButton(label)
            button.setProperty("role", "grade")
            button.setStyleSheet(grade_button_stylesheet(label))
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
        self.prompt_label.setText("<b>Review grades</b> before confirming this item.")
        self.review_table.set_mapping(self.current_grades, [rubric[0] for rubric in RUBRICS])
        self.review_table.show()

        self.confirm_row.addStretch()
        for index, (_column, title, _options) in enumerate(RUBRICS):
            button = QPushButton(f"Edit {title}")
            button.setProperty("role", "edit")
            button.clicked.connect(lambda _checked=False, rubric_index=index: self.edit_rubric(rubric_index))
            self.confirm_row.addWidget(button)

        confirm = QPushButton("Confirm and Save")
        confirm.setProperty("role", "confirm")
        confirm.clicked.connect(self.confirm_current_item)
        self.confirm_row.addWidget(confirm)
        self.confirm_row.addStretch()

    def edit_rubric(self, rubric_index: int) -> None:
        self.editing_existing_grade = True
        self.current_rubric_index = rubric_index
        self.show_rubric_prompt()

    def confirm_current_item(self) -> None:
        output_path = self.output_path
        if output_path is None:
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
        write_csv_rows(output_path, output_fields, self.completed_rows)
        self.current_index += 1
        self.show_current_item()


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 12))
    window = GraderWindow()
    window.show()
    sys.exit(app.exec())
