from datetime import date

class Player:
    def __init__(self, full_name: str, birth_date: date, team: str,
                 home_city: str, squad: str, position: str):
        self.full_name = full_name
        self.birth_date = birth_date
        self.team = team
        self.home_city = home_city
        self.squad = squad
        self.position = position

    def __repr__(self):
        return (f"Player(full_name='{self.full_name}', birth_date={self.birth_date}, "
                f"team='{self.team}', home_city='{self.home_city}', "
                f"squad='{self.squad}', position='{self.position}')")

    def __eq__(self, other):
        if isinstance(other, Player):
            return (
                    self.full_name == other.full_name
                    and self.birth_date == other.birth_date
                    and self.team == other.team
                    and self.home_city == other.home_city
                    and self.squad == other.squad
                    and self.position == other.position
            )
        return False

    def __hash__(self):
        return hash(
            (
                self.full_name,
                self.birth_date,
                self.team,
                self.home_city,
                self.squad,
                self.position,
            )
        )