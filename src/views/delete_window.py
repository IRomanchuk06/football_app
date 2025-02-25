from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDateEdit, QDialogButtonBox


class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Players")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.birth_date_edit = QDateEdit(calendarPopup=True)
        self.birth_date_edit.setDate(QDate.currentDate())
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

        self.birth_date_edit.setDate(QDate(2000, 1, 1))
        self.birth_date_edit.setSpecialValueText("Any")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_delete_params(self):
        return {
            "full_name": self.name_edit.text().strip() or None,
            "birth_date": self.birth_date_edit.date().toPyDate() if self.birth_date_edit.date() != QDate(2000, 1, 1) else None,
            "team": self.team_edit.text().strip() or None,
            "home_city": self.home_city_edit.text().strip() or None,
            "squad": self.squad_edit.text().strip() or None,
            "position": self.position_edit.text().strip() or None
        }