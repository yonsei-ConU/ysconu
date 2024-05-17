from datetime import datetime

from discord import Embed, DMChannel
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

from typing import Optional
from ..db import db
import asyncio

from re import compile


class Log(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("log")

    @command(name="로그채널")
    @has_permissions(administrator=True)
    async def set_log_channel(self, ctx, activity: Optional[str] = "조회"):
        lv = db.record("SELECT log_channel FROM guilds WHERE GuildID = ?", ctx.guild.id)
        lv = lv[0]
        if activity == "조회":
            if not lv or lv == 1:
                await ctx.send(f"현재 {ctx.guild.name}의 로그 채널이 없어요!")
                return
            else:
                await ctx.send(f"현재 {ctx.guild.name}의 로그 채널은 <#{lv}>(이)에요!")
                return
        elif activity == "초기화":
            await ctx.send(f"{ctx.guild.name}애서 로그 기능을 껐어요!")
            ch = 1
        elif activity == "설정":
            await ctx.send("어느 채널을 로그 채널로 설정할 건가요?")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=10,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
            except asyncio.TimeoutError:
                await ctx.send("로그 채널을 설정하지 않기로 했어요.")
                return
            check = compile("<#[0-9]{18,19}>")
            c = check.match(msg.content)
            if not c:
                await ctx.send("올바르지 않은 형식이에요!")
                return
            if msg.content[21].isdigit():
                ch = msg.content[2:21]
            else:
                ch = msg.content[2:20]
            await ctx.send(f"이제 {ctx.guild.name}의 로그 채널은 <#{ch}>(이)에요!")
        else:
            await ctx.send("`커뉴야 로그채널 <조회/설정/초기화>`")
            return
        db.execute("UPDATE guilds SET log_channel = ? WHERE GuildID = ?", ch, ctx.guild.id)
        db.commit()

    @Cog.listener()
    async def on_member_update(self, before, after):
        if not before.guild:
            return
        logchannel = db.record("SELECT log_channel FROM guilds WHERE GuildID = ?", before.guild.id)
        if before.display_name != after.display_name:
            embed = Embed(title=f"{str(after)}이(가) 닉변함",
                          colour=after.colour,
                          timestamp=datetime.utcnow())

            fields = [("Before", before.display_name, False),
                      ("After", after.display_name, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            try:
                await self.bot.get_channel(logchannel[0]).send(embed=embed)
            except AttributeError:
                pass

        elif before.roles != after.roles:
            embed = Embed(title=f"{after}의 역할이 바뀜",
                          colour=after.colour,
                          timestamp=datetime.utcnow())

            if len(before.roles) < len(after.roles):
                changes = ",".join([r.name for r in (set(after.roles) - set(before.roles))])
                embed.add_field(name="새로 추가된 역할(들)", value=changes)

            else:
                changes = ",".join([r.name for r in (set(before.roles) - set(after.roles))])
                embed.add_field(name="없어진 역할(들)", value=changes)

            try:
                await self.bot.get_channel(logchannel[0]).send(embed=embed)
            except AttributeError:
                pass

    @Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.author.bot:
            if before.content != after.content:
                logchannel = db.record("SELECT log_channel FROM guilds WHERE GuildID = ?", before.guild.id)
                embed = Embed(title=f"{str(after.author)} (ID {after.author.id})의 메세지가 수정됨",
                              description=f"메세지가 수정된 채널: <#{after.channel.id}>",
                              colour=after.author.colour,
                              timestamp=datetime.utcnow())

                if not before.content:
                    fields = [("Before", "없음", False),
                              ("After", after.content, False)]
                else:
                    fields = [("Before", before.content, False),
                              ("After", after.content, False)]

                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                try:
                    await self.bot.get_channel(logchannel[0]).send(embed=embed)
                except AttributeError:
                    pass

    @Cog.listener()
    async def on_member_ban(self, guild, member):
        logchannel = db.record("SELECT log_channel FROM guilds WHERE GuildID = ?", guild.id)
        embed = Embed(title=f"{str(member)} (ID {member.id}) 이(가) 서버에서 차단됨",
                      colour=member.colour,
                      timestamp=datetime.utcnow())
        try:
            await self.bot.get_channel(logchannel[0]).send(embed=embed)
        except AttributeError:
            return

    @Cog.listener()
    async def on_guild_channel_create(self, channel):
        logchannel = db.record("SELECT log_channel FROM guilds WHERE GuildID = ?", channel.guild.id)
        try:
            embed = Embed(title=f"새로운 채팅 채널 (ID {channel.id}) 이(가) 생성됨",
                          description=f"채널 이름: {channel.name}\n카테고리: <#{channel.category_id}>\n연령 제한 채널 여부: {channel.is_nsfw()}",
                          colour=0xffd6fe,
                          timestamp=datetime.utcnow())
        except AttributeError:
            embed = Embed(title=f"새로운 음성 채널 (ID {channel.id}) 이(가) 생성됨",
                          description=f"채널 이름: {channel.name}\n카테고리: <#{channel.category_id}>",
                          colour=0xffd6fe,
                          timestamp=datetime.utcnow())
        try:
            await self.bot.get_channel(logchannel[0]).send(embed=embed)
        except AttributeError:
            return

    @Cog.listener()
    async def on_guild_channel_delete(self, channel):
        logchannel = db.record("SELECT log_channel FROM guilds WHERE GuildID = ?", channel.guild.id)
        try:
            embed = Embed(title=f"있던 채팅 채널 (ID {channel.id}) 이(가) 삭제됨",
                          description=f"채널 이름: {channel.name}\n카테고리: <#{channel.category_id}>\n연령 제한 채널 여부: {channel.is_nsfw()}",
                          colour=0xffd6fe,
                          timestamp=datetime.utcnow())
        except AttributeError:
            embed = Embed(title=f"있던 음성 채널 (ID {channel.id}) 이(가) 삭제됨",
                          description=f"채널 이름: {channel.name}\n카테고리: <#{channel.category_id}>",
                          colour=0xffd6fe,
                          timestamp=datetime.utcnow())
        try:
            await self.bot.get_channel(logchannel[0]).send(embed=embed)
        except AttributeError:
            return

    @Cog.listener()
    async def on_guild_role_create(self, role):
        logchannel = db.record("SELECT log_channel FROM guilds WHERE GuildID = ?", role.guild.id)
        embed = Embed(title=f"새로운 역할 (ID {role.id}) 이(가) 생성됨",
                      description=f"역할 이름: {role.name}\n역할 색깔: {role.color}\n온라인 멤버와 구별 표시: {role.hoist}",
                      colour=role.color,
                      timestamp=datetime.utcnow())
        try:
            await self.bot.get_channel(logchannel[0]).send(embed=embed)
        except AttributeError:
            return

    @Cog.listener()
    async def on_guild_role_delete(self, role):
        logchannel = db.record("SELECT log_channel FROM guilds WHERE GuildID = ?", role.guild.id)
        embed = Embed(title=f"있던 역할 (ID {role.id}) 이(가) 삭제됨",
                      description=f"역할 이름: {role.name}\n역할 색깔: {role.color}\n온라인 멤버와 구별 표시: {role.hoist}",
                      colour=role.color,
                      timestamp=datetime.utcnow())
        try:
            await self.bot.get_channel(logchannel[0]).send(embed=embed)
        except AttributeError:
            return

    @Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot and not isinstance(message.channel, DMChannel):
            logchannel = db.record("SELECT log_channel FROM guilds WHERE GuildID = ?", message.guild.id)
            embed = Embed(title=f"{str(message.author)} (ID {message.author.id})의 메세지가 삭제됨",
                          description=f"메세지가 삭제된 채널: <#{message.channel.id}>",
                          colour=message.author.colour,
                          timestamp=datetime.utcnow())

            if message.content:
                embed.add_field(name="내용", value=message.content)
            else:
                embed.add_field(name="내용", value="없음")

            try:
                await self.bot.get_channel(logchannel[0]).send(embed=embed)
            except AttributeError:
                return

            if message.attachments:
                at_ = ""
                for at in message.attachments:
                    at_ += "\n"
                    at_ += at.url
                await self.bot.get_channel(logchannel[0]).send(f"또한 이런 첨부 파일(들)이 삭제됨: {at_}")

    @Cog.listener()
    async def on_member_join(self, member):
        logchannel = db.record("SELECT log_channel FROM guilds WHERE GuildID = ?", member.guild.id)
        embed = Embed(title="새로운 멤버가 들어옴",
                      colour=0x00ff00,
                      timestamp=datetime.utcnow())
        try:
            invites = await member.guild.invites()
        except:
            return
        invites_saved = db.records("SELECT invite_code, uses FROM invites WHERE guildid = ?", member.guild.id)
        inviter = ""
        for invite in invites:
            for invite_to_compare in invites_saved:
                if invite_to_compare[0] == invite.code and invite_to_compare[1] != invite.uses:
                    inviter = invite.inviter
        if not inviter:
            inviter = "추적할 수 없음"
        fields = [("사용자명#태그", member, True),
                  ("현재 서버 멤버 수", member.guild.member_count, True),
                  ("데려온 사람", inviter, True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        try:
            await self.bot.get_channel(logchannel[0]).send(embed=embed)
        except AttributeError:
            pass

    @Cog.listener()
    async def on_member_remove(self, member):
        logchannel = db.record("SELECT log_channel FROM guilds WHERE GuildID = ?", member.guild.id)
        embed = Embed(title="있던 멤버가 나감",
                      colour=0xff0000,
                      timestamp=datetime.utcnow())
        inviter = db.record("SELECT invited_by FROM exp WHERE UserID = ? AND GuildID = ?", member.id, member.guild.id)

        fields = [("사용자명#태그", member, True),
                  ("남은 서버 멤버 수", member.guild.member_count, True),
                  ("서버에 들어왔던 날짜", member.joined_at, True),
                  ("서버에 들어온 후 나갈 때까지 지난 시간", datetime.utcnow() - member.joined_at, True)]
        try:
            fields.append(("그 사람을 데려왔던 사람", self.bot.get_user(inviter[0]), True))
        except TypeError:
            pass

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        try:
            if logchannel:
                await self.bot.get_channel(logchannel[0]).send(embed=embed)
        except AttributeError:
            pass


def setup(bot):
    bot.add_cog(Log(bot))