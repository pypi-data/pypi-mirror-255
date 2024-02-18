import csv
from pathlib import Path
from helpmepick.models.champion import Champion
from helpmepick.persistence.base import BaseChampIO


class CsvChampIO(BaseChampIO):
    def __init__(self, data_folder: Path) -> None:
        super().__init__(data_folder)

    def get_champ_path(self, champion: Champion) -> Path:
        return self.root / f"{champion}.csv"

    def load_champ(self, champion: Champion) -> list[tuple[Champion, float, int]]:
        with open(self.get_champ_path(champion)) as f:
            r = csv.reader(f)
            res = [
                (Champion(champion), float(wr), int(matches))
                for champion, wr, matches in r
            ]
        return res

    def save_champ(
        self, champion: Champion, data: list[tuple[Champion, float, int]]
    ) -> None:
        with open(self.get_champ_path(champion), "wt", newline='') as f:
            w = csv.writer(f)
            w.writerows(data)
        return
