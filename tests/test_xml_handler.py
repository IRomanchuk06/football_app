import pytest
from datetime import date
from xml.etree import ElementTree as ET
from unittest.mock import Mock, patch
from src.models.player import Player
from src.repositories.database_repository import DatabaseRepository
from src.services.xml_handler import XMLHandler


@pytest.fixture
def mock_repo():
    return Mock(spec=DatabaseRepository)


@pytest.fixture
def sample_players():
    return [
        Player(
            full_name="John Doe",
            birth_date=date(2000, 1, 1),
            team="Team A",
            home_city="City",
            squad="Squad 1",
            position="Forward"
        ),
        Player(
            full_name="Jane Smith",
            birth_date=date(1995, 5, 15),
            team="Team B",
            home_city="Town",
            squad="Squad 2",
            position="Midfielder"
        )
    ]


def test_import_from_xml_success(mock_repo, tmp_path):
    xml_content = '''<players>
        <player>
            <full_name>Test Player</full_name>
            <birth_date>1990-12-31</birth_date>
            <team>Test Team</team>
            <home_city>Test City</home_city>
            <squad>Test Squad</squad>
            <position>Test Position</position>
        </player>
    </players>'''
    xml_file = tmp_path / "test_import.xml"
    xml_file.write_text(xml_content)

    handler = XMLHandler(mock_repo)
    handler.import_from_xml(str(xml_file))

    expected_player = Player(
        full_name="Test Player",
        birth_date=date(1990, 12, 31),
        team="Test Team",
        home_city="Test City",
        squad="Test Squad",
        position="Test Position"
    )
    mock_repo.add_player.assert_called_once_with(expected_player)


def test_import_from_xml_invalid_file(mock_repo):
    handler = XMLHandler(mock_repo)
    with patch("builtins.print") as mock_print:
        handler.import_from_xml("nonexistent.xml")
        mock_print.assert_called_once()
        assert "Error importing from XML" in mock_print.call_args[0][0]
    mock_repo.add_player.assert_not_called()


def test_export_to_xml_success(mock_repo, tmp_path, sample_players):
    xml_path = tmp_path / "export.xml"
    mock_repo.get_players.return_value = sample_players

    handler = XMLHandler(mock_repo)
    handler.export_to_xml(str(xml_path))

    tree = ET.parse(xml_path)
    root = tree.getroot()

    assert len(root) == 2
    for i, player_element in enumerate(root):
        assert player_element.find("full_name").text == sample_players[i].full_name
        assert player_element.find("birth_date").text == sample_players[i].birth_date.isoformat()
        assert player_element.find("team").text == sample_players[i].team
        assert player_element.find("home_city").text == sample_players[i].home_city
        assert player_element.find("squad").text == sample_players[i].squad
        assert player_element.find("position").text == sample_players[i].position


def test_export_selected_to_xml(mock_repo, tmp_path, sample_players):
    xml_path = tmp_path / "selected.xml"
    handler = XMLHandler(mock_repo)

    with patch.object(handler, 'export_to_xml') as mock_export:
        handler.export_selected_to_xml(str(xml_path), sample_players)
        mock_export.assert_called_once_with(str(xml_path), sample_players)


def test_export_to_xml_empty(mock_repo, tmp_path):
    xml_path = tmp_path / "empty.xml"
    mock_repo.get_players.return_value = []

    handler = XMLHandler(mock_repo)
    handler.export_to_xml(str(xml_path))

    tree = ET.parse(xml_path)
    root = tree.getroot()
    assert len(root) == 0


def test_import_from_xml_missing_field(mock_repo, tmp_path):
    xml_content = '''<players>
        <player>
            <birth_date>2000-01-01</birth_date>
            <team>Team A</team>
            <home_city>City</home_city>
            <squad>Squad 1</squad>
            <position>Forward</position>
        </player>
    </players>'''
    xml_file = tmp_path / "broken.xml"
    xml_file.write_text(xml_content)

    handler = XMLHandler(mock_repo)
    with patch("builtins.print") as mock_print:
        handler.import_from_xml(str(xml_file))
        mock_print.assert_called_once()
        assert "Error importing from XML" in mock_print.call_args[0][0]
    mock_repo.add_player.assert_not_called()

def test_export_to_xml_error(mock_repo, tmp_path):
    invalid_path = tmp_path / "invalid_directory"
    invalid_path.mkdir()

    handler = XMLHandler(mock_repo)
    with patch("builtins.print") as mock_print:
        handler.export_to_xml(str(invalid_path))
        mock_print.assert_called_once()
        assert "Error exporting to XML" in mock_print.call_args[0][0]
