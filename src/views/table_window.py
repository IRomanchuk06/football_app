from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QTableView, QHeaderView


class TableDialog(QDialog):
    def __init__(self, players, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Table View")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()
        self.table_view = QTableView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Full Name", "Birth Date", "Team", "Home City", "Squad", "Position"])

        for player in players:
            row = [
                QStandardItem(player.full_name),
                QStandardItem(player.birth_date.isoformat()),
                QStandardItem(player.team),
                QStandardItem(player.home_city),
                QStandardItem(player.squad),
                QStandardItem(player.position)
            ]
            self.model.appendRow(row)

        self.table_view.setModel(self.model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table_view)
        self.setLayout(layout)

