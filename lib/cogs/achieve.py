import asyncio
from typing import Optional

from ..db import db
from ..utils.send import send
from discord import Embed
from discord.app_commands import command as slash, choices, Choice
from discord.ext.commands import Cog, command


def to_visual_ach_list_desc(achievement_got, achievement_descriptions, better_list):
    bool_to_emoji = ['❌', '✅']
    int_to_emoji = ['❌', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣']
    if not better_list:
        desc = '\n'.join([f'{a}: {achievement_descriptions[a]}' for a in achievement_descriptions])
    else:
        desc = []
        for a in achievement_descriptions:
            if ', ' in a:
                r = len(list(filter(lambda x: x in achievement_got, a.split(", "))))
                if r == len(a.split(", ")):
                    desc.append(f'✅ {a}: {achievement_descriptions[a]}')
                else:
                    desc.append(f'{int_to_emoji[r]} {a}: {achievement_descriptions[a]}')
            else:
                desc.append(f'{bool_to_emoji[a in achievement_got]} {a}: {achievement_descriptions[a]}')
        desc = '\n'.join(desc)
    return desc


class Achieve(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="도전과제")
    async def ach_list_normal(self, ctx, activity: Optional[str], seat: Optional[int], *, name: Optional[str]):
        await self.achievement_list(ctx, activity, seat, name=name)

    @slash(name="도전과제", description="도전과제에 관한 각종 명령어 세트 (원본: `커뉴야 도전과제`)")
    @choices(
        무엇=[Choice(name='내가달성한거', value=''), Choice(name='페이지순', value='페이지순'), Choice(name='리더보드', value='리더보드'),    Choice(name='목록', value='목록'), Choice(name='설명', value='설명'), Choice(name='미션', value='미션'),    Choice(name='미션', value='미션'), Choice(name='장착', value='장착')])
    async def ach_list_slash(self, interaction, 무엇: Optional[str], 장착자리: Optional[int], *, 도전과제이름: Optional[str]):
        await self.achievement_list(interaction, 무엇, 장착자리, 도전과제이름)

    async def achievement_list(self, ctx, activity, seat, name):
        if not activity:
            my_ach = db.records("SELECT name FROM achievement_progress WHERE UserID = ? and ach_type = 0",
                                ctx.author.id)
            tjfaud = ''
            for a in my_ach:
                tjfaud += f",{a[0]}"
            embed = Embed(color=0xffd6fe, title=f"{str(ctx.author)} 님이 달성한 도전 과제")
            if not tjfaud:
                embed.add_field(name="도전 과제 개수: 0개", value="달성한 도전 과제들\n없음!")
            else:
                l = len(my_ach)
                embed.add_field(name=f"도전 과제 개수: {l}개", value=f"달성한 도전 과제들\n{tjfaud[1:]}")
            await send(ctx, embed=embed)
        elif activity in ["랭킹", "리더보드"]:
            score_info = db.records(
                "SELECT * FROM (SELECT UserID, count(name) as n FROM achievement_progress GROUP BY UserID) ORDER BY n DESC LIMIT 10")
            tjfaud = ""
            ids = []
            scores = []
            for score in score_info:
                ids.append(score[0])
                scores.append(score[1])
            for uid in ids:
                a = ids.index(uid)
                b = scores[a]
                c = scores.index(b) + 1
                tjfaud += f"\n{c}. {self.bot.get_user(uid)} (달성한 도전 과제 {b}개)"
            embed = Embed(color=0xffd6fe, title=f"전체 도전과제 랭킹", description=tjfaud)
            await send(ctx, embed=embed)
        elif activity == "장착":
            if not seat or (seat and seat not in [1, 2, 3, 4, 5]):
                await send(ctx, "올바르지 않은 자리에요!")
                return
            cur = db.record("SELECT name FROm achievement_progress WHERE UseriD = ?", ctx.author.id)[0]
            if cur:
                if seat == 1:
                    db.execute("UPDATE games SET p1 = ? WHERE UserID = ? ", name, ctx.author.id)
                elif seat == 2:
                    db.execute("UPDATE games SET p2 = ? WHERE UserID = ? ", name, ctx.author.id)
                elif seat == 3:
                    db.execute("UPDATE games SET p3 = ? WHERE UserID = ? ", name, ctx.author.id)
                elif seat == 4:
                    db.execute("UPDATE games SET p4 = ? WHERE UserID = ? ", name, ctx.author.id)
                else:
                    db.execute("UPDATE games SET p5 = ? WHERE UserID = ? ", name, ctx.author.id)

                embed = Embed(color=0xffd6fe, title="대표 업적 설정 완료",
                              description=f"{seat}번 자리에 {name} 도전과제를 대표 업적으로 설정했습니다")
                await send(ctx, embed=embed)
                db.commit()
            else:
                await send(ctx, '달성하지 못한 도전과제에요!')
                return
        elif activity == "목록":
            embed = Embed(color=0xffd6fe, title="획득 가능한 도전과제 목록")
            if not seat:
                embed.add_field(name="도전과제 목차",
                                value="1. 기본 도전 과제\n2. 커뉴봇 명령어 관련 도전 과제\n3. 커뉴봇 스펙 관련 도전 과제\n4. 공식서버 관련 도전 과제\n5. 프리미엄 도전 과제\n6. 이스터 에그 도전 과제\n7. 미션형 도전 과제\n8. 기간 한정 도전 과제\n9. 명예 도전 과제")
                embed.set_footer(text="`커뉴야 도전과제 목록 <1~9>`로 도전과제 목록을 확인하세요")
                await send(ctx, embed=embed)
                return
            better_list = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0] & 512 == 512
            achievement_got = set()
            if better_list:
                achs = db.records("SELECT name FROM achievement_progress WHERE UserID = ?", ctx.author.id)
                for ach in achs:
                    achievement_got.add(ach[0])
            if seat == 1:
                achievement_descriptions = {
                    '커뉴봇 사용자': '커뉴봇을 사용하세요',
                    '출첵': '출석체크를 진행하세요',
                    '감사합니다': '커뉴야 공식서버 명령어를 실행하세요',
                    '감사합니다2': '커뉴야 초대 명령어를 실행하세요',
                    '공식서버 입문자': '공식서버에서 1레벨을 달성하세요',
                    '프로필 꾸미기': '소개작성 명령어로 프로필에 소개글을 작성하세요',
                    '스펙 확인': '`커뉴야 스펙` 명령어로 자신의 스펙을 확인하세요'
                }
                desc = to_visual_ach_list_desc(achievement_got, achievement_descriptions, better_list)
                embed.add_field(name="기본 도전 과제", value=desc)
            elif seat == 2:
                achievement_descriptions = {
                    '강화의 시작, 평범한 강화, 고급스러운 강화, 숙련된 강화, 낮은 확률을 뚫는, 사실상 만렙, 만렙을 초월한': '강화 명령어로 레벨 100~600, 650을 달성하세요',
                    '능지떡상, 능지개떡상': '퀴즈 명령어로 4만점, 10만점을 달성하세요',
                    '능지 1등급': '퀴즈 명령어로 정답률이 0% 는 아니지만 4% 이하인 문제를 맞히세요',
                    '묵찌빠 승자': '커뉴봇과 묵찌빠를 해 이기세요',
                    '엄청난 운빨': '운빨테스트 명령어에서 0.1% 확률에 당첨되세요',
                    '최강의 운빨': '운빨테스트 명령어에서 0.01% 확률에 당첨되세요',
                    '도박의 신': '코인 룰렛에서 단 하나의 수에 걸어 룰렛을 이기세요',
                    '쿨탐 버근가': '명령어 쿨타임이 0.00초 남았다는 메세지를 보세요',
                    '코인 투자자, 코인 부자, 코인 대부호': '코인에서 현금 1억, 10억, 1조 코인을 가지세요',
                    '몰빵 가즈아': '전재산이 1억이 넘었고 현금 이외의 코인을 가지지 않은 상태에서 전재산에 75% 이상을 룰렛에 거세요',
                    '블랙잭!': '`커뉴야 코인 블랙잭`에서 블랙잭 21 카드패를 가지세요',
                    '능지 9등급': '퀴즈 명령어로 정답률이 100%는 아니지만 96% 이상인 문제를 틀리세요',
                    '맛있는 팝콘': '`커뉴야 오목 관전`으로 이루어지고 있는 오목 대국을 관전하세요',
                    '황금의 묵찌빠': '묵찌빠 점수 4500점을 달성하세요',
                    '번개같은 출석': '출석체크에서 1등하세요',
                    '2등도 잘한거야': '출석체크 2등을 하세요',
                    '단골 출첵러, 프로 출첵러': '10연속, 50연속으로 출석체크를 하세요',
                    '퀴즈 출제자, 프로 퀴즈 출제자': '퀴즈 명령어로 문제 20개, 100개 이상을 내고 `커뉴야 퀴즈 내문제`를 실행하세요',
                    '커뉴핑크 사용자, 커뉴핑크 초보 탈출, 커뉴핑크 중수': '커뉴핑크 명령어에서 2, 10, 16레벨을 달성하세요'
                }
                desc = to_visual_ach_list_desc(achievement_got, achievement_descriptions, better_list)
                embed.add_field(name="커뉴봇 명령어 관련 도전 과제", value=desc)
            elif seat == 3:
                achievement_descriptions = {
                    '단골 사용자 1, 단골 사용자 2, 단골 사용자 3': '커뉴봇 명령어를 1000번, 10000번, 100000번 이상 사용하세요',
                    '명령어 마스터, 명령어의 전설, 명령어의 신': f'서로 다른 명령어 50종류, 100종류, {len(self.bot.commands)}종류(모두)를 사용하세요',
                    '광기, 진짜 광기': '서로 다른 5종류, 10종류의 명령어를 500번 이상씩 사용하세요',
                    '압도적 지분가': '한 명령어에서 사용횟수가 200회 이상이면서 75% 이상의 지분을 보유하세요'
                }
                desc = to_visual_ach_list_desc(achievement_got, achievement_descriptions, better_list)
                embed.add_field(name="커뉴봇 스펙 관련 도전 과제", value=desc)
                embed.set_footer(text="이 도전과제들은 커맨드 사용횟수 정보를 수집하기 시작한 2021년 9월 6일부터 사용된 커맨드만 적용됩니다\n또한 이 도전과제들은 달성조건이 "
                                      "충족된다고 바로 달성되지 않고 `커뉴야 스펙`명령어를 실행했을 때 도전과제 달성 조건에 맞는지 확인합니다.")
            elif seat == 4:
                achievement_descriptions = {
                    '공식서버 입문자, 공식서버 활동자, 공식서버 고렙, 공식서버 고인물, 공식서버 초고렙, 공식서버 정복자': '공식서버에서 1, 5, 16, 30, 62, 100레벨에 달성하세요 (이 중 공식서버 입문자는 1페이지 도전과제로 취급됩니다)',
                    '나무를 키우는 자, 내일지구가멸망해도나무를키우겠다, 드루이드': '잡초키우기에서 300, 1000, 10000레벨을 달성하세요',
                    '우주 저 너머로, 우주 저 끝까지': '우주탐험에서 10000, 100000레벨을 달성하세요',
                    '우주 구석구석 탐험해주겠다': '우주탐험 도중 채널을 잠금해제 하세요',
                    '잡소리 독자': '커뉴의 잡소리 모음에서 최근에 올라온 잡소리에 반응을 다세요',
                    '1만배수 사냥꾼': '<#743339107731767366>금성-숫자렙업노가다 에서 10000의 배수를 가져가세요',
                    '뿌잉뿌잉>_<': '커뉴는 기여워...!',
                    '공식서버 만수르': '공식서버 돈 1000000을 가지세요',
                    '인플루언서': '봇 개발에 큰 영향을 미치세요 (공식서버의 칭호와 동일, 수동으로 부여되는 도전과제)',
                    '눈치게임 고수, 눈치게임 개고수': '<#1000636815239299082>의 고정메세지에 있는 특정한 미션을 완료하세요'
                }
                desc = to_visual_ach_list_desc(achievement_got, achievement_descriptions, better_list)
                embed.add_field(name="공식서버 관련 도전 과제", value=desc)
            elif seat == 5:
                achievement_descriptions = {
                    '정말 감사합니다': '뀨를 구매하세요 (수동으로 부여되는 도전과제',
                    '알파 센타우리': '알파 센타우리를 구매하세요'
                }
                desc = to_visual_ach_list_desc(achievement_got, achievement_descriptions, better_list)
                embed.add_field(name="프리미엄 도전 과제", value=desc)
                embed.set_footer(text="이외의 도전과제들이 존재하지만, `알파 센타우리`를 구매한 뒤 `ㅋㅇ도전과제`로 확인해주세요")
            elif seat == 6:
                achievement_list = ['가위바위보에서 무슨 짓을...', '제발 이루어졌으면', '굉장한 찍신', '잠수의 제왕', '그런 페이지는 존재하지 않습니다', 'ㄹㅇㅋㅋ', '21134**999999**',
                 '로또 안사고 뭐해요', '이걸 왜사요', '수포자', '미래를 보는 자', '아니 씨밧', '아니 씨밧!', '삶과 우주 그리고 모든 것에 대한 궁극적 질문의 해답',
                 '2 * 3²', '안 사줄 수가 없어!', '개같은 출석', '서두르면 일을 그르친다', '여긴 지역 아닌데?', '돈으로 살 수 없는 것 그렇기에 더 소중한 것', 'ㅇㅇㅌㅌ',
                 '이일일삼ㅅ...갸아앍 너무빨라', '에러 안 났잖아', '시차 적응 좀 해요', '피겅', '으으ㅐ', '차담 마려벤요?', '뭔 오태민 하면 나오냐', '핑이나 막아라!',
                 '있지만 없는 것', ':flag_za:', '설명좀', '업뎃을 기대하시는 거에요?', '설명대로', '얼마나 심심하셨길래...', '3웨', 'ㅎ😩ㅎ', '상시숭배', '다시 하는 1주년 이벤트', '과거를 보는 자']
                bool_to_emoji = ['❌', '✅']
                if not better_list:
                    desc = ', '.join([a for a in achievement_list])
                else:
                    desc = '\n'.join([f'{bool_to_emoji[a in achievement_got]} {a}' for a in achievement_list])
                embed.add_field(name="이스터 에그 도전 과제", value=desc)
                flag_za_check = db.record("SELECT count(*) FROM achievement_progress WHERE UserID = ? AND (name = '아니 씨밧' OR name = '아니 씨밧!' OR name = 'ㅇㅇㅌㅌ' OR name = '피겅' OR name = '으으ㅐ' OR name = '차담 마려벤요?' OR name = '뭔 오태민 하면 나오냐' OR name = '핑이나 막아라!' OR name = '3웨' OR name = 'ㅎ😩ㅎ')", ctx.author.id)[0]
                if flag_za_check >= 5:
                    embed.set_footer(text="이 도전과제들의 경우 획득조건을 알려주지 않습니다. 이름이나 `커뉴야 도전과제 설명`을 보고 추론해서 도전 과제를 달성해 보세요!",
                                     icon_url="https://cdn.discordapp.com/emojis/1205125640580239450.webp?size=96&quality=lossless")
                    l = grant_check(":flag_za:", ctx.author.id)
                    if l == 1:
                        await grant(ctx, ":flag_za:", "서준의 오타 도전과제를 충분히 달성한 후 이스터에그 도전과제의 :zany_face:가 :flag_za:로 바뀌게 하세요")
                else:
                    embed.set_footer(text="이 도전과제들의 경우 획득조건을 알려주지 않습니다. 이름이나 `커뉴야 도전과제 설명`을 보고 추론해서 도전 과제를 달성해 보세요!",
                                    icon_url="https://cdn.discordapp.com/emojis/594239588399317079.png?v=1")
                await send(ctx, embed=embed)
                return
            elif seat == 7:
                achievement_descriptions = {
                    '진정한 레벨업': '공식서버에서 경험치를 보상으로 받을 수 있는 명령어를 사용하지 않으면서 경험치 3000을 벌어들이세요',
                    '숫자를 많이 세다': '공식서버에서 이 이름을 가진 칭호를 획득한 뒤 그 달성 조건을 한 번 더 만족시키세요'
                }
                desc = to_visual_ach_list_desc(achievement_got, achievement_descriptions, better_list)
                embed.add_field(name="미션형 도전 과제", value=desc)
                embed.set_footer(text='이 도전과제의 경우 커뉴야 도전과제 미션 이라는 명령어를 통해 따로 미션을 시작하고, 그 상태로 조건을 만족해야만 도전과제를 달성할 수 있습니다.')
            elif seat == 8:
                achievement_descriptions = {
                    '1st anniversary': '공식서버의 1주년 이벤트에 참여하세요 (2021.07.27 ~ 2021.08.12)',
                    '1st anniversary VIP': '공식서버의 1주년 이벤트에서 가장 많은 점수를 가져간 5명 안에 들어가세요 (2021.08.12)',
                    '생일축하해': '커뉴봇 생일축하 이벤트에 참여하세요',
                    '알파 센타우리 초기접근자': '2021 연말 업데이트 이전 알파 센타우리를 구매하세요',
                    '새해 복 많이 받으세요': '연말연시 이벤트에서 미션 5단계를 클리어하세요 (수동 지급)',
                    '역사적인 선택': '이거 해서 뭐해요...',
                    '2nd anniversary': '공식서버의 2주년 이벤트에 참여하세요',
                    '커뉴핑크 초기 개척자': '커뉴핑크의 초기 버전에서 22레벨을 달성하세요'
                }
                desc = to_visual_ach_list_desc(achievement_got, achievement_descriptions, better_list)
                embed.add_field(name="기간 한정 도전 과제", value=desc)
            elif seat == 9:
                achievement_descriptions = {
                    '절대신': '도전과제 목록 기준 1,2,3,4,6페이지에 있는 모든 도전 과제를 달성하세요',
                    '진정한 절대신': '이 도전 과제를 제외한 다른 모든 도전 과제를 달성하세요 (만약 새로운 도전 과제가 나온다면 그 도전 과제를 달성하기 전까지 이 도전 과제 달성은 취소됩니다)',
                    '최고의 인플루언서': '봇 개발에 매우 큰 영향을 미치세요. 방법은 저도 모릅니다.'
                }
                desc = to_visual_ach_list_desc(achievement_got, achievement_descriptions, better_list)
                embed.add_field(name="명예 도전 과제", value=desc)
            elif seat == 10:
                achievement_descriptions = {
                    '알파 센타우리 접근자': '게임을 시작하세요...',
                    '연구 입문자': '2000 아니 씨밧을 모아 연구를 시작하세요',
                    '진정한 시작': '오타 연구소에서 피곦을 연구하세요',
                    '피카츄?': '처음으로 전력 1000000만큼을 생산하세요',
                    '프록시마b': '프록시마b에 도착하세요',
                    '활발한 거래자': '알데바락 우주센터와 100회 이상 성공적으로 거래하세요',
                    '뭉탱태로 있다가 유링겟ㅍㅇ 아니그냥': '쿼크 뭉탱태 유링겟ㅍㅇ 추출기를 구매하세요'
                }
                desc = to_visual_ach_list_desc(achievement_got, achievement_descriptions, better_list)
                embed.add_field(name="알파 센타우리의 인게임 도전 과제 (여긴 어쩐 일로 찾아오셨나요?)", value=desc)
            elif seat == 69:
                l = grant_check("그런 페이지는 존재하지 않습니다", ctx.author.id)
                if l == 1:
                    await grant(ctx, "그런 페이지는 존재하지 않습니다", "도전과제 목록에서 페이지 인수를 69로 설정하세요")
            embed.set_footer(text="일부 도전과제의 경우 달성조건을 알려주지 않을 수 있습니다")
            await send(ctx, embed=embed)
        elif activity == "설명":
            try:
                des = db.record("SELECT description FROM achievements WHERE name = ?", name)[0]
            except TypeError:
                await send(ctx, "그런 도전과제는 존재하지 않아요!")
                return
            setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
            if setting & 64:
                users = db.record("SELECT count(distinct UserID) FROM achievement_progress")[0]
                cleared = db.record("SELECT count(*) FROM achievement_progress WHERE name = ?", name)[0]
                des += f"\n달성률 {round(cleared / users * 100, 3)}%"
            embed = Embed(color=0xffd6fe, title=f"도전 과제 설명: {name}", description=des)
            l = grant_check(name, ctx.author.id)
            if l == 1:
                embed.set_footer(text='아직 달성하지 못한 도전과제에요!')
            else:
                embed.set_footer(text='달성한 도전과제에요!')
            await send(ctx, embed=embed)
            if name == '설명좀':
                l = grant_check("설명좀", ctx.author.id)
                if l == 1:
                    await grant(ctx, "설명좀", "그런 도전과제는 존재하지 않아요!")
        elif activity == "페이지순":
            setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
            if setting & 32 == 0:
                await send(ctx, "해금하지 못한 기능이에요! `커뉴야 뀨 구매 도전과제 페이지순 정렬`으로 먼저 이 기능을 해금하세요")
                return
            sort = [[], [], [], [], [], [], [], [], [], [], []]
            my_ach = db.records("SELECT name FROM achievement_progress WHERE UserID = ?", ctx.author.id)
            for ach in my_ach:
                sort[db.record("SELECT page FROM achievements WHERE name = ?", ach[0])[0]].append(ach[0])
            pages = [[], [], [], [], [], [], [], [], [], [], []]
            tjfaud_temp = ''
            for s in sort:
                for t in s:
                    if not s.index(t):
                        tjfaud_temp += t
                    else:
                        tjfaud_temp += ("," + t)
                if s:
                    pages[sort.index(s)] = tjfaud_temp
                tjfaud_temp = ''
            embed = Embed(color=0xffd6fe, title=f"{str(ctx.author)} 님이 달성한 도전 과제: {len(my_ach)}개")
            for i in range(len(pages)):
                if pages[i]:
                    embed.add_field(name=f"{i}페이지", value=pages[i], inline=False)
            await send(ctx, embed=embed)
        elif activity == '미션':
            current_mission = db.record("SELECT mission_achievement, mission_temp FROM games WHERE UserID = ?",
                                        ctx.author.id)
            if current_mission[0] == '진정한 레벨업':
                await send(ctx, '도전과제 달성 여부를 불러오는 중이에요...')
                await asyncio.sleep(1)
                xp_now = \
                db.record("SELECT XP FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", ctx.author.id)[0]
                dx = db.record("SELECT uses FROM cmd_uses WHERE UserID = ? AND command = '우주탐험'", ctx.author.id)[0]
                wz = db.record("SELECT uses FROM cmd_uses WHERE UserID = ? AND command = '잡초키우기'", ctx.author.id)[0]
                check = current_mission[1].split(",")
                if int(check[1]) != dx or int(check[2]) != wz:
                    await send(ctx, '진정한 레벨업 도전과제 달성을 실패했어요! 다시 시도하려면 `커뉴야 도전과제 미션 진정한 레벨업`을 입력해주세요.')
                    db.execute("UPDATE games SET mission_achievement = NULL, mission_temp = NULL WHERE UserID = ?",
                               ctx.author.id)
                    db.commit()
                    return
                xp_gained = xp_now - int(check[0])
                if xp_gained >= 3000:
                    await grant(ctx, "진정한 레벨업",
                                "공식서버에서 `커뉴야 잡초키우기` 및 `커뉴야 우주탐험`명령어를 사용하지 않은 채로 경험치 3000을 얻으세요 (미션형 도전과제)")
                    db.execute("UPDATE games SET mission_achievement = NULL, mission_temp = NULL WHERE UserID = ?",
                               ctx.author.id)
                    db.commit()
                    return
                await send(ctx, f'미션이 진행 중이에요! 3000 exp를 벌어야 하고 현재는 그중 {xp_gained}만큼 번 상태에요.')
                return
            if not name:
                await send(ctx, '`커뉴야 도전과제 미션 (도전과제명)`')
                return
            mission_check = db.record("SELECT name FROM achievements WHERE name = ? AND page = 7", name)
            if not mission_check:
                await send(ctx, "그런 도전과제는 존재하지 않아요!")
                return
            await send(ctx, "정말로 해당 미션을 시작할 건가요? `시작`이라고 입력해 시작하세요")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
            except asyncio.TimeoutError:
                await send(ctx, "미션형 도전과제를 시작하지 않기로 했어요.")
                return
            if msg.content != '시작':
                await send(ctx, "미션형 도전과제를 시작하지 않기로 했어요.")
                return
            if name == '진정한 레벨업':
                l = grant_check("진정한 레벨업", ctx.author.id)
                if l == 0:
                    await send(ctx, "이미 달성한 도전과제에요!")
                    return
                await send(ctx, 
                    "**진정한 레벨업**도전과제를 시작했어요! 우주탐험과 잡초키우기는 잠깐 당신의 손에서 벗어나 있으라고 하세요...\n\n도전과제를 완료했다고 생각하시면 `커뉴야 도전과제 미션`을 꼭 다시 입력하셔야 돼요!")
                xp_now = \
                db.record("SELECT XP FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", ctx.author.id)[0]
                dx = db.record("SELECT uses FROM cmd_uses WHERE UserID = ? AND command = '우주탐험'", ctx.author.id)[0]
                wz = db.record("SELECT uses FROM cmd_uses WHERE UserID = ? AND command = '잡초키우기'", ctx.author.id)[0]
                db.execute("UPDATE games SET mission_achievement = ?, mission_temp = ? WHERE UserID = ?", name,
                           f"{xp_now},{dx},{wz}", ctx.author.id)
                db.commit()
            elif name == '숫자를 많이 세다':
                l = grant_check("숫자를 많이 세다", ctx.author.id)
                if l == 0:
                    await send(ctx, "이미 달성한 도전과제에요!")
                    return
                await send(ctx, "**숫자를 많이 세다**도전과제를 시작했어요! 제발 끊기지 않도록 기도하세요.\n\n이 도전 과제를 달성하면 커뉴봇이 개인 메세지를 보낼 거에요!")
                current_number = db.record("SELECT num FROM channels WHERE ChannelID = 743339107731767366")[0]
                current_number += 5
                db.execute("UPDATE games SET mission_achievement = ?, mission_temp = ? WHERE UserID = ?", name,
                           current_number, ctx.author.id)
                db.commit()

    @command(name="프로필")
    async def profile_normal(self, ctx):
        await self.represent(ctx)

    @slash(name="프로필", description="자신의 프로필을 보여줘요.")
    async def profile_slash(self, interaction):
        await self.represent(interaction)

    async def represent(self, ctx):
        chs = db.record("SELECT p1, p2, p3, p4, p5 FROM games WHERE UserID = ?", ctx.author.id)
        s = db.record("SELECT sogae FROM games WHERE UserID = ?", ctx.author.id)
        l1 = []
        for ch in chs:
            if ch:
                l1.append(ch)
        if not s:
            tjfaud = "\n대표 업적:"
        else:
            tjfaud = f"`{s[0]}`\n대표 업적:"
        for ele_ in l1:
            tjfaud += f"\n{ele_}"
        embed = Embed(color=0xffd6fe)
        embed.add_field(name=f"{ctx.author.display_name}님의 프로필", value=tjfaud)
        await send(ctx, embed=embed)

    @command(name="소개작성")
    async def sogae_normal(self, ctx, *, sogae: str):
        await self.represent(ctx, sogae)

    @slash(name="소개작성", description="프로필에 표시할 소개를 작성해요.")
    async def sogae_slash(self, interaction, *, 소개: str):
        await self.represent(interaction, 소개)

    async def write_sogae(self, ctx, sogae: str):
        if len(sogae) > 100:
            await send(ctx, "소개글이 너무 길어요!")
            return
        await send(ctx, f"{sogae}로 소개글을 바꿀려고 해요. 이렇게 바꿀려는 게 맞나요?\n`변경`이라고 입력해 소개글을 변경하세요")
        try:
            msg = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
            )
        except asyncio.TimeoutError:
            await send(ctx, "소개글 변경을 취소했어요.")
            return
        if msg.content == "변경":
            await send(ctx, "소개글 변경을 완료했어요! `커뉴야 프로필`명령어로 확인해 보세요")
            l = grant_check("프로필 꾸미기", ctx.author.id)
            if l == 1:
                await grant(ctx, "프로필 꾸미기", "소개작성 명령어로 소개글을 작성하기")
            db.execute("UPDATE games SET sogae = ? WHERE UserID = ?", sogae, ctx.author.id)
            db.commit()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print('achieve cog ready')


async def setup(bot):
    await bot.add_cog(Achieve(bot))


def grant_check(achievement, userid):
    if db.record("SELECT name FROM achievement_progress WHERE UserID = ? AND name = ?", userid, achievement):
        return 0
    return 1


async def grant(ctx, achievement, desc, ach_type=0):
    embed = Embed(color=0xffd6fe, title="도전 과제를 달성함!")
    embed.add_field(name=achievement, value=f"{desc}\n`커뉴야 도전과제`명령어로 확인해 보세요")
    db.execute("INSERT INTO achievement_progress (UserId, name, ach_type) VALUES (?, ?, ?)", ctx.author.id, achievement,
               ach_type)
    db.commit()
    await ctx.channel.send(ctx.author.mention, embed=embed)
    return
