import math
from fastapi.responses import StreamingResponse
import io
from pathlib import Path
from typing import List, Annotated

from PIL import Image
from fastapi import FastAPI, Depends, HTTPException


from driver.sqlite import Sqlite

from resources.enums import fetch_heroes, Hero
from resources.matchups import fetch_matchup_winrate_for, Matchup
from resources.matchups import fetch_teamup_winrate_for, Teamup
from resources.infobox import fetch_info_for_hero_with_users, Infobox
from resources.winloss import fetch_sample_win_loss_data_for_against, WinlossAgainst
from resources.winloss import fetch_poissonan_win_loss_for, WinlossHero
from resources.freshness import fetch_db_freshness, DbFreshness

from resources.normalizer import image_url_to_filename
from graphs.winrate_vs_x import plot_win_pick

app = FastAPI()


async def get_sqlite():
    engine = Sqlite(path=Path("/static/mlbb.sqlite"))
    async with engine as db:
        yield db


SqliteSession = Annotated[Sqlite, Depends(get_sqlite)]


@app.get("/sample/winloss/{hero}/{against}")
async def get_sample_hero_against_winloss(
    db: SqliteSession, hero: str, against: str, matches: int = 10, samples: int = 10
) -> list[WinlossAgainst]:
    return await fetch_sample_win_loss_data_for_against(
        db, hero, against, matches=matches
    )


@app.get("/distribution/poissonan/{hero}")
async def get_poissonan_distribution_hero(
    db: SqliteSession, hero: str, matches: int = 10
) -> WinlossHero:
    return await fetch_poissonan_win_loss_for(db, hero, matches=matches)


@app.get("/pmf/poisson")
def get_poissonnan_dist(winrate: float, matches: int):
    if winrate < 0.0 or winrate > 1:
        raise HTTPException(
            status_code=422, detail="winrate must be between 0.0 and 1.0"
        )
    if matches < 0:
        raise HTTPException(status_code=422, detail="matches must be >= 0")

    def poisson(Lambda: float, k: int):
        return Lambda ** (k) * math.exp(-Lambda) / math.factorial(k)

    x = [*range(matches + 1)]
    return {"P": [poisson(winrate * matches, k) for k in x], "x": x}


@app.get("/list/heroes")
async def list_heroes(db: SqliteSession) -> List[Hero]:
    return await fetch_heroes(db, order_by="name")


@app.get("/user/{user}/{hero}")
async def get_user_hero_info(db: SqliteSession, user: str, hero: str) -> Infobox:
    data = await fetch_info_for_hero_with_users(db, hero, [user])
    return data


@app.get("/check/db")
async def get_db_freshness(db: SqliteSession) -> DbFreshness:
    data = await fetch_db_freshness(db)
    return data


HeroList = Annotated[List[Hero], Depends(list_heroes)]


@app.get("/matchup/{hero}")
async def get_matchup_for(
    driver: SqliteSession, heroes: HeroList, hero, min_matchup: int = 3
):
    hero_name_to_heroes = {h.name: h for h in heroes}
    matchup: list[Matchup] = await fetch_matchup_winrate_for(
        driver, hero, min_matchup=min_matchup
    )
    x = [m.matchup_rate for m in matchup]
    y = [m.win_delta for m in matchup]
    images = [
        Image.open(
            Path("/asset")
            / (image_url_to_filename(hero_name_to_heroes[m.against].image) + ".png")
        )
        for m in matchup
    ]
    fig = plot_win_pick(
        x,
        y,
        images,
        title="Win rate increase vs Matchup rate",
        ylims=(-100.0, 100.0),
        xlims=(0, 60.0),
        y_line=0,
    )
    fig.gca().set_xlabel(f"Matchup rate (%) (at least {min_matchup} matchups)")
    fig.gca().set_ylabel("Win rate increase from base win rate (%)")
    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png")
    buffer.seek(0)  # Reset pointer to the start

    return StreamingResponse(buffer, media_type="image/png")


@app.get("/teamup/{hero}")
async def get_teamups_for(
    driver: SqliteSession, heroes: HeroList, hero, min_matchup: int = 3
):
    hero_name_to_heroes = {h.name: h for h in heroes}
    matchup: list[Teamup] = await fetch_teamup_winrate_for(
        driver, hero, min_matchup=min_matchup
    )
    x = [m.teamup_rate for m in matchup]
    y = [m.win_delta for m in matchup]
    images = [
        Image.open(
            Path("/asset")
            / (image_url_to_filename(hero_name_to_heroes[m.teamup].image) + ".png")
        )
        for m in matchup
    ]
    fig = plot_win_pick(
        x,
        y,
        images,
        title="Win rate increase vs Teamup rate",
        ylims=(-100.0, 100.0),
        xlims=(0, 60.0),
        y_line=0,
    )
    fig.gca().set_xlabel(f"Teamup rate (%) (at least {min_matchup} matchups)")
    fig.gca().set_ylabel("Win rate increase from base win rate (%)")

    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png")
    buffer.seek(0)  # Reset pointer to the start

    return StreamingResponse(buffer, media_type="image/png")


@app.get("/")
async def root():
    return {"message": "Go to /docs for usage"}
