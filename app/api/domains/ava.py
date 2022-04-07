""" ava: avatar server (for both ingame & external) """
from __future__ import annotations

import os
import random

from pathlib import Path
from typing import Literal

from fastapi import APIRouter
from fastapi import Response
from fastapi.responses import FileResponse

import app.state
import app.utils

AVATARS_PATH = Path.cwd() / ".data/avatars"
DEFAULT_AVATARS_PATH = AVATARS_PATH / "default"

router = APIRouter(tags=["Avatars"])


@router.get("/favicon.ico")
async def get_favicon() -> Response:
    return FileResponse(get_default_avatar(True), media_type="image/ico")


@router.get("/{user_id}.{extension}")
async def get_avatar(
    user_id: int,
    extension: Literal["jpg", "jpeg", "png"],
) -> Response:
    avatar_path = AVATARS_PATH / f"{user_id}.{extension}"

    if not avatar_path.exists():
        avatar_path = get_default_avatar()

    return FileResponse(
        avatar_path,
        media_type=app.utils.get_media_type(extension),
    )


@router.get("/{user_id}")
async def get_avatar_osu(user_id: int) -> Response:
    for extension in ("jpg", "jpeg", "png"):
        avatar_path = AVATARS_PATH / f"{user_id}.{extension}"

        if avatar_path.exists():
            return FileResponse(
                avatar_path,
                media_type=app.utils.get_media_type(extension),
            )

    return FileResponse(get_default_avatar(), media_type="image/jpeg")


def get_default_avatar(default = False) -> str:
    count = len(next(os.walk(DEFAULT_AVATARS_PATH))[2])

    print(count)

    if default:
        return DEFAULT_AVATARS_PATH / "1.jpg"

    index = random.randint(1, count)

    return DEFAULT_AVATARS_PATH / f"{index}.jpg"
