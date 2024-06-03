from datetime import datetime, timedelta
from typing import Optional

from discord import Embed, Member
from discord.ext.commands import Cog
from discord.ext.commands import command


class Info(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="유저정보", aliases=["계정정보", "계정"])
    async def user_info(self, ctx, *, target: Optional[Member]):
        target = target or ctx.author

        embed = Embed(title="사용자 정보",
                      colour=target.colour,
                      timestamp=datetime.now())

        embed.set_thumbnail(url=target.avatar_url)

        fields = [("사용자명", str(target), True),
                  ("사용자 아이디", target.id, True),
                  ("봇인지 여부", target.bot, True),
                  ("가장 높은 역할", target.top_role.mention, True),
                  # ("현재 상태", str(target.status).title(), True),
                  # ("상태메세지",
                  #  f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}",
                  #  True),
                  ("계정 생성 날짜", target.created_at + timedelta(hours=9), True),
                  ("서버에 들어온 날짜", target.joined_at + timedelta(hours=9), True),
                  ("들어온 후 지난 시간", datetime.now() - target.joined_at, True),
                  ("서버 부스트 여부", bool(target.premium_since), True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @command(name="서버정보")
    async def server_info(self, ctx):
        embed = Embed(title="서버정보",
                      colour=0xffd6fe,
                      timestamp=datetime.now())
        owner = str(ctx.guild.owner)

        embed.set_thumbnail(url=ctx.guild.icon_url)

        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

        fields = [("ID", ctx.guild.id, True),
                  ("서버장", owner, True),
                  ("생성 날짜", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                  ("총 멤버 수", len(ctx.guild.members), True),
                  ("사람 멤버 수", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
                  ("봇들", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
                  ("밴당한 ㅂㅅ들", len(await ctx.guild.bans()), True),
                  # ("멤버 상태",
                  #  f"온라인: {statuses[0]}명\n 자리 비움: {statuses[1]}명\n 다른 용무 중: {statuses[2]}명\n 오프라인: {statuses[3]}",
                  #  True),
                  ("채팅채널", len(ctx.guild.text_channels), True),
                  ("음성채널", len(ctx.guild.voice_channels), True),
                  ("카테고리", len(ctx.guild.categories), True),
                  ("역할", len(ctx.guild.roles), True),
                  ("초대", len(await ctx.guild.invites()), True),
                  ("\u200b", "\u200b", True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("info")


def setup(bot):
    bot.add_cog(Info(bot))