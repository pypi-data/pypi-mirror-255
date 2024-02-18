from abc import ABC, abstractmethod
from typing import Iterator
from helpmepick.models.pool import Pool, RolePool


class BasePoolIO(ABC):
    @abstractmethod
    def load_pool(self) -> Pool:
        pass

    @abstractmethod
    def save_pool(self, pool: Pool) -> None:
        pass

    def orderedpool(self, rolepool: RolePool) -> Iterator[tuple[str,int]]:
        """Iterate through a RolePool first sorted by prio, then champion name."""
        for k, v in sorted(rolepool.items(), key=lambda t: t[::-1]):
            yield k,v
