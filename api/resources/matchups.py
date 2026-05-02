from dataclasses import dataclass
from driver.sqlite import Sqlite


@dataclass
class Matchup:
    name: str
    against: str
    matchup_rate: float
    win_delta: float


async def fetch_matchup_winrate_for(
    driver: Sqlite, hero: str, *, min_matchup: int = 3
) -> list[Matchup]:
    cursor = await driver.conn.execute(
        "WITH this_hero AS (SELECT * from heroes where name = ?)"
        " SELECT"
        "     h.name,"
        "     h2.name as against,"
        "     100. * count(distinct hm2.match_id) / total.total as matchup_rate,"
        "     (100. * sum(hm.is_team_win) / count(distinct hm2.match_id)) - total.base_winrate as win_delta"
        "     FROM this_hero h"
        " LEFT JOIN heroes_in_matches hm"
        " ON hm.hero_id = h.hero_id"
        " LEFT JOIN heroes_in_matches hm2"
        " ON hm.match_id = hm2.match_id"
        " AND hm.team_side <> hm2.team_side"
        " LEFT JOIN heroes h2"
        " ON h2.hero_id = hm2.hero_id"
        " LEFT JOIN ("
        "   SELECT"
        "       hero_id,"
        "       count(distinct match_id) as total,"
        "       100. * sum(hm0.is_team_win) / count(distinct match_id) as base_winrate"
        "   FROM heroes_in_matches hm0"
        "   GROUP BY 1"
        "   ) total"
        "   ON total.hero_id = h.hero_id"
        " GROUP BY 1,2 HAVING count(distinct hm2.match_id) >= ?;",
        (hero, min_matchup),
    )
    res = []
    for name, against, matchup_rate, win_delta in await cursor.fetchall():
        res.append(
            Matchup(
                name=name,
                against=against,
                matchup_rate=matchup_rate,
                win_delta=win_delta,
            )
        )
    return res


@dataclass
class Teamup:
    name: str
    teamup: str
    teamup_rate: float
    win_delta: float


async def fetch_teamup_winrate_for(
    driver: Sqlite, hero: str, *, min_matchup: int = 3
) -> list[Teamup]:
    cursor = await driver.conn.execute(
        "WITH this_hero AS (SELECT * from heroes where name = ?)"
        " SELECT"
        "     h.name,"
        "     h2.name as teamup,"
        "     100. * count(distinct hm2.match_id) / total.total as teamup_rate,"
        "     (100. * sum(hm.is_team_win) / count(distinct hm2.match_id)) - total.base_winrate as win_delta"
        "     FROM this_hero h"
        " LEFT JOIN heroes_in_matches hm"
        "   ON hm.hero_id = h.hero_id"
        " LEFT JOIN heroes_in_matches hm2"
        "   ON hm.match_id = hm2.match_id"
        "   AND hm.team_side = hm2.team_side"
        "   AND hm.username <> hm2.username"
        " LEFT JOIN heroes h2"
        "   ON h2.hero_id = hm2.hero_id"
        " LEFT JOIN ("
        "   SELECT"
        "       hero_id,"
        "       count(distinct match_id) as total,"
        "       100. * sum(hm0.is_team_win) / count(distinct match_id) as base_winrate"
        "   FROM heroes_in_matches hm0"
        "   GROUP BY 1"
        "   ) total"
        "   ON total.hero_id = h.hero_id"
        " GROUP BY 1,2 HAVING count(distinct hm2.match_id) >= ?;",
        (hero, min_matchup),
    )
    res = []
    for name, teamup, teamup_rate, win_delta in await cursor.fetchall():
        res.append(
            Teamup(
                name=name, teamup=teamup, teamup_rate=teamup_rate, win_delta=win_delta
            )
        )
    return res
