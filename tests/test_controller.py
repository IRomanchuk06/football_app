import pytest
from unittest.mock import MagicMock
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