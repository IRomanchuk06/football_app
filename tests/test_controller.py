import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QApplication, QTreeView
from src.controllers.player_controller import PlayerController
from src.models.player import Player
from src.exceptions.exceptions import PlayerNotFoundError, DeletionFailedError


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


def test_import_from_xml_success(controller):
    controller, mock_repo = controller
    mock_signal = MagicMock()
    controller.players_updated = mock_signal

    mock_xml_handler = MagicMock()
    mock_xml_handler.import_from_xml.side_effect = Exception("DB error")

    with patch('src.controllers.player_controller.XMLHandler', return_value=mock_xml_handler):
        with pytest.raises(RuntimeError) as exc_info:
            controller.import_from_xml("test.xml")

        assert "XML import failed" in str(exc_info.value)
        mock_signal.emit.assert_not_called()


def test_import_from_xml_failure(controller):
    controller, mock_repo = controller
    mock_signal = MagicMock()
    controller.players_updated = mock_signal

    mock_xml_handler = MagicMock()
    mock_xml_handler.import_from_xml.side_effect = Exception("Invalid XML")

    with patch('src.controllers.player_controller.XMLHandler', return_value=mock_xml_handler):
        with pytest.raises(RuntimeError) as exc_info:
            controller.import_from_xml("invalid.xml")

        assert "XML import failed" in str(exc_info.value)
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

    controller.export_to_xml("export.xml")

    mock_repo.get_players.assert_called_once()


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

    controller.export_to_xml("export.xml", test_players)

    mock_repo.get_players.assert_not_called()


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