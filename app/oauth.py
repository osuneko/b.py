import requests
import uuid

from requests import HTTPError

import app.settings
from app.constants.privileges import Privileges
from app.logging import log, Ansi


class DiscordOAuth:

   # list of session ids to disguise the user id in the state parameter to prevent users from verifying random accounts by changing the user id
    session_ids = { }

    def get_link(user_id: int) -> str:
        """Returns a oauth link for a given user id."""

        DiscordOAuth.session_ids = {sid: uid for sid, uid in DiscordOAuth.session_ids.items() if uid != user_id}

        session_id = uuid.uuid4().__str__()
        DiscordOAuth.session_ids[session_id] = user_id
        return f"https://discord.com/oauth2/authorize?response_type=code&client_id={app.settings.DISCORD_CLIENT_ID}&scope=identify&redirect_uri=https://osu.{app.settings.DOMAIN}/discord_oauth_callback&&state={session_id}"

    async def verify_user(code: int, session_id: str) -> int:
        """
        Handles the reception of an oauth code by requesting a token from Discord and verifies the user by grabbing the discord's user ID.
        Returns:
            errorcode
            0 = success
            1 = wrong session id
            2 = wrong code
            3 = discord call error
            4 = discord account already in use

            discord name
            The discord name of the user or "" if an error occured

            discord user id
            The discord user id of the user or 0 if an error occured

            discord avatar id
            The discord avatar id of the user or 0 if an error occured
        """

        if not session_id in DiscordOAuth.session_ids:
            return 1, "", 0, 0


        headers = { "Content-Type": "application/x-www-form-urlencoded" }
        data = {
            "client_id": app.settings.DISCORD_CLIENT_ID,
            "client_secret": app.settings.DISCORD_CLIENT_SECRET,
            "grant_type": 'authorization_code',
            "code": code,
            "redirect_uri": f"https://osu.{app.settings.DOMAIN}/discord_oauth_callback"
        }

        r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
        try:
            r.raise_for_status()
        except HTTPError:
            return 2, "", 0, 0

        headers = { "Authorization": f"Bearer {r.json()['access_token']}" }

        r = requests.get("https://discord.com/api/users/@me", headers=headers)
        try:
            r.raise_for_status()
        except HTTPError:
            return 3, "", 0, 0

        discord_name = f"{r.json()['username']}#{r.json()['discriminator']}"
        discord_id = r.json()["id"]
        avatar_id = r.json()["avatar"]

        if await app.state.services.database.fetch_one("SELECT 1 FROM users WHERE discord_id = :discord_id", {"discord_id": discord_id}):
            return 4, "", 0, 0

        user_id = DiscordOAuth.session_ids[session_id]
        del DiscordOAuth.session_ids[session_id]
        await app.state.services.database.execute("UPDATE users SET discord_id = :discord_id WHERE id = :user_id", {"discord_id": discord_id, "user_id": user_id})

        p = await app.state.sessions.players.from_cache_or_sql(id=user_id)

        await p.add_privs(Privileges.VERIFIED)

        if p.id == 3:
            # this is the first player registering on
            # the server, grant them full privileges.
            await p.add_privs(
                Privileges.STAFF
                | Privileges.NOMINATOR
                | Privileges.WHITELISTED
                | Privileges.TOURNAMENT
                | Privileges.DONATOR
                | Privileges.ALUMNI,
            )

        log(f"User {p} was linked to discord user {discord_id} ({discord_name})", Ansi.LCYAN)

        p.send_bot(f"Your account was successfully linked and verified! ({discord_name})")

        return 0, discord_name, discord_id, avatar_id
