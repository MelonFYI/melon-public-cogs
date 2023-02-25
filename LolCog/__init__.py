from redbot.core.bot import Red

from .lolcog import LolCog


async def setup(bot: Red):
    cog = LolCog(bot)
    bot.add_cog(cog)
