from collections import defaultdict
import json
from dataclasses import dataclass


from driver.sqlite import Sqlite


@dataclass
class UserInfo:
    username: str
    winrate: float
    hero_winrate: float


@dataclass
class Infobox:
    hero_name: int
    winrate: float
    matches: int
    users: list[UserInfo] | None = None


async def fetch_info_for_hero_with_users(
    driver: Sqlite, hero: str, users: list[str]
) -> Infobox:
    cursor = await driver.conn.execute(
        "SELECT"
        "   h.name as hero_name,"
        "   username,"
        "   total.winrate as hero_winrate,"
        "   total.total as hero_matches,"
        "   userinfo.winrate as user_winrate,"
        "   100. * sum(is_team_win) / count(distinct match_id) as user_hero_winrate "
        "FROM heroes h "
        "LEFT JOIN heroes_in_matches hm "
        "   ON hm.hero_id = h.hero_id "
        "LEFT JOIN (SELECT hero_id, count(distinct match_id) as total, 100. * sum(is_team_win) / count(distinct match_id) as winrate FROM heroes_in_matches GROUP BY 1) total"
        "   ON total.hero_id = hm.hero_id "
        "LEFT JOIN (SELECT user_id, 100. * sum(is_team_win) / count(distinct match_id) as winrate FROM heroes_in_matches WHERE username in (SELECT value FROM json_each(?)) GROUP BY 1) userinfo"
        "   ON userinfo.user_id = hm.user_id "
        "WHERE h.name = ?"
        "GROUP BY 1, 2, 3, 4",
        (json.dumps(users), hero),
    )
    infobox = None
    usersinfo: dict[str, UserInfo] = defaultdict()
    for (
        hero_name,
        username,
        hero_winrate,
        hero_matches,
        user_winrate,
        user_hero_winrate,
    ) in await cursor.fetchall():
        if not infobox:
            infobox = Infobox(
                hero_name=hero_name, winrate=hero_winrate, matches=hero_matches
            )
        if username in users:
            usersinfo[username] = UserInfo(
                username=username,
                winrate=user_winrate,
                hero_winrate=user_hero_winrate,
            )
    assert infobox is not None
    infobox.users = [u for u in usersinfo.values()]
    return infobox
