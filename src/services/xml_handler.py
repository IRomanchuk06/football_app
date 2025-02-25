import xml.etree.ElementTree as ET
from datetime import date
from src.models.player import Player
from src.repositories.database_repository import DatabaseRepository


class XMLHandler:
    def __init__(self, db_repository: DatabaseRepository):
        self.db_repository = db_repository

    def import_from_xml(self, xml_file_path: str):
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            for player_element in root.findall("player"):
                full_name = player_element.find("full_name").text
                birth_date = date.fromisoformat(player_element.find("birth_date").text)
                team = player_element.find("team").text
                home_city = player_element.find("home_city").text
                squad = player_element.find("squad").text
                position = player_element.find("position").text

                player = Player(
                    full_name=full_name,
                    birth_date=birth_date,
                    team=team,
                    home_city=home_city,
                    squad=squad,
                    position=position,
                )

                self.db_repository.add_player(player)

            print("Data imported from XML successfully.")
        except Exception as e:
            print(f"Error importing from XML: {e}")

    def export_to_xml(self, xml_file_path: str, players: list[Player] = None):
        try:
            if not xml_file_path.endswith(".xml"):
                xml_file_path += ".xml"

            if players is None:
                players = self.db_repository.get_players()

            root = ET.Element("players")

            for player in players:
                player_element = ET.SubElement(root, "player")

                ET.SubElement(player_element, "full_name").text = player.full_name
                ET.SubElement(player_element, "birth_date").text = player.birth_date.isoformat()
                ET.SubElement(player_element, "team").text = player.team
                ET.SubElement(player_element, "home_city").text = player.home_city
                ET.SubElement(player_element, "squad").text = player.squad
                ET.SubElement(player_element, "position").text = player.position

            tree = ET.ElementTree(root)
            tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)

            print(f"Data exported to XML successfully: {xml_file_path}")
        except Exception as e:
            print(f"Error exporting to XML: {e}")

    def export_selected_to_xml(self, xml_file_path: str, selected_players: list[Player]):
        self.export_to_xml(xml_file_path, selected_players)