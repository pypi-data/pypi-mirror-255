from abc import ABC, abstractmethod
from pathlib import Path

from helpmepick.models.champion import Champion

class BaseChampIO(ABC):

    def __init__(self, data_folder: Path) -> None:
        assert data_folder.exists(), f"Passed data folder {data_folder} does not exist"
        assert data_folder.is_dir(), f"Passed data folder {data_folder} is not a directory"
        self.root = data_folder
    
    @abstractmethod
    def get_champ_path(self, champion: Champion) -> Path:
        pass

    @abstractmethod
    def load_champ(self, champion: Champion) -> list[tuple[Champion, float, int]]:
        pass

    @abstractmethod
    def save_champ(self, champion: Champion, data: list[tuple[Champion, float, int]]) -> None:
        pass
