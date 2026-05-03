from collections import defaultdict
from dataclasses import dataclass
from driver.sqlite import Sqlite


@dataclass
class WinlossHero:
    name: str
    matches: int
    distribution: dict[int, int]


async def fetch_poissonan_win_loss_for(
    driver: Sqlite, hero: str, *, sample_size=10, matches=10
) -> WinlossHero:
    res = defaultdict(int)
    for _ in range(sample_size):
        cursor = await driver.conn.execute(
            "WITH this_hero AS (SELECT * from heroes where name = ?)"
            ", main_table AS ("
            " SELECT"
            "     h.name,"
            "     hm.is_team_win"
            " FROM this_hero h"
            " LEFT JOIN heroes_in_matches hm"
            "   ON hm.hero_id = h.hero_id"
            " ORDER BY RANDOM()"
            " LIMIT ?"
            ")"
            " SELECT count(*) as matches, sum(is_team_win) as wins FROM main_table",
            (hero, matches),
        )
        for matches, wins in await cursor.fetchall():
            res[wins] += 1
    return WinlossHero(name=hero, matches=matches, distribution=res)


@dataclass
class WinlossAgainst:
    name: str
    against: str
    matches: int
    wins: int


async def fetch_sample_win_loss_data_for_against(
    driver: Sqlite, hero: str, against: str, *, sample_size=10, matches=10
) -> list[WinlossAgainst]:
    res = []
    for _ in range(sample_size):
        cursor = await driver.conn.execute(
            "WITH this_hero AS (SELECT * from heroes where name = ?)"
            ", against_hero AS (SELECT hero_id from heroes where name = ?)"
            ", main_table AS ("
            " SELECT"
            "     h.name,"
            "     h2.name as against,"
            "     hm.is_team_win"
            " FROM this_hero h"
            " LEFT JOIN heroes_in_matches hm"
            "   ON hm.hero_id = h.hero_id"
            " INNER JOIN (SELECT * FROM heroes_in_matches him JOIN against_hero WHERE him.hero_id = against_hero.hero_id) hm2"
            "   ON hm.match_id = hm2.match_id"
            "   AND hm.team_side <> hm2.team_side"
            " LEFT JOIN heroes h2"
            "   ON h2.hero_id = hm2.hero_id"
            " ORDER BY RANDOM()"
            " LIMIT ?"
            ")"
            " SELECT name, against, count(*) as matches, sum(is_team_win) as wins FROM main_table GROUP BY 1, 2",
            (hero, against, matches),
        )
        for name, against, matches, wins in await cursor.fetchall():
            res.append(
                WinlossAgainst(
                    name=name,
                    against=against,
                    matches=matches,
                    wins=wins,
                )
            )
    return res


# @dataclass
# class Teamup:
#     name: str
#     teamup: str
#     teamup_rate: float
#     win_delta: float


# async def fetch_teamup_winrate_for(
#     driver: Sqlite, hero: str, *, min_matchup: int = 3
# ) -> list[Teamup]:
#     cursor = await driver.conn.execute(
#         "WITH this_hero AS (SELECT * from heroes where name = ?)"
#         " SELECT"
#         "     h.name,"
#         "     h2.name as teamup,"
#         "     100. * count(distinct hm2.match_id) / total.total as teamup_rate,"
#         "     (100. * sum(hm.is_team_win) / count(distinct hm2.match_id)) - total.base_winrate as win_delta"
#         "     FROM this_hero h"
#         " LEFT JOIN heroes_in_matches hm"
#         "   ON hm.hero_id = h.hero_id"
#         " LEFT JOIN heroes_in_matches hm2"
#         "   ON hm.match_id = hm2.match_id"
#         "   AND hm.team_side = hm2.team_side"
#         "   AND hm.username <> hm2.username"
#         " LEFT JOIN heroes h2"
#         "   ON h2.hero_id = hm2.hero_id"
#         " LEFT JOIN ("
#         "   SELECT"
#         "       hero_id,"
#         "       count(distinct match_id) as total,"
#         "       100. * sum(hm0.is_team_win) / count(distinct match_id) as base_winrate"
#         "   FROM heroes_in_matches hm0"
#         "   GROUP BY 1"
#         "   ) total"
#         "   ON total.hero_id = h.hero_id"
#         " GROUP BY 1,2 HAVING count(distinct hm2.match_id) >= ?;",
#         (hero, min_matchup),
#     )
#     res = []
#     for name, teamup, teamup_rate, win_delta in await cursor.fetchall():
#         res.append(
#             Teamup(
#                 name=name, teamup=teamup, teamup_rate=teamup_rate, win_delta=win_delta
#             )
#         )
#     return res
