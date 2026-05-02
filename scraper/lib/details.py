from urllib.parse import SplitResult
from dataclasses import dataclass


@dataclass
class HeroMatchDetails:
    level: int
    icon: str
    username: str
    equipments: list[str]
    kills: int
    death: int
    assists: int
    score: float
    hero_damage: int
    participation: int


@dataclass
class MatchDetail:
    match_id: str
    season: int
    team_result: str
    team: list[HeroMatchDetails]
    enemy: list[HeroMatchDetails]
    duration: str = ""
    match_time: str = ""

    @classmethod
    def win_from_url(cls, url: SplitResult) -> "MatchDetail":
        match_id = url.path.split("/")[-1]
        season = int(url.query.split("=")[-1])
        return cls(
            match_id=match_id,
            season=season,
            team_result="win",
            team=list(),
            enemy=list(),
        )

    @classmethod
    def lost_from_url(cls, url: SplitResult) -> "MatchDetail":
        match_id = url.path.split("/")[-1]
        season = int(url.query.split("=")[-1])
        return cls(
            match_id=match_id,
            season=season,
            team_result="lose",
            team=list(),
            enemy=list(),
        )

    def with_duration_on(self, duration: str, match_time: str) -> "MatchDetail":
        self.duration = duration
        self.match_time = match_time
        return self
