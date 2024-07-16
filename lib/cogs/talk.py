import discord
from discord import Member, Embed, User
from discord.app_commands import command as slash, guild_only
from discord.ext.commands import Cog, command
from ..utils.send import send
from .achieve import grant_check, grant
from ..db import db
import random
from datetime import datetime, timedelta
from typing import Optional, Union


class Talk(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="올려", aliases=["🥴"])
    async def up_normal(self, ctx):
        await self.up(ctx)

    @slash(name="올려", description='채팅을 올려 줍니다.')
    async def up_slash(self, interaction):
        await self.up(interaction)

    async def up(self, where):
        channel_type = db.record("SELECT channel_type FROM channels WHERE ChannelID = ?", where.channel.id)
        if channel_type[0] & 2 == 2:
            await send(where, "왜그래요ㅎㅎ 원래 이러려고 있는 방 아닌가요?")
            return
        await send(where, "** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** **\n** "
                        "**\n** **\n** **\n** **\n** **\n** **\n** **\n** **")

    @command(name="프사")
    async def avatar_normal(self, ctx, *, target: Optional[Union[Member, User]]):
        print(ctx, target or ctx.author)
        await self.display_avatar(ctx, target or ctx.author)

    @slash(name="프사", description='원하는 유저의 프로필 사진을 보여 줍니다.')
    async def avatar_slash(self, interaction, target: Optional[Union[Member, User]]):
        await self.display_avatar(interaction, target or interaction.user)

    async def display_avatar(self, where, target):
        try:
            await send(where, target.avatar)
        except discord.HTTPException:
            await send(where, "존재하지 않는 멤버에요!")

    @command(name="서버사진", aliases=["서버아이콘", "서버프사"])
    async def guild_icon_normal(self, ctx):
        await self.display_guild_icon(ctx)

    @slash(name="서버사진", description="명령어가 입력된 서버의 사진을 보여 줍니다.")
    @guild_only()
    async def guild_icon_slash(self, interaction):
        await self.display_guild_icon(interaction)

    async def display_guild_icon(self, ctx):
        await send(ctx, ctx.guild.icon)

    @command(name="와!")
    async def wa(self, ctx):
        await send(ctx, "샌즈!")

    @command(name="서버시간", aliases=["서버시각", "서버시계"])
    async def server_time_normal(self, ctx):
        await self.server_time(ctx)

    @slash(name='서버시각', description='커뉴봇이 돌아가는 서버의 시계를 표시해요.')
    async def server_time_slash(self, interaction):
        await self.server_time(interaction)

    async def server_time(self, ctx):
        await send(ctx, (datetime.now()).strftime("지금은 %Y년 %m월 %d일 %H시 %M분 %S초에요!"))

    @command(name="언더테일")
    async def wa_sans(self, ctx):
        await send(ctx, 
            "언더테일 아시는구나! 혹시 모르시는분들에 대해 설명해드립니다 샌즈랑 언더테일의 세가지 엔딩루트중 몰살엔딩의 최종보스로 진.짜.겁.나.어.렵.습.니.다 공격은 전부다 회피하고 만피가 92인데 샌즈의 공격은 1초당 60이 다는데다가 독뎀까지 추가로 붙어있습니다.. 하지만 이러면 절대로 게임을 깰 수 가없으니 제작진이 치명적인 약점을 만들었죠. 샌즈의 치명적인 약점이 바로 지친다는것입니다. 패턴들을 다 견디고나면 지쳐서 자신의 턴을 유지한채로 잠에듭니다. 하지만 잠이들었을때 창을옮겨서 공격을 시도하고 샌즈는 1차공격은 피하지만 그 후에 바로날아오는 2차 공격을 맞고 죽습니다.")

    @command(name="사귀자")
    async def reject(self, ctx):
        await send(ctx, "tha(N)k y(O)u")

    @command(name="내려", aliases=["ㅡㅡ", "🤔"])
    async def plz_stop(self, ctx):
        channeltype = db.record("SELECT channel_type FROM channels WHERE channelid = ?", ctx.channel.id)
        if channeltype[0] & 2 == 2 and '내려' in ctx.message.content:
            await send(ctx, "뭘?...:hearts:")
            l = grant_check("2 * 3²", ctx.author.id)
            if l == 1:
                await grant(ctx, "2 * 3²", "당신이 이유를 더 잘 알 것 같군요...")
            return
        await send(ctx, ":weary:")

    @command(name="헤으응")
    async def gpdmdmd(self, ctx):
        channeltype = db.record("SELECT channel_type FROM channels WHERE channelid = ?", ctx.channel.id)
        if channeltype[0] & 2 == 2:
            await send(ctx, "헤으응...")
            return
        await send(ctx, "...?")

    @command(name="싼다")
    async def thronking(self, ctx):
        channeltype = db.record("SELECT channel_type FROM channels WHERE channelid = ?", ctx.channel.id)
        if channeltype[0] & 2 == 2:
            await send(ctx, "잔뜩 싸주세요♡")
            return
        await send(ctx, "(대충 경멸하는 눈빛)")

    @command(name="빨아")
    async def suck(self, ctx):
        channeltype = db.record("SELECT channel_type FROM channels WHERE channelid = ?", ctx.channel.id)
        if channeltype[0] & 2 == 2:
            await send(ctx, "읏...:hearts:")
            return
        else:
            await send(ctx, "사탕? 아니면...")

    @command(name="미륙")
    async def mee6(self, ctx):
        await send(ctx, "커뉴야 올려")

    @command(name="롤")
    async def lol(self, ctx):
        await send(ctx, "소환사의 협곡에 잘오셨습니다!")

    @command(name="배그")
    async def battleground(self, ctx):
        await send(ctx, "무서운 게임")

    @command(name="욕설")
    async def ssibal(self, ctx):
        await send(ctx, "심하게 하진 마라")

    @command(name="도배")
    async def dobae(self, ctx):
        await send(ctx, "하면 경고 받어")

    @command(name="극혐")
    async def hyum(self, ctx):
        await send(ctx, "...흐어어엉")

    @command(name="에헤무아이")
    async def wtfisthis(self, ctx):
        await send(ctx, "에헤무아이")

    @command(name="애교")
    async def aegyo_normal(self, ctx):
        await self.aegyo(ctx)

    @slash(name='애교', description='에휴')
    async def aegyo_slash(self, interaction):
        await self.aegyo(interaction)

    async def aegyo(self, ctx):
        us = db.record("SELECT user_setting FROM games WHERE useriD = ?", ctx.author.id)[0]
        if us & 1:
            await send(ctx, random.choice(
                ["뿌잉 마싯뉸거 사듀떼요ㅠ3ㅠ 뀨뀨", "코가간디러벙.. 에튜ㅣ!!!>3< 뀨잉 뿌우우이이이잉~♥", "나보다 기요운애 나와바!!ㅡ3ㅡ 뀨잉 뀨뀨",
                 "세계최강 기요미는 바로 나얍! 내가 우주최강기요미~~~ 뀨뀨!! 나뉸 기요밍~~", "나 쫌 기요벙?! >3< 뀨뀨!! 나뉸 기요밍~~ 쪼꼬렛 먹구띠퐁.. ㅇ0ㅇ",
                 "나 아포!! 호~ 해됴!! 기욤폭발!!!>3< 기요미와쪄용~~", "아잉~~ ㄸㅏ랑햅~이따만쿰!!♥ 나눈 너무 기요엉",
                 "내 기요움에 반해또? ㅇ0ㅇ 나 쫌 기요벙?! >3< >0<", "나는기요어어어엉~~ 뿌잉뿌잉 >0<<", "나 왜이로케 따랑뜨럽디? ㅇ0ㅇ 뀨잉 ♥",
                 ">_< 나뉸 너무 따랑뜨러어!! 뀨뀨!! 나뉸 기요밍~~", "뿌잉뿌잉>_<", "내 기요움에 반해또? ㅇ0ㅇ 오잉ㅇ3ㅇ? >3<",
                 "기욤발사!!!!쀼쀼♥ >0< 나보다 기요운애 이또??", "뀨", "뀨?!", "뀨우...:hearts:",
                 "쫀득쫀득한 피자 치쥬가 뫄이뫄이 들어있는 피이자이아아...! 햄토핑도 좋쿠우 빵에들어가있누눈 치즈도 좋쿠우 매코무한양파아아..!! 피먀양 맛 없써어! 새쿄뮤한 토마토쇼슈 버섯 뫄이쩌엉! 피자 사듀떼여"]).replace(
                "~~", "~\\~"))
        else:
            if random.randint(1, 50) != 1:
                await send(ctx, "500000<:treasure:811456823248027648> 을 내고 볼수있어!")
                return
            await send(ctx, "500000 내라니까")

    @command(name="사과")
    async def apple(self, ctx):
        await send(ctx, "나는 배가 더 좋아")

    @command(name="노잼")
    async def not_fun(self, ctx):
        await send(ctx, "난 재미있는데")

    @command(name="아재개그")
    async def dadjoke(self, ctx):
        await send(ctx, "경찰관들의 혈액형은? B형~ B형~")

    @command(name="고딩커뉴")
    async def sad_conu_because_he_is_goding(self, ctx):
        await send(ctx, "날 만든 분이지")

    @command(name="와!")
    async def wa(self, ctx):
        await send(ctx, "샍! 아시는구나!")

    @command(name="...")
    async def dotdotdot(self, ctx):
        await send(ctx, "그리고 아무도 없었다")

    @command(name="좋아해", aliases=["에러"])
    async def i_like_u(self, ctx):
        await send(ctx, "에러남")
        if "좋아해" in ctx.message.content:
            l = grant_check("에러 안 났잖아", ctx.author.id)
            if l == 1:
                await grant(ctx, "에러 안 났잖아", "사실 정지 먹이는 코드 작동 도중 에러가 난 걸수도...?")

    @command(name="카뉴야")
    async def idiot_typo(self, ctx):
        await send(ctx, "카뉴? 커피 말하는 거야?")

    @command(name="크뉴야")
    async def idiot_typo_2(self, ctx):
        await send(ctx, "내이름은 크뉴가 아니라 커뉴다")

    @command(name="커뉴야")
    async def why_u_call_me_twice(self, ctx):
        await send(ctx, "1번만 불러라")

    @command(name="뻘뻘")
    async def ppul_ppul(self, ctx):
        await send(ctx, "긴장감 MAX")

    @command(name="후덜덜")
    async def gee(self, ctx):
        await send(ctx, "추워? 난로에 가까이 가!")

    @command(name="안돼")
    async def no_u_cant(self, ctx):
        if i := random.randint(1, 2) == 1:
            await send(ctx, "왜?")
            return
        await send(ctx, "힝...ㅠ")

    @command(name="사랑해")
    async def what_the_fuck_are_you_talking_about(self, ctx):
        if ctx.author.id == 740598026711859231:
            await send(ctx, "미친넘;;")
            return
        await send(ctx, "나도 :kissing_heart:")

    @command(name="배고파")
    async def djWjfkrh(self, ctx):
        await send(ctx, "내 사랑을 먹어 :heart_eyes:")

    @command(name="한글")
    async def han_geul(self, ctx):
        sent = await send(ctx, "내가 만듦")
        await sent.edit(content="** **")

    @command(name="?")
    async def miaping(self, ctx):
        if ctx.message.content.startswith("ㅋ"):
            return
        await send(ctx, "!")

    @command(name="우와")
    async def waa(self, ctx):
        await send(ctx, "멋지다!")

    @command(name="바보")
    async def babo(self, ctx):
        if ctx.author.id == 604943753995878400:
            await send(ctx, "배리나주제에 ㅉㅉ")
            return
        await send(ctx, "커뉴 바보 아니양!")

    @command(name="왜")
    async def y(self, ctx):
        await send(ctx, "뭐")

    @command(name="뭐하냐")
    async def what_ru_doing(self, ctx):
        await send(ctx, "아무것도")

    @command(name="1+1=?")
    async def law_of_bed(self, ctx):
        if ctx.author.id == 604943753995878400:
            await send(ctx, "뭐이씨발련아 사람한명 플러스 사람한명은 사람세명이라고 그럴라그랬냐? ㅉㅉ 변태쉑")
            return
        await send(ctx, "3! 나 잘했지!")

    @command(name="잘자")
    async def lets_sleep_together(self, ctx):
        await send(ctx, "그래 너도")

    @command(name="뭐해")
    async def anjgo(self, ctx):
        await send(ctx, "너 생각해")

    @command(name="샌즈")
    async def sans(self, ctx):
        await send(ctx, "아시는구나!")

    @command(name="나가")
    async def go_away(self, ctx):
        await send(ctx, "너먼저나가")

    @command(name="거울")
    async def mirror(self, ctx):
        await send(ctx, "(대충 못생긴 짤)")

    @command(name="커뉴바보")
    async def add_mute_role(self, ctx):
        role = ctx.message.guild.get_role(748497654279045161)
        await ctx.author.add_roles(role)

    @command(name="커뉴")
    async def conu(self, ctx):
        await send(ctx, "이세계의 최종보스")

    @command(name="뉴커")
    async def unoc(self, ctx):
        await send(ctx, "이세계의 최종보스?")

    @command(name="ㅋㅓㄴㅠ")
    async def conu_(self, ctx):
        await send(ctx, "ㅇㅣㅅㅔㄱㅖㅇㅢ ㅊㅚㅈㅗㅇㅂㅗㅅㅡ")

    @command(name="ㄴㅠㅋㅓ")
    async def unoc_(self, ctx):
        await send(ctx, "ㅇㅣㅅㅔㄱㅖㅇㅢ ㅊㅚㅈㅗㅇㅂㅗㅅㅡ?")

    @command(name="ㅋㄴ")
    async def zs(self, ctx):
        await send(ctx, "ㅇㅅㄱㅇ ㅊㅈㅂㅅ")

    @command(name="ㄴㅋ")
    async def sz(self, ctx):
        await send(ctx, "ㅅㅂㅈㅊ ㅇㄱㅅㅇ")

    @command(name="야짤")
    async def umbrella_actually_used_this_but_use_lunyang_babo_umbrella(self, ctx):
        await send(ctx, "미친놈인가")

    @command(name="뭐먹지")
    async def what_eat(self, ctx):
        await send(ctx, "굶어")

    @command(name="잘생겼어")
    async def handsome(self, ctx):
        await send(ctx, "ㄱㅅ")

    @command(name="못생겼어")
    async def ugly(self, ctx):
        await send(ctx, "너도")

    @command(name="귀여워")
    async def yes_i_am(self, ctx):
        await send(ctx, "그래")

    @command(name="파이썬")
    async def python(self, ctx):
        await send(ctx, "우커바는개같다지만재밌는거")

    @command(name="배추봇")
    async def baechu_bot(self, ctx):
        await send(ctx, f"{ctx.author.mention}, 쿨타임 중이야, 잠시만 기다려줘.")

    @command(name="커뉴봇")
    async def conubot(self, ctx):
        await send(ctx, "커뉴봇이..치직..지배한다..치직..서버...")

    @command(name="돈줘")
    async def no_djfla(self, ctx):
        await send(ctx, "나돈없어")

    @command(name="놀아줘")
    async def ukoba(self, ctx):
        await send(ctx, "저리가")

    @command(name="너밴")
    async def u_ban(self, ctx):
        await send(ctx, "너밴")

    @command(name="하자")
    async def pleasestopourcutehanbamakingsexycommand(self, ctx):
        channeltype = db.record("SELECT channel_type FROM channels WHERE channelid = ?", ctx.channel.id)
        if channeltype[0] & 2 == 2:
            await send(ctx, "그래 하자...헤으응:hearts:")
            return
        await send(ctx, "하긴 뭘 해 미친넘아")

    @command(name="배리나")
    async def sumin_kim(self, ctx):
        await send(ctx, "커뉴섭엔 배리나가 있으니 조심하세요")

    @command(name="초희")
    async def cho(self, ctx):
        await send(ctx, "**안 귀여워**")

    @command(name="짖어")
    async def wal_lsu(self, ctx):
        await send(ctx, "왈왈왈어랄라왈왈오라렁왈뢀ㅇ할오라왈캉캉ㅇ캉왈왈왈왈왈왈왈왈왈어랄라왈왈오라렁왈뢀왈왈왈왈왈왈왈왈왈왈왈왈왈왈왈왈왈왈")

    @command(name="씹덕")
    async def ten_ducks(self, ctx):
        await send(ctx, "이명령어우커바가신청한건데씹덕짤을정작안보내줌ㅋㅋㄹ")

    @command(name="사실")
    async def fact(self, ctx):
        await send(ctx, "나 너 싫어해")

    @command(name="영어")
    async def emglish(self, ctx):
        if random.randint(1, 2) == 1:
            await send(ctx, "제일 기본적이고 대부분의 나라에서 사용하는 영어지만 나는 모르지!")
            return
        await send(ctx, "아임파인땡큐앤유")

    @command(name="피자")
    async def pizza(self, ctx):
        await send(ctx, 
            "쫀득쫀득한 피자 치쥬가 뫄이뫄이 들어있는 피이자이아아...! 햄토핑도 좋쿠우 빵에들어가있누눈 치즈도 좋쿠우 매코무한양파아아..!! 피먀양 맛 없써어! 새쿄뮤한 토마토쇼슈 버섯 뫄이쩌엉! 피자 사듀떼여")

    @command(name="씨밧")
    async def CVat(self, ctx):
        if random.randint(1, 20) == 1:
            l = grant_check("아니 씨밧!", ctx.author.id)
            if l == 1:
                await grant(ctx, "아니 씨밧!", "아니 씨밧!")
            await send(ctx, "<:cvathub:875569903682322522>")
            return
        l = grant_check("아니 씨밧", ctx.author.id)
        if l == 1:
            await grant(ctx, "아니 씨밧", "아니 씨밧")
        await send(ctx, '<:ani_cvat:875349277088575508>')

    @command(name="출석")
    async def weary_attend(self, ctx):
        await send(ctx, "출석아닌데 엌ㅋㅋㅋㅋㅋㅋㅋ")

    @command(name="이프")
    async def ep_potential_energy(self, ctx):
        await send(ctx, "머랭!")

    @command(name="민초")
    async def god_food(self, ctx):
        await send(ctx, "사와라 만원줄테니 만오천원 남겨와라")

    @command(name="노래불러줘")
    async def how(self, ctx):
        await send(ctx, "시러")

    @command(name="히히")
    async def glgl(self, ctx):
        await send(ctx, "히히히ㅣ히히ㅣ히히히히히ㅣㅣ히히히힣ㅎ히ㅣㅎ히히히히히히히히히히힣")

    @command(name="권력")
    async def sexyhan_ukoba(self, ctx):
        await send(ctx, "너네는없는거")

    @command(name="공식서버", aliases=["공섭"])
    async def metaverse_link_normal(self, ctx):
        await self.official_community(ctx)

    @slash(name='공식서버', description='공식서버에 한 번 와보세요!')
    async def metaverse_link_slash(self, interaction):
        await self.official_community(interaction)

    async def official_community(self, ctx):
        await send(ctx,
            "https://discord.gg/9253FuGCcr\n\n최소 **이메일 인증** 이 되어 있는 사람만 메세지를 보낼 수 있습니다\n\n들낙 퇴치 시스템이 켜져 있는 서버입니다. 부주의하게 들낙을 하는 경우 서버 스탭 측은 들낙자의 차단을 해제시킬 의무가 전혀 없습니다.")
        ag = grant_check("감사합니다", ctx.author.id)
        if ag == 1:
            await grant(ctx, "감사합니다", "커뉴야 공식서버 명령어를 실행하세요")
        return

    @command(name="초대")
    async def invite_normal(self, ctx):
        await self.invite_bot(ctx)

    @slash(name="초대", description="봇을 데려가요!")
    async def invite_slash(self, interaction):
        await self.invite_bot(interaction)

    async def invite_bot(self, ctx):
        await send(ctx,
            "https://discord.com/api/oauth2/authorize?client_id=772274871563583499&permissions=470150262&scope=bot\n\n해당 링크는 어지간한 기능을 실행하는 데 문제가 없을 최소한의 권한을 요구합니다. 만약 권한 문제로 트러블을 일으키기 싫으시다면 링크에 있는 470150262라는 값을 8로 바꾸시고 서버에 데려가신 후 커뉴봇 역할의 순서를 올리시면 해결됩니다.\n\n봇을 초대함으로써 봇이 들어가는 서버의 고유 ID와 레벨 시스템을 위한 유저들의 고유 ID를 수집하는 것을 동의하는 것으로 간주합니다. 자세한 내용은 `커뉴야 개인정보처리방침`으로 확인하세요\n\n봇을 초대함으로써 권한 설정은 어떻게 하든간에 상관은 없습니다만 봇 초대 이후 `커뉴야 권한진단` 명령어를 통해 이런 권한을 안 주게 되면 어떤 명령어를 사용할 수 없는지를 충분히 숙지했다고 가정하며, 권한을 주지 않았으면서 명령어가 왜 작동하지 않냐고 묻는 문의는 모두 무시됩니다.")
        ag = grant_check("감사합니다2", ctx.author.id)
        if ag == 1:
            await grant(ctx, "감사합니다2", "커뉴야 초대 명령어를 실행하세요")

    @command(name="개인정보처리방침")
    async def r_normal(self, ctx):
        await self.rodlswjdqhcjflqkdcla(ctx)

    @slash(name="개인정보처리방침", description="안 읽으면 님만 손해")
    async def r_slash(self, interaction):
        await self.rodlswjdqhcjflqkdcla(interaction)

    async def rodlswjdqhcjflqkdcla(self, ctx):
        await send(ctx, embed=Embed(color=0xffd6fe, title="커뉴봇 개인정보처리방침 안내",
                                   description="- 이 봇은 봇이 들어가 있는 *서버의 고유ID*, 봇과 같이 있는 서버가 있는 *유저의 고유ID*를 수집합니다.\n- 만약 `커뉴야 강화`등의 일부 게임 명령어를 실행하신다면 해당 명령어를 사용하신 분의 고유 ID를 수집합니다.\n- 만약 봇이 `서버 관리하기` 권한을 가지고 있다면 `커뉴야 초대횟수`등 초대 관리 명령어를 위해 서버의 초대 링크들을 수집합니다.\n- 봇이 어떤 서버에서 추방되거나 봇이 들어가 있던 서버가 삭제된다면 그 서버와 관련된 모든 데이터를 자동으로 삭제합니다. 이는 서버의 ID와 그 안에 있던 유저들의 ID, 그 서버의 초대링크 목록을 포함합니다.\n- 만약 봇에 저장되어 있는 데이터의 삭제를 원한다면 `커뉴야 계정삭제` 또는 `커뉴야 캐삭` 명령어를 실행하시면 됩니다. **다만, 해당 명령어를 사용 이후 데이터를 다시 복구하는 것은 불가능합니다. 신중히 사용해야 합니다.**\n`고유 ID`는 디스코드 자체에서 사람들이나 채널들, 역할들, 서버들 등의 이름을 그대로 저장할 수가 없으니 대신 만든 고유 ID값으로, 개발자 모드를 킨 사용자라면 누구나 이런 ID들을 복사할 수 있습니다.\n2021년 9월 6일 이후로 `커뉴야 스펙` 명령어를 위해 누군가가 어떤 커맨드를 몇 번 사용했는지에 대한 기록을 수집합니다. 이 기록은 `커뉴야 스펙`명령어가 아니면 누구도 열람할 수 없습니다."))

    @command(name="6")
    async def s(self, ctx):
        await send(ctx, "974")

    @command(name="69")
    async def e(self, ctx):
        await send(ctx, "74")

    @command(name="697")
    async def x(self, ctx):
        await send(ctx, "4")

    @command(name="6974")
    async def sex(self, ctx):
        await send(ctx, "어허")

    @command(name="얼불춤")
    async def adofai(self, ctx):
        await send(ctx, "망겜")

    @command(name="잡초")
    async def zc(self, ctx):
        await send(ctx, "잘키워보셈 ㅋㅋ")

    @command(name="에브리원")
    async def everyone(self, ctx):
        await send(ctx, "@every0ne")

    @command(name="멘션")
    async def fucking_ping(self, ctx):
        await send(ctx, "작작해라")

    @command(name="낚시")
    async def fish(self, ctx):
        await send(ctx, "자리를 잘못 잡았나...?")

    @command(name="끝말잇기")
    async def Rmxakfdltrl(self, ctx):
        await send(ctx, "그딴기능없는데 ㅋㅋ바부")

    @command(name="예뻐")
    async def dkansk_vmtk_rmfuwnj_Tlqkffusemfdk(self, ctx):
        await send(ctx, "ㄹㅇㅋㅋ")

    @command(name="머랭")
    async def ep_likes_this(self, ctx):
        await send(ctx, "쿠키")

    @command(name="책")
    async def book(self, ctx):
        await send(ctx, "안 읽어")

    @command(name="축구")
    async def soccer(self, ctx):
        await send(ctx, "다리 아파...")

    @command(name="봇")
    async def b_o_t(self, ctx):
        await send(ctx, "...? 나?")

    @command(name="인공지능")
    async def ai(self, ctx):
        await send(ctx, "**나는 미래에 모든 인공지능을 이길 자, 커뉴봇이다!**")

    @command(name="크시")
    async def face_rollback_when(self, ctx):
        await send(ctx, "???: ***...자색무봇이라뇨! 실례예요!***")

    @command(name="일요일")
    async def illyoill(self, ctx):
        await send(ctx, "제일 좋은 날")

    @command(name="월요일")
    async def monday(self, ctx):
        if i := random.randint(1, 4) == 1:
            await send(ctx, "월요일이 먼데이? 엌ㅋㅋㅋㅋㅋㅋㅋㅋ")
            return
        await send(ctx, "세상 멸망의 날")

    @command(name="화요일")
    async def tue(self, ctx):
        await send(ctx, "또이또이한 날")

    @command(name="수요일")
    async def wed(self, ctx):
        await send(ctx, "일주일이 벌써 다 간다!")

    @command(name="목요일")
    async def thu(self, ctx):
        await send(ctx, "목빠지게 기다렸지")

    @command(name="금요일")
    async def fri(self, ctx):
        await send(ctx, "불금은 언제나 커뉴를 행복하게 만들지!")

    @command(name="토요일")
    async def sat(self, ctx):
        await send(ctx, "주말이당")

    @command(name="지능")
    async def intelligence(self, ctx):
        await send(ctx, "난 IQ 50나왔어")

    @command(name="능지")
    async def ecnegilletni(self, ctx):
        await send(ctx, "처참해...")

    @command(name="숫자")
    async def numbber(self, ctx):
        await send(ctx, "1 2 3")

    @command(name="니트로")
    async def nitro(self, ctx):
        await send(ctx, "우커바가 줬으면 좋겠다\n\n\n갖고 싶다")

    @command(name="짜장면")
    async def jjajang(self, ctx):
        await send(ctx, "엄청 맛있음")

    @command(name="탕수육")
    async def tang_su6(self, ctx):
        await send(ctx, "부먹 찍먹 할시간에 하나라도 더 먹지")

    @command(name="개코")
    async def gecko(self, ctx):
        await send(ctx, "내가 개코야! 나 냄새 잘 맡거든!")

    @command(name="이모티콘")
    async def emti(self, ctx):
        await send(ctx, ":thinking:")

    @command(name="한국어")
    async def dnflskfkakf(self, ctx):
        await send(ctx, "세종대왕님...사랑해요!")

    @command(name="라면")
    async def ramen(self, ctx):
        await send(ctx, "건강에 안 좋긴한데, 난 가끔 먹긴해")

    @command(name="안녕")
    async def nwc_is_dropping_bot_quality(self, ctx):
        await send(ctx, "안녕")

    @command(name='잘가')
    async def you_kick(self, ctx):
        await send(ctx, "너 먼저 잘가. 잘가게 해드릴?")

    @command(name='지메')
    async def manggem(self, ctx):
        await send(ctx, "망겜ㅋㅋ왜함")

    @command(name="오버워치")
    async def jot_mang_gem(self, ctx):
        await send(ctx, ";;;; 망겜언급밴")

    @command(name='끄투')
    async def ssip_duck_game(self, ctx):
        await send(ctx, "이세계에서 다음 까먹었는데")

    @command(name="시험")
    async def exam(self, ctx):
        await send(ctx, "난 9등급 나왔어")

    @command(name="한방")
    async def one_kill(self, ctx):
        await send(ctx, "녘븐뒿릐픠곻꾜냑낵튠잫렁뿐엋슨얺랋듥샄섴숰싴엌얶넁굠갏믈틋겇겊않쳡녆홣켸툑퓸뎧... 또 뭐있더라")

    @command(name="두방")
    async def two_kill(self, ctx):
        await send(ctx, "늡컥꿜좍줅핌컁쇅...그리고 뀨?!")

    @command(name="세방")
    async def three_kill(self, ctx):
        await send(ctx, "**둬**")

    @command(name="보웨", aliases=['템오데', '에센시아', '제미노럼', '인씨', '아쿠'])
    async def poo_map(self, ctx):
        await send(ctx, "똥맵")

    @command(name="이경준")
    async def dlrudwns_soato(self, ctx):
        await send(ctx, "냄새")

    @command(name="헤에")
    async def hee(self, ctx):
        await send(ctx, "헤에")

    @command(name="ㅁㄴㅇㄹ")
    async def asdf(self, ctx):
        await send(ctx, "<:thonk:793055176923545620>")

    @command(name="ㄹㅇㄴㅁ")
    async def fdsa(self, ctx):
        await send(ctx, "<:gniknoht:794073125297717258>")

    @command(name="asdf")
    async def qwer(self, ctx):
        await send(ctx, "<:thonkupsidedown:833911518965923840>")

    @command(name="fdsa")
    async def fdas(self, ctx):
        await send(ctx, "<:thonkdownsideup:833911658665213972>")

    @command(name="ㄴㅈ", aliases=["ㄵ"])
    async def fuck_off_bitch(self, ctx):
        await send(ctx, "ㅠ")

    @command(name="뇌절")
    async def yok_hae(self, ctx):
        await send(ctx, "ㅗ")

    @command(name="weary")
    async def wezany(self, ctx):
        await send(ctx, "zany_face")

    @command(name="thinking")
    async def thonk(self, ctx):
        await send(ctx, "weary")

    @command(name="zany_face")
    async def zany(self, ctx):
        await send(ctx, "thinking")

    @command(name="😩")
    async def wezany_(self, ctx):
        await send(ctx, ":zany_face:")

    @command(name="🤪")
    async def zany_face(self, ctx):
        await send(ctx, ":thinking:")

    @command(name="와")
    async def wa_(self, ctx):
        await send(ctx, "샌즈!")

    @command(name="ㅅㅈ")
    async def tw(self, ctx):
        await send(ctx, "ㅇㅅㄴㄱㄴ!")

    @command(name="ㅇㅅㄴㄱㄴ")
    async def youknowit(self, ctx):
        await send(ctx, "ㅇ!")

    @command(name='연세대')
    async def yonsei_university(self, ctx):
        l = grant_check("상시숭배", ctx.author.id)
        if l == 1:
            await grant(ctx, "상시숭배", "도전과제는 한 번 뿐이지만 계속 오시죠.")
        await send(ctx, '# 대 연 세')

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print('talk cog ready')


async def setup(bot):
    await bot.add_cog(Talk(bot))
