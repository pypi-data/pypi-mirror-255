from helpmepick.models.champion import Champion
from helpmepick.models.role import Role

RolePool = dict[Champion, int]


class Pool:
    def __init__(self, pool: dict[Role, RolePool]) -> None:
        if set(pool) != set(Role):
            raise ValueError(
                f"Passed pool is missing roles: {', '.join(set(Role) - set(pool))}"
            )
        self.pool = pool

    def _exists(self, champion: Champion, role: Role, isin: bool = True) -> None:
        """Raises an exception if champion does not exist for a role,
        or if it does if isin is False."""
        if (champion in self.pool[role]) ^ isin:
            raise ValueError(
                f"Champion {champion} {'not' if isin else 'already'} in pool for role {role}"
            )

    def add_champion(self, champion: Champion, role: Role, priority: int) -> None:
        self._exists(champion, role, isin=False)
        if champion in self.pool[role]:
            raise ValueError(f"Champion {champion} already in pool for role {role}")
        self.pool[role][champion] = priority

    def delete_champion(self, champion: Champion, role: Role) -> None:
        self._exists(champion, role)
        del self.pool[role][champion]

    def edit_champion(self, champion: Champion, role: Role, priority: int) -> None:
        self._exists(champion, role)
        self.pool[role][champion] = priority

    def get_champions_for(self, role: Role) -> RolePool:
        return self.pool[role]
