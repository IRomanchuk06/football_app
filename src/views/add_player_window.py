from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog, QLineEdit, QFormLayout, QDateEdit, QDialogButtonBox, QMessageBox


class AddPlayerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Player")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.name_edit = QLineEdit()

        self.birth_date_edit = QDateEdit(calendarPopup=True)
        self.birth_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.birth_date_edit.setDateRange(
            QDate(1900, 1, 1),
            QDate.currentDate().addYears(-16)
        )

        self.birth_date_edit.setDate(QDate.currentDate().addYears(-20))

        self.team_edit = QLineEdit()
        self.home_city_edit = QLineEdit()
        self.squad_edit = QLineEdit()
        self.position_edit = QLineEdit()

        layout.addRow("Full Name:", self.name_edit)
        layout.addRow("Birth Date:", self.birth_date_edit)
        layout.addRow("Team:", self.team_edit)
        layout.addRow("Home City:", self.home_city_edit)
        layout.addRow("Squad:", self.squad_edit)
        layout.addRow("Position:", self.position_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def validate(self):
        errors = []

        if not self.name_edit.text().strip():
            errors.append("Full Name is required")

        if self.birth_date_edit.date() > QDate.currentDate():
            errors.append("Birth date cannot be in the future")

        if not self.team_edit.text().strip():
            errors.append("Team is required")

        if not self.home_city_edit.text().strip():
            errors.append("Home City is required")

        if not self.squad_edit.text().strip():
            errors.append("Squad is required")

        if not self.position_edit.text().strip():
            errors.append("Position is required")

        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        self.accept()

    def get_data(self) -> dict:
        return {
            "full_name": self.name_edit.text().strip(),
            "birth_date": self.birth_date_edit.date().toPyDate(),
            "team": self.team_edit.text().strip(),
            "home_city": self.home_city_edit.text().strip(),
            "squad": self.squad_edit.text().strip(),
            "position": self.position_edit.text().strip()
        }