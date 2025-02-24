from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox


class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Players")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        self.condition_edit = QLineEdit()
        self.condition_edit.setPlaceholderText("SQL condition (e.g., team='Team A')")
        layout.addRow("Delete Condition:", self.condition_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)