from asyncio import sleep
from datetime import datetime, timedelta
from platform import python_version
from time import time
from typing import Optional

from apscheduler.triggers.cron import CronTrigger
from discord import Activity, ActivityType, Embed
from discord import __version__ as discord_version
from discord.ext.commands import Cog
from discord.ext.commands import command
from psutil import Process, virtual_memory

from .achieve import grant_check, grant
from ..db import db


class Meta(Cog):
    def __init__(self, bot):
        self.bot = bot

        self._message = "playing {guilds:,}개의 서버 / {users:,}명의 유저 | 커뉴야 도움"

        bot.scheduler.add_job(self.set, CronTrigger(second=10))

    @property
    def message(self):
        return self._message.format(users=len(self.bot.users), guilds=len(self.bot.guilds))

    @message.setter
    def message(self, value):
        if value.split(" ")[0] not in ("playing", "watching", "listening", "streaming"):
            raise ValueError("Invalid activity type.")

        self._message = value

    async def set(self):
        _type, _name = self.message.split(" ", maxsplit=1)

        await self.bot.change_presence(activity=Activity(
            name=_name, type=getattr(ActivityType, _type, ActivityType.playing)
        ))

    @command(name="상메업뎃111")
    async def update_m(self, ctx):
        while True:
            await self.set()
            await sleep(600)

    @command(name='서버개수')
    async def server_count(self, ctx):
        await ctx.send(len(self.bot.guilds))

    # @command(name="setactivity")
    # async def set_activity_message(self, ctx, *, text: str):
    # 	self.message = text
    # 	await self.set()

    @command(name="핑")
    async def ping(self, ctx, check: Optional[str]):
        start = time()
        message = await ctx.send(f"디스코드 API 지연시간: {self.bot.latency * 1000:,.0f} ms")
        end = time()

        await message.edit(
            content=f"디스코드 API 지연시간: {self.bot.latency * 1000:,.0f} ms\n봇 응답 시간: {(end - start) * 1000:,.0f} ms")
        if end - start > 2:
            l = grant_check("도배 멈춰...", ctx.author.id)
            if l == 1:
                await grant(ctx, "도배 멈춰...", "`커뉴야 핑`명령어에서 핑이 2000ms를 초과한다는 답변을 받으세요")

        if check == "싫어":
            l = grant_check("ㄹㅇㅋㅋ", ctx.author.id)
            if l == 1:
                await grant(ctx, "ㄹㅇㅋㅋ", "모두가 공감할 내용을 치세요")
                db.execute("UPDATE games SET user_setting = user_setting + 2 WHERE UserID = ?", ctx.author.id)
                db.commit()
        if check == "싫어ㅓ":
            l = grant_check("ㅇㅇㅌㅌ", ctx.author.id)
            if l == 1:
                await grant(ctx, "ㅇㅇㅌㅌ", "모두가 공감항 내용을 치세요")

    @command(name="스탯")
    async def show_bot_stats(self, ctx):
        embed = Embed(title="봇 스탯",
                      colour=ctx.author.colour,
                      thumbnail=self.bot.user.avatar_url,
                      timestamp=datetime.utcnow())

        proc = Process()
        with proc.oneshot():
            uptime = timedelta(seconds=time() - proc.create_time())
            cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
            mem_total = virtual_memory().total / 1000000
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)

        fields = [
            ("봇 버전:", self.bot.VERSION, True),
            ("파이썬 버전:", python_version(), True),
            ("discord.py 버전", discord_version, True),
            ("켜진 후 지난 시간", uptime, True),
            ("CPU 처리 시간", cpu_time, True),
            ("쳐먹는 메모리", f"{mem_usage:,.3f} / {mem_total:,.0f} MB ({mem_of_total:.0f}%)", True),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @command(name="꺼져")
    async def shutdown(self, ctx):
        if ctx.author.id == 724496900920705045:
            await ctx.send("봇을 끄는 중이에요...")

            count_channels = db.records("SELECT ChannelID, num FROM channels WHERE channel_type & 1 == 1")
            for channel_to_send in count_channels:
                try:
                    await self.bot.get_channel(channel_to_send[0]).send(
                        f"{channel_to_send[1]} 봇이 잠시 동안 오프라인이 될 거에요. 그 동안은 잠시 숫자를 세지 말아 주세요!")
                except AttributeError:
                    db.execute("DELETE FROM channels WHERE ChannelID = ?", channel_to_send[0])
            with open("./data/banlist.txt", "w", encoding="utf-8") as f:
                f.writelines([f"{item}\n" for item in self.bot.banlist])
            db.commit()

            db.commit()
            self.bot.scheduler.shutdown()
            await self.bot.logout()
        else:
            await ctx.send("ㅈㄹ")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("meta")


def setup(bot):
    bot.add_cog(Meta(bot))