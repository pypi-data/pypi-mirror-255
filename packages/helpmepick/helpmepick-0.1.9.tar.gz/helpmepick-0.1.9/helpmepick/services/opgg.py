import requests
import bs4
import re
from warnings import warn
from helpmepick.models.champion import Champion
from helpmepick.models.region import Region
from helpmepick.models.role import Role
from helpmepick.models.tier import Tier
from rapidfuzz.distance.DamerauLevenshtein import distance


def retrieve_opgg_data(
    champion: Champion, role: Role, region: Region = Region.g, tier: Tier = Tier.e_
) -> requests.models.Response:
    url = f"https://www.op.gg/champions/{champion.name}/counters/{role.name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    params = {"region": region, "tier": tier}
    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code != 200:
        raise ValueError(
            f"Request on url {resp.url} threw status code {resp.status_code}"
        )
    return resp


def parse_champion_name(name: str) -> Champion:
    plain = "".join([letter for letter in name.lower() if letter.isalpha()])
    # try to fit it plainly, else use a min-dist approach
    try:
        champion = Champion(plain)
    except ValueError:
        mindist = 100.0
        champion = Champion.annie
        for candidate in Champion:
            dist = distance(plain, candidate)
            if dist < mindist:
                mindist = dist
                champion = candidate
            # special case: Nunu & Willump - like names
            if plain.startswith(candidate):
                champion = candidate
                break
            # this shouldn't happen but oh well
            if dist == 0:
                break
    return champion


def parse_row(row: str) -> tuple[Champion, float, int]:
    pattern = r"(\D+)(\d+[.,]?\d*)%(\d+[.,]?\d+)"
    res = re.findall(pattern, row)
    if len(res) > 1:
        warn(f"Warning: parsing row {row} threw multiple result groups")
    name, winrate, matches = res[0]
    # matches number may contain a comma, e.g. '1,584'
    return parse_champion_name(name), float(winrate), int(matches.replace(",", ""))


def parse_data(resp: requests.models.Response) -> list[tuple[Champion, float, int]]:
    soup = bs4.BeautifulSoup(resp.content, "html.parser")
    table_list = soup.find_all("table")
    if len(table_list) != 1:
        warn(f"Warning: table list for url {resp.url} has multiple tables")
    # first row is omitted as it's the header
    rows = table_list[0].find_all("tr")[1:]
    return [parse_row(row.text) for row in rows]
