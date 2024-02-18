from pathlib import Path
import yaml
from helpmepick.models.champion import Champion
from helpmepick.models.pool import Pool
from helpmepick.models.role import Role
from helpmepick.pool.base import BasePoolIO


class YamlPoolIO(BasePoolIO):
    def __init__(self, path: Path) -> None:
        self.path = path

    def load_pool(self) -> Pool:
        assert self.path.exists(), f"Passed pool path {self.path} does not exist"
        with open(self.path) as f:
            pool = yaml.safe_load(f)
        return Pool(
            {
                Role(r): {Champion(c): prio for c, prio in self.orderedpool(rolepool)}
                for r, rolepool in pool.items()
            }
        )

    def save_pool(self, pool: Pool) -> None:
        serialized = {
            r.value: {c.name: prio for c, prio in self.orderedpool(rolepool)}
            for r, rolepool in pool.pool.items()
        }
        with open(self.path, "wt") as f:
            yaml.safe_dump(serialized, f, sort_keys=False)
