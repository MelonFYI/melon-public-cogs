import discord
from redbot.core import commands

class LinkChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if any(link in message.content.lower() for link in ["http://", "https://", "www."]):
            await message.channel.send("⚠️ **Warning**: Your message contains a link. Please make sure it is appropriate and relevant to the conversation.")

def setup(bot):
    bot.add_cog(LinkChecker(bot))
