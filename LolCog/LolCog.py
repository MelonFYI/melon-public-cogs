import discord
from redbot.core import commands
from riotwatcher import LolWatcher

class LolCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = None
        self.watcher = None

    @commands.command()
    async def setapikey(self, ctx, api_key: str):
        self.api_key = api_key
        self.watcher = LolWatcher(api_key)
        await ctx.send("API key set.")

    @commands.command()
    async def lol(self, ctx, name: str):
        if self.api_key is None:
            await ctx.send("Please set the Riot API key using the `setapikey` command.")
            return

        regions = ["na1", "euw1", "kr", "jp1", "eun1", "br1", "oc1", "tr1", "ru", "la1", "la2"]
        region = None
        while region is None:
            await ctx.send("Please enter the region the player is on (e.g. na1, euw1):")
            region_input = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author)
            if region_input.content.lower() in regions:
                region = region_input.content.lower()
            else:
                await ctx.send("Invalid region. Please try again.")

        summoner = self.watcher.summoner.by_name(region, name)
        if summoner is None:
            await ctx.send("Summoner not found.")
            return

        matches = self.watcher.match.matchlist_by_account(region, summoner["accountId"], end_index=6)
        if matches is None:
            await ctx.send("No matches found.")
            return

        for match in matches["matches"]:
            match_info = self.watcher.match.by_id(region, match["gameId"])
            participant_id = None
            for participant in match_info["participantIdentities"]:
                if participant["player"]["summonerName"].lower() == name.lower():
                    participant_id = participant["participantId"]
                    break
            if participant_id is None:
                await ctx.send("Error: could not find participant ID.")
                return
            participant_stats = None
            for participant in match_info["participants"]:
                if participant["participantId"] == participant_id:
                    participant_stats = participant["stats"]
                    break
            if participant_stats is None:
                await ctx.send("Error: could not find participant stats.")
                return
            win = "Victory" if participant_stats["win"] else "Defeat"
            champ = self.watcher.static_champ_list()["data"][str(match["champion"])]["name"]
            await ctx.send(f"{win} as {champ} ({match['gameId']})")

def setup(bot):
    bot.add_cog(LolCog(bot))
