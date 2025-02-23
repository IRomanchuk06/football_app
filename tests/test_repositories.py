from datetime import date

import pytest

from src.models.player import Player
from src.repositories.database_repository import DatabaseRepository


@pytest.fixture
def temp_db():
    db = DatabaseRepository(":memory:")
    db._initialize_db()
    return db


@pytest.fixture
def sample_player():
    return Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 15),
        team="Red Warriors",
        home_city="New York",
        squad="Main Squad",
        position="Forward"
    )


def test_add_player(temp_db, sample_player):
    temp_db.add_player(sample_player)
    players = temp_db.get_players()

    assert len(players) == 1
    assert players[0].full_name == sample_player.full_name
    assert players[0].birth_date == sample_player.birth_date
    assert players[0].team == sample_player.team
    assert players[0].home_city == sample_player.home_city
    assert players[0].squad == sample_player.squad
    assert players[0].position == sample_player.position


def test_get_players(temp_db, sample_player):
    temp_db.add_player(sample_player)
    players = temp_db.get_players()

    assert len(players) == 1
    assert players[0].full_name == sample_player.full_name


def test_find_players_by_full_name(temp_db, sample_player):
    temp_db.add_player(sample_player)
    result = temp_db.find_players(full_name="John")

    assert len(result) == 1
    assert result[0].full_name == "John Doe"

    empty_result = temp_db.find_players(full_name="Unknown")
    assert len(empty_result) == 0


def test_find_players_by_team(temp_db, sample_player):
    temp_db.add_player(sample_player)
    result = temp_db.find_players(team="Red")

    assert len(result) == 1
    assert result[0].team == "Red Warriors"

    empty_result = temp_db.find_players(team="Blue")
    assert len(empty_result) == 0


def test_find_players_by_multiple_filters(temp_db, sample_player):
    temp_db.add_player(sample_player)
    result = temp_db.find_players(full_name="John", team="Red")

    assert len(result) == 1
    assert result[0].full_name == "John Doe"
    assert result[0].team == "Red Warriors"

    empty_result = temp_db.find_players(full_name="John", team="Blue")
    assert len(empty_result) == 0


def test_find_players_by_birth_date(temp_db, sample_player):
    temp_db.add_player(sample_player)
    result = temp_db.find_players(birth_date=date(1990, 5, 15))

    assert len(result) == 1
    assert result[0].birth_date == date(1990, 5, 15)

    empty_result = temp_db.find_players(birth_date=date(1989, 12, 31))
    assert len(empty_result) == 0


def test_find_players_with_multiple_filters(temp_db, sample_player):
    temp_db.add_player(sample_player)
    result = temp_db.find_players(
        full_name="John",
        birth_date=date(1990, 5, 15),
        team="Red",
        home_city="New York",
        squad="Main Squad",
        position="Forward"
    )

    assert len(result) == 1
    assert result[0].full_name == "John Doe"
    assert result[0].birth_date == date(1990, 5, 15)
    assert result[0].team == "Red Warriors"
    assert result[0].home_city == "New York"
    assert result[0].squad == "Main Squad"
    assert result[0].position == "Forward"


def test_find_players_with_no_matches(temp_db, sample_player):
    temp_db.add_player(sample_player)
    result = temp_db.find_players(
        full_name="Jane",
        team="Blue",
        home_city="Los Angeles"
    )

    assert len(result) == 0


def test_find_players_with_birth_date_filter(temp_db, sample_player):
    temp_db.add_player(sample_player)
    result = temp_db.find_players(birth_date=date(1990, 5, 15))

    assert len(result) == 1
    assert result[0].birth_date == date(1990, 5, 15)

    empty_result = temp_db.find_players(birth_date=date(2000, 1, 1))
    assert len(empty_result) == 0


def test_find_players_with_team_filter(temp_db, sample_player):
    temp_db.add_player(sample_player)
    result = temp_db.find_players(team="Red")

    assert len(result) == 1
    assert result[0].team == "Red Warriors"

    empty_result = temp_db.find_players(team="Blue")
    assert len(empty_result) == 0


def test_find_players_with_home_city_filter(temp_db, sample_player):
    temp_db.add_player(sample_player)
    result = temp_db.find_players(home_city="New York")

    assert len(result) == 1
    assert result[0].home_city == "New York"

    empty_result = temp_db.find_players(home_city="Los Angeles")
    assert len(empty_result) == 0


def test_find_players_with_squad_filter(temp_db, sample_player):
    temp_db.add_player(sample_player)
    result = temp_db.find_players(squad="Main Squad")

    assert len(result) == 1
    assert result[0].squad == "Main Squad"

    empty_result = temp_db.find_players(squad="Reserve Squad")
    assert len(empty_result) == 0


def test_find_players_with_position_filter(temp_db, sample_player):
    temp_db.add_player(sample_player)
    result = temp_db.find_players(position="Forward")

    assert len(result) == 1
    assert result[0].position == "Forward"

    empty_result = temp_db.find_players(position="Goalkeeper")
    assert len(empty_result) == 0


def test_delete_players_by_full_name(temp_db, sample_player):
    temp_db.add_player(sample_player)
    deleted_count = temp_db.delete_players(full_name="John")

    assert deleted_count == 1
    assert len(temp_db.get_players()) == 0


def test_delete_players_by_team(temp_db, sample_player):
    temp_db.add_player(sample_player)
    deleted_count = temp_db.delete_players(team="Red")

    assert deleted_count == 1
    assert len(temp_db.get_players()) == 0


def test_delete_players_by_multiple_filters(temp_db, sample_player):
    temp_db.add_player(sample_player)
    deleted_count = temp_db.delete_players(full_name="John", team="Red Warriors")

    assert deleted_count == 1
    assert len(temp_db.get_players()) == 0


def test_delete_players_with_no_match(temp_db, sample_player):
    temp_db.add_player(sample_player)
    deleted_count = temp_db.delete_players(full_name="Jane")

    assert deleted_count == 0
    assert len(temp_db.get_players()) == 1


def test_delete_players_without_filters(temp_db, sample_player):
    temp_db.add_player(sample_player)
    deleted_count = temp_db.delete_players()

    assert deleted_count == 1
    assert len(temp_db.get_players()) == 0


def test_delete_players_by_birth_date(temp_db, sample_player):
    temp_db.add_player(sample_player)
    deleted_count = temp_db.delete_players(birth_date=date(1990, 5, 15))

    assert deleted_count == 1
    assert len(temp_db.get_players()) == 0


def test_delete_players_by_home_city(temp_db, sample_player):
    temp_db.add_player(sample_player)
    deleted_count = temp_db.delete_players(home_city="New York")

    assert deleted_count == 1
    assert len(temp_db.get_players()) == 0


def test_delete_players_by_squad(temp_db, sample_player):
    temp_db.add_player(sample_player)
    deleted_count = temp_db.delete_players(squad="Main Squad")

    assert deleted_count == 1
    assert len(temp_db.get_players()) == 0


def test_delete_players_by_position(temp_db, sample_player):
    temp_db.add_player(sample_player)
    deleted_count = temp_db.delete_players(position="Forward")

    assert deleted_count == 1
    assert len(temp_db.get_players()) == 0
