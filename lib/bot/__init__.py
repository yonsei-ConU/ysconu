import traceback
import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Embed, Intents, Forbidden, Object
from discord.ext.commands import (Bot, CommandNotFound, BadArgument, MissingPermissions,
                                  MissingRequiredArgument, Context, CommandOnCooldown)
from nest_asyncio import apply
from time import sleep

from lib.cogs.achieve import grant_check, grant
from lib.db import db
from discord.app_commands import command as slash, choices, Choice

# -*- coding: utf-8 -*-

apply()
PREFIX = "커뉴야 "
OWNER_IDS = [724496900920705045]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument, MissingPermissions, Forbidden)
errors = set()


class ConU(Bot):
    def __init__(self, **options):
        super().__init__(command_prefix=("커뉴야 ", "ㅋ"),
                         owner_ids=OWNER_IDS,
                         intents=Intents.all(),
                         **options
                         )
        self.ready = False
        self.stdout = self.get_channel(773409630125817887)

        self.guild = self.get_guild(743101101401964647)
        self.scheduler = AsyncIOScheduler()

        try:
            with open("./data/banlist.txt", "r", encoding="utf-8") as f:
                self.banlist = [int(line.strip()) for line in f.readlines()]
        except FileNotFoundError:
            self.banlist = []

        db.autosave(self.scheduler)

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        await self.load_extension(f'lib.cogs.study_NEW')
        synced = await self.tree.sync()
        # synced = [2]
        print(f"동기화된 커맨드: {len(synced)}개")

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
                     ((member.id,) for member in self.guild.members if not member.bot))

        to_remove = []
        stored_members = db.column("SELECT UserID FROM exp")
        for id_ in stored_members:
            if not self.guild.get_member(id_):
                to_remove.append(id_)

        # db.multiexec("DELETE FROM exp WHERE UserID = ?",
        # 			 ((id_,) for id_ in to_remove))

        db.commit()

    async def process_commands(self, message):
        if message.author.bot:
            return

        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None:

            if ctx.guild is not None:

                ch = db.record("SELECT channel_type FROM channels WHERE channelid = ?", message.channel.id)
                try:
                    ch_ = ch[0] % 32 // 8
                except TypeError:
                    ch_ = 0
                if ch_ == 0:
                    pass
                elif ch_ == 1:
                    if str(ctx.command) in ["우주탐험", "잡초키우기", "오목", "퀴즈", "강화", "서버강화", "코인", "업다운", "운빨테스트", "서버추천",
                                            "가위바위보", "묵찌빠", "랜덤채팅", "프로필", "도잔과제", "커뉴핑크"]:
                        await ctx.send('이 채널은 커맨드금지 1레벨이 걸려 있어 이 커맨드를 사용할 수 없어요!')
                        return
                elif ch_ == 2:
                    if str(ctx.command) not in ["레벨", "경험치부스트", "커맨드금지", "경험치설정", "경험치부스트설정", "리더보드", "채널부스트",
                                                "채널부스트설정"]:
                        await ctx.send('이 채널은 커맨드금지 2레벨이 걸려 있어 이 커맨드를 사용할 수 없어요!')
                        return
                elif ch_ == 3 and str(ctx.command) != "커맨드금지":
                    await ctx.send('이 채널은 커맨드금지 3레벨이 걸려 있어 이 커맨드를 사용할 수 없어요!')
                    return
                try:
                    ch = ch[0] & 32
                except TypeError:
                    ch = 0
                if ch:
                    if str(ctx.command) == "올려":
                        return

            else:
                if ctx.command.name not in ["가위바위보", "묵찌빠", "오목", "코인", "도움", "업데이트", "공식서버", "초대", "문의", "퀴즈", "업다운",
                                       "관리", "꺼져", "운빨테스트", "공지", "골라", "서버시간", "랜덤숫자", "서버추천", "파이값", "말해", "골라", "섞어", "소수판정", "소인수분해", "글자수", "핑", "나중업뎃", "뀨", "스펙", "지분", "도전과제", "코인", "커뉴핑크", "계산"]:
                    await ctx.send("현재 개인 메세지에서는 사용할 수 없는 명령어에요! 이게 왜 안 되지 싶은 명령어는 주저하지 말고 `커뉴야 문의`로 물어보세요.")
                    return
            if message.author.id in self.banlist:
                await ctx.send("정지먹은 주제에 커맨드를 왜 쳐 써? :weary:")

            elif not self.ready:
                await ctx.send("ㅈㅁ요 저 방금 켜짐")

            else:
                await self.invoke(ctx)
                l = grant_check("커뉴봇 사용자", ctx.author.id)
                if l == 1:
                    await grant(ctx, "커뉴봇 사용자", "커뉴봇을 사용하세요")
                if ctx.author.id not in errors:
                    r = db.execute("UPDATE cmd_uses SET uses = uses + 1 WHERE USERID = ? AND command = ?",
                                   ctx.author.id,
                                   ctx.command.name)
                    db.commit()
                    if not r:
                        db.execute("INSERT INTO cmd_uses (USERID, command, uses) VALUES (?, ?, 1)", ctx.author.id,
                                   ctx.command.name)
                        db.commit()
                else:
                    errors.remove(ctx.author.id)
                if ctx.guild is not None:
                    await self.get_channel(806879079383040060).send(
                        f"{ctx.guild.name} {ctx.guild.id}\n{ctx.channel.name} {ctx.channel.id}\n{str(ctx.author)} {ctx.author.id}\n{ctx.command}")
                else:
                    await self.get_channel(806879079383040060).send(
                        f"DM\n{str(ctx.author)} {ctx.author.id}\n{ctx.command}")

    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        et = traceback.format_exc()
        if "Forbidden: 403" in et:
            return
        embed = Embed(title='<a:ablobweary:801762171008319508> 에러남 <a:ablobweary:801762171008319508>',
                              colour=0xe74c3c)  # Red
        embed.add_field(name='Event', value=err)
        embed.description = '```py\n%s\n```' % et
        await self.get_user(724496900920705045).send(embed=embed)
        if err == "on_command_error":
            await args[0].send("에러남")

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("입력해야 하는데 입력되지 않은 요소가 있어요. 명령어를 확인해 주세요.")

        elif isinstance(exc, CommandOnCooldown):
            if '도움' in ctx.message.content and ctx.command.name in {'잡초키우기', '우주탐험', '퀴즈', '커뉴핑크'}:
                ctx.command.reset_cooldown(ctx)
                await self.invoke(ctx)
                return
            await ctx.send(f"그 커맨드는 쿨탐을 돌고 있어요. {exc.retry_after:,.2f} 초 후에 다시 해 주세요.")
            errors.add(ctx.author.id)
            if exc.retry_after < 0.005:
                l = grant_check("쿨탐 버근가", ctx.author.id)
                if l == 1:
                    await grant(ctx, "쿨탐 버근가", "쿨타임이 있는 명령어에서 0.00초 후에 다시 하라는 내용을 보세요")

        elif hasattr(exc, "original"):
            # if isinstance(exc.original, HTTPException):
            # 	await ctx.send("Unable to send message.")

            if isinstance(exc.original, Forbidden):
                return

            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(743101101401964647)
            self.stdout = self.get_channel(773409630125817887)
            # self.scheduler.add_job(self.update_realtime_lb, CronTrigger(day_of_week=0, hour=0, minute=0, second=10))
            # self.scheduler.start()

            self.update_db()

            # for gid in [1040887723159994379, 998961724008972308, 1044512214171799582, 1232956416424284192]:
            #     await self.get_guild(gid).leave()

            guilds = db.records("SELECT GuildID FROM guilds")
            for guild in guilds:
                try:
                    gotten_guild = self.get_guild(guild[0])
                    print(gotten_guild.id)
                    print(gotten_guild.name)
                except AttributeError:
                    db.execute("DELETE FROM guilds WHERE GuildID = ?", guild[0])
                    db.execute("DELETE FROM mutes WHERE GuildID = ?", guild[0])
                    db.execute("DELETE FROM roles WHERE GuildID = ?", guild[0])
                    db.execute("DELETE FROM Giwons WHERE GuildID = ?", guild[0])
                    db.commit()
            print("guild optimize complete")
            channels = db.records("SELECT ChannelId FROM channels")
            for channel in channels:
                try:
                    print(self.get_channel(channel[0]).name)
                except AttributeError:
                    db.execute("DELETE FROM channels WHERE channelid = ?", channel[0])
                    db.commit()
            print("channel optimize complete")

            await self.stdout.send("봇 가동이 시작되었습니다.")
            self.ready = True
            print("bot ready")

        else:
            print("bot reconnected")


with open("../../token.txt", "r", encoding="utf-8") as tf:
    TOKEN = tf.read()
print('running bot...')
ConU().run(token=TOKEN, reconnect=True)
