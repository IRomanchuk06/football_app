import sqlite3
from typing import List, Optional
from datetime import date
from src.models.player import Player

class DatabaseRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self._initialize_db()

    def _initialize_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                team TEXT NOT NULL,
                home_city TEXT NOT NULL,
                squad TEXT NOT NULL,
                position TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def add_player(self, player: Player):
        self.cursor.execute("""
            INSERT INTO players (full_name, birth_date, team, home_city, squad, position) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (player.full_name, player.birth_date.isoformat(), player.team,
              player.home_city, player.squad, player.position))
        self.connection.commit()

    def get_players(self) -> List[Player]:
        self.cursor.execute("SELECT full_name, birth_date, team, home_city, squad, position FROM players")
        rows = self.cursor.fetchall()
        return [Player(full_name=row[0], birth_date=date.fromisoformat(row[1]), team=row[2],
                       home_city=row[3], squad=row[4], position=row[5]) for row in rows]

    def find_players(self, full_name: Optional[str] = None, birth_date: Optional[date] = None,
                     team: Optional[str] = None, home_city: Optional[str] = None,
                     squad: Optional[str] = None, position: Optional[str] = None) -> List[Player]:
        query = "SELECT full_name, birth_date, team, home_city, squad, position FROM players WHERE 1=1"
        params = []

        if full_name:
            query += " AND full_name LIKE ?"
            params.append(f"%{full_name}%")
        if birth_date:
            query += " AND birth_date = ?"
            params.append(birth_date.isoformat())
        if team:
            query += " AND team LIKE ?"
            params.append(f"%{team}%")
        if home_city:
            query += " AND home_city LIKE ?"
            params.append(f"%{home_city}%")
        if squad:
            query += " AND squad LIKE ?"
            params.append(f"%{squad}%")
        if position:
            query += " AND position LIKE ?"
            params.append(f"%{position}%")

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [Player(full_name=row[0], birth_date=date.fromisoformat(row[1]), team=row[2],
                       home_city=row[3], squad=row[4], position=row[5]) for row in rows]

    def delete_players(self, full_name: Optional[str] = None, birth_date: Optional[date] = None,
                       team: Optional[str] = None, home_city: Optional[str] = None,
                       squad: Optional[str] = None, position: Optional[str] = None) -> int:
        query = "DELETE FROM players WHERE 1=1"
        params = []

        if full_name:
            query += " AND full_name LIKE ?"
            params.append(f"%{full_name}%")
        if birth_date:
            query += " AND birth_date = ?"
            params.append(birth_date.isoformat())
        if team:
            query += " AND team LIKE ?"
            params.append(f"%{team}%")
        if home_city:
            query += " AND home_city LIKE ?"
            params.append(f"%{home_city}%")
        if squad:
            query += " AND squad LIKE ?"
            params.append(f"%{squad}%")
        if position:
            query += " AND position LIKE ?"
            params.append(f"%{position}%")

        self.cursor.execute(query, params)
        affected_rows = self.cursor.rowcount
        self.connection.commit()
        return affected_rows

    def __del__(self):
        self.connection.close()
