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
                birth_date DATE NOT NULL,
                age INTEGER NOT NULL,
                team TEXT NOT NULL,
                home_city TEXT NOT NULL,
                squad TEXT NOT NULL,
                position TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def _calculate_age(self, birth_date: date) -> int:
        today = date.today()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        return age

    def _execute_query(self, query: str, params: List) -> List[Player]:
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [Player(
            full_name=row[0],
            birth_date=date.fromisoformat(row[1]),
            team=row[2],
            home_city=row[3],
            squad=row[4],
            position=row[5]
        ) for row in rows]

    def add_player(self, player: Player):
        age = self._calculate_age(player.birth_date)
        self.cursor.execute("""
            INSERT INTO players (full_name, birth_date, age, team, home_city, squad, position) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (player.full_name, player.birth_date.isoformat(), age, player.team,
              player.home_city, player.squad, player.position))
        self.connection.commit()

    def get_players(self) -> List[Player]:
        query = "SELECT full_name, birth_date, team, home_city, squad, position FROM players"
        return self._execute_query(query, [])

    def find_players(self, full_name: Optional[str] = None, birth_date: Optional[date] = None,
                     team: Optional[str] = None, home_city: Optional[str] = None,
                     squad: Optional[str] = None, position: Optional[str] = None) -> List[Player]:
        query, params = self._build_search_query(full_name, birth_date, team, home_city, squad, position)
        return self._execute_query(query, params)

    def delete_players(self, full_name: Optional[str] = None, birth_date: Optional[date] = None,
                       team: Optional[str] = None, home_city: Optional[str] = None,
                       squad: Optional[str] = None, position: Optional[str] = None) -> int:
        query, params = self._build_delete_query(full_name, birth_date, team, home_city, squad, position)
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.rowcount

    def _build_delete_query(self, full_name, birth_date, team, home_city, squad, position):
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

        return query, params

    def _build_search_query(self, full_name, birth_date, team, home_city, squad, position):
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

        return query, params

    def __del__(self):
        self.connection.close()
