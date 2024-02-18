from enum import Enum


class Role(str, Enum):
    top = "top"
    jungle = "jungle"
    mid = "mid"
    bot = "bot"
    support = "support"


ALL_ROLE_NAMES = {role.name for role in Role}
