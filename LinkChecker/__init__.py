from .linkchecker import LinkChecker

def setup(bot):
    bot.add_cog(LinkChecker(bot))
