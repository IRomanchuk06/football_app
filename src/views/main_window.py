from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QTreeView,
    QFileDialog, QDialog, QHeaderView, QLabel, QHBoxLayout, QComboBox, QSpinBox,
)
from src.controllers.player_controller import PlayerController
from src.exceptions.exceptions import PlayerNotFoundError
from src.views.add_player_window import AddPlayerDialog
from src.views.delete_window import DeleteDialog
from src.views.search_window import SearchDialog
from src.views.table_window import TableDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.page_size = 10
        self.controller = PlayerController(db_path=":memory:")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Football Manager")
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        control_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.search_btn = QPushButton("Search")
        self.delete_btn = QPushButton("Delete")
        self.table_view_btn = QPushButton("Table View")
        control_layout.addWidget(self.add_btn)
        control_layout.addWidget(self.search_btn)
        control_layout.addWidget(self.delete_btn)
        control_layout.addWidget(self.table_view_btn)

        io_layout = QHBoxLayout()
        self.import_btn = QPushButton("Import XML")
        self.export_btn = QPushButton("Export XML")
        self.export_selected_btn = QPushButton("Export Selected")
        io_layout.addWidget(self.import_btn)
        io_layout.addWidget(self.export_btn)
        io_layout.addWidget(self.export_selected_btn)

        pagination_layout = QHBoxLayout()
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10", "25", "50"])
        self.stats_label = QLabel()
        pagination_layout.addWidget(QLabel("Page:"))
        pagination_layout.addWidget(self.page_spin)
        pagination_layout.addWidget(QLabel("Items:"))
        pagination_layout.addWidget(self.page_size_combo)
        pagination_layout.addWidget(self.stats_label)

        self.tree_view = QTreeView()
        self.tree_view.setSelectionMode(QTreeView.ExtendedSelection)
        self.tree_view.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        main_layout.addLayout(control_layout)
        main_layout.addLayout(io_layout)
        main_layout.addLayout(pagination_layout)
        main_layout.addWidget(self.tree_view)
        central_widget.setLayout(main_layout)

        self.add_btn.clicked.connect(self.show_add_dialog)
        self.search_btn.clicked.connect(self.show_search_dialog)
        self.delete_btn.clicked.connect(self.show_delete_dialog)
        self.table_view_btn.clicked.connect(self.show_table_view)
        self.import_btn.clicked.connect(self.import_xml)
        self.export_btn.clicked.connect(self.export_xml)
        self.export_selected_btn.clicked.connect(self.export_selected)
        self.page_spin.valueChanged.connect(self.page_changed)
        self.page_size_combo.currentTextChanged.connect(self.page_size_changed)

        self.update_display()

    def update_display(self):
        offset = (self.current_page - 1) * self.page_size
        players, total = self.controller.get_paginated_players(offset, self.page_size)

        current_count = len(players)
        total_pages = max(1, (total + self.page_size - 1) // self.page_size) if total > 0 else 0

        if total_pages == 0:
            self.current_page = 0
            self.page_spin.setRange(0, 0)
            page_info = "0/0"
            items_info = "0/0"
        else:
            if self.current_page > total_pages:
                self.current_page = total_pages
            self.page_spin.setRange(1, total_pages)
            page_info = f"{self.current_page}/{total_pages}"
            items_info = f"{current_count}/{total}" if total > 0 else "0/0"

        self.page_spin.setValue(self.current_page if total_pages > 0 else 0)
        self.stats_label.setText(
            f"Total: {total} | Page: {page_info} | Items: {items_info}"
        )

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Player", "Details"])
        for p in players:
            parent = QStandardItem(p.full_name)
            parent.appendRow([QStandardItem("Birth Date"), QStandardItem(p.birth_date.isoformat())])
            parent.appendRow([QStandardItem("Team"), QStandardItem(p.team)])
            parent.appendRow([QStandardItem("Home City"), QStandardItem(p.home_city)])
            parent.appendRow([QStandardItem("Squad"), QStandardItem(p.squad)])
            parent.appendRow([QStandardItem("Position"), QStandardItem(p.position)])
            model.appendRow(parent)
        self.tree_view.setModel(model)
        self.tree_view.expandAll()

    def show_add_dialog(self):
        dialog = AddPlayerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.controller.add_player(
                    dialog.name_edit.text(),
                    dialog.birth_date_edit.date().toPyDate(),
                    dialog.team_edit.text(),
                    dialog.home_city_edit.text(),
                    dialog.squad_edit.text(),
                    dialog.position_edit.text()
                )
                self.update_display()
                QMessageBox.information(self, "Success", "Player added")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def show_search_dialog(self):
        dialog = SearchDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                search_params = dialog.get_search_params()
                results = self.controller.search_players(**search_params)
                self.show_results(results)
            except PlayerNotFoundError as e:
                QMessageBox.information(self, "No results", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def show_delete_dialog(self):
        dialog = DeleteDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                delete_params = dialog.get_delete_params()
                count = self.controller.delete_players(**delete_params)
                self.update_display()
                QMessageBox.information(self, "Deleted", f"Removed {count} players")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def import_xml(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import XML", "", "XML Files (*.xml)")
        if path:
            try:
                self.controller.import_from_xml(path)
                self.update_display()
                QMessageBox.information(self, "Imported", "Data loaded successfully")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", str(e))

    def export_xml(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export XML", "", "XML Files (*.xml)")
        if path:
            try:
                self.controller.export_to_xml(path)
                QMessageBox.information(self, "Exported", "Data saved successfully")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def export_selected(self):
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            QMessageBox.warning(self, "Error", "No selection")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export Selected", "", "XML Files (*.xml)")
        if path:
            try:
                players = [self.controller.get_player_by_name(i.data()) for i in indexes if i.column() == 0]
                self.controller.export_to_xml(path, players)
                QMessageBox.information(self, "Exported", "Selection saved")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def page_changed(self):
        self.current_page = self.page_spin.value()
        self.update_display()

    def page_size_changed(self):
        self.page_size = int(self.page_size_combo.currentText())
        self.current_page = 1
        self.update_display()

    def show_results(self, players):
        dialog = QDialog(self)
        dialog.setWindowTitle("Search Results")
        dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout()
        tree = QTreeView()
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Player", "Details"])

        for player in players:
            player_item = QStandardItem(player.full_name)

            team_item = [QStandardItem("Team"), QStandardItem(player.team)]
            birth_date_item = [QStandardItem("Birth Date"), QStandardItem(str(player.birth_date))]
            home_city_item = [QStandardItem("Home City"), QStandardItem(player.home_city)]
            squad_item = [QStandardItem("Squad"), QStandardItem(player.squad)]
            position_item = [QStandardItem("Position"), QStandardItem(player.position)]

            player_item.appendRow(team_item)
            player_item.appendRow(birth_date_item)
            player_item.appendRow(home_city_item)
            player_item.appendRow(squad_item)
            player_item.appendRow(position_item)

            model.appendRow(player_item)

        tree.setModel(model)
        tree.expandAll()
        tree.setHeaderHidden(False)
        tree.setAlternatingRowColors(True)

        layout.addWidget(tree)
        dialog.setLayout(layout)
        dialog.exec_()

    def show_table_view(self):
        offset = (self.current_page - 1) * self.page_size
        players, _ = self.controller.get_paginated_players(offset, self.page_size)
        dialog = TableDialog(players, self)
        dialog.exec_()
