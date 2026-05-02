from dataclasses import dataclass
from core.storage import Sqlite

from core.datafetch import FetchResult


@dataclass
class HeroWinDelta:
    hero_id: int
    image: str
    win_delta: float
    pick_rate: float

    @classmethod
    def fetch(cls, driver: Sqlite, min_matches: int = 3) -> FetchResult:
        hero_ids = driver.cursor.execute(
            "select hero_id, image from heroes where hero_id in (select hero_id from heroes_in_matches group by 1 having count(*) > ?)",
            (min_matches,),
        ).fetchall()
        values = []
        for hid, image in hero_ids:
            values.append((hid, image, *self.get_win_delta_for(hid)))
        return FetchResult(
            columns=["hero_id", "image", "win_delta", "pick_rate"], values=values
        )
