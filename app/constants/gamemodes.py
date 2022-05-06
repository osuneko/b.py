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
    "vn!cs0",
    "rx!std",
    "rx!taiko",
    "rx!catch",
    "rx!mania",  # unused
    "rx!cs0",
    "ap!std",
    "ap!taiko",  # unused
    "ap!catch",  # unused
    "ap!mania",  # unused
    "ap!cs0"
)


@unique
@pymysql_encode(escape_enum)
class GameMode(IntEnum):
    VANILLA_OSU = 0
    VANILLA_TAIKO = 1
    VANILLA_CATCH = 2
    VANILLA_MANIA = 3
    VANILLA_CS0 = 4

    RELAX_OSU = 5
    RELAX_TAIKO = 6
    RELAX_CATCH = 7
    RELAX_MANIA = 8  # unused
    RELAX_CS0 = 9 

    AUTOPILOT_OSU = 10
    AUTOPILOT_TAIKO = 11  # unused
    AUTOPILOT_CATCH = 12  # unused
    AUTOPILOT_MANIA = 13  # unused
    AUTOPILOT_CS0 = 14

    @classmethod
    @functools.lru_cache(maxsize=32)
    def from_params(cls, mode_vn: int, mods: Mods) -> GameMode:
        mode = mode_vn

        if mods & Mods.AUTOPILOT:
            mode += 10
        elif mods & Mods.RELAX:
            mode += 5

        return cls(mode)

    @property
    def as_vanilla(self) -> int:
        if self.value in (10, 14):
            return self.value - 10
        elif self.value in (5, 6, 7, 9):
            return self.value - 5
        else:
            return self.value

    # i don't think we wanna cache this..?
    def as_cs0(self, bmap: Beatmap) -> int:
        if bmap.cs == 0:
            if self.value in (10, 14):
                return self.AUTOPILOT_CS0
            elif self.value in (5, 6, 7, 9):
                return self.RELAX_CS0
            else:
                return self.VANILLA_CS0

        return None

    def __repr__(self) -> str:
        return GAMEMODE_REPR_LIST[self.value]
