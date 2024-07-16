from asyncio import sleep
import datetime
from typing import Optional, Union
import discord
import random

from discord import Embed, Member, NotFound, Object, DMChannel
from discord.utils import find
from discord.ext.commands import Cog, Greedy, Converter, cooldown
from discord.ext.commands import BadArgument, BucketType
from discord.ext.commands import command, has_permissions, bot_has_permissions
import time
import asyncio
import re

from .achieve import grant_check, grant
from ..db import db
from discord.app_commands import command as slash, choices, Choice
from ..utils.send import send
from ..utils import converters

global num
num = 0
global current_count
current_count = -1
global excount
excount = dict()

global important_embed
global reaction_message
global z1list
z1list = []
global cherry
global z7list
z7list = []


# profanity.load_censor_words_from_file("./data/profanity.txt")


class BannedUser(Converter):
    async def convert(self, ctx, arg):
        if ctx.guild.me.guild_permissions.ban_members:
            if arg.isdigit():
                try:
                    return (await ctx.guild.fetch_ban(Object(id=int(arg)))).user
                except NotFound:
                    raise BadArgument

        banned = [e.user for e in await ctx.guild.bans()]
        if banned:
            if (user := find(lambda u: str(u) == arg, banned)) is not None:
                return user
            else:
                raise BadArgument


class author():
    def __init__(self, id):
        self.id = id


class Dmdmo():
    def __init__(self, author, channel):
        self.author = author
        self.channel = channel


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        self.links_allowed = (759432499221889034,)
        self.images_allowed = (759432499221889034,)

    async def kick_members(self, message, targets, reason, ctx):
        for target in targets:
            if (message.guild.me.top_role.position > target.top_role.position
                    and not target.guild_permissions.administrator):
                await target.kick(reason=reason)
                embed = Embed(title="멤버 추방됨",
                              colour=0xDD2222,
                              timestamp=datetime.datetime.now())
                embed.set_thumbnail(url=target.avatar_url)
                fields = [("추방된 사람: ", f"{target.name}", False),
                          ("추방한 사람:", message.author.display_name, False),
                          ("이유:", reason, False)]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                punish_log = db.record("SELECT punish_log FROM guilds WHERE GuildID = ?", ctx.guild.id)
                try:
                    punish_log = punish_log[0]
                except TypeError:
                    return
                try:
                    await self.bot.get_channel(punish_log).send(embed=embed)
                except AttributeError:
                    pass

    @command(name="추방", aliases=["킥", "강퇴"])
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "없음!"):
        if not len(targets):
            await send(ctx, "누구를 추방할지도 말해 주세요!")
        else:
            await self.kick_members(ctx.message, targets, reason, ctx)
            await send(ctx, "완료")

    @command(name="밴")
    @bot_has_permissions(send_messages=True, ban_members=True)
    async def ban_command(
            self,
            ctx,
            targets: Greedy[Union[discord.Member, converters.User]],
            delete_message_days: Optional[int] = 1,
            *,
            reason: Optional[str] = "없음!",
    ):
        # NOTE: This is here to get mypy to shut up. Need to look at typehints for this.
        delete_message_days = delete_message_days or 1

        if ctx.author.guild_permissions.value & 4 == 0:
            await send(ctx, "차단할 권한이 없어요!")
            if targets is not None:
                l = grant_check("차담 마려벤요?", ctx.author.id)
                if l == 1:
                    await grant(ctx, "차담 마려벤요?", "차단할 권한이 없을 때 누군가를 차단하려고 하세요")
            return

        if not targets:
            await send(ctx, f"유효한 대상이 정해져 있지 않아요.")
        elif not 0 <= delete_message_days <= 7:
            await send(ctx, 
                f"메세지를 삭제하려는 기간이 올바르지 않아요. (0에서 7까지만 가능)"
            )
        else:
            count = 0

            async with ctx.typing():
                for target in targets:
                    try:
                        await ctx.guild.ban(
                            target,
                            delete_message_days=delete_message_days,
                            reason=(
                                    (f"{reason}" if target in ctx.guild.members else f"{reason} (핵밴)")
                                    + f"{ctx.author.name}에 의해 실행됨"
                            ),
                        )
                        count += 1
                    except discord.Forbidden:
                        await send(ctx, 
                            "권한 문제로 해당 유저를 밴하는 것을 실패했어요."
                        )

                if count > 0:
                    await send(ctx, f"{count:,} 명이 밴당했어요.")
                else:
                    await send(ctx, f"아무도 밴당하지 않았어요.")
            for target in targets:
                try:
                    await target.ban(reason=reason)
                    embed = Embed(title="멤버 차단됨",
                                  colour=0xDD2222,
                                  timestamp=datetime.datetime.now())
                    embed.set_thumbnail(url=target.avatar_url)
                    fields = [("차단된 멤버", f"{target.name}", False),
                              ("차단한 멤버", ctx.author.display_name, False),
                              ("이유", reason, False)]
                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)
                    punish_log = db.record("SELECT punish_log FROM guilds WHERE GuildID = ?", ctx.guild.id)
                    try:
                        punish_log = punish_log[0]
                    except TypeError:
                        return
                    try:
                        await self.bot.get_channel(punish_log).send(embed=embed)
                    except AttributeError:
                        pass
                except Exception as e:
                    return

    @command(name="차단해제", aliases=["언밴"])
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def unban_command(self, ctx, targets: Greedy[BannedUser], *, reason: Optional[str] = "없음!"):
        if not len(targets):
            await send(ctx, "누구를 차단 해제할 건지도 말해 주세요!")
        else:
            for target in targets:
                await ctx.guild.unban(target, reason=reason)
                embed = Embed(title="멤버 차단 해제됨",
                              colour=0xDD2222,
                              timestamp=datetime.datetime.now())
                embed.set_thumbnail(url=target.avatar_url)
                fields = [("차단 해제된 멤버", target.name, False),
                          ("차단 해제한 멤버", ctx.author.display_name, False),
                          ("이유", reason, False)]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                punish_log = db.record("SELECT punish_log FROM guilds WHERE GuildID = ?", ctx.guild.id)
                try:
                    punish_log = punish_log[0]
                except TypeError:
                    return
                try:
                    await self.bot.get_channel(punish_log).send(embed=embed)
                except AttributeError:
                    pass
            await send(ctx, "완료")

    @command(name="지워", aliases=["삭제"])
    @has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 1):
        if ctx.guild.me.guild_permissions.value & 8192 == 0:
            await send(ctx, 
                random.choice(["너가 지워 너가", "권한도 안주면서 도대채 뭘 하라는 걸까요?ㅋㅋ", "지금 안된다고 뻘문의하지 마세요~~", "`커뉴야 권한진단` " * 30]))
            return

        def _check(message):
            return not len(targets) or message.author in targets

        if 0 < limit <= 255:
            with ctx.channel.typing():
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit,
                                                  after=datetime.datetime.now() - datetime.timedelta(days=14),
                                                  check=_check)

                await send(ctx, f"{len(deleted):,} 개의 메세지를 지웠어요.", delete_after=3)

        else:
            await send(ctx, "삭제하려는 메세지가 너무 많아요! 255개 이하로만 정해 주세요")

    async def mute_members(self, message, targets, hours, reason, ctx):
        unmutes = []
        mute_role = db.record("SELECT muted_role FROM guilds WHERE GuildID = ?", message.guild.id)

        if not mute_role[0]:
            await send(ctx, "뮤트된 사람에게 주어질 뮤트 역할이 설정되어 있지 않아요! `커뉴야 뮤트역할`으로 해당 역할을 먼저 설정해 주세요")
            return

        mute_role = self.bot.get_guild(ctx.guild.id).get_role(mute_role[0])

        for target in targets:
            if mute_role not in target.roles:
                if message.guild.me.top_role.position > target.top_role.position:
                    role_ids = ",".join([str(r.id) for r in target.roles])
                    end_time = datetime.datetime.now() + datetime.timedelta(seconds=hours) if hours else None

                    db.execute("INSERT INTO mutes VALUES (?, ?, ?, ?)",
                               target.id, role_ids, getattr(end_time, "isoformat", lambda: None)(), message.guild.id)

                    await target.edit(roles=[mute_role])

                    embed = Embed(title="멤버 뮤트됨",
                                  colour=0xDD2222,
                                  timestamp=datetime.datetime.now())

                    embed.set_thumbnail(url=target.avatar_url)

                    if not reason:
                        reason = "없음!"

                    fields = [("뮤트당한 멤버", target.display_name, False),
                              ("뮤트시킨 멤버", message.author.display_name, False),
                              ("기간", f"{hours:,} 초" if hours else "무기한", False),
                              ("이유", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    punish_log = db.record("SELECT punish_log FROM guilds WHERE GuildID = ?", ctx.guild.id)
                    try:
                        punish_log = punish_log[0]
                    except TypeError:
                        return
                    try:
                        await self.bot.get_channel(punish_log).send(embed=embed)
                    except AttributeError:
                        pass
                    notification = db.record("SELECT guild_type FROM Guilds WHERE GUILDID = ?", ctx.guild.id)[0]
                    if notification & 32:
                        await target.send(f"{ctx.guild.name} 서버에서 {hours:,}초동안 뮤트되셨습니다. (이유: {reason})")
                    if hours:
                        unmutes.append(target)

        return unmutes

    @command(name="뮤트")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def mute_command(self, ctx, targets: Greedy[Member], *args):
        args = list(args)
        if not len(targets):
            await send(ctx, "누구를 뮤트시킬지도 말해 주세요!")
            return
        duration = 0
        reason = ""
        for arg in args:
            if arg.endswith("d") or arg.endswith("일"):
                try:
                    arg = int(arg[:len(arg) - 1])
                    duration += 86400 * arg
                except ValueError:
                    pass
            elif arg.endswith("h"):
                try:
                    arg = int(arg[:len(arg) - 1])
                    duration += 3600 * arg
                except ValueError:
                    pass
            elif arg.endswith("시간"):
                try:
                    arg = int(arg[:len(arg) - 2])
                    duration += 3600 * arg
                except ValueError:
                    pass
            elif arg.endswith("m") or arg.endswith("분"):
                try:
                    arg = int(arg[:len(arg) - 1])
                    duration += 60 * arg
                except ValueError:
                    pass
            elif arg.endswith("s") or arg.endswith("초"):
                try:
                    arg = int(arg[:len(arg) - 1])
                    duration += arg
                except ValueError:
                    pass
            else:
                reason += arg
        if not duration:
            await send(ctx, "뮤트 기간이 정해져있지 않아요!")
            return
        unmutes = await self.mute_members(ctx.message, targets, duration, reason, ctx)
        await send(ctx, "완료")
        if not unmutes:
            return
        if len(unmutes):
            await sleep(duration)
            await self.unmute_members(ctx.guild, targets, ctx)

    async def unmute_members(self, guild, targets, ctx, *, reason="자동"):
        mute_role = db.record("SELECT muted_role FROM guilds WHERE GuildID = ?", guild.id)
        mute_role = self.bot.get_guild(ctx.guild.id).get_role(mute_role[0])
        for target in targets:
            if mute_role in target.roles:
                role_ids = db.field("SELECT RoleIDs FROM mutes WHERE UserID = ? AND GuildID = ?", target.id, guild.id)
                roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

                db.execute("DELETE FROM mutes WHERE UserID = ? AND GuildID = ?", target.id, guild.id)

                await target.edit(roles=roles)

                embed = Embed(title="멤버 뮤트 해제됨",
                              colour=0xDD2222,
                              timestamp=datetime.datetime.now())

                embed.set_thumbnail(url=target.avatar_url)

                fields = [("언뮤트된 멤버", target.display_name, False),
                          ("이유", reason, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                punish_log = db.record("SELECT punish_log FROM guilds WHERE GuildID = ?", ctx.guild.id)
                try:
                    punish_log = punish_log[0]
                except TypeError:
                    return
                try:
                    await self.bot.get_channel(punish_log).send(embed=embed)
                except AttributeError:
                    pass

    @command(name="언뮤트", aliases=["뮤트해제"])
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True, manage_guild=True)
    async def unmute_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "없음!"):
        if not len(targets):
            await send(ctx, "누구를 언뮤트할 건지도 말해 주세요!")

        else:
            await self.unmute_members(ctx.guild, targets, ctx, reason=reason)

    @command(name="공지발신")
    async def fire_announcement(self, ctx):
        if ctx.author.id != 724496900920705045: return
        global important_embed
        await send(ctx, "보낼 내용 차례대로 보내주셈\n제목\n내용\n푸터")
        wpahr = await self.bot.wait_for(
            "message",
            check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
        )
        sodyd = await self.bot.wait_for(
            "message",
            check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
        )
        vnxj = await self.bot.wait_for(
            "message",
            check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
        )
        channels = db.records("SELECT announcement_channel FROM guilds WHERE announcement_channel IS NOT NULL")
        important_embed = Embed(color=0xffd6fe, title=wpahr.content, description=sodyd.content)
        important_embed.set_footer(text=vnxj.content)
        for channel_to_send in channels:
            try:
                announcement_channel = self.bot.get_channel((channel_to_send[0]))
                if announcement_channel is not None:
                    await announcement_channel.send(embed=important_embed)
            except discord.errors.Forbidden:
                pass

    @command(name="처벌내역", aliases=["처벌로그"])
    @has_permissions(administrator=True)
    async def set_punishlog_channel(self, ctx, activity: Optional[str] = "조회"):
        punish_log = db.record("SELECT punish_log FROM guilds WHERE GuildID = ?", ctx.guild.id)
        punish_log = punish_log[0]
        if activity == "조회":
            try:
                await send(ctx, f"현재 {ctx.guild.name}의 처벌 로그 채널은 <#{punish_log}>(이)에요!")
                return
            except TypeError:
                await send(ctx, f"현재 {ctx.guild.name}에는 처벌 내역이 없어요!")
                return
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity == "끔":
            await send(ctx, f"이제 {ctx.guild.name}에서는 새로 사람이 들어오거나 나가도 알림이 표시되지 않아요!")
            ch = None
        elif activity == "설정":
            await send(ctx, "어느 채널을 처벌 로그로 설정할 건가요?")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=10,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                ch = msg.content[2:20]
            except asyncio.TimeoutError:
                await send(ctx, "처벌 로그를 설정하지 않기로 했어요.")
                return
            await send(ctx, f"이제 {ctx.guild.name}의 처벌 로그 채널은 <#{msg.content[2:20]}>(이)에요!")
        else:
            await send(ctx, "`커뉴야 처벌내역 <조회/설정/끔>`")
            return
        db.execute("UPDATE guilds SET punish_log = ? WHERE GuildID = ?", ch, ctx.guild.id)
        db.commit()

    @command(name="공지채널")
    async def announcement_channel(self, ctx, activity: Optional[str]):
        rhdwl_cosjf = db.record("SELECT announcement_channel FROM guilds WHERE GuildID = ?", ctx.guild.id)
        rhdwl_cosjf = rhdwl_cosjf[0]
        if activity == "조회":
            if rhdwl_cosjf == 1:
                await send(ctx, f"현재 {ctx.guild.name}의 공지 채널이 없어요!")
                return
            else:
                await send(ctx, f"현재 {ctx.guild.name}의 공지 채널은 <#{rhdwl_cosjf}>(이)에요!")
                return
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity == "초기화":
            await send(ctx, f"이제 {ctx.guild.name}에서는 봇 공지를 받지 않아요!")
            ch = 1
        elif activity == "설정":
            await send(ctx, "어느 채널을 공지 채널로 설정할 건가요?")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=10,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                ch = msg.content[2:20]
            except asyncio.TimeoutError:
                await send(ctx, "공지 채널을 설정하지 않기로 했어요.")
                return
            try:
                await self.bot.get_channel(int(ch)).send(embed=Embed(color=ctx.author.color, title="공지 채널 지정",
                                                                     description=f"이제 이 채널이 {ctx.guild.name}에서 봇 공지를 받는 채널로 설정됐어요!"))
            except AttributeError:
                await send(ctx, "채널을 올바르게 입력해 주세요!")
                return
            await send(ctx, f"이제 {ctx.guild.name}의 공지 채널은 <#{msg.content[2:20]}>(이)에요!")
        elif activity == "끔":
            return
        else:
            await send(ctx, "`커뉴야 공지채널 <조회/설정/초기화>`")
            return
        db.execute("UPDATE guilds SET announcement_channel = ? WHERE GuildID = ?", ch, ctx.guild.id)
        db.commit()

    @command(name="공지")
    async def announcement(self, ctx):
        global important_embed
        await send(ctx, embed=important_embed)

    @command(name="답변")
    async def send_dm(self, ctx, target: Optional[int], *, content: Optional[str]):
        if ctx.author.id != 724496900920705045:
            return
        try:
            await self.bot.get_user(target).send(content)
            await send(ctx, "완료")
        except:
            await send(ctx, "병보")

    @command(name="관리")
    async def mod_info(self, ctx):
        await send(ctx, embed=Embed(color=ctx.author.color, title="커뉴봇 관리 명령어 도움!",
                                   description="**레벨 관련 관리 명령어**\n`커뉴야 경험치범위`, `커뉴야 경험치쿨타임`, `커뉴야 레벨업채널`, `커뉴야 경험치설정`, `커뉴야 경부설정`, `커뉴야 채널부스트설정`, `커뉴야 레벨업문구`,`커뉴야 초대당경부`, `커뉴야 경험치초기화`\n\n**채널 관련 관리 명령어**\n`커뉴야 숫자채널`, `커뉴야 환영채널`, `커뉴야 공지채널`, `커뉴야 무규방`, `커뉴야 세로채널`, `커뉴야 처벌로그`, `커뉴야 커맨드금지`\n\t\n**시스템 관련 관리 명령어**\n`커뉴야 들낙퇴치`, `커뉴야 같이반응`, `커뉴야 봇메세지무시`, `커뉴야 닉홍보금지`\n\t\n**역할 관련 관리 명령어**\n`커뉴야 레벨역할`, `커뉴야 이름색역할`\n\n**일반 관리 명령어**\n`커뉴야 뮤트`, `커뉴야 언뮤트`, `커뉴야 추방`, `커뉴야 차단`\n`커뉴야 슬로우모드`\n\n**기타 관리 명령어**\n`커뉴야 홍보`, `커뉴야 기원추가`, `커뉴야 기원삭제`, `커뉴야 환영문구`, `커뉴야 나갈때문구`, `커뉴야 권한진단`"))

    @command(name="경험치설정")
    @has_permissions(administrator=True)
    async def set_exp(self, ctx, target: Optional[Member], amount: Optional[int] = -1):
        target = target or None
        if target is None:
            await send(ctx, "누구의 경험치를 설정할 건지도 말해 주세요!\n올바른 사용법: `커뉴야 경험치설정 <대상> <경험치>`")
            return
        if amount == -1:
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=15,
                    check=lambda message: message.author == ctx.author and message.channel == ctx.channel
                )
                try:
                    amount = int(msg.content)
                except TypeError:
                    await send(ctx, "정수로만 입력해 주세요!")
                    return
            except asyncio.TimeoutError:
                await send(ctx, "경험치를 설정하지 않기로 했어요.")
                return
        elif amount < 0:
            await send(ctx, "0 이상으로만 입력해 주세요!")
            return
        else:
            try:
                db.execute("UPDATE exp SET XP = ?, Level = 0 WHERE UserID = ? AND GuildID = ?", amount, target.id,
                           ctx.guild.id)
                db.commit()
            except ValueError:
                await send(ctx, "알맞은 요소를 입력해 주세요!")
                return
            await send(ctx, 
                f"{target.display_name}의 경험치를 성공적으로 {amount}(으)로 바꿨어요. 경험치가 설정된 사람이 한 번 더 챗을 치면 레벨이 정상적으로 반영될 거에요.")

    @command(name="경험치부스트설정", aliases=["경부설정"])
    @has_permissions(administrator=True)
    async def set_exp_boost(self, ctx, target: Optional[Member], amount: Optional[float] = -1,
                            reason: Optional[str] = ""):
        target = target or None
        if target is None:
            await send(ctx, "누구의 경험치 부스트를 설정할 건지도 말해 주세요!\n올바른 사용법: `커뉴야 경부설정 <대상> <경부> <이유>`")
            return
        if amount == -1:
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=15,
                    check=lambda message: message.author == ctx.author and message.channel == ctx.channel
                )
                try:
                    amount = int(msg.content)
                except ValueError:
                    await send(ctx, "정수로만 입력해 주세요!")
                    return
            except asyncio.TimeoutError:
                await send(ctx, "경험치 부스트를 설정하지 않기로 했어요.")
                return
        if amount < 0:
            await send(ctx, "0 이상으로만 입력해 주세요!")
            return
        try:
            db.execute("UPDATE exp SET XPBoost = ?, temp = ? WHERE UserID = ? AND GuildID = ?", amount, reason,
                       target.id, ctx.guild.id)
            db.commit()
        except ValueError:
            await send(ctx, "알맞은 요소를 입력해 주세요!")
            return
        await send(ctx, f"{target.display_name}의 경험치 부스트를 성공적으로 {amount}(으)로 바꿨어요.")

    @command(name="숫자채널")
    @has_permissions(administrator=True)
    async def count_channel(self, ctx, target: Optional[discord.channel.TextChannel], activity: Optional[str]):
        target = target or ctx.channel
        target = target.id
        if not activity or activity in ['지정', '설정']:
            await send(ctx, f"정말 해당 채널을 숫자 세기 채널로 설정할 건가요?\n`네`라고 입력해서 확실시해 주세요")
            try:
                msg1 = await self.bot.wait_for(
                    "message",
                    timeout=15,
                    check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                await send(ctx, "해당 채널을 숫자 세기 채널로 설정하지 않기로 했어요.")
                return
            if msg1.content != "네":
                return
            this_channel, channel_type = db.record("SELECT ChannelID, channel_type FROM channels WHERE ChannelID = ?",
                                                   target)
            if this_channel is None:
                db.execute("INSERT INTO channels (ChannelID, channel_type) VALUES (?, 1)", ctx.channel.id)
            else:
                if channel_type & 1 == 1:
                    await send(ctx, "해당 채널은 이미 숫자세기 채널로 지정되어 있어요!")
                    return
                db.execute("UPDATE channels SET channel_type = ? WHERE ChannelID = ?", channel_type + 1, target)
            await send(ctx, "좋아요. 그렇다면 이 채널에서는 지금까지 숫자를 얼마나 세었나요? 숫자로만 입력해 주세요")
            try:
                msg2 = await self.bot.wait_for(
                    "message",
                    timeout=15,
                    check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
                )
                try:
                    msg2 = int(msg2.content)
                except ValueError:
                    await send(ctx, "숫자로만 입력해 주세요")
                    return
            except asyncio.TimeoutError:
                await send(ctx, "아무 숫자도 세지 않았다고 가정할게요.")
                msg2 = 0
            db.execute("UPDATE channels SET num = ? WHERE ChannelID = ?", msg2, target)
            await send(ctx, "성공적으로 해당 채널을 숫자세기 채널로 설정했어요!")
            db.commit()
        elif activity == '해제':
            count = db.record("SELECT channel_type FROM channels WHERE ChannelID = ?", target)[0]
            if not count:
                await send(ctx, "해당 채널은 숫자채널로 지정되어 있지 않아요!")
                return
            await send(ctx, "정말로 해당 채널을 숫자채널에서 해제시킬 건가요? `해제`라고 입력해 진행하세요")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=15,
                    check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                await send(ctx, "숫자채널 해제를 취소했어요.")
                return
            if msg.content == '해제':
                count -= 1
                db.execute("UPDATE channels SET channel_type = ?, num = NULL WHERE ChannelID = ?", count, target)
                db.commit()
                await send(ctx, "숫자채널 해제를 완료했어요!")

    @command(name="무규채널", aliases=["무규방", "믁귺방"])
    @has_permissions(administrator=True)
    async def ruleless_channel(self, ctx):
        await send(ctx, "정말 이 채널을 무규 채널로 설정할 건가요?\n`네`라고 입력해서 확실시해 주세요")
        try:
            msg1 = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            await send(ctx, "이 채널을 무규 채널로 설정하지 않기로 했어요.")
            return
        if msg1.content != "네":
            return
        this_channel, channel_type = db.record("SELECT ChannelID, channel_type FROM channels WHERE ChannelID = ?",
                                               ctx.channel.id)
        if this_channel is None:
            db.execute("INSERT INTO channels (ChannelID, channel_type) VALUES (?, 2)", ctx.channel.id)
        else:
            if channel_type & 2 == 2:
                await send(ctx, "이 채널은 이미 무규 채널로 지정되어 있어요!")
                return
            db.execute("UPDATE channels SET channel_type = ? WHERE ChannelID = ?", channel_type + 2, ctx.channel.id)
        await send(ctx, "성공적으로 이 채널을 무규 채널로 설정했어요! 바뀐 점은 아마도 없을 거에요")
        db.commit()

    @command(name="세로채널", aliases=["세로방"])
    @has_permissions(administrator=True)
    async def vertical_channel(self, ctx, activity: Optional[str] = "설정"):
        if activity == "해제":
            channel_type = db.record("SELECT channel_type FROM channels WHERE ChannelID = ?", ctx.channel.id)
            channel_type = channel_type[0]
            if channel_type & 4 != 4:
                await send(ctx, "이 채널은 세로 채널이 아니에요!")
                return
            db.execute("UPDATE channels SET channel_type = ? WHERE ChannelID = ?", channel_type - 4, ctx.channel.id)
            db.commit()
            await send(ctx, "세로 채널 해제를 완료했어요!")
        elif activity == "설정":
            await send(ctx, "정말 이 채널을 세로 채널로 설정할 건가요?\n`네`라고 입력해서 확실시해 주세요")
            try:
                msg1 = await self.bot.wait_for(
                    "message",
                    timeout=15,
                    check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                await send(ctx, "이 채널을 세로 채널로 설정하지 않기로 했어요.")
                return
            if msg1.content != "네":
                return
            this_channel, channel_type = db.record("SELECT ChannelID, channel_type FROM channels WHERE ChannelID = ?",
                                                   ctx.channel.id)
            if this_channel is None:
                db.execute("INSERT INTO channels (ChannelID, channel_type) VALUES (?, 4)", ctx.channel.id)
            else:
                if channel_type & 4 == 4:
                    await send(ctx, "이 채널은 이미 세로 채널로 지정되어 있어요!")
                    return
                db.execute("UPDATE channels SET channel_type = ? WHERE ChannelID = ?", channel_type + 4, ctx.channel.id)
            await send(ctx, "성공적으로 이 채널을 세로 채널로 설정했어요! 이제 이 채널에서는 한글자까지만 말할 수 있어요")
            db.commit()

    @command(name="홍보")
    @has_permissions(administrator=True)
    @cooldown(1, 100, BucketType.guild)
    async def advertise(self, ctx):
        server_level = db.record("SELECT enchant_level FROM Guilds WHERE GuildID = ?", ctx.guild.id)
        server_level = server_level[0]
        if server_level < 50:
            await send(ctx, f"홍보를 하기에는 서버 레벨이 너무 낮아요! `커뉴야 서버강화` 명령어로 현재 {server_level}레벨인 서버를 50레벨로 만들어보세요.")
            return
        await send(ctx, "서버의 소개(홍보글)을 보내 주세요.\n링크 말고 **홍보글만** 보내주세요! 없으면 `** **` 을 입력하시면 돼요.")
        try:
            hongbo_geul = await self.bot.wait_for(
                "message",
                timeout=120,
                check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            await send(ctx, "홍보글 작성을 취소했어요.")
            return
        hongbo_geul = hongbo_geul.content
        if len(hongbo_geul) > 40 + 5 * (server_level - 50):
            await send(ctx, 
                f"현재 서버 레벨로는 {40 + 5 * (server_level - 50)}글자까지의 홍보글만 지정할 수 있어요! 홍보글을 짧게 바꾸거나 서버강화 레벨을 더 올려 보세요/")
            return
        await send(ctx, "서버의 초대 링크를 보내 주세요!")
        try:
            invite_link = await self.bot.wait_for(
                "message",
                timeout=20,
                check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            await send(ctx, "홍보글 작성을 취소했어요.")
            return
        await send(ctx, "홍보글 작성을 완료했어요! 다른 서버에서 `커뉴야 서버추천`명령어가 사용되면 이곳이 나올 가능성이 생겨요.")
        invite_link = invite_link.content
        inv = re.compile("(https://)discord[.]gg/[a-zA-Z0-9]{7,10}")
        i = inv.match(invite_link)
        if not i or i.end() != len(invite_link):
            await send(ctx, "링크로써는 올바르지 않은 형식이에요!")
            return
        hongbo_geul = f"{hongbo_geul}\n{invite_link}"
        db.execute("UPDATE guilds SET advert = ? WHERE GuildID = ?", hongbo_geul, ctx.guild.id)
        db.commit()

    @command(name="초대당경부")
    async def xpboost_per_invite(self, ctx, activity: Optional[str], amount: Optional[float]):
        if not activity:
            activity = '조회'
        if activity == "조회":
            inb = db.record("SELECT invite_boost FROM guilds WHERE GuildID = ?", ctx.guild.id)
            inb = inb[0]
            await send(ctx, f"현재 {ctx.guild.name}에서 한 명을 초대할 때마다 경부 {inb}%를 지급해요!")
            return
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity == "설정":
            if amount is None:
                await send(ctx, "`커뉴야 초대당경부 설정 (퍼센트)`")
                return
            if amount < 0:
                await send(ctx, "올바르지 않은 값이에요!")
                return
            await send(ctx, f"설정을 완료했어요! 이제 {ctx.guild.name}에서 한 명을 초대할 때마다 {amount}%만큼의 경부를 지급할게요")
            db.execute("UPDATE guilds SET invite_boost = ? WHERE GuildID = ?", amount, ctx.guild.id)
            db.commit()

    @command(name="처벌알림")
    @has_permissions(administrator=True)
    async def notify_punishment(self, ctx, activity: Optional[str] = "조회"):
        servertype = db.record("SELECT guild_type FROM guilds WHERE GuildID = ?", ctx.guild.id)
        servertype = servertype[0]
        notify = servertype & 32 == 32
        if activity == "조회":
            if notify:
                await send(ctx, f"현재 {ctx.guild.name}에는 처벌 알림 시스템이 **켜져** 있어요!")
            else:
                await send(ctx, f"현재 {ctx.guild.name}에는 처벌 알림 시스템이 **꺼져** 있어요!")
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity == "끔" or activity == "꺼":
            if notify:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype - 32, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 처벌받은 사람에게 DM이 가지 않아요.")
            else:
                await send(ctx, f"이미 {ctx.guild.name}에서는 처벌받은 사람에게 DM이 가지 않아요!")
                return
            db.commit()
        elif activity == "켬" or activity == "켜":
            if notify:
                await send(ctx, f"이미 {ctx.guild.name}에서는 처벌받은 사람에게 DM으로 처벌받았다는 알림이 가요!")
            else:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype + 32, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 처벌받은 사람에게 DM으로 처벌받았다는 알림이 가요.")
            db.commit()
        elif activity == "도움":
            await send(ctx, 
                "처벌 알림 시스템은 뮤트 등의 처벌을 받은 사람에게 DM으로 처벌을 받았다고 알려주는 시스템이에요. 서버 내의 채널에다가 알림을 보내는 `커뉴야 처벌내역`명령어와는 다른 명령어에요!")

    @command(name="기원닉띄기")
    @has_permissions(administrator=True)
    async def notify_punishment(self, ctx, activity: Optional[str] = "조회"):
        servertype = db.record("SELECT guild_type FROM guilds WHERE GuildID = ?", ctx.guild.id)
        servertype = servertype[0]
        notify = servertype & 256 == 256
        if activity == "조회":
            if notify:
                await send(ctx, f"현재 {ctx.guild.name}에는 기원 닉 띄기 시스템이 **켜져** 있어요!")
            else:
                await send(ctx, f"현재 {ctx.guild.name}에는 기원 닉 띄기 시스템이 **꺼져** 있어요!")
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity == "끔" or activity == "꺼":
            if notify:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype - 256, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 기원 닉네임에 띄어쓰기를 하지 않아요.")
            else:
                await send(ctx, f"이미 {ctx.guild.name}에서는 기원 닉네임에 띄어쓰기를 하지 않아요!")
                return
            db.commit()
        elif activity == "켬" or activity == "켜":
            if notify:
                await send(ctx, f"이미 {ctx.guild.name}에서는 기원 닉네임에 띄어쓰기를 하고 있어요!")
            else:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype + 256, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 기원 닉네임에 띄어쓰기를 해요.")
            db.commit()
        elif activity == "도움":
            await send(ctx, 
                "기원 닉 띄기 시스템은 `커뉴야 기원추가`로 서버 내 멤버에게 기원 닉네임을 부여하면 닉네임과 일차 사이에 띄어쓰기를 하나 마나를 설정하는 명령어에요.\n\n만약 누군가에게 `기말1등급기원` 을 기원했다 치고 오늘이 그 기원의 3일차라고 치면 닉네임이 다음과 같이 돼요.\n이 시스템이 꺼짐: 기말1등급기원3일차\n이 시스템이 켜짐: 기말1등급기원 3일차")

    @command(name="같이반응")
    @has_permissions(administrator=True)
    async def e_ee(self, ctx, activity: Optional[str] = "조회"):
        servertype = db.record("SELECT guild_type FROM guilds WHERE GuildID = ?", ctx.guild.id)
        servertype = servertype[0]
        together = servertype & 4 == 4
        if activity == "조회":
            if together:
                await send(ctx, f"현재 {ctx.guild.name}에는 같이 반응해 주기 시스템이 **켜져** 있어요!")
            else:
                await send(ctx, f"현재 {ctx.guild.name}에는 같이 반응해 주기 시스템이 **꺼져** 있어요!")
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity == "끔" or activity == "꺼":
            if together:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype - 4, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 사람들의 말에 커뉴봇이 같이 반응해주지 않아요.")
            else:
                await send(ctx, f"이미 {ctx.guild.name}에서는 사람들의 말에 커뉴봇이 같이 반응해주지 않아요!")
                return
            db.commit()
        elif activity == "켬" or activity == "켜":
            if together:
                await send(ctx, f"이미 {ctx.guild.name}에서는 사람들의 말에 커뉴봇이 같이 반응해요!")
            else:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype + 4, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 사람들의 말에 커뉴봇이 같이 반응해요.")
            db.commit()
        elif activity == "도움":
            await send(ctx, 
                "같이 반응해주기 시스템은 사람들이 'ㅋㅋ', 'ㄷㄷㄷ' 등의 말을 했을 때 봇도 따라해주는 기능이에요!")

    @command(name="올려금지")
    async def no_up(self, ctx, activity: Optional[str] = "조회"):
        channeltype = db.record("SELECT channel_type FROM channels WHERE ChannelID = ?", ctx.channel.id)[0]
        noup = channeltype & 32 == 32
        if activity == "조회":
            if noup:
                await send(ctx, f"현재 {ctx.channel.name}에는 올려 명령어를 금지하고 있어요!")
            else:
                await send(ctx, f"현재 {ctx.channel.name}에는 올려 명령어를 금지하고 있지 않아요!")
        if not ctx.author.guild_permissions.value & 16:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity == "끔" or activity == "꺼":
            if noup:
                db.execute("UPDATE channels SET channel_type = ? WHERE channelid = ?", channeltype - 32, ctx.channel.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.channel.name}에서는 올려 명령어를 사용할 수 있어요.")
            else:
                await send(ctx, f"이미 {ctx.channel.name}에서는 올려 명령어를 사용할 수 있어요!")
                return
            db.commit()
        elif activity == "켬" or activity == "켜":
            if noup:
                await send(ctx, f"이미 {ctx.channel.name}에서는 올려 명령어를 사용할 수 없어요!")
            else:
                db.execute("UPDATE channels SET channel_type = ? WHERE channelid = ?", channeltype + 32, ctx.channel.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.channel.name}에서는 올려 명령어의 사용을 금지해요.")
            db.commit()
        elif activity == "도움":
            await send(ctx, 
                "올려 금지 시스템은 스크롤을 올리는 명령어인 `커뉴야 올려`의 사용을 금지하는 명령어에요.")

    @command(name="레벨업메시지", aliases=["레벨업메세지", "레벨업문구", "렙업메세지", "렙업메시지", "렙업문구"])
    @has_permissions(administrator=True)
    async def set_levelup_message(self, ctx, activity: Optional[str] = "조회"):
        lvup_message = db.record("SELECT levelup_message FROM guilds WHERE GuildID = ?", ctx.guild.id)
        lvup_message = lvup_message[0]
        if activity == "조회":
            await send(ctx, f"{lvup_message}")
            return
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity == "초기화":
            await send(ctx, f"{ctx.guild.name}의 레벨업 문구를 기본값으로 설정했어요!")
            new_msg = "렙업!"
        elif activity == "설정":
            await send(ctx, 
                "새로 바꿀 레벨업 문구를 입력해 주세요!\n사용할 수 있는 변수값들은 다음과 같아요:\n```<멤버_사용자명#태그>: 멤버의 사용자명과 태그\n<멤버_이름>: 멤버의 사용자명\n<멤버_멘션>: 멤버를 멘션\n<레벨>: 멤버가 도달한 레벨```")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                new_msg = msg.content
            except asyncio.TimeoutError:
                await send(ctx, "레벨업 문구를 설정하지 않기로 했어요.")
                return
            await send(ctx, f"이제 {ctx.guild.name}의 레벨업 문구는 {new_msg}(이)에요!")
        else:
            await send(ctx, "`커뉴야 레벨업메세지 <조회/설정/초기화>`")
            return
        db.execute("UPDATE guilds SET levelup_message = ? WHERE GuildID = ?", new_msg, ctx.guild.id)
        db.commit()

    @command(name="들어올때메세지", aliases=["들어올때메시지", "환영메세지", "환영메시지", "환영문구"])
    @has_permissions(administrator=True)
    async def set_welcome_message(self, ctx, activity: Optional[str] = "조회"):
        welcome_message = db.record("SELECT join_message FROM guilds WHERE GuildID = ?", ctx.guild.id)
        welcome_message = welcome_message[0]
        if activity == "조회":
            await send(ctx, f"{welcome_message}")
            return
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity == "초기화":
            await send(ctx, f"{ctx.guild.name}의 환영 문구를 기본값으로 설정했어요!")
            new_msg = "안녕하세요"
        elif activity == "설정":
            await send(ctx, 
                "새로 바꿀 환영 문구를 입력해 주세요!\n사용할 수 있는 변수값들은 다음과 같아요:\n```<멤버_사용자명#태그>: 멤버의 사용자명과 태그\n<멤버_이름>: 멤버의 사용자명\n<멤버_멘션>: 멤버를 멘션\n<서버명>: 서버 이름\n<서버_멤버수>: 서버의 총 멤버수\n<서버_순인원>: 서버의 봇 제외 멤버수\n<데려온_사람>: 이 사람을 데려온 사람의 사용자명#태그\n<데려온_사람_닉네임>: 이 사람을 데려온 사람의 서버 내 닉네임\n<데려온_사람_초대횟수>: 이 사람을 데려온 사람이 총 데려온 사람 수```")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                new_msg = msg.content
            except asyncio.TimeoutError:
                await send(ctx, "환영 문구를 설정하지 않기로 했어요.")
                return
            await send(ctx, f"이제 {ctx.guild.name}의 환영 문구는 {new_msg}(이)에요!")
        else:
            await send(ctx, "`커뉴야 환영메세지 <조회/설정/초기화>`")
            return
        db.execute("UPDATE guilds SET join_message = ? WHERE GuildID = ?", new_msg, ctx.guild.id)
        db.commit()

    @command(name="나갈때메세지", aliases=["나갈때메시지", "나갈때문구"])
    @has_permissions(administrator=True)
    async def set_leave_message(self, ctx, activity: Optional[str] = "조회"):
        leave_message = db.record("SELECT leave_message FROM guilds WHERE GuildID = ?", ctx.guild.id)
        leave_message = leave_message[0]
        if activity == "조회":
            await send(ctx, f"{leave_message}")
            return
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity == "초기화":
            await send(ctx, f"{ctx.guild.name}의 나갈 때 문구를 기본값으로 설정했어요!")
            new_msg = ":weary:"
        elif activity == "설정":
            await send(ctx, 
                "새로 바꿀 나갈 때 문구를 입력해 주세요!\n사용할 수 있는 변수값들은 다음과 같아요:\n```<멤버_사용자명#태그>: 멤버의 사용자명과 태그\n<멤버_이름>: 멤버의 사용자명\n<멤버_멘션>: 멤버를 멘션\n<서버명>: 서버 이름\n<서버_멤버수>: 서버의 총 멤버수\n<서버_순인원>: 서버의 봇 제외 멤버수\n<데려온_사람>: 이 사람을 데려온 사람의 사용자명#태그\n<데려온_사람_닉네임>: 이 사람을 데려온 사람의 서버 내 닉네임\n<데려온_사람_초대횟수>: 이 사람을 데려온 사람이 총 데려온 사람 수```")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                new_msg = msg.content
            except asyncio.TimeoutError:
                await send(ctx, "나갈 때 문구를 설정하지 않기로 했어요.")
                return
            await send(ctx, f"이제 {ctx.guild.name}의 나갈 때 문구는 {new_msg}(이)에요!")
        else:
            await send(ctx, "`커뉴야 나갈때메세지 <조회/설정/초기화>`")
            return
        db.execute("UPDATE guilds SET leave_message = ? WHERE GuildID = ?", new_msg, ctx.guild.id)
        db.commit()

    @command(name="기원추가")
    @has_permissions(administrator=True)
    async def add_giwon(self, ctx, target: Optional[Member]):
        today = ((time.time() + 32400) // 86400)
        if not target:
            await send(ctx, "지정된 멤버가 없어요.\n올바른 사용법: `커뉴야 기원추가 (기원대상)`")
            return
        await send(ctx, "추가할 기원의 이름을 말해 주세요!")
        try:
            msg1 = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
            )
            new_giwon = msg1.content
        except asyncio.TimeoutError:
            await send(ctx, "기원을 추가하지 않기로 했어요.")
            return
        giwons = db.record("SELECT TargetID FROM Giwons WHERE GuildID = ? AND TargetID = ?", ctx.guild.id, target.id)
        if giwons is not None:
            if giwons[0] == target.id:
                await send(ctx, f"이미 {ctx.guild.name}서버에서 기원을 받고 있는 대상이에요!")
                return
        await send(ctx, f"{str(target)}에게 {new_giwon}을 기원하기 시작하려고 해요. \"네\"라고 입력해서 확실시해주세요.")
        try:
            msg3 = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
            )
            if msg3.content != "네":
                return
        except asyncio.TimeoutError:
            await send(ctx, "기원을 추가하지 않기로 했어요.")
            return
        await send(ctx, f"기원 추가를 완료했어요! 오늘은 {new_giwon} 기원의 1일차에요.")
        check_space = db.record("SELECT guild_type FROM guilds WHERE GuildID = ?", ctx.guild.id)[0] & 256 == 256
        if not check_space:
            await target.edit(nick=f"{new_giwon}1일차")
        else:
            await target.edit(nick=f"{new_giwon} 1일차")
        db.execute("INSERT INTO Giwons (Giwon_name, GuildID, TargetID, last_giwon_date) VALUES (?, ?, ?, ?)", new_giwon,
                   ctx.guild.id, target.id, today)
        db.commit()

    @command(name="기원삭제")
    @has_permissions(administrator=True)
    async def delete_giwon(self, ctx, *, target_giwon: Optional[str]):
        if not target_giwon:
            await send(ctx, "삭제할 기원도 말해 주세요! `커뉴야 기원삭제 <삭제할 기원>`")
            return
        guild_giwons = db.records("SELECT Giwon_name FROM Giwons WHERE GuildID = ?", ctx.guild.id)
        for giwon in guild_giwons:
            if giwon[0] == target_giwon:
                await send(ctx, f"{target_giwon} 기원 삭제를 완료했어요!")
                db.execute("DELETE FROM Giwons WHERE Giwon_name = ? AND GuildID = ?", target_giwon, ctx.guild.id)
                return
        else:
            await send(ctx, "이 서버에는 그런 기원이 없어요!")

    @command(name="슬로우모드", aliases=["슬로우"])
    @has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        if seconds > 21600:
            await send(ctx, "슬로우모드는 6시간 (21600초) 까지만 설정할 수 있어요!")
            return
        await ctx.channel.edit(slowmode_delay=seconds)

    @command(name="뮤트역할")
    @has_permissions(administrator=True)
    async def mute_role_config(self, ctx):
        await send(ctx, "새로 정할 뮤트 역할을 말해 주세요! 역할 멘션 형태로 입력해 주셔야만 해요")
        try:
            msg = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author == ctx.author and message.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            await send(ctx, "뮤트 역할을 바꾸지 않기로 했어요.")
            return
        try:
            role = int(msg.content[3:21])
        except ValueError:
            await send(ctx, "역할 멘션 형태로만 입력해 주세요")
            return
        db.execute("UPDATE guilds SET muted_role = ? WHERE GuildID = ?", role, ctx.guild.id)
        db.commit()
        await send(ctx, "뮤트역할 설정을 완료했어요!")

    @command(name="채널부스트", aliases=["채부"])
    @cooldown(2, 1, BucketType.user)
    async def display_channel_boost(self, ctx, ch: Optional[discord.channel.TextChannel]):
        ch = ch or ctx.channel
        if ch.id == 916323859731464202:
            await send(ctx, "?")
            return
        channelboost = db.record("SELECT ChannelBoost FROM channels WHERE ChannelID = ?", ch.id)
        channelboost = channelboost[0]
        xpboost = db.record("SELECT XPBoost FROM exp WHERE UserID = ? AND guildid = ?", ctx.author.id, ctx.guild.id)
        xpboost = xpboost[0]
        min_xp, max_xp = db.record("SELECT min_xp, max_xp FROM guilds WHERE GuildID = ?", ctx.guild.id)
        embed = Embed(color=ctx.author.color)
        embed.add_field(name=f"{ch.name}의 채널부스트", value=f"{channelboost}")
        try:
            embed.set_footer(
                text=f"이 채널에서 받는 경험치: {round(min_xp * channelboost * xpboost)} ~ {round(max_xp * channelboost * xpboost)}")
        except OverflowError:
            pass
        await send(ctx, embed=embed)

    @command(name="채널부스트설정", aliases=["채부설정"])
    @has_permissions(administrator=True)
    async def set_channel_boost(self, ctx, boost: Optional[float]):
        if boost is None:
            await send(ctx, "설정할 부스트 값도 정해 주세요! `커뉴야 채널부스트설정 <부스트>`")
            return
        db.execute("UPDATE channels SET ChannelBoost = ? WHERE ChannelID = ?", boost, ctx.channel.id)
        await send(ctx, f"성공적으로 {ctx.channel.name}의 채널 부스트를 {boost}로 바꿨어요!")

    @command(name="초대설정")
    @has_permissions(administrator=True)
    async def set_invites(self, ctx, target: Optional[Member], new_invite: Optional[int] = -1):
        target = target or None
        if target is None:
            await send(ctx, "누구의 초대 횟수를 설정할 건지도 말해 주세요!\n올바른 사용법: `커뉴야 초대설정 <대상> <횟수>`")
            return
        if new_invite == -1:
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=15,
                    check=lambda message: message.author == ctx.author and message.channel == ctx.channel
                )
                try:
                    new_invite = int(msg.content)
                except ValueError:
                    await send(ctx, "정수로만 입력해 주세요!")
                    return
            except asyncio.TimeoutError:
                await send(ctx, "초대 횟수를 설정하지 않기로 했어요.")
                return
        if new_invite < 0:
            await send(ctx, "0 이상으로만 입력해 주세요!")
            return
        try:
            db.execute("UPDATE exp SET invite_score = ? WHERE UserID = ? AND GuildID = ?", new_invite,
                       target.id, ctx.guild.id)
            db.commit()
        except ValueError:
            await send(ctx, "알맞은 요소를 입력해 주세요!")
            return
        await send(ctx, f"{target.display_name}의 초대 횟수를 성공적으로 {new_invite}(으)로 바꿨어요.")

    @command(name="이름색")
    async def equip_name_color(self, ctx, color: Optional[str] = ""):
        color_roles = db.records("SELECT RoleID, role_info FROM roles WHERE role_type = 2 AND GuildID = ?",
                                 ctx.guild.id)
        for color_role in color_roles:
            if color == (role_to_add := ctx.guild.get_role(color_role[0])).name:
                if role_to_add in ctx.author.roles:
                    await ctx.author.remove_roles(role_to_add)
                    await send(ctx, f"{color} 역할 장착을 해제했어요!")
                    return
                else:
                    await ctx.author.add_roles(role_to_add)
                    await send(ctx, f"{color} 역할을 장착했어요!")
                    return
        if color == "":
            await self.color_role(ctx=ctx, activity="목록")
            return
        await send(ctx, "그런 이름색은 없는 거 같아요!")

    @command(name="이름색역할")
    @has_permissions(administrator=True)
    async def color_role(self, ctx, activity: Optional[str] = "목록", role_name: Optional[discord.role.Role] = ""):
        if activity == "목록":
            colorroles = db.records("SELECT RoleID FROM roles WHERE GuildID = ? AND role_type = 2", ctx.guild.id)
            tjfaud = ""
            roles_list = []
            for role in colorroles:
                role_to_append = ctx.guild.get_role(role[0])
                try:
                    roles_list.append([role_to_append.id, (str(role_to_append.color))[1:]])
                except AttributeError:
                    db.execute("DELETE FROM roles WHERE RoleID = ?", role[0])
            for role in roles_list:
                r = int(role[1][0:2], 16)
                g = int(role[1][2:4], 16)
                b = int(role[1][4:6], 16)
                v = max(r, g, b)
                t = min(r, g, b)
                try:
                    if r == v:
                        hue = 60 * (g - b) / (v - t)
                    elif g == v:
                        hue = 120 + 60 * (b - r) / (v - t)
                    else:
                        hue = 240 + 60 * (r - g) / (v - t)
                except ZeroDivisionError:
                    hue = 99999999
                if hue < 0:
                    hue += 360
                role[1] = hue
            for j in range(len(roles_list)):
                for i in range(len(roles_list) - 1):
                    if roles_list[i][1] > roles_list[i + 1][1]:
                        roles_list[i], roles_list[i + 1] = roles_list[i + 1], roles_list[i]
            for role in roles_list:
                tjfaud = tjfaud + f"{ctx.guild.get_role(role[0]).mention} "
            await send(ctx, 
                embed=Embed(color=ctx.author.color, title=f"{ctx.guild.name}의 이름색 역할 목록", description=tjfaud))
        elif activity == "추가":
            if role_name:
                role_name = role_name.id
            else:
                await send(ctx, "어떤 역할을 이름색 역할로 추가할 건가요? **역할 멘션의 형태로 입력해 주세요!**")
                try:
                    msg1 = await self.bot.wait_for(
                        "message",
                        timeout=20,
                        check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                    )
                except asyncio.TimeoutError:
                    await send(ctx, "이름색 역할을 추가하지 않기로 했어요.")
                    return
                role = re.compile("<@&\d{18,19}>")
                rolecheck = role.match(msg1.content)
                if not rolecheck:
                    await send(ctx, "올바르지 않은 형식이에요! 역할핑 형태로 말해주세요")
                    return
                if msg1.content[22].isdigit():
                    role_name = int(msg1.content[3:22])
                else:
                    role_name = int(msg1.content[3:21])
            db.execute("INSERT INTO roles (RoleID, GuildID, role_type, role_info) VALUES (?, ?, 2, ?)", role_name,
                       ctx.guild.id, ctx.guild.get_role(role_name).name)
            await send(ctx, f"{ctx.guild.name}에서 {ctx.guild.get_role(role_name).mention} 역할을 이름색 역할로 받을 수 있어요!")
            db.commit()
        elif activity == "삭제":
            await send(ctx, "어떤 이름색 역할을 삭제할 건가요?\n역할 자체가 지워지지는 않아요")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                role = int(msg.content[3:21])
            except asyncio.TimeoutError:
                await send(ctx, "이름색 역할을 삭제하지 않기로 했어요.")
                return
            roles = db.records("SELECT RoleID FROM roles WHERE GuildID = ? AND role_type = 2", ctx.guild.id)
            for role_to_check in roles:
                if role_to_check[0] == role:
                    break
            else:
                await send(ctx, f"그 역할은 이름색 역할에 포함되어 있지 않아요!")
                return
            db.execute("DELETE FROM roles WHERE RoleID = ?", role)
            await send(ctx, "해당 이름색 역할을 삭제했어요. 역할 자체가 지워진 건 아니에요!")
            db.commit()
        elif activity == "수정":
            await send(ctx, "어떤 이름색 역할을 수정할 건가요? 역할 멘션의 형태로 입력해 주세요!")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                role = int(msg.content[3:21])
            except asyncio.TimeoutError:
                await send(ctx, "이름색 역할을 수정하지 않기로 했어요.")
                return
            role_to_config = db.record("SELECT role_type, role_info FROM roles WHERE RoleID = ?", role)
            if role_to_config[0] & 2 != 2:
                await send(ctx, "그 역할은 이름색 역할이 아니에요!")
                return
            await send(ctx, "해당 역할의 이름을 뭘로 수정할까요? 역할 이름 자체가 바뀌는 것은 아니에요.")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                after_name = msg.content
            except asyncio.TimeoutError:
                await send(ctx, "이름색 역할을 수정하지 않기로 했어요.")
                return
            db.execute("UPDATE roles SET role_info = ? WHERE RoleID = ?", after_name, role)
            db.commit()
            await send(ctx, "해당 이름색 역할의 이름 변경을 완료했어요!")
        else:
            await send(ctx, "`커뉴야 이름색역할 <목록/추가/삭제/수정>`")

    @command(name="계정삭제", aliases=["캐삭"])
    async def account_delete(self, ctx):
        await send(ctx, embed=Embed(color=0xffd6fe, title="계정 삭제 이전 주의사항 안내",
                                   description="1. 개인정보 처리 방침에도 나와 있듯 게정삭제 명령어로 삭제된 데이터는 어떤 방법으로도 복구할 수 없습니다.\n2. 이렇게 삭제되는 데이터는 봇과 같이 있는 서버에서 당신의 레벨 정보, 여태까지 모은 도전 과제, 강화 정보, 오목 정보 등을 모두 포함합니다.\n3. 요청이 들어오게 된다면 1일 안에 모든 데이터가 삭제되며, 만약 데이터가 삭제되지 않았다면 `커뉴야 문의`명령어를 통해 취소가 가능합니다. 계정삭제를 취소하겠다고 말 남겨 주세요.\n`삭제`라고 말해 계정삭제를 진행하세요"))
        try:
            msg = await self.bot.wait_for(
                "message",
                timeout=50,
                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
            )
        except asyncio.TimeoutError:
            await send(ctx, "작업을 취소했어요.")
            return
        if msg.content == "삭제":
            await send(ctx, "계정 삭제 처리를 진행합니다. 대부분의 경우 1일 안에 데이터가 모두 삭제될 예정이고 그 전에만 취소가 가능합니다.")
            await self.bot.get_channel(822461129384525824).send(f"{ctx.author.id} 의 계정삭제 요청")

    @command(name="권한진단")
    @has_permissions(administrator=True)
    async def permission_diagnose(self, ctx):
        perm = ctx.guild.get_member(772274871563583499).guild_permissions.value
        missing = []
        if perm & 2 == 0:
            missing.append("멤버 추방하기")
        if perm & 4 == 0:
            missing.append("멤버 차단하기")
        if perm & 8 == 0:
            missing.append("관리자")
        if perm & 16 == 0:
            missing.append("채널 관리하기")
        if perm & 32 == 0:
            missing.append("서버 관리하기")
        if perm & 64 == 0:
            missing.append("반응 추가하기")
        # 128: 감사로그 256: 우선발언권, 512: 영상공유
        if perm & 1024 == 0:
            missing.append("채널 보기")
        if perm & 2048 == 0:
            missing.append("메세지 보내기")
        # 4096: tts 메세지 보내기
        if perm & 8192 == 0:
            missing.append("메세지 관리")
        if perm & 16384 == 0:
            missing.append("링크 첨부")
        if perm & 32768 == 0:
            missing.append("파일 첨부")
        if perm & 65536 == 0:
            missing.append("메세지 기록 보기")
        # 131072: 에블핑
        if perm & 262144 == 0:
            missing.append("외부 임티 사용")
        # 524288: 서버 인사이트 보기
        # 1048576: 음성채팅 연결
        # 2097152: 음성채팅 말하기
        # 4194304: 음성채팅 뮤트
        # 8388608: 음성채팅 소리안들리게
        # 16777216: 음성채팅 멤버 이동
        # 33554432: Use Voice Activity
        if perm & 67108864 == 0:
            missing.append("별명 변경하기")
        if perm & 134217728 == 0:
            missing.append("별명 관리하기")
        if perm & 268435456 == 0:
            missing.append("역할 관리하기")
        # 536870912: 웹후크 관리
        # 1073741824: 이모지 관리
        # 2147483648: /명령어 사용
        missing = ",".join(missing)
        embed = Embed(color=0xffd6fe)
        embed.add_field(name="커뉴봇 권한 진단",
                        value="**멤버 추방** 권한이 없다면 추방 명령어 등을 쓸 수 없어요.\n\n**멤버 차단** 권한이 없다면 차단 명령어와 들낙 퇴치 시스템 등을 쓸 수 없어요.\n\n**채널 관리**권한이 없다면 슬로우모드 명령어 등을 쓸 수 없어요.\n\n**서버 관리** 권한이 없다면 초대 추적 시스템이 작동을 하지 않아 사람이 들어오거나 나갈 때 메세지를 출력하고 초대횟수를 더하는 것이 불가능하고, 초대와 관련된 모든 명령어를 쓸 수 없어요.\n\n**채널 보기** 권한이 없다면 레벨시스템이 정상적으로 작동하지 않을 수 있고, 명령어를 써도 인식을 할 수 없을 수 있어요.\n\n**메세지 보내기** 권한이 없다면 대부분의 명령어를 쓸 수 없어요. 또한 레벨업 시 메세지를 보내는 등의 기능도 정상적으로 작동하지 않아요.\n\n**메세지 관리** 권한이 없다면 삭제 명령어와 퀴즈 출제, 들낙 퇴치 시스템 등을 사용할 수 없어요.\n\n**링크 첨부** 권한이 없다면 퀴즈를 풀 때 일부 문제가 표시되지 않아요.\n\n**메세지 기록 보기** 권한이 없다면 반응추가권이 없어지며 삭제 명령어를 쓸 수 없어요.\n\n**외부 임티 사용** 권한이 없다면 서버추천 명령어가 오작동할 가능성이 높으며 일부 강화 명령어 등 예기치 못한 상황에서 제대로 출력할 수가 없어요.\n\n**별명 관리** 권한이 없다면 기원추가 명령어 등의 명령어를 쓸 수 없어요.\n\n**역할 관리** 권한이 없다면 레벨역할, 이름색 역할 등 역할에 기반한 모든 기능을 사용할 수 없어요.\n\n**관리자** 권한이 없다면 다른 관리자가 의도하지 않은 권한설정으로 인해 일부 기능이 갑자기 작동하지 않을 가능성이 있어요.\n\n**관리자**권한이 있다면 다른 권한이 없다고 뜨더라도 있는 거나 마찬가지라고 생각하셔도 돼요.\n\n마지막으로, 관리자 권한이 있다고 해도 자기보다 높은 역할은 건드릴 수 없으며 서버장의 닉네임은 변경할 수 없어요.",
                        inline=False)
        if not missing:
            embed.add_field(name="그렇다면 봇에게 없는 권한들은?",
                            value="없음! 만약 작동하지 않는 명령어가 있다면 다음과 같은 이유 중 하나입니다.\n1. 스레드에서 명령어를 실행함.\n2. 명령어 사용 대상이 서버장이거나 커뉴봇보다 역할 순서가 높음.",
                            inline=False)
        else:
            embed.add_field(name="그렇다면 봇에게 없는 권한들은?", value=missing, inline=False)
        embed.set_footer(text="권한을 안 주고 왜 안되냐며 불평한다면 그것은 무조건 서버 관리자 책임이며 개발자는 그것에 대해 사과하거나 보상해 줄 의무가 전혀 없습니다.")
        await send(ctx, embed=embed)

    async def update_realtime_lb(self):
        while True:
            msg1 = await self.bot.get_channel(824519567777726504).fetch_message(824529296843735080)
            msg2 = await self.bot.get_channel(824519567777726504).fetch_message(824529364694990848)
            xps = db.records(
                "SELECT UserID, Level, XP FROM exp WHERE GuildID = 743101101401964647 AND XP > 1800 ORDER BY XP desc LIMIT 50")
            tjfaud = ""
            for i in range(50):
                tjfaud += f"\n{i + 1}. {str(self.bot.get_user(xps[i][0]))} (레벨: {xps[i][1]}, 경험치: {xps[i][2]})\n"
                if i == 24:
                    await msg1.edit(content=tjfaud)
                    tjfaud = ""
            await msg2.edit(content=tjfaud)

            coins = db.records("SELECT * FROM coins WHERE coin_name != '화력코인'")
            coins = list(coins)
            for i in range(24):
                try:
                    coins[i] = list(coins[i])
                except IndexError:
                    break
                # coins[i][1]: 가격
                # coins[i][2]: 변동성
                n = coins[i][2]
                if random.randint(1, 2) == 1:
                    cdelta = random.uniform(-1 * n, 0)
                else:
                    cdelta = random.uniform(0, (10000 / (100 - n)) - 100)
                    if int(int(coins[i][1]) * (1 + cdelta / 100)) > 9223372036854775807:
                        cdelta = random.uniform(-0.7 * n, 0)
                db.execute("UPDATE coins SET value = ?, value_temp = ?, value_delta = ? WHERE coin_name = ?",
                           int(int(coins[i][1]) * (1 + cdelta / 100)), coins[i][2],
                           int(int(coins[i][1]) * (1 + cdelta / 100)) - coins[i][1], coins[i][0])
            db.commit()
            await self.send_attend_ready_message()
            await sleep(100)
            await self.send_attend_ready_message()
            await sleep(100)
            await self.send_attend_ready_message()
            await sleep(100)
            await self.send_attend_ready_message()
            await sleep(100)
            await self.send_attend_ready_message()
            await sleep(100)
            await self.send_attend_ready_message()
            await sleep(100)

    async def send_attend_ready_message(self):
        if (time.time() + 32400) % 86400 < 86400 - 300:
            return
        people_to_send = db.records("SELECT UserID FROM games WHERE user_setting & 65536 = 65536")
        for pts in people_to_send:
            await self.bot.get_user(pts[0]).send('11시 55분이 넘었어요. 어서 출석체크를 준비하세요! 알림을 끄려면 `커뉴야 출첵알림 꺼`를 입력하세요.')

    @command(name='출첵알림')
    async def attend_notification_command(self, ctx, activity: Optional[str] = ''):
        actual_user_setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
        user_setting = actual_user_setting  & 196608 // 65536
        switch = "꺼켜"[bool(user_setting & 2)]
        if not user_setting:
            await send(ctx, '먼저 뀨 상점에서 출첵 준비 알림을 구매해야 사용할 수 있는 기능이에요!')
            return
        elif user_setting == 2:
            await send(ctx, '??')
            return
        elif not activity:
            await send(ctx, f'현재는 출첵 준비 알림이 {switch}져 있어요!')
        elif activity in ['켜', '꺼']:
            if switch == activity:
                await send(ctx, '잘못된 입력이에요!')
                return
            else:
                await send(ctx, '변경을 완료했어요!')
                new_user_setting = actual_user_setting ^ 131072
                db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", new_user_setting, ctx.author.id)
                db.commit()
        else:
            await send(ctx, '`커뉴야 출첵알림 <(빈 칸)/꺼/켜>`')

    @command(name="커맨드금지")
    async def prohibit_commands(self, ctx, lvl: Optional[int]):
        if lvl is None:
            ctype = db.record("SELECT channel_type FROM channels WHERE ChannelID = ?", ctx.channel.id)[0]
            noup = ctype & 32 == 32
            ctype = ctype % 32 // 8
            tjfaud = f"현재 <#{ctx.channel.id}>의 커맨드금지 레벨은 {ctype} 레벨이에요!\n\n```0레벨: 모든 커맨드를 사용할 수 있습니다.\n1레벨: 모든 게임관련 커맨드를 금지합니다.\n2레벨: 레벨 시스템 관련 명령어 제외 모든 커맨드를 금지합니다.\n3레벨: 이 커맨드를 제외한 모든 커맨드를 금지합니다.\n\n금지 설정은 커뉴야 커맨드금지 (레벨)```"
            if noup:
                tjfaud += "\n또한 `커뉴야 올려` 명령어도 금지된 채널이에요!"
            await send(ctx, tjfaud)
            return
        if not ctx.author.guild_permissions.value & 16:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if lvl in [0, 1, 2, 3]:
            ctype = db.record("SELECT channel_type FROM channels WHERE ChannelID = ?", ctx.channel.id)
            ctype = ctype[0] % 32 // 8
            await send(ctx, f"커맨드 금지 레벨을 {lvl}(으)로 바꿨어요!")
            typedelta = 8 * (lvl - ctype)
            db.execute("UPDATE channels SET channel_type = channel_type + ? WHERE channelid = ?", typedelta,
                       ctx.channel.id)
            db.commit()

    @command(name="봇메세지무시", aliases=["봇메시지무시", "봇무시"])
    @has_permissions(administrator=True)
    async def ignore_bot_message(self, ctx, activity: Optional[str] = "조회"):
        servertype = db.record("SELECT guild_type FROM guilds WHERE GuildID = ?", ctx.guild.id)
        servertype = servertype[0]
        anti = servertype & 8 == 8
        if activity == "조회":
            if anti:
                await send(ctx, f"현재 {ctx.guild.name}에는 봇 메세지 무시하기 시스템이 **켜져** 있어요!")
            else:
                await send(ctx, f"현재 {ctx.guild.name}에는 봇 메세지 무시하기 시스템이 **꺼져** 있어요!")
        elif activity == "끔" or activity == "꺼":
            if anti:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype - 8, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 봇이 보낸 메세지를 무시하지 않아요.")
            else:
                await send(ctx, f"이미 {ctx.guild.name}에서는 봇이 보낸 메세지를 무시하지 않아요!")
                return
            db.commit()
        elif activity == "켬" or activity == "켜":
            if anti:
                await send(ctx, f"이미 {ctx.guild.name}에서는 봇이 보낸 메세지를 무시하고 있어요!")
            else:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype + 8, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 봇이 보낸 메세지를 무시해요.")
            db.commit()
        elif activity == "도움":
            await send(ctx, 
                "봇 메세지 무시하기 시스템은 말 그대로 봇이 보낸 메세지를 무시하는 시스템이에요. 이 시스템이 켜져 있다면 숫자채널, 세로채널 등의 채널에서 봇이 조건에 맞지 않는 메세지를 보내더라도 메세지가 삭제되지 않아요.")

    @command(name="닉홍보금지")
    @has_permissions(administrator=True)
    @bot_has_permissions(manage_nicknames=True)
    async def censor_nickname_ad(self, ctx, activity: Optional[str] = "조회"):
        servertype = db.record("SELECT guild_type FROM guilds WHERE GuildID = ?", ctx.guild.id)
        servertype = servertype[0]
        anti = servertype & 16 == 16
        if activity == "조회":
            if anti:
                await send(ctx, f"현재 {ctx.guild.name}에는 닉네임 홍보 금지 시스템이 **켜져** 있어요!")
            else:
                await send(ctx, f"현재 {ctx.guild.name}에는 닉네임 홍보 금지 시스템이 **꺼져** 있어요!")
        elif activity == "끔" or activity == "꺼":
            if anti:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype - 16, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 홍보성 닉네임이 있더라도 경고하지 않아요.")
            else:
                await send(ctx, f"이미 {ctx.guild.name}에서는 홍보성 닉네임을 금지하지 않아요!")
                return
            db.commit()
        elif activity == "켬" or activity == "켜":
            if anti:
                await send(ctx, f"이미 {ctx.guild.name}에서는 홍보성 닉네임을 금지하고 있어요!")
            else:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype + 16, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 홍보성 닉네임이 있다면 그 유저를 경고해요.")
            db.commit()
        elif activity == "도움":
            await send(ctx, 
                "닉네임 홍보 금지 시스템은 멤버의 닉네임이 바뀔 때 서버 링크가 들어가 있다면 그 멤버의 닉네임을 원래대로 되돌려 놓는 시스템이에요.")

    @command(name='경험치초기화')
    async def reset_lb(self, ctx):
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        await send(ctx, 
            '정말로 모든 서버 멤버의 경험치를 초기화 하시겠습니까? 이 작업은 복구할 수 **없으니** 신중히 결정하세요.\n`레벨`: 레벨과 경험치 정보만 초기화합니다. 모든 멤버가 레벨 0, 경험치 0이 됩니다.\n`경부`: 경험치 부스트 정보만 초기화합니다. 모든 멤버의 경험치 부스트가 1이 됩니다.\n`전부`: 레벨과 경험치, 경험치 부스트 정보를 전부 초기화합니다.\n다른 걸 입력하면 취소횝니다.')
        try:
            msg = await self.bot.wait_for(
                "message",
                timeout=600,
                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
            )
        except asyncio.TimeoutError:
            await send(ctx, "경험치 초기화 작업을 취소했어요")
            return
        check = 0
        if msg.content == '레벨':
            db.execute("UPDATE exp SET XP = 0, Level = 0 WHERE GuildID = ?", ctx.guild.id)
            check = 1
        elif msg.content == '경부':
            db.execute("UPDATE exp SET XPBoost = 1 WHERE GuildID = ?", ctx.guild.id)
            check = 1
        elif msg.content == '전부':
            db.execute("UPDATE exp SET XP = 0, Level = 0, XPBoost = 1 WHERE GuildID = ?", ctx.guild.id)
            check = 1
        if check == 1:
            db.commit()
            await send(ctx, f'{msg.content} 초기화했어요!')

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print('("mod")')

    @Cog.listener()
    async def on_reaction_add(self, reaction, user):  # 나중에 여기 잡소리 반응 다는거 함수 따로 만들자
        global reaction_message
        global cherry
        global z1list, z7list
        try:
            if reaction.message.id == reaction_message:
                if user.id in z1list:
                    return
                z1list.append(user.id)
                l = grant_check("잡소리 독자", user.id)
                if l == 1:
                    await grant(Dmdmo(author(user.id), reaction.message.channel), "잡소리 독자", "최근에 올라온 커뉴의 잡소리 모음에 반응을 다세요")
        except NameError:
            pass
        try:
            if reaction.message.id == cherry and reaction.emoji == "😩":
                if user.id in z7list:
                    return
                await reaction.message.channel.send(f"{user}님이 😩반응을 다셨습니다!")
                z7list.append(user.id)
        except NameError:
            pass

    @Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name == after.display_name:
            return
        servertype = db.record("SELECT guild_type FROM guilds WHERE GuildID = ?", after.guild.id)
        servertype = servertype[0]
        adblock = servertype & 16 == 16
        if adblock:
            ad_nick = re.compile("discord[.]gg/.*")
            ad = ad_nick.search(after.display_name)
            if ad:
                await self.ad_finalize(before, after)

    async def ad_finalize(self, before, after):
        await after.edit(nick=before.display_name)
        punish_log = db.record("SELECT punish_log FROM guilds WHERE GuildID = ?", after.guild.id)
        punish_log = self.bot.get_channel(punish_log[0])
        embed = discord.Embed(color=0xDD2222, title="닉네임 홍보 금지 시스템으로 닉네임이 바뀜",
                              description=f"닉네임 변경 조치된 유저: {after.mention}", timestamp=datetime.datetime.now())
        embed.set_thumbnail(url=after.avatar_url)
        try:
            await punish_log.send(embed=embed)
        except AttributeError:
            pass

    @Cog.listener()
    async def on_message(self, message):
        global reaction_message
        global cherry
        global z1list, z7list
        if message.is_system() or message.author.bot:
            return
        if random.randint(1, 8145060) == 1:
            l = grant_check("로또 안사고 뭐해요", message.author.id)
            if l == 1:
                await grant(message, "로또 안사고 뭐해요", "채팅을 칠 때마다 1/8,145,060의 확률로 얻을 수 있는 도전과제")
        if message.channel.id == 797349679107932201 and message.content.startswith("<@&815931875675471874>"):
            reaction_message = message.id
            z1list = []
            return
        elif message.content.startswith("<@&883633338953388042>") and message.channel.id == 901802045894455316:
            cherry = message.id
            z7list = []
            return

        for ping in message.mentions:
            try:
                shake = db.record("SELECT user_setting FROM games WHERE UserID = ?", ping.id)[0]
            except TypeError:
                shake = 0
            if shake & 2:
                await message.add_reaction(self.bot.get_emoji(825663930931085312))
                if '핑이나 막아라!' in message.content:
                    l = grant_check("핑이나 막아라!", message.author.id)
                    if l == 1:
                        await grant(message, "핑이나 막아라!", "핑이나 막아라! 라는 내용의 메세지를 보낸 후 커뉴봇이 핑셰이크 반응을 다는 것을 보세요")
                break
        if isinstance(message.channel, DMChannel):
            return
        if message.channel.id == 863409796933877770:
            await message.delete()
            await self.bot.get_channel(863412514230370304).send(
                embed=Embed(color=0xffd6fe, title=f"{str(message.author)}님의 신고", description=message.content))
            if message.attachments:
                at_ = ""
                for at in message.attachments:
                    at_ += "\n"
                    at_ += at.url
                await self.bot.get_channel(863412514230370304).send(f"또한 이런 첨부 파일(들)을 같이 보냄: {at_}")
        channel_type = db.record("SELECT channel_type FROM channels WHERE ChannelID = ?", message.channel.id)
        if message.guild.id == 743101101401964647:
            db.execute("UPDATE serverstat SET fire = fire + 1 WHERE day = ?", ((time.time() + 32400) // 86400))
            if message.author.bot:
                db.execute("UPDATE serverstat SET fire_bot = fire_bot + 1 WHERE day = ?",
                           ((time.time() + 32400) // 86400))
                db.commit()

        try:
            channel_type = channel_type[0]
        except TypeError:
            db.execute("INSERT INTO channels (ChannelID) VALUES (?)", message.channel.id)
            db.commit()
            channel_type = 0
        servertype = db.record("SELECT guild_type FROM guilds WHERE guildid = ?", message.guild.id)
        try:
            servertype = servertype[0]
        except TypeError:
            servertype = 0
        if message.channel.id == 1000636815239299082 and not message.author.bot:
            global current_count
            global excount
            if message.author.id in excount:
                if excount[message.author.id] < time.time():
                    del excount[message.author.id]
                else:
                    await message.delete()
                    return
            number = message.content.split()[0]
            check = 1
            try:
                number = int(number)
                if current_count == -1:
                    current_count = int(message.content) + 1
                else:
                    if number != current_count:
                        check = 0
                    else:
                        current_count += 1
            except ValueError:
                check = 0
            if not check:
                current_count = 1
                await message.channel.send(f'{message.author.display_name} 님에 의해 세던 게 끊겼습니다...')
                excount[message.author.id] = time.time() + 7200
            if current_count == 301:
                l = grant_check("눈치게임 고수", message.author.id)
                if l == 1:
                    await grant(message, "눈치게임 고수", "미자르에서 300을 세세요. 이런!")
            if current_count == 1001:
                l = grant_check("눈치게임 개고수", message.author.id)
                if l == 1:
                    await grant(message, "눈치게임 개고수", "미자르에서 1000을 세세요. 이런!")
        if channel_type & 1 == 1:
            if message.author.bot and servertype & 8 == 8:
                return
            num = db.record("SELECT num FROM channels WHERE ChannelID = ?", message.channel.id)
            num = num[0]
            if not message.content.startswith(str(num)):
                await message.delete()
            else:
                if "\n" in message.content:
                    await message.delete()
                    await message.channel.send(f"{num} 숫자채널에서는 메시지 하나에 숫자 여러 개를 세는 것을 막기 위해 한 줄로만 보낼 수 있어요!")

                num += 1
                db.execute("UPDATE channels SET num = ? WHERE ChannelID = ?", num, message.channel.id)
                db.commit()
                if message.channel.id == 743339107731767366:
                    if str(num + 10) == (str(num + 10))[::-1]:
                        await self.bot.get_channel(787284733552885760).send(
                            "<@&818437192975777802> 곧 거울수가 다가와요! <#743339107731767366>에서 확인해 보세요!")
                    if (num + 10) % 1000 == 0:
                        await self.bot.get_channel(787284733552885760).send(
                            "<@&819818448918020116> 곧 1000의 배수가 다가와요! <#743339107731767366>에서 확인해 보세요!")
                    if (num - 1) % 10000 == 0:
                        l = grant_check("1만배수 사냥꾼", message.author.id)
                        if l == 1:
                            await grant(message, "1만배수 사냥꾼", "공식서버의 숫자채널에서 10000의 배수 숫자를 세세요")
                    mission_users = db.records(
                        "SELECT UserID, mission_temp FROM games WHERE mission_achievement = '숫자를 많이 세다'")
                    for u in mission_users:
                        if message.author.id != u[0]:
                            try:
                                await self.bot.get_user(u[0]).send('`숫자를 많이 세다`도전과제를 실패했어요!')
                            except:
                                pass
                            db.execute(
                                "UPDATE games SET mission_achievement = NULL, mission_temp = NULL WHERE UserID = ?",
                                u[0])
                            db.commit()
                            return
                        if num >= int(u[1]) + 100:
                            await grant(message, '숫자를 많이 세다', "숫자를 많이 세다 칭호를 얻은 뒤 금성채널에서 한 번 더 100연속으로 숫자를 세세요")
                            await message.author.send('`숫자를 많이 세다`도전과제를 성공했어요! `커뉴야 도전과제` 명령어로 확인해 보세요')
                            db.execute(
                                "UPDATE games SET mission_achievement = NULL, mission_temp = NULL WHERE UserID = ?",
                                message.author.id)
                            db.commit()
                            return
                    venus_notification_users = db.records("SELECT UserID FROM games WHERE venus = ?", num - 1)
                    for vnu in venus_notification_users:
                        try:
                            await self.bot.get_user(vnu[0]).send(f'{num - 1}이 금성에서 세어졌어요! 다른 수 알림을 받고 싶으시면 `커뉴야 금성알림`')
                        except:
                            pass
        if message.channel.id == 760780692363411466 and not message.author.bot:
            await message.delete()
            await message.channel.send(message.content)
            return
        elif message.content == "ㅁㅎ9ㅐㄹ유ㅛㅍ티마ㅓㄱ혇ㄴ유ㅛㅊ9페8ㅐㅑㅚ머매ㅣㅎ묘ㅐ훃며ㅛㄹ988ㅂ 2489 ㅈㄷ묠ㄴ이ㅗㅕㅍㅌㅋ차ㅓ":
            await self.update_realtime_lb()
        elif message.content == "원준눈나":
            await message.channel.send("사랑행:smiling_face_with_3_hearts: :smiling_face_with_3_hearts:")
        elif message.content == "커뉴야":
            await message.channel.send("?")
        elif message.channel.id == 809285369450856491 and message.author.id == 724496900920705045:
            if message.content.startswith("SELECT"):
                returned = db.records(message.content)
                await message.channel.send(returned)
            else:
                db.execute(message.content)
                db.commit()
                await message.channel.send("완료")
        if message.content == "서바준보":
            await message.add_reaction(random.choice(
                ["👍", "🤣", "😁", "😄", "😃", "😀", "😆", "😂", self.bot.get_emoji(875349277088575508),
                 self.bot.get_emoji(875569903682322522)]))
            await message.channel.send(random.choice(["ㄹㅇㅋㅋ 섴ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ밬ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ준ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ봌ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ",
                                                      "ㅇㅇㅌㅌ 섵ㅌㅌㅌㅌㅌㅌㅌㅌㅌㅌㅌㅌ뱥ㅌㅌㅌㅌㅌㅌㅌㅌㅌㅌ준ㅌㅌㅌㅌㅌㅌㅌㅌㅌㅌㅂㅎㅌㅌㅌㅌㅌㅌㅌㅌㅌㅌㅌㅌㅌ"]))
            return

        babo = re.compile(".바.보")
        babg = re.compile(".뱌.ㅂㅎ")
        t = babo.match(message.content) or babg.match(message.content)
        if t and message.content[0] not in ["커", "켜", "컼"]:
            o = ord(message.content[0]) - 44032
            if o > 0 and not o % 28:
                o += 44032
                t1 = chr(o + 24)
            else:
                t1 = message.content[0]
            p = ord(message.content[2]) - 44032
            if o > 0 and not p % 28:
                p += 44032
                t2 = chr(p + 24)
            else:
                t2 = message.content[2]
            await message.add_reaction(random.choice(["👍", "🤣", "😁", "😄", "😃", "😀", "😆", "😂"]))
            await message.channel.send(f"ㄹㅇㅋㅋ {t1}ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ밬ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ{t2}ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ봌ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ")
        babo = re.compile(".병.신")
        t = babo.match(message.content)
        if t and message.content[0] != "커":
            o = ord(message.content[0]) - 44032
            if o > 0 and not o % 28:
                o += 44032
                t1 = chr(o + 24)
            else:
                t1 = message.content[0]
            p = ord(message.content[2]) - 44032
            if o > 0 and not p % 28:
                p += 44032
                t2 = chr(p + 24)
            else:
                t2 = message.content[2]
            await message.add_reaction(random.choice(["👍", "🤣", "😁", "😄", "😃", "😀", "😆", "😂"]))
            await message.channel.send(f"ㄹㅇㅋㅋ {t1}ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ병ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ{t2}ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ신ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ")
        babo = re.compile(".병.보")
        t = babo.match(message.content)
        if t and message.content[0] != "커":
            o = ord(message.content[0]) - 44032
            if o > 0 and not o % 28:
                o += 44032
                t1 = chr(o + 24)
            else:
                t1 = message.content[0]
            p = ord(message.content[2]) - 44032
            if o > 0 and not p % 28:
                p += 44032
                t2 = chr(p + 24)
            else:
                t2 = message.content[2]
            await message.add_reaction(random.choice(["👍", "🤣", "😁", "😄", "😃", "😀", "😆", "😂"]))
            await message.channel.send(f"ㄹㅇㅋㅋ {t1}ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ병ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ{t2}ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ봌ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ")
        if message.content.startswith("우커바"):
            await message.channel.send("우리 커여운 한바♡♡")
        elif channel_type & 4 == 4:
            if len(message.content) == 1 or (message.author.bot and channel_type & 8 == 8):
                return
            custom_emoji = re.compile("<a?:\w*:\d{18,19}>")
            c = custom_emoji.match(message.content)
            if not c:
                await message.delete()
                return
            if c.end() != len(message.content):
                await message.delete()
                return
        elif message.content == "민트초코":
            await message.channel.send(
                "달콤하고 쌉싸름한게 진짜 인생에 큰 행복이며 겁나 맛있으니 민초안먹는 흑우는 없을거라 믿는다 와 진짜 민트초코는 전설이다 민트초코 하와이안 피자 싸움수준 ㄹㅇ 실화냐? 민트초코압승이지 아ㅋㅋ")
        if message.content.startswith("커누야") or message.content.startswith("커뉴애") or message.content.startswith(
                "zㅓ뉴야") or message.content.startswith("zj뉴야") or message.content.startswith("zjsbdi"):
            await message.channel.send("<:ThinkingWeary:802379135036555284>")
        if servertype & 4 == 4:
            if message.content == "ㅎㅇ" and not message.author.bot:
                await message.channel.send("ㅎㅇ")
            elif message.content == "ㅂㅇ" and not message.author.bot:
                await message.channel.send("ㅂㅇ")
            elif len(message.content) != 0 and not message.author.bot:
                if len(message.content.replace("ㅠ", "")) == 0:
                    c = message.content
                    c = c + "ㅠ"
                elif len(message.content.replace("ㅋ", "")) == 0:
                    c = message.content
                    c = c + "ㅋ"
                elif len(message.content.replace("ㅎ", "")) == 0:
                    c = message.content
                    c = c + "ㅎ"
                elif len(message.content.replace("ㄷ", "")) == 0:
                    c = message.content
                    c = c + "ㄷ"
                try:
                    await message.channel.send(c)
                except NameError:
                    pass


async def setup(bot):
    await bot.add_cog(Mod(bot))
