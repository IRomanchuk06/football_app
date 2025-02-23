from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QTreeView,
    QFileDialog,
)
from datetime import date
from src.controllers.player_controller import PlayerController
from src.exceptions.exceptions import PlayerNotFoundError
from src.services.xml_handler import XMLHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Football App")
        self.setGeometry(100, 100, 800, 600)

        self.controller = PlayerController(db_path=":memory:")
        self.xml_handler = XMLHandler(self.controller.db_repo)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        layout.addWidget(self.name_input)

        self.birth_date_input = QLineEdit()
        self.birth_date_input.setPlaceholderText("Birth Date (YYYY-MM-DD)")
        layout.addWidget(self.birth_date_input)

        self.team_input = QLineEdit()
        self.team_input.setPlaceholderText("Team")
        layout.addWidget(self.team_input)

        self.home_city_input = QLineEdit()
        self.home_city_input.setPlaceholderText("Home City")
        layout.addWidget(self.home_city_input)

        self.squad_input = QLineEdit()
        self.squad_input.setPlaceholderText("Squad")
        layout.addWidget(self.squad_input)

        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Position")
        layout.addWidget(self.position_input)

        self.add_button = QPushButton("Add Player")
        self.add_button.clicked.connect(self.on_add_player_clicked)
        layout.addWidget(self.add_button)

        self.search_button = QPushButton("Search Players")
        self.search_button.clicked.connect(self.on_search_players_clicked)
        layout.addWidget(self.search_button)

        self.import_db_button = QPushButton("Load DB from XML")
        self.import_db_button.clicked.connect(self.on_import_db_clicked)
        layout.addWidget(self.import_db_button)

        self.import_players_button = QPushButton("Add Players from XML")
        self.import_players_button.clicked.connect(self.on_import_players_clicked)
        layout.addWidget(self.import_players_button)

        self.export_db_button = QPushButton("Export DB to XML")
        self.export_db_button.clicked.connect(self.on_export_db_clicked)
        layout.addWidget(self.export_db_button)

        self.export_selected_button = QPushButton("Export Selected Players to XML")
        self.export_selected_button.clicked.connect(self.on_export_selected_clicked)
        layout.addWidget(self.export_selected_button)

        self.tree_view = QTreeView()
        self.tree_view.setSelectionMode(QTreeView.MultiSelection)
        layout.addWidget(self.tree_view)

        central_widget.setLayout(layout)

        self.update_player_list()

    def on_add_player_clicked(self):
        try:
            full_name = self.name_input.text().strip()
            birth_date_str = self.birth_date_input.text().strip()
            team = self.team_input.text().strip()
            home_city = self.home_city_input.text().strip()
            squad = self.squad_input.text().strip()
            position = self.position_input.text().strip()

            if not full_name:
                raise ValueError("Full Name cannot be empty.")
            if not birth_date_str:
                raise ValueError("Birth Date cannot be empty.")
            if not team:
                raise ValueError("Team cannot be empty.")
            if not home_city:
                raise ValueError("Home City cannot be empty.")
            if not squad:
                raise ValueError("Squad cannot be empty.")
            if not position:
                raise ValueError("Position cannot be empty.")

            birth_date = date.fromisoformat(birth_date_str)

            self.controller.add_player(full_name, birth_date, team, home_city, squad, position)

            self.name_input.clear()
            self.birth_date_input.clear()
            self.team_input.clear()
            self.home_city_input.clear()
            self.squad_input.clear()
            self.position_input.clear()

            self.update_player_list()

            QMessageBox.information(self, "Success", "Player added successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def on_search_players_clicked(self):
        try:
            search_conditions = {
                "full_name": self.name_input.text().strip() or None,
                "birth_date": date.fromisoformat(self.birth_date_input.text().strip()) if self.birth_date_input.text().strip() else None,
                "team": self.team_input.text().strip() or None,
                "home_city": self.home_city_input.text().strip() or None,
                "squad": self.squad_input.text().strip() or None,
                "position": self.position_input.text().strip() or None,
            }

            players = self.controller.search_players(**search_conditions)

            model = self.controller.convert_players_to_tree(players)
            self.tree_view.setModel(model)

            QMessageBox.information(self, "Search Results", f"Found {len(players)} players.")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid date format. Use YYYY-MM-DD.")
        except PlayerNotFoundError as e:
            QMessageBox.warning(self, "Search Results", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def on_import_db_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load DB from XML", "", "XML Files (*.xml)")
        if file_path:
            self.xml_handler.import_from_xml(file_path)
            self.update_player_list()
            QMessageBox.information(self, "Success", "Database loaded from XML successfully!")

    def on_import_players_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Add Players from XML", "", "XML Files (*.xml)")
        if file_path:
            self.xml_handler.import_from_xml(file_path)
            self.update_player_list()
            QMessageBox.information(self, "Success", "Players added from XML successfully!")

    def on_export_db_clicked(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export DB to XML", "", "XML Files (*.xml)")
        if file_path:
            self.xml_handler.export_to_xml(file_path)
            QMessageBox.information(self, "Success", f"Database exported to XML: {file_path}")

    def on_export_selected_clicked(self):
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Error", "No players selected.")
            return

        selected_players = []
        for index in selected_indexes:
            if index.column() == 0:
                player_name = index.data()
                player = next((p for p in self.controller.get_all_players() if p.full_name == player_name), None)
                if player:
                    selected_players.append(player)

        if not selected_players:
            QMessageBox.warning(self, "Error", "No valid players selected.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Export Selected Players to XML", "", "XML Files (*.xml)")
        if file_path:
            self.xml_handler.export_to_xml(file_path, selected_players)
            QMessageBox.information(self, "Success", f"Selected players exported to XML: {file_path}")

    def update_player_list(self):
        players = self.controller.get_all_players()
        model = self.controller.convert_players_to_tree(players)
        self.tree_view.setModel(model)