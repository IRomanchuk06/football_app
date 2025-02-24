from datetime import date
from typing import Optional, List, Tuple

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTreeView

from src.exceptions.exceptions import PlayerNotFoundError, DeletionFailedError
from src.models.player import Player
from src.repositories.database_repository import DatabaseRepository
from src.services.xml_handler import XMLHandler


class PlayerController(QObject):
    player_added = pyqtSignal(Player)
    search_results = pyqtSignal(list)
    deletion_results = pyqtSignal(int)
    players_updated = pyqtSignal()

    def __init__(self, db_path: str):
        super().__init__()
        self.db_repo = DatabaseRepository(db_path)

    def add_player(self, full_name: str, birth_date: date, team: str, home_city: str, squad: str, position: str):
        if not full_name:
            raise ValueError("Full name cannot be empty")
        if birth_date > date.today():
            raise ValueError("Birth date cannot be in the future")

        player = Player(
            full_name=full_name,
            birth_date=birth_date,
            team=team,
            home_city=home_city,
            squad=squad,
            position=position
        )
        self.db_repo.add_player(player)
        self.player_added.emit(player)

    def search_players(self, full_name: Optional[str] = None, birth_date: Optional[date] = None,
                       team: Optional[str] = None, home_city: Optional[str] = None,
                       squad: Optional[str] = None, position: Optional[str] = None) -> List[Player]:
        players = self.db_repo.find_players(full_name=full_name, birth_date=birth_date, team=team,
                                            home_city=home_city, squad=squad, position=position)
        if not players:
            raise PlayerNotFoundError("No players found with the given criteria.")
        self.search_results.emit(players)
        return players

    def delete_players(self, full_name: Optional[str] = None, birth_date: Optional[date] = None,
                       team: Optional[str] = None, home_city: Optional[str] = None,
                       squad: Optional[str] = None, position: Optional[str] = None) -> int:
        deleted_count = self.db_repo.delete_players(full_name=full_name, birth_date=birth_date, team=team,
                                                    home_city=home_city, squad=squad, position=position)
        if deleted_count == 0:
            raise DeletionFailedError("No players found for deletion with the given criteria.")
        self.deletion_results.emit(deleted_count)
        return deleted_count

    def get_all_players(self) -> List[Player]:
        players = self.db_repo.get_players()
        self.players_updated.emit()
        return players

    def format_player_for_display(self, player: Player) -> str:
        return f"{player.full_name} | {player.birth_date} | {player.team} | {player.home_city} | {player.squad} | {player.position}"

    def display_all_players(self) -> List[str]:
        players = self.get_all_players()
        return [self.format_player_for_display(player) for player in players]

    def display_search_results(self, search_conditions: dict) -> List[str]:
        try:
            players = self.search_players(**search_conditions)
            return [self.format_player_for_display(player) for player in players]
        except PlayerNotFoundError as e:
            return [str(e)]

    def display_deleted_count(self, delete_conditions: dict) -> int:
        try:
            deleted_count = self.delete_players(**delete_conditions)
            return deleted_count
        except DeletionFailedError as e:
            return 0

    def convert_players_to_tree(self, players: List[Player]) -> QStandardItemModel:
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Full Name", "Birth Date", "Team", "Home City", "Squad", "Position"])

        for player in players:
            row = [
                QStandardItem(player.full_name),
                QStandardItem(str(player.birth_date)),
                QStandardItem(player.team),
                QStandardItem(player.home_city),
                QStandardItem(player.squad),
                QStandardItem(player.position)
            ]
            model.appendRow(row)

        return model

    def display_players_in_tree(self, tree_view: QTreeView):
        players = self.get_all_players()
        model = self.convert_players_to_tree(players)
        tree_view.setModel(model)

    def get_paginated_players(self, offset: int, limit: int) -> Tuple[List[Player], int]:
        players = self.db_repo.get_paginated_players(offset, limit)
        total = self.db_repo.count_players()
        self.players_updated.emit()
        return players, total

    def import_from_xml(self, file_path: str) -> None:
        try:
            xml_handler = XMLHandler(self.db_repo)
            xml_handler.import_from_xml(file_path)
            self.players_updated.emit()
        except Exception as e:
            raise RuntimeError(f"XML import failed: {str(e)}")

    def export_to_xml(self, file_path: str, players: Optional[List[Player]] = None) -> None:
        try:
            xml_handler = XMLHandler(self.db_repo)
            if players is None:
                players = self.get_all_players()
            xml_handler.export_to_xml(file_path, players)
        except Exception as e:
            raise RuntimeError(f"XML export failed: {str(e)}")

    def get_player_by_name(self, name: str) -> Optional[Player]:
        players = self.db_repo.find_players(full_name=name)
        return players[0] if players else None

    def count_players(self) -> int:
        return self.db_repo.count_players()

    def update_player(self, original_player: Player, new_data: dict) -> None:
        try:
            self.db_repo.update_player(original_player, new_data)
            self.players_updated.emit()
        except Exception as e:
            raise RuntimeError(f"Update failed: {str(e)}")

    def clear_database(self) -> None:
        self.db_repo.delete_all_players()
        self.players_updated.emit()
