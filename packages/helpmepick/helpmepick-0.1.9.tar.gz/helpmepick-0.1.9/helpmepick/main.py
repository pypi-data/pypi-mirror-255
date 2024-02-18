from collections import defaultdict
from enum import EnumMeta
from pathlib import Path
from helpmepick.models.champion import Champion
from helpmepick.models.region import Region
from helpmepick.models.role import Role, ALL_ROLE_NAMES
from helpmepick.models.tier import Tier
from helpmepick.models.pool import Pool
from helpmepick.persistence.csv import CsvChampIO
from helpmepick.pool.yaml import YamlPoolIO
from helpmepick.utils.throttler import Throttler
from helpmepick.services.opgg import retrieve_opgg_data, parse_data

from typing import Annotated, Callable, Iterable
import typer

DEFAULT_POOL_FNAME = "./pool.yaml"
DEFAULT_DATA_FOLDER = "./data"


def completer(cls: EnumMeta) -> Callable[[str], Iterable[str]]:
    def complete_f(x: str) -> Iterable[str]:
        for elem in cls:
            if elem.value.startswith(x):
                yield elem

    return complete_f


role_cli = Annotated[
    Role, typer.Argument(help="Selected Role", autocompletion=completer(Role))
]

champ_cli = Annotated[
    Champion, typer.Argument(help="Selected Champion", autocompletion=completer(Champion))
]

app = typer.Typer()
poolIO = YamlPoolIO(Path(DEFAULT_POOL_FNAME))

@app.command()
def init():
    # TODO: de-hardcode this, move onto config file
    pool_fname = DEFAULT_POOL_FNAME
    data_folder = DEFAULT_DATA_FOLDER

    pool_path = Path(pool_fname)
    if not pool_path.exists():
        print("Creating pool file at", str(pool_path))
        #pool_path.touch()
        poolIO.save_pool(Pool({Role(role):{} for role in ALL_ROLE_NAMES}))

    data_path = Path(data_folder)
    if not data_path.exists():
        print("Creating data folder at", str(data_path))
        data_path.mkdir()
        for role in ALL_ROLE_NAMES:
            (data_path / role).mkdir()


@app.command()
def add(
    role: role_cli,
    champion: champ_cli,
    priority: Annotated[
        int, typer.Argument(help="Priority for this champion, 1 is maximum")
    ],
):
    pool = poolIO.load_pool()
    pool.add_champion(champion, role, priority)
    poolIO.save_pool(pool)
    print(
        f"Champion {champion.name} successfully added to {role.name} role pool with priority {priority}"
    )

@app.command()
def update(role: role_cli):
    # TODO: add params for throttling, tiers, allow all roles, etc.
    pool = poolIO.load_pool()
    root_path = Path(DEFAULT_DATA_FOLDER)
    print("Updating role", role.name)
    champIO = CsvChampIO(root_path / role.name)
    for champ in Throttler(pool.get_champions_for(Role(role))):
        print("Updating champion", champ.name, end="...\t")
        resp = retrieve_opgg_data(champ, role)
        data = parse_data(resp)
        champIO.save_champ(champ,data)
        print("OK")

@app.command("vs")
def recommend(role: role_cli, enemy_champion: champ_cli):
    # TODO: add support for champions in pool where enemy is not represented
    rolepool = poolIO.load_pool().get_champions_for(role)
    root_path = Path(DEFAULT_DATA_FOLDER)
    champIO = CsvChampIO(root_path / role.name)
    matchup_data = []
    no_data = []
    # compile data
    for champion, priority in rolepool.items():
        # no mirror matchups
        if champion == enemy_champion:
            continue
        data_dict = {
            champ:(winrate, games) 
            for champ, winrate, games 
            in champIO.load_champ(champion)
        }
        if enemy_champion in data_dict:
            matchup_data.append(
                (champion, priority, *data_dict[enemy_champion])
            )
        else:
            no_data.append((champion, priority))
    # print it sorted by winrate>priority>games
    for champion, priority, winrate, games in sorted(matchup_data, key=lambda x: (-x[2], x[1], -x[3], x[0])):
        print(f"{champion.name: >15}: {winrate: 5.2f}% | {games: >5} games | Priority: {priority}")
    
    if len(no_data) > 0:
        print("No data for the following champions:")
        for champion, priority in sorted(no_data, key=lambda x: (x[1], x[0])):
            print(f"{champion.name: >15} | Priority: {priority}")

@app.command()
def ban(
    role: role_cli, 
    k: Annotated[
        int, typer.Argument(help="How many champions to list")
    ] = 5,
    min_games: Annotated[
        int, typer.Argument(help="Minimum number of games for a matchup to be considered")
    ] = 100):
    rolepool = poolIO.load_pool().get_champions_for(role)
    root_path = Path(DEFAULT_DATA_FOLDER)
    champIO = CsvChampIO(root_path / role.name)
    max_winrate = defaultdict(lambda: (0.0, 0.0))
    for champion, priority in rolepool.items():
        for enemy_champ, winrate, games in champIO.load_champ(champion):
            if games < min_games:
                continue
            max_winrate[enemy_champ] = max(max_winrate[enemy_champ], (winrate, games))
    results = sorted(max_winrate.items(), key= lambda x: (x[1],x[0]))[:k]
    for champion, (winrate, games) in results:
        print(f"{champion.name: >15} | Max winrate: {winrate: 5.2f}% ({games: >5} games)")

def main():
    app()

if __name__ == "__main__":
    main()