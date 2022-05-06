from __future__ import annotations

import functools
from enum import IntEnum
from enum import unique

from app.constants.mods import Mods
from app.utils import escape_enum
from app.utils import pymysql_encode

__all__ = (
    "GAMEMODE_REPR_LIST",
    "GameMode",
)

GAMEMODE_REPR_LIST = (
    "vn!std",
    "vn!taiko",
    "vn!catch",
    "vn!mania",
    "rx!std",
    "rx!taiko",
    "rx!catch",
    "rx!mania",  # unused
    "ap!std",
    "ap!taiko",  # unused
    "ap!catch",  # unused
    "ap!mania",  # unused
    "vn!std", # cs0
    "rx!std", # cs0
    "ap!std", # cs0
)


@unique
@pymysql_encode(escape_enum)
class GameMode(IntEnum):
    VANILLA_OSU = 0
    VANILLA_TAIKO = 1
    VANILLA_CATCH = 2
    VANILLA_MANIA = 3

    RELAX_OSU = 4
    RELAX_TAIKO = 5
    RELAX_CATCH = 6
    RELAX_MANIA = 7  # unused

    AUTOPILOT_OSU = 8
    AUTOPILOT_TAIKO = 9  # unused
    AUTOPILOT_CATCH = 10  # unused
    AUTOPILOT_MANIA = 11  # unused
    
    VANILLA_CS0 = 12
    RELAX_CS0 = 13
    AUTOPILOT_CS0 = 14

    @classmethod
    @functools.lru_cache(maxsize=32)
    def from_params(cls, mode_vn: int, mods: Mods) -> GameMode:
        mode = mode_vn

        if mods & Mods.AUTOPILOT:
            mode += 8
        elif mods & Mods.RELAX:
            mode += 4

        return cls(mode)

    @functools.cached_property
    def as_vanilla(self) -> int:
        if self.value & self.AUTOPILOT_OSU:
            return self.value - 8
        elif self.value & self.RELAX_OSU:
            return self.value - 4
        else:
            return self.value

    # i don't think we wanna cache this..?
    def as_cs0(self, bmap: Beatmap) -> int:
        if bmap.cs == 0:
            if self.value & self.RELAX_OSU:
                return self.RELAX_CS0
            elif self.value & self.AUTOPILOT_OSU:
                return self.AUTOPILOT_CS0
            else:
                return self.VANILLA_CS0

        return None

    def __repr__(self) -> str:
        return GAMEMODE_REPR_LIST[self.value]
