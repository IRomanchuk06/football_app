import pytest
from datetime import date
from src.models.player import Player

@pytest.fixture
def sample_player():
    return Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 15),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )

def test_player_initialization(sample_player):
    assert sample_player.full_name == "John Doe"
    assert sample_player.birth_date == date(1990, 5, 15)
    assert sample_player.team == "Team A"
    assert sample_player.home_city == "City X"
    assert sample_player.squad == "Squad 1"
    assert sample_player.position == "Forward"

def test_player_repr(sample_player):
    expected_repr = (
        "Player(full_name='John Doe', birth_date=1990-05-15, "
        "team='Team A', home_city='City X', "
        "squad='Squad 1', position='Forward')"
    )
    assert repr(sample_player) == expected_repr

def test_player_equality(sample_player):
    player1 = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 15),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )
    player2 = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 15),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )
    assert player1 == player2

def test_player_inequality(sample_player):
    player1 = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 15),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )
    player2 = Player(
        full_name="Jane Smith",
        birth_date=date(1992, 7, 12),
        team="Team B",
        home_city="City Y",
        squad="Squad 2",
        position="Midfielder"
    )
    assert player1 != player2

def test_player_hash(sample_player):
    player1 = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 15),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )
    player2 = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 15),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )
    assert hash(player1) == hash(player2)

def test_player_hash_different_objects(sample_player):
    player1 = Player(
        full_name="John Doe",
        birth_date=date(1990, 5, 15),
        team="Team A",
        home_city="City X",
        squad="Squad 1",
        position="Forward"
    )
    player2 = Player(
        full_name="Jane Smith",
        birth_date=date(1992, 7, 12),
        team="Team B",
        home_city="City Y",
        squad="Squad 2",
        position="Midfielder"
    )
    assert hash(player1) != hash(player2)

def test_player_eq_returns_false_for_non_player_object(sample_player):
    non_player_object = "This is not a Player object"
    assert sample_player.__eq__(non_player_object) is False
