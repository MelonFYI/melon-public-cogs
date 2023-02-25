import discord
from discord.ext import commands
import requests

class LolCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "https://{region}.api.riotgames.com/lol/"
        self.api_key = None
    
    @commands.command()
    async def set_api_key(self, ctx, key):
        """Set the Riot API key."""
        self.api_key = key
        await ctx.send("API key set.")
    
    @commands.command()
    async def last_matches(self, ctx, region, username):
        """Display the last 6 matches for the given user."""
        if self.api_key is None:
            await ctx.send("API key not set. Please use the `set_api_key` command to set the API key.")
            return
        
        # Get summoner ID
        summoner_url = self.base_url.format(region=region) + f"summoner/v4/summoners/by-name/{username}"
        headers = {"X-Riot-Token": self.api_key}
        summoner_response = requests.get(summoner_url, headers=headers)
        if summoner_response.status_code == 404:
            await ctx.send("Summoner not found.")
            return
        elif summoner_response.status_code != 200:
            await ctx.send("Error getting summoner information.")
            return
        summoner_id = summoner_response.json()["id"]
        
        # Get match list
        match_list_url = self.base_url.format(region=region) + f"match/v4/matchlists/by-account/{summoner_id}?endIndex=6"
        match_list_response = requests.get(match_list_url, headers=headers)
        if match_list_response.status_code != 200:
            await ctx.send("Error getting match list.")
            return
        match_list = match_list_response.json()["matches"]
        
        # Get match details
        matches = []
        for match in match_list:
            match_url = self.base_url.format(region=region) + f"match/v4/matches/{match['gameId']}"
            match_response = requests.get(match_url, headers=headers)
            if match_response.status_code != 200:
                await ctx.send("Error getting match information.")
                return
            match_data = match_response.json()
            participant_id = None
            for participant in match_data["participantIdentities"]:
                if participant["player"]["summonerName"].lower() == username.lower():
                    participant_id = participant["participantId"]
                    break
            if participant_id is None:
                await ctx.send(f"Error finding participant ID for {username}.")
                return
            participant_data = next(p for p in match_data["participants"] if p["participantId"] == participant_id)
            match_result = "win" if participant_data["stats"]["win"] else "loss"
            match_kills = participant_data["stats"]["kills"]
            match_deaths = participant_data["stats"]["deaths"]
            match_assists = participant_data["stats"]["assists"]
            matches.append(f"{match_result} ({match_kills}/{match_deaths}/{match_assists})")
        
        # Send match details to Discord
        matches_text = "\n".join(matches)
        await ctx.send(f"Last 6 matches for {username}:\n{matches_text}")
