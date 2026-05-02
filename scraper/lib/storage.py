from collections import defaultdict
from typing import Literal
import sqlite3

from lib.datafetch import FetchResult


class Sqlite:
    def __init__(self, path, create: bool = False):
        self.path = path
        uri = "file:" + path + f"?mode=rw{'c' if create else ''}"
        self.conn = sqlite3.connect(uri, uri=True)
        self.cursor = self.conn.cursor()

    def get_resource_links(
        self, entity: Literal["hero"] | Literal["item"]
    ) -> FetchResult:
        match entity:
            case "hero":
                self.cursor.execute("SELECT image, image2 FROM heroes")
                return FetchResult(
                    columns=["image", "image2"], values=self.cursor.fetchall()
                )
            case "item":
                self.cursor.execute("SELECT image, image2 FROM items")
                return FetchResult(
                    columns=["image", "image2"], values=self.cursor.fetchall()
                )
            case _:
                return FetchResult(columns=[], values=[])

    def get_win_delta_heroes(self, min_matches: int = 3) -> FetchResult:
        hero_ids = self.cursor.execute(
            "select hero_id, image from heroes where hero_id in (select hero_id from heroes_in_matches group by 1 having count(*) > ?)",
            (min_matches,),
        ).fetchall()
        values = []
        for hid, image in hero_ids:
            values.append((hid, image, *self.get_win_delta_for(hid)))
        return FetchResult(
            columns=["hero_id", "image", "win_delta", "pick_rate"], values=values
        )

    def get_win_delta_for(self, hero_id: int) -> tuple[float, float]:
        """Win Delta: win_rate of team with hero - win_rate of team without hero"""
        win_rate_with_hero, pick_rate = self.cursor.execute(
            "select"
            "   100. * cast(sum(is_team_win) as real) / count(is_team_win), "
            "   100. * cast(count(is_team_win) as real) / (select count(distinct match_id) from heroes_in_matches)"
            "from heroes_in_matches "
            "where hero_id = ?",
            (hero_id,),
        ).fetchone()
        win_rate_without_hero, *_ = self.cursor.execute(
            "select"
            "   100. * cast(sum(is_team_win) as real) / count(is_team_win) "
            "from heroes_in_matches "
            "where"
            "   (match_id, team_side) not in "
            "       (select match_id, team_side from heroes_in_matches where hero_id = ?);",
            (hero_id,),
        ).fetchone()
        return win_rate_with_hero - win_rate_without_hero, pick_rate

    def get_hero_winrate_for(
        self, username: str | None, min_matches: int = 3
    ) -> FetchResult:
        if username is None:
            self.cursor.execute(
                "SELECT"
                "   h.name,"
                "   100. * cast(sum(is_team_win) as real) / count(*),"  # win_rate
                "   count(*),"  # matches
                "   100. * cast(count(*) as real) / total.total, "  # pick_rate
                "   h.image "
                "FROM heroes_in_matches hxm "
                "LEFT JOIN heroes h "
                "   ON h.hero_id = hxm.hero_id "
                "JOIN ( SELECT count(distinct match_id) as total FROM heroes_in_matches) as total "
                "GROUP BY 1 having count(*) >= ?",
                (min_matches,),
            )
        else:
            self.cursor.execute(
                "SELECT"
                "   h.name,"
                "   100. * cast(sum(is_team_win) as real) / count(*),"  # win_rate
                "   count(*),"  # matches
                "   100. * cast(count(*) as real) / total.total, "  # pick_rate
                "   h.image "
                "FROM heroes_in_matches hxm "
                "LEFT JOIN heroes h "
                "   ON h.hero_id = hxm.hero_id "
                "JOIN ( SELECT count(distinct match_id) as total FROM heroes_in_matches WHERE username = ?) as total "
                "WHERE username = ?"
                "GROUP BY 1 having count(*) >= ?",
                (username, username, min_matches),
            )
        return FetchResult(
            columns=[
                "hero_name",
                "win_rate",
                "matches",
                "pick_rate",
                "image",
            ],
            values=self.cursor.fetchall(),
        )

    def get_item_winrate(self, min_matches: int = 3) -> FetchResult:
        self.cursor.execute(
            " SELECT"
            "     i.name,"
            "     i.item_id,"
            "     i.image,"
            "     100. * cast(sum(is_team_win) as real) / count(*),"
            "     count(distinct im.match_id),"
            "     100. * cast(count(distinct im.match_id) as real) / total.total"
            " FROM items_in_matches im"
            " LEFT JOIN items i"
            " ON i.item_id = im.item_id"
            " LEFT JOIN heroes_in_matches hm"
            " ON hm.user_id = im.user_id"
            " AND hm.match_id = im.match_id"
            " JOIN ( SELECT count(distinct match_id) as total FROM items_in_matches) as total"
            " WHERE i.name is not null"
            " GROUP BY 1 having count(*) >= ?",
            (min_matches,),
        )
        return FetchResult(
            columns=[
                "item_name",
                "item_id",
                "image",
                "win_rate",
                "matches",
                "pick_rate",
            ],
            values=self.cursor.fetchall(),
        )

    def get_item_winrate_for_hero(self, hero: str, min_matches: int = 3) -> FetchResult:
        self.cursor.execute(
            "WITH hero as (SELECT hero_id FROM heroes where name = ?)"
            " SELECT"
            "     i.name,"
            "     i.item_id,"
            "     i.image,"
            "     100. * cast(sum(is_team_win) as real) / count(*),"
            "     count(distinct im.match_id),"
            "     100. * cast(count(distinct im.match_id) as real) / total.total"
            " FROM items_in_matches im"
            " JOIN hero"
            " LEFT JOIN items i"
            "   ON i.item_id = im.item_id"
            " LEFT JOIN heroes_in_matches hm"
            "   ON hm.user_id = im.user_id"
            "   AND hm.match_id = im.match_id"
            " JOIN ( SELECT count(distinct match_id) as total FROM heroes_in_matches hm JOIN hero WHERE hm.hero_id = hero.hero_id) as total"
            " WHERE i.name is not null"
            "   AND hm.hero_id = hero.hero_id"
            " GROUP BY 1 having count(*) >= ?",
            (
                hero,
                min_matches,
            ),
        )
        return FetchResult(
            columns=[
                "item_name",
                "item_id",
                "image",
                "win_rate",
                "matches",
                "pick_rate",
            ],
            values=self.cursor.fetchall(),
        )

    def get_item_win_rate_heroes(self, min_matches: int = 3) -> dict[str, FetchResult]:
        hero_names = self.cursor.execute(
            "select name from heroes where hero_id in (select hero_id from heroes_in_matches group by 1 having count(*) > ?)",
            (min_matches,),
        ).fetchall()
        result = defaultdict()
        for name, *_ in hero_names:
            result[name] = self.get_item_winrate_for_hero(name, min_matches=min_matches)
        return result
