from discord.ext.commands import Cog


class StudyNew(Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(StudyNew(bot))
    print('NEW study cog ready')
