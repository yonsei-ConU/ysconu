import discord
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions
from typing import Optional
import asyncio
from datetime import datetime, timedelta
from time import time

from ..db import db
from discord.app_commands import command as slash, choices, Choice
from ..utils.send import send


class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="환영채널")
    @has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, activity: Optional[str] = "조회"):
        welcome_channel = db.record("SELECT welcome_channel FROM guilds WHERE GuildID = ?", ctx.guild.id)
        welcome_channel = welcome_channel[0]
        if activity == "조회":
            if welcome_channel == 1:
                await send(ctx, f"현재 {ctx.guild.name}의 환영 채널이 없어요!")
                return
            else:
                await send(ctx, f"현재 {ctx.guild.name}의 환영 채널은 <#{welcome_channel}>(이)에요!")
                return
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity == "초기화":
            await send(ctx, f"이제 {ctx.guild.name}에서는 새로 사람이 들어오거나 나가도 알림이 표시되지 않아요!")
            ch = 1
        elif activity == "설정":
            await send(ctx, "어느 채널을 환영 채널로 설정할 건가요?")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=10,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                ch = msg.content[2:20]
            except asyncio.TimeoutError:
                await send(ctx, "환영 채널을 설정하지 않기로 했어요.")
                return
            await send(ctx, f"이제 {ctx.guild.name}의 환영 채널은 <#{msg.content[2:20]}>(이)에요!")
        elif activity == "끔":
            return
        else:
            await send(ctx, "`커뉴야 환영채널 <조회/설정/초기화>`")
            return
        db.execute("UPDATE guilds SET welcome_channel = ? WHERE GuildID = ?", ch, ctx.guild.id)
        db.commit()

    @command(name="들낙퇴치")
    async def anti_dlnak(self, ctx, activity: Optional[str] = "조회"):
        servertype = db.record("SELECT guild_type FROM guilds WHERE GuildID = ?", ctx.guild.id)
        servertype = servertype[0]
        anti = servertype & 2 == 2
        if activity == "조회":
            if anti:
                await send(ctx, f"현재 {ctx.guild.name}에는 들낙 퇴치 시스템이 **켜져** 있어요!")
            else:
                await send(ctx, f"현재 {ctx.guild.name}에는 들낙 퇴치 시스템이 **꺼져** 있어요!")
            return
        elif activity == "도움":
            await send(ctx, 
                "들낙 퇴치 시스템은 들낙한 사람을 차단시켜서 다시 못 오게 만드는 시스템이에요! 들낙 퇴치 시스템이 켜져 있다면 나갈 때 커뉴봇 레벨 기준 0레벨이었거나 들어온 지 10분도 안 돼서 나간 사람을 들낙으로 간주, 차단해요.")
            return
        if not ctx.author.guild_permissions.value & 8:
            await send(ctx, "이 명령어를 실행할 권한이 없어요!")
            return
        if activity in ["끔", "꺼", "끄기"]:
            if anti:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype - 2, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 들낙을 퇴치하지 않아요.")
            else:
                await send(ctx, f"이미 {ctx.guild.name}에서는 들낙을 퇴치하지 않아요!")
                return
            db.commit()
        elif activity in ["켬", "켜", "켜기"]:
            if anti:
                await send(ctx, f"이미 {ctx.guild.name}에서는 들낙을 퇴치하고 있어요!")
            else:
                db.execute("UPDATE guilds SET guild_type = ? WHERE GuildID = ?", servertype + 2, ctx.guild.id)
                await send(ctx, f"변경을 완료했어요! 이제 {ctx.guild.name}에서는 들낙을 퇴치해요.")
            db.commit()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print('("welcome")')

    @Cog.listener()
    async def on_invite_create(self, invite):
        db.execute("INSERT INTO invites (invite_code, uses, guildid) VALUES (?, 0, ?)", invite.code, invite.guild.id)
        db.commit()

    @Cog.listener()
    async def on_invite_delete(self, invite):
        db.execute("DELETE FROM invites WHERE invite_code = ?", invite.code)
        db.commit()

    def to_visual_string(self, string_to_convert, member, inviter, invite_score):
        string_to_convert = string_to_convert.replace("<멤버_사용자명#태그>", str(member))
        string_to_convert = string_to_convert.replace("<멤버_이름>", str(member.display_name))
        string_to_convert = string_to_convert.replace("<멤버_멘션>", str(member.mention))
        string_to_convert = string_to_convert.replace("<서버명>", str(member.guild.name))
        string_to_convert = string_to_convert.replace("<서버_멤버수>", str(member.guild.member_count))
        string_to_convert = string_to_convert.replace("<서버_순인원>",
                                                      str(len(list(filter(lambda m: not m.bot, member.guild.members)))))
        string_to_convert = string_to_convert.replace("<데려온_사람>", str(inviter))
        string_to_convert = string_to_convert.replace("<데려온_사람_닉네임>", inviter.display_name)
        string_to_convert = string_to_convert.replace("<데려온_사람_초대횟수>", str(invite_score))

        return string_to_convert

    @Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 743101101401964647:
            db.execute("UPDATE serverstat SET member_delta = member_delta + 1 where day = ?",
                       ((time() + 32400) // 86400))
        welcomechannel, join_message = db.record("SELECT welcome_channel, join_message FROM Guilds WHERE GuildID = ?",
                                                 member.guild.id)
        try:
            invites = await member.guild.invites()
            invites_saved = db.records("SELECT invite_code, uses FROM invites WHERE guildid = ?", member.guild.id)
            for invite in invites:
                for invite_to_compare in invites_saved:
                    if invite_to_compare[0] == invite.code and invite_to_compare[1] != invite.uses:
                        inviter = invite.inviter
                        inb = db.record("SELECT invite_boost FROM guilds WHERE GuildID = ?", member.guild.id)[0]
                        db.execute("UPDATE invites SET uses = ? WHERE invite_code = ?", invite.uses, invite.code)
                        db.execute(
                            "UPDATE exp SET invite_score = invite_score + 1, xpboost = xpboost + ? WHERE UserID = ? AND GuildID = ?",
                            inviter.id, inb, member.guild.id)
                        db.execute("INSERT INTO exp (UserID, GuildID, invited_by) VALUES (?, ?, ?)", member.id,
                                   member.guild.id, inviter.id)
                        db.commit()
                        try:
                            invite_score = db.record("SELECT invite_score FROM exp WHERE UserID = ? AND GuildID = ?",
                                                     inviter.id, member.guild.id)
                            try:
                                invite_score = invite_score[0]
                            except TypeError:
                                db.execute("INSERT INTO exp (UserID, GuildID, invite_score) VALUES (?, ?, 1)",
                                           inviter.id, member.guild.id)
                            join_message = self.to_visual_string(join_message, member, inviter, invite_score)
                            await self.bot.get_channel(welcomechannel).send(join_message)
                            return
                        except AttributeError:
                            return
        except discord.errors.Forbidden:
            try:
                await self.bot.get_channel(welcomechannel).send(self.to_visual_string(join_message, member, 0, 0))
            except AttributeError:
                pass

    @Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id == 743101101401964647:
            db.execute("UPDATE serverstat SET member_delta = member_delta - 1 where day = ?",
                       ((time() + 32400) // 86400))
        welcomechannel, guild_type, leave_message = db.record(
            "SELECT welcome_channel, guild_type, leave_message FROM Guilds WHERE GuildID = ?", member.guild.id)
        lv = db.record("SELECT Level FROM exp WHERE UserID = ? AND GuildID = ?", member.id, member.guild.id)
        msg_to_send = ""
        try:
            lv = lv[0]
        except TypeError:
            pass
        if guild_type & 2 == 2:
            if lv == 0 or datetime.now() - member.joined_at < timedelta(minutes=10):
                msg_to_send += f"커뉴봇 들낙 퇴치 시스템에 따라 {str(member)}(이)라는 들낙자를 영구차단 시켰습니다.\n아래는 사유들입니다:"
                reason = ""
                if lv == 0:
                    reason += "\n0레벨인 상태에서 나감"
                if datetime.now() - member.joined_at < timedelta(minutes=10):
                    time_past_join_1 = datetime.now().strftime("%M분 %S초")
                    time_past_join_2 = member.joined_at.strftime("%M분 %S초")
                    time_past_join_3 = int(time_past_join_1[0:2]) - int(time_past_join_2[0:2])
                    time_past_join_4 = int(time_past_join_1[4:6]) - int(time_past_join_2[4:6])
                    if time_past_join_4 < 0:
                        time_past_join_4 += 60
                        time_past_join_3 -= 1
                    time_past_join = f"{time_past_join_3}분 {time_past_join_4}초"
                    reason += f"\n들어온 지 {time_past_join}만에 나감"
                msg_to_send = msg_to_send + reason
        if msg_to_send != "":
            await member.ban(reason="들낙")
            punish_log = db.record("SELECT punish_log FROM guilds WHERE GuildID = ?", member.guild.id)
            punish_log = self.bot.get_channel(punish_log[0])
            embed = discord.Embed(color=0xDD2222, title="들낙 퇴치 시스템으로 차단됨",
                                  description=f"차단된 사람: {str(member)}\n정확한 이유: {reason}", timestamp=datetime.now())
            embed.set_thumbnail(url=member.avatar_url)
            try:
                await punish_log.send(embed=embed)
            except AttributeError:
                pass
        inviter = db.record("SELECT invited_by FROM exp WHERE UserID = ? AND GuildID = ?", member.id, member.guild.id)
        try:
            inviter_ = self.bot.get_user(inviter[0])
            invite_score = db.record("SELECT invite_score FROM exp WHERE UserID = ? AND GuildID = ?", inviter[0],
                                     member.guild.id)
            try:
                invite_score = invite_score[0]
                invite_score -= 1
                inb = db.record("SELECT Invite_boost FROM GuildS WHERE GuildID = ?", member.guild.id)[0]
                db.execute(
                    "UPDATE exp SET invite_score = invite_score - 1, xpboost = xpboost - ? WHERE UserID = ? AND GuildID = ?",
                    inb, inviter[0],
                    member.guild.id)
            except TypeError:
                pass
            try:
                await self.bot.get_channel(welcomechannel).send(
                    self.to_visual_string(leave_message, member, inviter_, invite_score))
            except AttributeError:
                pass
        except TypeError:
            try:
                await self.bot.get_channel(welcomechannel).send(
                    f"{member.display_name}이 {member.guild.name}에서 나갔대요. <:fucyou:787118326081781810>")
            # await self.bot.get_channel(welcomechannel).send(self.to_visual_string(leave_message, member, 0, 0))
            except AttributeError:
                pass
        if msg_to_send != "":
            try:
                await self.bot.get_channel(welcomechannel).send(msg_to_send)
            except AttributeError:
                pass
        db.execute("DELETE FROM exp WHERE UserID = ? AND GuildID = ?", member.id, member.guild.id)
        db.commit()


async def setup(bot):
    await bot.add_cog(Welcome(bot))
