import profile
from dataclasses import dataclass


@dataclass
class EntitySummary:
    id: int
    n: str
    ix: str
    i2x: str


@dataclass
class MatchSummary:
    sid: int
    bid: int
    hid: int
    k: int
    d: int
    a: int
    lid: int
    s: int
    mvp: bool
    res: int
    ts: int
    hid_e: EntitySummary
    bid_s: str

    def __post_init__(self):
        self.hid_e = EntitySummary(**self.hid_e)


@dataclass
class MatchDetail:
    f: int  # team_side
    hid: int  # hero_id
    rid: int  # user_id
    zid: int  # server_id
    k: int
    d: int
    a: int
    tfr: int  # team_fight_ratio
    o: int  # hero_damage
    op: int  # hero_damage_percent
    s: int  # score (*100)
    mvp: int  # bool
    its: list[int]  # items
    eq: int  # ?
    ts: int  # ?
    bd: int  # ?
    fk: int  # team_total_kills
    fw: int  # is_team_win
    hid_e: EntitySummary
    its_e: list[EntitySummary]
    hlvl: int  # hero_level
    rname: str  # user_name

    def __post_init__(self):
        self.hid_e = EntitySummary(**self.hid_e)
        self.its_e = [EntitySummary(**e) for e in self.its_e if e is not None]

    def prepare_sqls_with_match_id(self, match_id: int) -> list[tuple[str, list]]:
        stmts = []
        # register hero
        hero = self.hid_e
        stmts.append(
            (
                "INSERT OR IGNORE INTO heroes (hero_id, name, image, image2) VALUES (?, ?, ?, ?);",
                (hero.id, hero.n, hero.ix, hero.i2x),
            ),
        )
        # register item
        items = self.its_e
        for item in items:
            stmts.append(
                (
                    "INSERT OR IGNORE INTO items (item_id, name, image, image2) VALUES (?, ?, ?, ?);",
                    (item.id, item.n, item.ix, item.i2x),
                ),
            )
        # register heroes_in_matches
        stmts.append(
            (
                """INSERT OR IGNORE INTO heroes_in_matches (
            match_id,
            team_side,
            hero_id,
            user_id,
            server_id,
            kills,
            deaths,
            assists,
            team_fight_ratio,
            hero_damage,
            hero_damage_percent,
            score,
            is_mvp,
            eq,
            ts,
            bd,
            team_total_kills,
            is_team_win,
            hero_level,
            username
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        );""",
                (
                    match_id,
                    self.f,
                    self.hid,
                    self.rid,
                    self.zid,
                    self.k,
                    self.d,
                    self.a,
                    self.tfr,
                    self.o,
                    self.op,
                    self.s,
                    self.mvp,
                    self.eq,
                    self.ts,
                    self.bd,
                    self.fk,
                    self.fw,
                    self.hlvl,
                    self.rname,
                ),
            )
        )
        # items in matches
        for item in self.its:
            stmts.append(
                (
                    "INSERT OR IGNORE INTO items_in_matches (match_id, user_id, item_id) VALUES (?, ?, ?);",
                    (match_id, self.rid, item),
                )
            )
        return stmts


@dataclass
class MatchResult:
    result: list[MatchDetail]

    def __post_init__(self):
        self.result = [MatchDetail(**t) for t in self.result]


@dataclass
class MatchResponse:
    code: int
    message: str
    traceID: str
    data: MatchResult

    def __post_init__(self):
        if self.code == 1002:
            raise ValueError(
                "Auth likely expired. Please update http headers in `--http-headers` file"
            )
        if self.data is not None:
            self.data = MatchResult(**self.data)
        else:
            self.data = MatchResult(result=[])
