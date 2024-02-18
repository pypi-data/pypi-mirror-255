from enum import Enum


class Tier(str, Enum):
    chall = "challenger"
    gm = "grandmaster"
    m = "master"
    d = "diamond"
    e = "emerald"
    p = "platinum"
    g = "gold"
    s = "silver"
    b = "bronze"
    i = "iron"
    m_ = "master_plus"
    d_ = "diamond_plus"
    e_ = "emerald_plus"
    p_ = "platinum_plus"
    g_ = "gold_plus"
