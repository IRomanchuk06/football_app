import os
import sqlite3

import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QApplication, QTreeView
from pytestqt import qtbot

from src.controllers.player_controller import PlayerController
from src.models.player import Player
from src.exceptions.exceptions import PlayerNotFoundError, DeletionFailedError
import xml.etree.ElementTree as ET

@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
    app.quit()


@pytest.fixture
def controller(qapp, qtbot):
    controller = PlayerController(db_path=":memory:")
    mock_repo = MagicMock()
    controller.db_repo = mock_repo
    return controller, mock_repo


def test_search_players_found(controller):
    controller, mock_repo = controller
    test_player = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 25),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )
    mock_repo.find_players.return_value = [test_player]

    result = controller.search_players(full_name="John Doe")

    assert len(result) == 1
    assert result[0].full_name == "John Doe"
    mock_repo.find_players.assert_called_once_with(
        full_name="John Doe",
        birth_date=None,
        team=None,
        home_city=None,
        squad=None,
        position=None
    )


def test_search_players_not_found(controller):
    controller, mock_repo = controller
    mock_repo.find_players.return_value = []

    with pytest.raises(PlayerNotFoundError):
        controller.search_players(full_name="Unknown Player")

    mock_repo.find_players.assert_called_once_with(
        full_name="Unknown Player",
        birth_date=None,
        team=None,
        home_city=None,
        squad=None,
        position=None
    )


def test_delete_players_found(controller):
    controller, mock_repo = controller
    mock_repo.delete_players.return_value = 2

    result = controller.delete_players(team="Team A")

    assert result == 2
    mock_repo.delete_players.assert_called_once_with(
        full_name=None,
        birth_date=None,
        team="Team A",
        home_city=None,
        squad=None,
        position=None
    )


def test_delete_players_not_found(controller):
    controller, mock_repo = controller
    mock_repo.delete_players.return_value = 0

    with pytest.raises(DeletionFailedError):
        controller.delete_players(position="Goalkeeper")

    mock_repo.delete_players.assert_called_once_with(
        full_name=None,
        birth_date=None,
        team=None,
        home_city=None,
        squad=None,
        position="Goalkeeper"
    )


def test_get_all_players(controller):
    controller, mock_repo = controller
    player1 = Player(full_name="John Doe", birth_date=date(1990, 5, 25),
                     team="Team A", home_city="City X", squad="Squad 1", position="Forward")
    player2 = Player(full_name="Jane Smith", birth_date=date(1992, 7, 12),
                     team="Team B", home_city="City Y", squad="Squad 2", position="Midfielder")

    mock_repo.get_players = MagicMock(return_value=[player1, player2])

    result = controller.get_all_players()
    assert len(result) == 2
    assert result[0].full_name == "John Doe"
    assert result[1].full_name == "Jane Smith"


def test_display_all_players(controller):
    controller, mock_repo = controller
    test_player = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 25),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )
    mock_repo.get_players.return_value = [test_player]

    result = controller.display_all_players()
    assert result == ["John Doe | 1990-05-25 | Team A | City X | Squad 1 | Forward"]


def test_convert_players_to_tree(controller):
    controller, _ = controller
    test_player = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 25),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )

    model = controller.convert_players_to_tree([test_player])
    assert isinstance(model, QStandardItemModel)
    assert model.rowCount() == 1
    assert model.columnCount() == 6
    assert model.item(0, 0).text() == "John Doe"
    assert model.item(0, 1).text() == "1990-05-25"
    assert model.item(0, 2).text() == "Team A"


def test_display_players_in_tree(controller, qtbot):
    controller, mock_repo = controller
    tree_view = QTreeView()
    qtbot.add_widget(tree_view)

    test_player = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 25),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )
    mock_repo.get_players.return_value = [test_player]

    controller.display_players_in_tree(tree_view)
    assert isinstance(tree_view.model(), QStandardItemModel)
    assert tree_view.model().rowCount() == 1
    assert tree_view.model().item(0, 0).text() == "John Doe"


def test_display_search_results(controller):
    controller, mock_repo = controller
    test_player = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 25),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )
    mock_repo.find_players.return_value = [test_player]

    result = controller.display_search_results({"full_name": "John Doe"})
    assert result == ["John Doe | 1990-05-25 | Team A | City X | Squad 1 | Forward"]


def test_display_deleted_count(controller):
    controller, mock_repo = controller
    mock_repo.delete_players.return_value = 3

    result = controller.display_deleted_count({"position": "Forward"})
    assert result == 3


def test_get_paginated_players(controller):
    controller, mock_repo = controller

    test_players = [
        Player(
            full_name="Player1",
            birth_date=date(2000, 1, 1),
            team="Team A",
            home_city="City A",
            squad="Squad 1",
            position="Forward"
        ),
        Player(
            full_name="Player2",
            birth_date=date(2001, 2, 2),
            team="Team B",
            home_city="City B",
            squad="Squad 2",
            position="Midfielder"
        )
    ]

    mock_repo.get_paginated_players.return_value = test_players
    mock_repo.count_players.return_value = 2

    players, total = controller.get_paginated_players(10, 0)

    assert len(players) == 2
    assert total == 2
    mock_repo.get_paginated_players.assert_called_once_with(10, 0)
    mock_repo.count_players.assert_called_once()


def test_import_from_xml_success(controller, qtbot):
    controller_obj, mock_repo = controller
    mock_handler = MagicMock()

    with patch('src.controllers.player_controller.XMLHandler', return_value=mock_handler):
        with qtbot.wait_signal(controller_obj.players_updated, timeout=1000):
            controller_obj.import_from_xml("test.xml")

    mock_handler.import_from_xml.assert_called_once_with("test.xml")

def test_import_from_xml_failure(controller):
    controller, mock_repo = controller
    mock_signal = MagicMock()
    controller.players_updated = mock_signal

    mock_xml_handler = MagicMock()
    mock_xml_handler.import_from_xml.side_effect = FileNotFoundError("File not found")

    with patch('src.controllers.player_controller.XMLHandler', return_value=mock_xml_handler):
        with pytest.raises(RuntimeError) as exc_info:
            controller.import_from_xml("invalid.xml")

        assert "File not found" in str(exc_info.value)
        mock_signal.emit.assert_not_called()

    mock_xml_handler.import_from_xml.side_effect = RuntimeError("Import failed")

    with patch('src.controllers.player_controller.XMLHandler', return_value=mock_xml_handler):
        with pytest.raises(RuntimeError) as exc_info:
            controller.import_from_xml("invalid.xml")

        assert "Import failed" in str(exc_info.value)
        mock_signal.emit.assert_not_called()

def test_export_to_xml_default(controller):
    controller, mock_repo = controller
    test_players = [
        Player(
            full_name="Test",
            birth_date=date.today(),
            team="Team A",
            home_city="City A",
            squad="Squad 1",
            position="Forward"
        )
    ]
    mock_repo.get_players.return_value = test_players

    file_path = "export.xml"
    controller.export_to_xml(file_path)

    mock_repo.get_players.assert_called_once()
    if os.path.exists(file_path):
        os.remove(file_path)


def test_export_to_xml_custom_players(controller):
    controller, mock_repo = controller
    test_players = [
        Player(
            full_name="Test",
            birth_date=date.today(),
            team="Team A",
            home_city="City A",
            squad="Squad 1",
            position="Forward"
        )
    ]

    file_path = "export.xml"
    controller.export_to_xml(file_path, test_players)

    mock_repo.get_players.assert_not_called()
    if os.path.exists(file_path):
        os.remove(file_path)


def test_export_to_xml_error_handling(controller):
    controller_obj, mock_repo = controller
    mock_handler = MagicMock()

    mock_handler.export_to_xml.side_effect = IOError("File not found")

    with patch('src.controllers.player_controller.XMLHandler', return_value=mock_handler):
        with pytest.raises(RuntimeError) as exc_info:
            controller_obj.export_to_xml("invalid_path.xml")

    assert "Export failed: File not found" in str(exc_info.value)

    mock_handler.export_to_xml.side_effect = ET.ParseError("XML parsing error")

    with patch('src.controllers.player_controller.XMLHandler', return_value=mock_handler):
        with pytest.raises(RuntimeError) as exc_info:
            controller_obj.export_to_xml("invalid_xml.xml")

    assert "Export failed: XML parsing error" in str(exc_info.value)

def test_get_player_by_name_found(controller):
    controller, mock_repo = controller
    test_player = Player(
        full_name="John Doe",
        birth_date=date(1990, 1, 1),
        team="Team A",
        home_city="City A",
        squad="Squad 1",
        position="Forward"
    )
    mock_repo.find_players.return_value = [test_player]

    result = controller.get_player_by_name("John Doe")

    assert result == test_player


def test_update_player_success(controller):
    controller, mock_repo = controller
    mock_signal = MagicMock()
    controller.players_updated = mock_signal

    original = Player(
        full_name="Old",
        birth_date=date(2000, 1, 1),
        team="Team A",
        home_city="City A",
        squad="Squad 1",
        position="Forward"
    )
    new_data = {"full_name": "New"}

    controller.update_player(original, new_data)

    mock_repo.update_player.assert_called_once_with(original, new_data)
    mock_signal.emit.assert_called_once()


def test_clear_database(controller):
    controller, mock_repo = controller
    mock_signal = MagicMock()
    controller.players_updated = mock_signal

    controller.clear_database()

    mock_repo.delete_all_players.assert_called_once()
    mock_signal.emit.assert_called_once()


def test_add_player_success(controller):
    controller_obj, mock_repo = controller
    test_data = {
        "full_name": "Lionel Messi",
        "birth_date": date(1987, 6, 24),
        "team": "PSG",
        "home_city": "Rosario",
        "squad": "First Team",
        "position": "Forward"
    }

    mock_signal = MagicMock()
    controller_obj.player_added = mock_signal

    controller_obj.add_player(**test_data)

    mock_repo.add_player.assert_called_once()
    added_player = mock_repo.add_player.call_args[0][0]
    assert isinstance(added_player, Player)
    assert added_player.full_name == test_data["full_name"]
    assert added_player.birth_date == test_data["birth_date"]
    mock_signal.emit.assert_called_once_with(added_player)


def test_add_player_with_invalid_data(controller):
    controller_obj, mock_repo = controller
    invalid_data = {
        "full_name": "",
        "birth_date": date(2025, 1, 1),
        "team": "",
        "home_city": "",
        "squad": "",
        "position": ""
    }

    with pytest.raises(ValueError):
        controller_obj.add_player(**invalid_data)

    mock_repo.add_player.assert_not_called()


def test_add_player_future_birth_date(controller):
    controller_obj, mock_repo = controller
    future_date = date.today().replace(year=date.today().year + 1)
    test_data = {
        "full_name": "Test",
        "birth_date": future_date,
        "team": "Team",
        "home_city": "City",
        "squad": "Squad",
        "position": "Position"
    }

    with pytest.raises(ValueError) as exc_info:
        controller_obj.add_player(**test_data)

    assert "Birth date cannot be in the future" in str(exc_info.value)
    mock_repo.add_player.assert_not_called()


def test_add_player_database_error(controller):
    controller_obj, mock_repo = controller
    test_data = {
        "full_name": "Test",
        "birth_date": date(2000, 1, 1),
        "team": "Team",
        "home_city": "City",
        "squad": "Squad",
        "position": "Position"
    }
    mock_repo.add_player.side_effect = sqlite3.Error("DB error")

    with pytest.raises(RuntimeError) as exc_info:
        controller_obj.add_player(**test_data)

    assert "Database error" in str(exc_info.value)


def test_get_all_players_database_error(controller):
    controller_obj, mock_repo = controller
    mock_repo.get_players.side_effect = sqlite3.Error("DB error")

    with pytest.raises(RuntimeError) as exc_info:
        controller_obj.get_all_players()

    assert "Database error" in str(exc_info.value)


def test_display_all_players_error(controller):
    controller_obj, mock_repo = controller
    mock_repo.get_players.side_effect = RuntimeError("Test error")

    result = controller_obj.display_all_players()

    assert result == ["Test error"]


def test_display_search_results_error(controller):
    controller_obj, mock_repo = controller
    mock_repo.find_players.side_effect = RuntimeError("Test error")

    result = controller_obj.display_search_results({"full_name": "Test"})

    assert result == ["Test error"]


def test_display_search_results_player_not_found(controller):
    controller_obj, mock_repo = controller
    mock_repo.find_players.side_effect = PlayerNotFoundError("No players found")

    result = controller_obj.display_search_results({"full_name": "Unknown"})

    assert result == ["No players found"]


def test_display_deleted_count_error(controller):
    controller_obj, mock_repo = controller
    mock_repo.delete_players.side_effect = RuntimeError("Test error")

    result = controller_obj.display_deleted_count({"position": "Forward"})

    assert result == 0


def test_display_deleted_count_deletion_failed(controller):
    controller_obj, mock_repo = controller
    mock_repo.delete_players.side_effect = DeletionFailedError("No players deleted")

    result = controller_obj.display_deleted_count({"position": "Goalkeeper"})

    assert result == 0


def test_search_players_database_error(controller):
    controller_obj, mock_repo = controller
    mock_repo.find_players.side_effect = sqlite3.Error("DB error")

    with pytest.raises(RuntimeError) as exc_info:
        controller_obj.search_players(full_name="Test")

    assert "Database error" in str(exc_info.value)
    mock_repo.find_players.assert_called_once()


def test_format_player_for_display(controller):
    controller, mock_repo = controller
    player = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 15),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )
    result = controller.format_player_for_display(player)
    assert result == "John Doe | 1990-05-15 | Team A | City X | Squad 1 | Forward"


def test_display_deleted_count_success(controller):
    controller, mock_repo = controller
    mock_repo.delete_players.return_value = 3
    result = controller.display_deleted_count({"full_name": "John"})
    assert result == 3
    mock_repo.delete_players.assert_called_once_with(full_name="John", birth_date=None,
                                                     team=None, home_city=None,
                                                     squad=None, position=None)


def test_display_deleted_count_failure(controller):
    controller, mock_repo = controller
    mock_repo.delete_players.side_effect = DeletionFailedError("Test error")
    result = controller.display_deleted_count({})
    assert result == 0


def test_display_players_in_tree_error(controller, qtbot):
    controller, mock_repo = controller
    mock_repo.get_players.side_effect = sqlite3.Error("DB error")

    from PyQt5.QtWidgets import QTreeView
    tree_view = QTreeView()
    qtbot.addWidget(tree_view)

    controller.display_players_in_tree(tree_view)

    model = tree_view.model()
    assert isinstance(model, QStandardItemModel)
    assert model.item(0, 0).text() == "Database error: DB error"

import os

def test_export_to_xml(controller):
    controller, mock_repo = controller
    mock_handler = MagicMock()
    XMLHandler = MagicMock(return_value=mock_handler)
    test_players = [MagicMock(spec=Player), MagicMock(spec=Player)]

    file_path = "export.xml"

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("src.controllers.player_controller.XMLHandler", XMLHandler)
        controller.export_to_xml(file_path, test_players)

    mock_handler.export_to_xml.assert_called_once_with(file_path, test_players)

    if os.path.exists(file_path):
        os.remove(file_path)



def test_get_player_by_name(controller):
    controller, mock_repo = controller
    mock_player = MagicMock(spec=Player)
    mock_repo.find_players.return_value = [mock_player]

    result = controller.get_player_by_name("John Doe")

    assert result == mock_player
    mock_repo.find_players.assert_called_once_with(full_name="John Doe")


def test_count_players(controller):
    controller, mock_repo = controller
    mock_repo.count_players.return_value = 42
    assert controller.count_players() == 42


def test_update_player(controller, qtbot):
    controller, mock_repo = controller
    original = MagicMock(spec=Player)
    new_data = {"team": "New Team"}

    with qtbot.wait_signal(controller.players_updated, timeout=1000):
        controller.update_player(original, new_data)

    mock_repo.update_player.assert_called_once_with(original, new_data)


def test_delete_players_database_error(controller):
    controller_obj, mock_repo = controller
    mock_repo.delete_players.side_effect = sqlite3.Error("Database connection failed")

    with pytest.raises(RuntimeError) as exc_info:
        controller_obj.delete_players(full_name="John Doe")

    assert "Database error: Database connection failed" in str(exc_info.value)
    mock_repo.delete_players.assert_called_once_with(
        full_name="John Doe",
        birth_date=None,
        team=None,
        home_city=None,
        squad=None,
        position=None
    )


def test_get_paginated_players_database_error(controller):
    controller_obj, mock_repo = controller
    mock_repo.get_paginated_players.side_effect = sqlite3.Error("Database connection failed")

    with pytest.raises(RuntimeError) as exc_info:
        controller_obj.get_paginated_players(offset=0, limit=10)

    assert "Database error: Database connection failed" in str(exc_info.value)
    mock_repo.get_paginated_players.assert_called_once_with(0, 10)
    mock_repo.count_players.assert_not_called()