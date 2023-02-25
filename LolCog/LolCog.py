import discord
from redbot.core import commands
import requests


class LolCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = None

    async def get_api_key(self):
        if not self.api_key:
            self.api_key = await self.bot.get_shared_api_tokens("lol_api")
        return self.api_key.get("api_key")

    @commands.command()
    async def setlolapikey(self, ctx, api_key):
        await self.bot.set_shared_api_tokens("lol_api", api_key=api_key)
        await ctx.send("Riot API key set!")

    @commands.command()
    async def last6(self, ctx, username: str, region: str):
        api_key = await self.get_api_key()
        if api_key is None:
            await ctx.send("Please set a Riot API key with the 'setlolapikey' command.")
            return
        try:
            r = requests.get(
                f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{username}?api_key={api_key}"
            )
            r.raise_for_status()
            account_id = r.json()["accountId"]
            r = requests.get(
                f"https://{region}.api.riotgames.com/lol/match/v4/matchlists/by-account/{account_id}?api_key={api_key}"
            )
            r.raise_for_status()
            matches = r.json()["matches"][:6]
            embed = discord.Embed(
                title=f"Last 6 matches for {username} on {region.upper()} server"
            )
            for match in matches:
                r = requests.get(
                    f"https://{region}.api.riotgames.com/lol/match/v4/matches/{match['gameId']}?api_key={api_key}"
                )
                r.raise_for_status()
                match_data = r.json()
                participants = match_data["participantIdentities"]
                participant_id = next(
                    participant["participantId"]
                    for participant in participants
                    if participant["player"]["accountId"] == account_id
                )
                participant_data = next(
                    participant
                    for participant in match_data["participants"]
                    if participant["participantId"] == participant_id
                )
                champ_id = participant_data["championId"]
                champ_name = requests.get(
                    f"http://ddragon.leagueoflegends.com/cdn/11.5.1/data/en_US/champion.json"
                ).json()["data"][str(champ_id)]["name"]
                embed.add_field(
                    name=f"**{champ_name}**\n{match['role'].title()} {match['lane'].title()}",
                    value=f"Match ID: [{match['gameId']}](https://{region}.matchhistory.leagueoflegends.com/{region}/match/{match['gameId']})",
                    inline=False,
                )
            await ctx.send(embed=embed)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                await ctx.send("Could not find player or region.")
            else:
                await ctx.send("An error occurred.")
        except KeyError:
            await ctx.send("An error occurred.")
