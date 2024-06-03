import asyncio
from typing import Optional

from discord import Member, Embed, errors
from discord.ext.commands import Cog, Greedy, command

from .achieve import grant_check, grant
from ..db import db


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="업데이트", aliases=["업뎃"])
    async def update(self, ctx, extra1: Optional[str], extra2: Optional[str]):
        # update_show_type = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0] & 4096 == 4096
        # if extra1 == '설정':
        #     if not extra2:
        #         visual_ust = ['방식별', '기능별'][update_show_type]
        #         await ctx.send(f"현재는 `커뉴야 업데이트`를 실행하면 {visual_ust}로 표시해요! 단, 24_seol 업데이트 또는 그 이후의 업데이트에만 적용돼요.\n\n`커뉴야 업데이트 설정 (방식별/기능별)`로 업데이트를 어떻게 표시할지 바꾸세요")
        #         return
        #     elif extra2 == '방식별':
        #         if update_show_type == 1:
        #             await ctx.send('성공적으로 변경했어요!')
        #             db.execute("UPDATE games SET user_setting = user_setting - 4096 WHERE UserID = ?", ctx.author.id)
        #         else:
        #             await ctx.send("이미 방식별로 표시하고 있어요!")
        #             return
        #     elif extra2 == '기능별':
        #         if update_show_type == 0:
        #             await ctx.send('성공적으로 변경했어요!')
        #             db.execute("UPDATE games SET user_setting = user_setting + 4096 WHERE UserID = ?", ctx.author.id)
        #         else:
        #             await ctx.send("이미 기능별로 표시하고 있어요!")
        #             return
        #     else:
        #         await ctx.send("`커뉴야 업데이트 설정 (방식별/기능별)`")
        #         return
        if not extra1:
            embed = Embed(color=0xffd6fe, title="커뉴봇 yonsei4 업데이트 (날짜: 2024년 6월 4일)")
            embed.add_field(name='이번 업데이트의 방향성',
                            value="은 모르겠고 신기능 아이디어 받는다니까요. 없으면 저야 편한거죠. \N{THUMBS UP SIGN}",
                            inline=False)
            embed.add_field(name="1. 새로운 기능",
                            value="커뉴봇은 더 이상 비슷한 사람들의 집합이 만든 여러 개의 개인용 서버에 들어가 있으려고 하지 않음 (명령어 아님, 개인용 서버 판별 알고리즘이 실험 중에 있지만 정확성이 매우 높다고 판정됨)",
                            inline=False)
            embed.add_field(name="2. 개선된 기능",
                            value="화력코인의 가격 변동 알고리즘을 변경, 보유 화력코인 등의 데이터를 전으로 롤백\ndatetime.utcnow()를 쓰는 모든 명령어에서 사용하는 함수를 datetime.now()로 변경 (눈에 띄는 변경사항은 아마도 없지만 이후 버전에서 봇이 더 안정적이게 됩니다.)\n`커뉴야 계산`명령어가 제대로 작동하기 시작, 몇 가지 함수를 지원",
                            inline=False)
            embed.add_field(name="3. 수정된 버그",
                            value="더 이상 화력코인의 가격이 음수가 되지 않음",
                            inline=False)
            embed.add_field(name="4. 삭제된 기능",
                            value="더미데이터로만 남아있던 몇몇 명령어들을 삭제",
                            inline=False)
            embed.set_footer(
                text="커뉴야 심심해 명령어로 나오는 TMI 개수: 220개 -> 220개\n도전과제 개수: 123개 -> 123개 ()\n이전 업데이트 yonsei3\n다음 업데이트 미출시")
            await ctx.send(embed=embed)
        elif extra1 == '코인':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 코인")
            embed.add_field(name='yonsei4', value='화력코인의 가격 변동 알고리즘을 변경, 보유 화력코인 등의 데이터를 전으로 롤백\n더 이상 화력코인의 가격이 음수가 되지 않음')
            embed.add_field(name='yonsei3', value='코인 가격이 0까지 떨어질 확률을 낮춤\n코인의 가격이 이따금씩 제대로 새로고침되지 않던 버그 수정')
            embed.add_field(name='yonsei1', value='새로운 기능\n\n`커뉴야 코인 그래프` 실험 단계 출시\n\n개선된 기능\n\n화력코인의 변동성을 소폭 감소시킴\n큰 수가 나오는 대부분의 기능에서 수를 쉼표로 구분\n룰렛: 가능한 수의 범위가 1~36임을 더 잘 보이는 곳에 명시, 홀수 또는 짝수에 거는 경우 줄임말을 인식\n블랙잭: 가능한 행동들의 설명을 튜토리얼에만 표시, 판이 끝난 이후 남은 코인을 표시, 판돈의 2배보다 보유 현금이 적을 경우 더블 다운을 할 수 없음\n\n수정된 버그\n\n알맞은 양의 코인을 가지고 있었음에도 판매되지 않던 버그 수정\n화력코인 변화량이 이상하게 표기되던 버그 수정\n지원금: 특정한 경우 지원금이 100000.0처럼 소수점으로 표기되던 버그 수정\n블랙잭: 더블 다운을 해도 카드를 더 뽑을 수 있던 버그 수정, 돈을 잃은 후 남은 돈이 0 이하이면 에러가 나면서 돈 변화가 반영되지 않던 버그 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '계산':
            embed = Embed(color=0xffd6fe, title='커뉴봇 기능 업데이트 내역: 계산')
            embed.add_field(name='yonsei4', value='몇 가지 연산들을 지원하도록, 사용할 수 있는 수준으로 명령어 출시')
            embed.add_field(name='yonsei1', value='매우 실험적인 버전으로 명령어 출시')
        elif extra1 == 'yonsei3':
            embed = Embed(color=0xffd6fe, title="커뉴봇 yonsei3 업데이트 (날짜: 2024년 5월 13일)")
            embed.add_field(name='이번 업데이트의 방향성',
                            value="은 모르겠고 신기능 아이디어 받습니다.",
                            inline=False)
            embed.add_field(name="1. 새로운 기능",
                            value="뀨 상점에 `출석체크 준비 알림` 추가",
                            inline=False)
            embed.add_field(name="2. 개선된 기능",
                            value="`커뉴야 코인`에서 코인 가격이 0으로 떨어질 확률을 낮춤 (가격이 0에 가까울 때 오를 확률이 증가한 건 아닙니다.)\n클오클 운영 도우미에서 "
                                  "`지원 관련 무기여 지수`값 결정 알고리즘을 변경 (이 기능은 곧 상용화됩니다.)",
                            inline=False)
            embed.add_field(name="3. 수정된 버그",
                            value="`커뉴야 숫자채널` 명령어가 제대로 작동하지 않던 버그 수정\n코인의 가격이 이따금씩 제대로 새로고침되지 않던 버그 수정\n`커뉴야 날짜차이` "
                                  "명령어에서 날짜 차이가 0이면 나던 에러 수정\n클오클 습격전 정산에서 클랜을 탈퇴한 사람이 비정상적인 행보를 보일 경우 나던 에러 수정",
                            inline=False)
            embed.add_field(name="4. 공식서버 전용 업데이트",
                            value="실시간 리더보드의 정보가 이따금씩 제대로 새로고침되지 않던 버그 수정",
                            inline=False)
            embed.set_footer(
                text="커뉴야 심심해 명령어로 나오는 TMI 개수: 210개 -> 220개\n도전과제 개수: 123개 -> 123개 ()\n이전 업데이트 yonsei2\n다음 업데이트 yonsei4")
            await ctx.send(embed=embed)
        elif extra1 == '클오클':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 클오클 (관련된 모든 명령어의 업데이트 내역이 여기에 표시됨)")
            embed.add_field(name='yonsei3', value='지원 관련 무기여 지수 결정 알고리즘을 변경', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '숫자채널':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 숫자채널")
            embed.add_field(name='yonsei3', value='명령어 실행 시 나던 에러를 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '날짜차이':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 날짜차이")
            embed.add_field(name='yonsei3', value='결과로 나온 날짜 차이가 0일이면 나던 에러 수정', inline=False)
            embed.add_field(name='yonsei1', value='뒤에 날짜 하나만 입력했을 때를 빼면 명령어가 작동하지 않던 버그 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == 'yonsei2':
            embed = Embed(color=0xffd6fe, title="커뉴봇 yonsei2 업데이트 (날짜: 2024년 3월 22일)")
            embed.add_field(name='이번 업데이트의 방향성',
                            value="작고 빠른 업데이트 방향을 처음으로 시도해본 업데이트 (쿨타임 이슈 해결을 중심으로 함)",
                            inline=False)
            embed.add_field(name="1. 개선된 기능",
                            value="잡초키우기, 우주탐험, 퀴즈, 커뉴핑크 명령어에서 도움을 출력하라는 명령이 있을 때 쿨타임을 무시 (실험적이며 이후 버전에서 롤백되거나 확장될 수 "
                                  "있음)\n이제 **모든 기능**에서 봇이 보낸 메세지를 무시\n`커뉴야 커뉴핑크`명령어의 밸런스 조절\n`커뉴야 커뉴핑크`에서 프리셋 이름을 "
                                  "l1번처럼 입력해도 인식\n`커뉴야 소수판정`의 입력 범위를 10의 1980제곱까지 가능하도록 함\n`커뉴야 다음거울수`의 입력 범위를 10의 "
                                  "1800제곱-1까지 가능하도록 함",
                            inline=False)
            embed.add_field(name="2. 수정된 버그",
                            value="`커뉴야 커뉴핑크`에서 명령어 사용당 경험치를 상수만큼 올려주는 색깔의 효과가 제대로 적용되지 않던 버그 수정",
                            inline=False)
            embed.add_field(name="3. 삭제된 기능",
                            value="모든 기능에서 봇 메세지를 무시함에 따라, `커뉴야 봇메세지무시`기능을 삭제, 또한 봇으로 서버강화 시도하는 것을 막는 기능도 삭제",
                            inline=False)
            embed.set_footer(
                text="커뉴야 심심해 명령어로 나오는 TMI 개수: 210개 -> 210개\n도전과제 개수: 122개 -> 123개 (추가된 도전과제: 과거를 보는 자(6p))\n이전 업데이트 "
                     "yonsei1\n다음 업데이트 yonsei3\n이 업데이트 또는 이후 업데이트에서 밸런스 조절이라는 말이 있다면 명령어별 세부 업데이트 내역에 자세한 내용이 실어집니다.")
            await ctx.send(embed=embed)
        elif extra1 == '커뉴핑크':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 커뉴핑크")
            embed.add_field(name='yonsei2', value='# 밸런스 조절\nSimpleGreen의 경험치 추가량 5 -> 3으로 **너프**\n# 버그 수정\n명령어 실행당 경험치를 상수로 더하는 색의 효과가 적용되지 않던 버그 수정')
            embed.add_field(name='yonsei1', value='명령어 출시', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '소수판정':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 소수판정")
            embed.add_field(name='yonsei2', value='가능한 입력값의 범위를 10의 1900제곱까지에서 10의 1980제곱까지로 상향')
            await ctx.send(embed=embed)
        elif extra1 == '다음거울수':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 다음거울수")
            embed.add_field(name='yonsei2', value='가능한 입력값의 범위를 10의 1500제곱-1까지에서 10의 1800제곱-1까지로 상향')
            await ctx.send(embed=embed)
        elif extra1 == '봇메세지무시':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 다음거울수")
            embed.add_field(name='yonsei2', value='명령어 삭제')
            await ctx.send(embed=embed)
        elif extra1 == 'yonsei1':
            embed = Embed(color=0xffd6fe, title="커뉴봇 yonsei1 업데이트 (날짜: 2024년 3월 18일)")
            embed.add_field(name='이번 업데이트의 방향성',
                            value="`커뉴야 커뉴핑크` 릴리즈를 비롯해 연세대학교 학생이 된 걸 기념하는 대규모 업데이트",
                            inline=False)
            embed.add_field(name="1. 새로운 기능",
                            value="새로운 게임 기능 `커뉴야 커뉴핑크` 추가\n이번 업데이트 그 이후에 업데이트되었고 `도움`, `업데이트`, `관리`나 대화 명령어가 아닌 "
                                  "명령어들에 대해, `커뉴야 업데이트 (명령어)`를 치면 해당 명령어가 근래에 어떻게 업데이트되었는지를 알려줌\n유용한 기능 `커뉴야 다음거울수`, "
                                  "`커뉴야 계산` (매우 실험적임) 추가\n뀨 상점에 `퀴즈 주제 다중 선택`, `TMI 트래커` 추가\n아직은 실험 단계지만, 코인 가격을 그래프로 "
                                  "보여주는 `커뉴야 코인 그래프` 추가",
                            inline=False)
            embed.add_field(name="2. 개선된 기능",
                            value="`커뉴야 타이머`가 3.5분 등 정수가 아닌 입력도 인식함\n`커뉴야 퀴즈`에서 중복이 뜰 확률 계산 알고리즘을 약간 개선\n`커뉴야 올려`명령어로 "
                                  "채팅이 조금 더 많이 올라감\n화력코인의 변동성을 소폭 감소시킴\n`커뉴야 코인` 중 큰 수가 나오는 대부분의 기능에서 수를 쉼표로 구분\n`커뉴야 "
                                  "코인 룰렛`에서 가능한 수의 범위가 1~36임을 더 잘 보이는 곳에 명시\n`커뉴야 코인 룰렛`에서 홀수 또는 짝수에 거는 경우 줄임말을 "
                                  "인식\n`커뉴야 코인 블랙잭`에서 가능한 행동들의 설명을 튜토리얼에만 표시\n`커뉴야 코인 블랙잭`에서 판이 끝난 이후 남은 코인을 표시\n`커뉴야 "
                                  "코인 블랙잭`에서 돈이 부족할 경우 더 이상 더블 다운을 할 수 없음\n`커뉴야 묵찌빠`에서 레이팅 차이가 더 많이 나는 상대와도 매칭이 되도록 "
                                  "변경, 그에 맞게 경기 종료 이후 레이팅 변화 공식을 수정\n`커뉴야 심심해`명령어의 쿨타임이 90초로 감소\n`커뉴야 뀨 상점`에서 아이템들의 "
                                  "페이지를 더 자세히 나눔\n`커뉴야 스펙`에서 발견한 TMI 개수를 새로 표시",
                            inline=False)
            embed.add_field(name="3. 수정된 버그",
                            value="도움말에 있었던 여러 가지 소소한 표기오류들과 누락된 사항들을 수정\n이전에 봇을 사용한 적이 거의 없을 때 `커뉴야 강화`, `커뉴야 스펙`을 "
                                  "실행하면 나던 에러 수정\n`커뉴야 지분`에서 모든 사람이 같은 횟수만큼 명령어를 사용했을 때 지분 순위가 비정상적으로 표시되던 버그 "
                                  "수정\n도전과제 `코인 대부호`가 조건을 만족함에도 달성되지 않던 버그 수정\n`커뉴야 코인`에서 알맞은 양의 코인을 가지고 있었음에도 판매되지 "
                                  "않던 버그 수정\n`커뉴야 코인 블랙잭`에서 더블 다운을 해도 카드를 더 뽑을 수 있던 버그 수정\n`커뉴야 코인`에서 화력코인 변화량이 이상하게 "
                                  "표기되던 버그 수정\n`커뉴야 코인 지원금`에서 특정한 경우 지원금이 100000.0처럼 소수점으로 표기되던 버그 수정\n`커뉴야 코인 블랙잭`에서 "
                                  "돈을 잃은 후 남은 돈이 0 이하이면 에러가 나면서 돈 변화가 반영되지 않던 버그 수정\n`커뉴야 뀨 인벤`에서 출첵내역 연장이 표시되지 않던 버그 "
                                  "수정\n`커뉴야 날짜차이`가 제대로 작동하지 않던 버그 수정\n역할 또는 채널을 입력받던 명령어들이 입력을 인식하지 못하던 버그 수정\n도전과제 "
                                  "`명령어의 신`이 서로 다른 255개의 명령어만 사용해도 달성되던 버그 수정",
                            inline=False)
            embed.add_field(name="4. 삭제된 기능",
                            value="존재의 필요성이 처음부터 없었던 `커뉴야 으으ㅐ느느 ㅏ` 삭제",
                            inline=False)
            embed.add_field(name="5. 공식서버 전용 업데이트",
                            value="뀨 전용 게임 알파 센타우리 업데이트 (자세한 내용은 접근 권한 보유자만 ㅋㅇ업뎃 참고)", inline=False)
            embed.add_field(name="핫픽스 #1: 2024/03/18",
                            value="- `커뉴야 커뉴핑크 광산`에서 금을 캘 수 있는 상황일 때 나던 에러를 수정했습니다.\n- `커뉴야 심심해`가 90초당 1000번까지 사용 "
                                  "가능하던 버그를 수정했습니다.")
            embed.set_footer(text="커뉴야 심심해 명령어로 나오는 TMI 개수: 200개 -> 210개\n도전과제 개수: 115개 -> 122개 (추가된 도전과제: 블랙잭!(2p), "
                                  "커뉴핑크 사용자, 커뉴핑크 초보 탈출, 커뉴핑크 중수(2p), 상시숭배, 다시 하는 1주년 이벤트(6p), 커뉴핑크 초기 개척자(8p))\n이전 "
                                  "업데이트 24_seol\n다음 업데이트 yonsei2")
            await ctx.send(embed=embed)
        elif extra1 == '업데이트':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 업데이트")
            embed.add_field(name='yonsei1', value='지금 보고 있는 업데이트 내역처럼 뒤에 특정한 기능 이름을 입력하면 명령어가 근래에 어떻게 업데이트되었는지를 알려줌', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '다음거울수':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 다음거울수")
            embed.add_field(name='yonsei1', value='명령어 출시', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '뀨':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 뀨")
            embed.add_field(name='yonsei1', value='새로운 기능\n\n상점에 `퀴즈 주제 다중 선택`, `TMI 트래커` 추가\n\n개선된 기능\n\n상점의 아이템들의 페이지를 더 자세히 나눔\n\n수정된 버그\n\n인벤에서 출첵내역 연장이 표시되지 않던 버그 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '타이머':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 타이머")
            embed.add_field(name='yonsei1', value='시간 입력이 정수가 아니어도 인식함', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '퀴즈':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 퀴즈")
            embed.add_field(name='yonsei1', value='중복이 뜰 확률 계산 알고리즘을 약간 개선', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '올려':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 올려")
            embed.add_field(name='yonsei1', value='채팅이 조금 더 많이 올라감', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '묵찌빠':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 묵찌빠")
            embed.add_field(name='yonsei1', value='레이팅 차이가 더 많이 나는 상대와도 매칭이 되도록 변경, 그에 맞게 경기 종료 이후 레이팅 변화 공식을 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '심심해':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 심심해")
            embed.add_field(name='yonsei1', value='TMI 개수가 210개까지 증가, 명령어의 쿨타임이 90초로 감소', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '도움':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 도움")
            embed.add_field(name='yonsei1', value='여러 가지 소소한 표기오류들과 누락된 사항들을 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '강화':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 강화")
            embed.add_field(name='yonsei1', value='이전에 봇을 사용한 적이 거의 없을 때 명령어를 실행하면 나던 에러 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '스펙':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 스펙")
            embed.add_field(name='yonsei1', value='이전에 봇을 사용한 적이 거의 없을 때 명령어를 실행하면 나던 에러 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '지분':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 지분")
            embed.add_field(name='yonsei1', value='모든 사람이 같은 횟수만큼 명령어를 사용했을 때 지분 순위가 비정상적으로 표시되던 버그 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '도전과제':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 도전과제")
            embed.add_field(name='yonsei1', value='도전과제 개수가 122개까지 증가, `코인 대부호`가 조건을 만족함에도 달성되지 않던 버그 수정, `명령어의 신`이 서로 다른 255개의 명령어만 사용해도 달성되던 버그 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '로그채널':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 로그채널")
            embed.add_field(name='yonsei1', value='근래에 만들어진 채널을 로그 채널로 정하려고 할 때 봇이 인식하지 못하던 버그 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '레벨역할':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 레벨역할")
            embed.add_field(name='yonsei1', value='근래에 만들어진 역할을 레벨 역할으로 정하려고 할 때 봇이 인식하지 못하던 버그 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '이름색역할':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 이름색역할")
            embed.add_field(name='yonsei1', value='근래에 만들어진 역할을 이름색 역할으로 정하려고 할 때 봇이 인식하지 못하던 버그 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '세로채널':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 세로채널")
            embed.add_field(name='yonsei1', value='근래에 만들어진 커스텀 이모지 하나만 세로채널에 보냈을 때 봇이 메세지를 삭제하던 버그 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '알파센타우리':
            embed = Embed(color=0xffd6fe, title="커뉴봇 기능 업데이트 내역: 알파센타우리")
            embed.add_field(name='yonsei1', value='새로운 기능\n\n(스포방지)\n\n개선된 기능\n\n`ㅋㅇ프로필` 명령어에서 자동 획득 아니 씨밧 부스트에 대한 보너스를 반영\n`ㅋㅇ거래` 명령어에서 거래 품목 개수가 1일 때 추가 거래 품목을 늘리는 거래를 제안할 확률 증가\n\n수정된 버그\n\n`ㅋㅇ프로필` 명령어에서 일부 스탯이 표시되지 않던 버그 수정\n메타벗과 뇌저를 연구해도 `ㅋㅇ우주선`명령어가 제대로 작동하지 않던 버그 수정', inline=False)
            await ctx.send(embed=embed)
        elif extra1 == '24_seol':
            embed = Embed(color=0xffd6fe, title="커뉴봇 24_seol 업데이트 (날짜: 2024년 2월 9일)")
            embed.add_field(name='이번 업데이트의 방향성',
                            value="설맞이 중대 업데이트",
                            inline=False)
            embed.add_field(name="1. 새로운 기능",
                            value="`커뉴야 코인`에서 보유 현금과 보유 코인 가치의 총합을 알려주는 `커뉴야 코인 자산` 추가\n`커뉴야 코인`에서 새로운 도박 기능인 `커뉴야 코인 "
                                  "블랙잭` 추가\n유용한 기능에 `커뉴야 소수판정`, `커뉴야 소인수분해`, `커뉴야 글자수` 추가\n뀨 상점에 `더 좋은 도전과제 목록`, "
                                  "`금성챗 특정숫자 알림` 추가\n이제 개인 메세지에서도 일부 명령어를 사용할 수 있음\n`커뉴야 업데이트 (버전)`을 입력하면 이전 업데이트 로그를 "
                                  "볼 수 있음 (첫 출시 버전 이름을 birth로 설정했으며, 그동안은 버전 이름을 나누어 놓지 않았기에 이전 버전 이름들은 임의로 부여함)",
                            inline=False)
            embed.add_field(name="2. 개선된 기능",
                            value="`커뉴야 코인 지원금` 명령어의 메커니즘 변경: 이제부터는 가진 자산이 얼마나 되는지와 상관없이 지원금을 받을 수 있지만 30분의 쿨타임이 "
                                  "부여됨\n`커뉴야 코인`의 코인 개수 정밀도를 개선\n쿨타임이 쓸데없이 길었던 일부 명령어들의 쿨타임을 감소\n`커뉴야 도전과제 설명`에서 "
                                  "도전과제를 달성했는지도 같이 표시\n도전과제 달성 시 핑을 같이 해줌\n`커뉴야 타이머`로 설정할 수 있는 최대 시간을 더 높게 바꿈\n`커뉴야 "
                                  "커맨드금지`에서 올려금지가 켜져 있는지도 같이 표시\n많은 사람이 활동 중인 서버에 봇이 있거나 많은 사람이 봇을 동시에 사용하는 경우 응답속도가 "
                                  "빨라짐\n`커뉴야 도전과제 목록`이 약간 더 간결해짐\n뀨 아이템 `새로운 줄임말`에서 `커뉴야 ㅈㅋ 비료`를 `커뉴야 ㅈㅋ ㅂㄹ`로도 줄일 수 "
                                  "있음",
                            inline=False)
            embed.add_field(name="3. 수정된 버그",
                            value="일부 대화 명령어에서 나타나던 버그 수정\n`커뉴야 스톱워치 시작`을 시도하면 나던 에러 수정\n뀨 아이템 지분 순위에서 사용자 한 명의 지분이 "
                                  "100%일 때 지분 순위가 공동 1위라고 표시되던 버그 수정\n도전과제 `몰빵 가즈아`를 제대로 획득할 수 없던 버그 수정 (그럴 일은 없겠지만 "
                                  "업데이트 이후에도 버그가 난다면 문의해주세요. 조금 다른 문제입니다.)\n`커뉴야 묵찌빠 매칭`에서 두 사람이 처음에 같은 걸 냈을 때 매칭이 "
                                  "잡혔다고 다시 한 번 말하던 버그 수정\n`커뉴야 이름색`명령어가 제대로 작동하지 않던 버그 수정",
                            inline=False)
            embed.add_field(name="4. 삭제된 기능",
                            value="존재의 필요성이 사라지게 된 `커뉴야 잡소리` 삭제\n2번 항목에서 언급한 최적화의 일환으로 메세지를 보낼 때마다 체크하던 기능들 중 사용률이 극히 "
                                  "낮던 일부를 삭제\n업데이트 hs21 이후 아무도 발견하지 못한 대화 명령어 일부를 삭제",
                            inline=False)
            embed.add_field(name="5. 공식서버 전용 업데이트",
                            value="뀨 전용 게임 알파 센타우리의 **알데바락 우주센터** 업데이트 (자세한 내용은 접근 권한 보유자만 ㅋㅇ업뎃 참고)\n매일매일 서버스탯이 평균적으로 "
                                  "조금 더 빨리 올라오며, 항목들 중 '봇이 보낸 메세지 개수'만 볼드체로 안 되던 것을 수정\n`커뉴야 서바준보 (텍스트)` 가 아닌 `커뉴야 "
                                  "서바준보`를 실행하면 이제 랜덤한 서준의 오타 사진을 보냄", inline=False)
            embed.set_footer(text="커뉴야 심심해 명령어로 나오는 TMI 개수: 180개 -> 200개\n도전과제 개수: 110개 -> 115개 (추가된 도전과제: 능지개떡상(2p), "
                                  "만렙을 초월한 (2p), 단골 사용자 3(3p), 3웨(6p), ㅎ😩ㅎ(6p))\n`설명좀`, `핑이나 막아라!`도전과제의 달성조건이 "
                                  "변경됐습니다\n이전 업데이트 hs35\n다음 업데이트 yonsei1")
            await ctx.send(embed=embed)
        elif extra1 == 'hs35':
            embed = Embed(color=0xffd6fe, title="커뉴봇 업데이트 (날짜: 2024년 1월 27일)")
            embed.add_field(name='이번 업데이트의 방향성',
                            value="설맞이 중대 업데이트를 앞에 두고 하는 버그 수정",
                            inline=False)
            embed.add_field(name="1. 새로운 기능",
                            value="-",
                            inline=False)
            embed.add_field(name="2. 개선된 기능",
                            value="여러분에겐 개선이 아니겠지만, 서버스탯이 보내진 이후 즉시 화력코인 가격을 업데이트\n`커뉴야 나중업뎃`명령어를 도움말에 표시",
                            inline=False)
            embed.add_field(name="3. 수정된 버그",
                            value="도전과제 목록에서 `눈치게임 고수`가 2개 표시되던 버그 수정\n`커뉴야 코인 지원금`에서 총 자산이 100만이 넘어도 지원금이 받아지던 버그 수정",
                            inline=False)
            embed.add_field(name="4. 공식서버 전용 업데이트",
                                value="`잡소리 독자` 도전과제가 정말로 부활했을 거임.")
            embed.set_footer(text="커뉴야 심심해 명령어로 나오는 TMI 개수: 180개 -> 180개\n도전과제 개수: 110개 -> 110개\n이전 업데이트 hs34\n다음 "
                                  "업데이트 24_seol")
            await ctx.send(embed=embed)
        elif extra1 == 'hs34':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2024년 01월 22일)')
            embed.add_field(name='이번 업데이트의 방향성', value='현재까지 뀨로 구매한 아이템들의 목록을 볼 수 있는 `커뉴야 뀨 인벤토리` 명령어 추가\n뀨 상점에 `지분 '
                                                       '순위` 추가\n관리 명령어 `커뉴야 경험치초기화` 추가\n`커뉴야 코인` 및 그와 관련된 도전과제 부활',
                            inline=False)
            embed.add_field(name='1. 새로운 기능', value='봇으로 서버강화를 시도할 경우 단순히 메세지를 무시하는 것을 넘어서 일정 기간 동안 서버강화를 정지', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 강화목록` 명령어에서 강화 슬롯이 10개 이상인 유저는 `공식서버 가입 후 커뉴야 구매 강화슬롯추가권 '
                                                    '명령어로 최대 10개까지 이 값을 늘리세요` 라는 문구가 더 이상 뜨지 않음\n뀨 결제 수단에 계좌이체 '
                                                    '추가\n`커뉴야 커맨드금지`로 채널에서 금지된 커맨드를 사용하려고 할 때 사용금지된 커맨드임을 알려줌',
                            inline=False)
            embed.add_field(name='3. 수정된 버그', value='일부 도전과제의 설명이 실제와 다르던 버그 수정\n`커뉴야 날짜차이`에서 어떤 경우 날짜 차이가 음수로 나오던 버그 '
                                                    '수정', inline=False)
            embed.add_field(name='4. 공식서버 전용 업데이트', value='잡초키우기에서 내일지구가멸망해도나무를키우겠다 도전과제 달성 시 해당 칭호 역할 대신 나무를 키우는 자 '
                                                          '역할이 한 번 더 부여되던 버그 수정\n잡초키우기에서 비료를 한 번에 많이 살 수 있도록 '
                                                          '변경\n공식서버가 아닌 서버에서 잡초키우기나 우주탐험 명령어를 실행할 경우 주는 보상을 하향\n`잡소리 '
                                                          '독자`도전과제가 부활했을 수도 있고 부활하지 않았을 수도 있음', inline=False)
            embed.set_footer(text='커뉴야 심심해 명령어로 나오는 TMI 개수: 170개 -> 180개\n도전과제 개수: 104개 -> 110개(+:코인 대부호(2p), '
                                  '퀴즈 출제자(2p), 프로 퀴즈 출제자(2p), 드루이드(4p), 설명대로(6p), 얼마나 심심하셨길래...(6p))\n이전 업데이트 '
                                  'hs33\n다음 업데이트 hs35')
            await ctx.send(embed=embed)
        elif extra1 == 'hs33':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2024년 01월 20일)')
            embed.add_field(name='이번 업데이트의 방향성', value='어뷰징 의심으로 인한 핫픽스', inline=False)
            embed.add_field(name='1. 새로운 기능', value='봇으로 서버강화를 시도할 경우 단순히 메세지를 무시하는 것을 넘어서 일정 기간 동안 서버강화를 정지', inline=False)
            embed.add_field(name='2. 개선된 기능', value='-', inline=False)
            embed.add_field(name='3. 수정된 버그', value='-', inline=False)
            embed.add_field(name='4. 공식서버 전용 업데이트', value='-', inline=False)
            embed.set_footer(text='커뉴야 심심해 명령어로 나오는 TMI 개수: 170개 -> 170개\n도전과제 개수: 104개 -> 104개\n이전 업데이트 hs32\n다음 '
                                  '업데이트 hs34')
            await ctx.send(embed=embed)
        elif extra1 == 'hs32':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2024년 01월 19일)')
            embed.add_field(name='이번 업데이트의 방향성', value='오랜만의 업데이트인 만큼, 이 업데이트는 새로운 기능을 마구 추가하기보다는 일부 기능을 개선하고, 알려진 버그 '
                                                       '몇 개를 수정하는 등 편의성에 중점을 둔 업데이트입니다. 앞으로 새로운 기능에 대한 요청이 있다면 빠르게 '
                                                       '업데이트할 수 있다는 암시 정도의 업데이트이기도 합니다!', inline=False)
            embed.add_field(name='1. 새로운 기능', value='-', inline=False)
            embed.add_field(name='2. 개선된 기능', value='커뉴의 규칙 위반자 판별 휴리스틱을 완화 (인간어 번역: 우주탐험 명령어에서 수회 튜토리얼이 보여지던 현상을 '
                                                    '완화)\n이 명령어에서 이 업데이트와 앞으로의 업데이트에 대해 업데이트의 전반적인 방향성을 설명\n이 명령어를 '
                                                    '`커뉴야 업데이트`와 `커뉴야 업데이트 공식서버` 두 개로 나누지 않고, 그 대신 공식서버 안에서 이 명령어가 '
                                                    '실행되는 경우 공식서버 관련 업데이트와 함께 표기', inline=False)
            embed.add_field(name='3. 수정된 버그', value='`커뉴야 오목`에서 오목판의 마지막 줄이 이상하게 나오던 버그 수정\n미션형 도전과제 `진정한 레벨업`이 제대로 '
                                                    '작동되지 않던 버그 수정', inline=False)
            embed.add_field(name='4. 공식서버 전용 업데이트', value='<#1000636815239299082> 부활', inline=False)
            embed.set_footer(text='커뉴야 심심해 명령어로 나오는 TMI 개수: 160개 -> 170개\n도전과제 개수: 101개 -> 104개\n이전 업데이트 hs31\n다음 '
                                  '업데이트 hs33')
            await ctx.send(embed=embed)
        elif extra1 == 'hs31':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2023년 07월 04일)')
            embed.add_field(name='업데이트 공지', value='최근 봇으로 `커뉴야 서버강화` 명령어를 매크로로 지정한 사례가 적발되었습니다.\n\n확인 결과 5000회 넘게 '
                                                  '서버강화 명령어를 Dyno봇 매크로에 심어둔 채 돌리는 것이 발견되었습니다.\n\n이제 다음과 같은 변경사항이 '
                                                  '있습니다.\n\n- `커뉴야 봇메세지무시` 명령어에 의한 봇 메세지 무시 기능이 꺼져 있어도, 서버강화 명령어는 항상 '
                                                  '봇 메세지를 무시합니다. 이런 시도가 잦은 서버는 아래와 같은 방식의 제재를 가하겠습니다.\n\n해당 서버에 대해서는, '
                                                  '서버에서 커뉴봇이 바로 나가고, 나중에 커뉴봇을 부르더라도 커뉴봇이 즉시 나가는 조치를 취했습니다.\n\n감사합니다.')
            embed.set_footer(text='이런거 보면 신고해요\n업데이트 명령어에 쓴 게 없어서 공지로 대체합니다.\n이전 업데이트 darkness\n다음 업데이트 hs32')
            await ctx.send(embed=embed)
        elif extra1 == 'darkness':
            embed = Embed(color=0xffd6fe, title='커뉴봇 없데이트 (날짜: ???)')
            embed.add_field(name='네 뭐 없네요...', value='개발자가 정신적으로 매우 힘든 나날을 보내던 와중인 만큼 업데이트도 없던 시기입니다. 잠수함 패치는 생각보다 더 '
                                                     '많이 이루어졌지만, 이때는 그저 암흑시기일 뿐이었어요...')
            embed.set_footer(text='이전 업데이트 hs30\n다음 업데이트 hs31')
            await ctx.send(embed=embed)
        elif extra1 == 'hs30':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2022년 02월 02일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 할거`기능에 새로운 기능 다수 추가: 중간 목표 설정, 정기적 목표, 같이 할 일 설정 가능\n`커뉴야 '
                                                    '같이공부`추가: 같이 공부할 사람을 만들 수 있음\n`커뉴야 기원닉띄기`추가: 서버 기원 닉네임을 띄어쓰거나 그렇지 '
                                                    '않게 할 수 있음\n`커뉴야 뀨 설명추`가: 아이템의 설명을 볼 수 있음\n`커뉴야 숫자채널 (채널) '
                                                    '해제`추가\n미션형 도전과제 추가: 여태껏 있던 도전과제랑은 다름... `커뉴야 도전과제 목록 7`\n`커뉴야 '
                                                    '잡소리`추가: 공식서버 16레벨 이상 또는 그랬다가 나간 사람들 중 일부를 위한 명령어\n`커뉴야 색깔`명령어 '
                                                    '추가\n`커뉴야 날짜차이`명령어 추가', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 할거` 명령어의 전반적인 편의성 개선\n권한을 주지 않은 상태에서 일부 명령어를 실행할 경우 봇이 '
                                                    '띠꺼워짐\n`커뉴야 기원` 최적화\n`커뉴야 오목`에서 대국이 끝났을 때 관전 중인 채널에 끝났다고 알림\n일부 '
                                                    '명령어에 대한 도움말 추가\n`커뉴야 숫자채널` 뒤에 채널을 붙이면 현재 채널이 아닌 채널도 숫자채널 지정 '
                                                    '가능\n`커뉴야 오타원본`을 `커뉴야 오타ㅏ원본`으로도 사용 가능, 커뉴야 오타원본명령어에서 국기들 등의 새로운 '
                                                    '사진들을 추가\n커뉴봇 프로필을 클릭하면 바로 서버에 추가 버튼을 눌러 자신의 서버에 초대할 수 있음',
                            inline=False)
            embed.add_field(name='3. 수정된 버그', value='`커뉴야 퀴즈 신고`에서 코드를 잘못 입력하면 나던 에러 수정\n`커뉴야 오목 자동매칭`버그 수정\n`커뉴야 '
                                                    '초대당경부`명령어가 오작동하던 버그 수정\n퀴즈를 신고할 때 아이디를 잘못 입력하면 나던 에러 수정',
                            inline=False)
            embed.set_footer(text='커뉴야 심심해 명령어로 나오는 TMI 개수: 120개 -> 120개\n도전과제 개수: 96개 -> 101개\n이전 업데이트 hs29\n다음 업데이트 '
                                  'darkness')
            await ctx.send(embed=embed)
        elif extra1 == 'hs29':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 12월 24일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 스톱워치 내역`추가: 이전 스톱워치들의 내역을 확인할 수 있음 (자세한 도움말은 `커뉴야 도움 '
                                                    '스톱워치`)\n새로운 디버그 기능 `커뉴야 디엠테스트`추가: 오목같은거 하기 전에 해보세요\n`커뉴야 뀨 보유` '
                                                    '추가, `커뉴야 뀨 상점`에서 더 다양한 아이템을 판매하기 시작\n`커뉴야 뀨 가격`에 원하는 금액 결제에 관한 '
                                                    '내용 추가\n`커뉴야 도전과제 설명` 추가: 뒤에 도전과제 이름을 입력하면 특정한 도전과제에 관한 설명을 볼 수 '
                                                    '있음', inline=False)
            embed.add_field(name='2. 개선된 기능', value='매일매일 서버스탯 자동화 UI 개선\n`커뉴야 오목 목록`에서 방 안에 누가 있는지도 보여줌\n몇몇 명령어에 대해 '
                                                    '다른 형태 추가\n`커뉴야 스펙`에서 뀨 보유량도 볼 수 있음\n도전과제 등 일부 명령어들을 최적화',
                            inline=False)
            embed.add_field(name='3. 수정된 버그', value='오목에서 몇 수까지 진행되었는지 보일 때 수가 하나씩 밀리는 버그 수정\n아무 방에도 들어가 있지 않았는데 '
                                                    '끼임해제를 하면 나던 에러 수정\n`커뉴야 뀨`를 실행하면 가끔 입력과 관계없이 도움이 뜨던 버그 수정',
                            inline=False)
            embed.set_footer(text='커뉴야 심심해 명령어로 나오는 TMI 개수: 100개 -> 120개\n도전과제 개수: 83개 -> 96개\n이전 업데이트 hs28\n다음 업데이트 '
                                  'hs30')
            await ctx.send(embed=embed)
        elif extra1 == 'hs28':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 12월 16일)')
            embed.add_field(name='업데이트 공지', value='매일매일 서버스탯 자동화 작업이 완료되었습니다!\n기술적으로 **서버 총 메세지 개수** 스탯은 커뉴봇으로 집계가 '
                                                  '불가능하기 때문에 서버스탯에 포함시키지 않았고, 서버화력 계산이 조금 더 정확해집니다. (이전에는 모종의 이유로 삭제된 '
                                                  '채널에서 해당 날 동안 보내진 메세지가 화력에 들어가지 않았지만 이제는 들어갑니다)\n\n또한 봇이 보낸 메세지 개수도 '
                                                  '따로 서버스탯에 기록해 전의 통계보다 조금 더 믿을만하도록 바꿨습니다.\n\n마지막으로 새로 사람들이 하루 동안 '
                                                  '벌어들인 경험치의 수도 이제부터 서버스탯에 기록됩니다.\n\n그러나 *내일 올라오는 오늘 서버스탯* 에서는 서버 화력이 '
                                                  '오늘 실제로 보내진 메세지보다 더 적게 측정될 것입니다.\n\n이는 자동화 작업이 오늘 끝마쳐졌기 때문에 자동화 작업을 '
                                                  '마치기 전 보내진 메세지는 집계되지 않았기 때문입니다. 고로 12월 17일부터를 다루는 서버스탯에서는 정상적으로 반영될 '
                                                  '것입니다.\n\n감사합니다!')
            embed.set_footer(text='업데이트 명령어에 쓴 게 없어서 공지로 대체합니다.\n이전 업데이트 hs27\n다음 업데이트 hs29')
            await ctx.send(embed=embed)
        elif extra1 == 'hs27':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 12월 05일)')
            embed.add_field(name='업데이트 공지', value='봇의 유료 재화 `뀨` 를 가지고 무언가를 살 수 있게 되었습니다.\n\n`커뉴야 뀨 도움` 으로 자세한 정보들을 '
                                                  '알아보실 수 있을 것 같네요.\n\n상점에서 무언가를 팔기는 하지만 그게 뭔지는 아직 잘 모르겠습니다.\n\n과연 '
                                                  '그것을 사면 무슨 일이 생길까요?')
            embed.set_footer(text='업데이트 명령어에 쓴 게 없어서 공지로 대체합니다.\n이전 업데이트 hs26\n다음 업데이트 hs28')
            await ctx.send(embed=embed)
        elif extra1 == 'hs26':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 11월 26일)')
            embed.add_field(name='업데이트 공지', value='11월 21일에 진행된 업데이트 이후 버그 두 개가 발견되어 이 버그들을 고쳐냈습니다.\n\n- 공식서버 아이템 중 '
                                                  '`원하는 사람 강제닉변권` 등의 아이템이 구매 자체가 안 됐던 버그\n- `커뉴야 스펙` 명령어를 실행할 수 없었던 '
                                                  '버그\n\n감사합니다!')
            embed.set_footer(text='업데이트 명령어에 쓴 게 없어서 공지로 대체합니다.\n이전 업데이트 hs25\n다음 업데이트 hs27')
            await ctx.send(embed=embed)
        elif extra1 == 'hs25':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 11월 21일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 섞어` 추가: 입력받은 값들을 랜덤한 순서대로 섞어서 다시 출력', inline=False)
            embed.add_field(name='2. 개선된 기능', value='더 이상 `커뉴야 심심해`명령어로 나오는 TMI가 추가되었다는 내용과 도전과제가 추가되었다는 내용은 이 란에 '
                                                    '표시하지 않는 대신 아래에 표시\n`커뉴야 퀴즈 풀기`에서 문제를 틀리면 잃는 점수 공식 수정\n전반적인 최적화 '
                                                    '진행: 데이터베이스 문제 등에 대해 최적화\n(공식서버) 매크로 방지에 걸려서 정지를 먹는 경우 처벌 내역 채널에 '
                                                    '아이디 대신 유저명 기록\n(공식서버) 특히 높은 레벨에서 잡초키우기 보상 너프\n`커뉴야 오목`에서 대국 도중 몇 '
                                                    '수 째인지 표기', inline=False)
            embed.add_field(name='3. 수정된 버그', value='커뉴봇에게 바보라 하면 화내던 기능에서 바보라 하지도 않았는데 메세지를 지우는 버그 수정, 공식서버 바깥에서는 해당 '
                                                    '기능이 작동하지 않음\n(공식서버) 상점에서 원하는 사람 강제닉변권 등의 일부 아이템을 구매하면 나던 에러 '
                                                    '수정\n`커뉴야 출첵내역`에서 15일 이상이 지난 출석체크 정보가 삭제되지 않던 버그 수정\n묵찌빠에서 게임 종료시 '
                                                    '점수 득실이 반대로 되던 버그 수정', inline=False)
            embed.set_footer(text='커뉴야 심심해 명령어로 나오는 TMI 개수: 60개 -> 80개\n도전과제 개수: 75개 -> 85개\n이전 업데이트 hs24\n다음 업데이트 hs26')
            await ctx.send(embed=embed)
        elif extra1 == 'hs24':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 10월 18일)')
            embed.add_field(name='업데이트 공지', value='지금 좀 많이 급해서 공지 제대로 못 쓰네요 죄송합니다 :jasuk:\n\n일단 1차 업데이트를 완료했습니다.\n\n업데이트 해야 될 건 '
                                                '많은데 시간이 없어서 이번주 안으로 좀 나눠서 해야 할 듯합니다.\n\n업데이트가 모두 완료된다면 `커뉴야 업데이트` '
                                                '명령어에 최종본을 말해드리고자 합니다.\n\n어쨌든 현재까지 업데이트 내용은 약 20개의 도전과제 추가 (그 중 일부는 '
                                                '숨겨진 도전과제라 `커뉴야 스펙` 에 있는 도전과제 개수에도 포함이 안된다네요), `커뉴야 심심해`, `커뉴야 스톱워치` '
                                                '명령어 추가, `커뉴야 우주탐험` 에서 탐험하는 천체의 사진 출력 (일부 지역은 사진 도저히 못찾겠어서 못넣은거 3개 '
                                                '있음) 등등입니다.\n\n좀 정신상태가 제대로 돌아오고 나면 다시 공지 쓸게요 내일이나 '
                                                '모레쯤\n\n감사합니다ㅃ\n\n힘들다')
            embed.set_footer(text='업데이트 명령어에 쓴 게 없어서 공지로 대체합니다.\n이전 업데이트 hs23\n다음 업데이트 hs25')
            await ctx.send(embed=embed)
        elif extra1 == 'hs23':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 09월 29일)')
            embed.add_field(name='1. 새로운 기능', value='상점에서 파는 아이템을 신고할 수 있는 `커뉴야 상점 신고` 기능 추가\n시스템 관리명령어 `커뉴야 처벌알림` '
                                                    '추가: 처벌받은 사람에게 DM으로 알려주는 기능\n실시간 매치를 지원하는 게임에서 끼임현상이 발생했을 때 쓰는 '
                                                    '`커뉴야 끼임해제`추가\n자신이 어느 방에 들어갔는지 알 수 있는 `커뉴야 어디`추가\n나중 업데이트의 아이디어를 '
                                                    '적어두는 `커뉴야 나중업뎃`추가', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 서바준보`명령어에서 서준의 최근 오타를 반영\n`커뉴야 오목`에서 방을 나갈 수 있는 `커뉴야 오목 '
                                                    '퇴장`추가\n`커뉴야 상점`UI 개선(아마도?)\n매크로 방지 시스템 전체적으로 개편 (방지 절차 자체를 개편, '
                                                    '정지가 풀리는 것도 처벌내역 채널에 알려줌)\n틀딱드립을 방지하기 위해 `뀨`로 시작하는 일부 메세지에서는 봇이 '
                                                    '반응하지 않음', inline=False)
            embed.add_field(name='3. 수정된 버그', value='`커뉴야 오목`에서 시간초과로 승부가 결정날 때 점수를 얻거나 잃는 것이 뒤집어졌던 버그\n`커뉴야 구매`로 원하는 '
                                                    '사람 강제닉변권 등을 살 시에 나오던 에러\n`커뉴야 애교`의 일부 애교에서 ~가 너무 많아 취소선으로 바뀌던 '
                                                    '버그\n`커뉴야 코인`에서 너무 많은 재산을 가지고 있을 때 나던 버그', inline=False)
            embed.set_footer(text='이전 업데이트 hs22\n다음 업데이트 hs24')
            await ctx.send(embed=embed)
        elif extra1 == 'hs22':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 09월 14일)')
            embed.add_field(name='1. 새로운 기능', value='문자열을 오타로 변환해주는 `커뉴야 서바준보`명령어 추가', inline=False)
            embed.add_field(name='2. 개선된 기능', value='보유중인 코인의 양을 ,구분으로 표시\n상점에서 자신의 아이템이 팔릴 때 디엠으로 알림을 보냄\n우주탐험, '
                                                    '잡초키우기 매크로방지 수정', inline=False)
            embed.add_field(name='3. 수정된 버그', value='`커뉴야 코인 룰렛`에서 뒤에 수를 입력하지 않을 때 나던 에러 수정', inline=False)
            embed.set_footer(text='이전 업데이트 hs21\n다음 업데이트 hs23')
            await ctx.send(embed=embed)
        elif extra1 == 'hs21':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 09월 06일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 스펙`명령어 추가: 자신의 봇 커맨드 사용 횟수 등 많은 정보를 수집 (이번 패치 이후 사용된 커맨드부터 '
                                                    '기록 시작), **커맨드 사용횟수 정보를 수집하기 시작**', inline=False)
            embed.add_field(name='2. 개선된 기능', value='공식서버 잡소리 채널들에서 반응을 달았다 뗐다 하는 것을 표시하지 않음\n`커뉴야 상점 등록`, `커뉴야 상점 '
                                                    '삭제`에서 등록이나 삭제 뒤에 추가로 말하면 아이템 이름 입력 가능\n다른 봇이 관리 명령어를 사용하면 그 처리를 '
                                                    '무시', inline=False)
            embed.add_field(name='3. 수정된 버그', value='`커뉴야 레벨업채널 끔`사용시 아무것도 출력하지 않던 버그 수정\n`커뉴야 레벨업문구 설정`에서 나오던 표기오류를 '
                                                    '수정\n봇에게 밴 권한을 안 줬을 때 밴 명령어를 쓰면 에러 메세지가 출력되던 오류 수정', inline=False)
            embed.set_footer(text='이전 업데이트 hs20\n다음 업데이트 hs22')
            await ctx.send(embed=embed)
        elif extra1 == 'hs20':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 08월 25일)')
            embed.add_field(name='업데이트 공지', value='업데이트가 완료되었습니다!\n\n항상 그랬듯 다양한 버그가 수정되었으며 공식서버에서 `커뉴야 상점` 명령어를 대폭 '
                                                  '개편했습니다.\n\n`커뉴야 상점 등록` 으로 자기가 자기만의 상점 아이템을 등록할 수 있고, `커뉴야 상점 삭제` 로 '
                                                  '해당 아이템의 삭제가 가능합니다.\n\n또한 `커뉴야 코인 지원금` 등 몇몇 명령어들도 더 '
                                                  '추가되었습니다.\n\n**뿌잉뿌잉>_<**\n\n뀨우?!')
            embed.set_footer(text='업데이트 명령어에 쓴 게 없어서 공지로 대체합니다.\n이전 업데이트 hs19\n다음 업데이트 hs21')
            await ctx.send(embed=embed)
        elif extra1 == 'hs19':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 08월 13일)')
            embed.add_field(name='업데이트 공지', value='봇에 또 한번 업데이트가 이루어졌습니다.\n\n~~업데이트 명령어로 뭐 추가됐는지 안써놓음 ㅅㄱ~~\n\n봇 인증을 '
                                                  '대비해서 그에 따른 개인정보 처리방침 패치, 몇 가지의 도전과제 추가, 리더보드 명령어에서 기능을 다양화 하는 등 몇 '
                                                  '가지의 패치를 진행했습니다.\n\n제 두뇌를 자극할만한 기능을 던져주십쇼.\n\n쫀득쫀득한 피자 치쥬가 뫄이뫄이 '
                                                  '들어있는 피이자이아아...! 햄토핑도 좋쿠우 빵에들어가있누눈 치즈도 좋쿠우 매코무한양파아아..!! 피먀양 맛 없써어! '
                                                  '새쿄뮤한 토마토쇼슈 버섯 뫄이쩌엉! 피자 사듀떼여')
            embed.set_footer(text='나와 있다 시피 업데이트 명령어에 쓴 게 없어서 공지로 대체합니다.\n이전 업데이트 hs18\n다음 업데이트 hs20')
            await ctx.send(embed=embed)
        elif extra1 == 'hs18':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 08월 03일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 타이머`기능 추가', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 채널부스트`명령어에서 이 채널에서 받는 경험치: 항목에 자신의 경험치 부스트 기준으로 얻는 경험치를 표시', inline=False)
            embed.add_field(name='3. 수정된 버그', value='도전과제 중 `잡소리 독자`에 버그가 있는 것으로 판명되어 해당 도전 과제를 잠시 삭제\n`커뉴야 잡초키우기`, '
                                                    '`커뉴야 우주탐험`명령어를 공식서버 바깥에서 실행했을 때 연동이 안 되던 오류 수정, 다른 서버에서 벌어들인 돈을 '
                                                    '공식서버 돈으로 합침', inline=False)
            embed.set_footer(text='이전 업데이트 hs17\n다음 업데이트 hs19')
            await ctx.send(embed=embed)
        elif extra1 == 'hs17':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 07월 24일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 닉홍보금지`기능 추가: 닉네임에 서버 링크를 걸어둘 시 다시 이전 닉네임으로 되돌려 놓음\n오목에서 렌주룰 '
                                                    '방 추가(8000~9999번방): 흑만 33, 44, 장목이 불가능한 룰로 이전에 존재했던 룰보다 흑백간 격차가 '
                                                    '적음', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 도전과제 목록`에서 5페이지 추가: 기간 한정 도전 과제들의 목록을 확인 가능\n채널 생성 로그에서 '
                                                    '음성채널이 생성되는 것도 표시\n오목에서 임베드 밑에 이 방이 어떤 규칙으로 진행되는 방인지 표시',
                            inline=False)
            embed.add_field(name='3. 수정된 버그', value='`커뉴야 코인`명령어 부활, `커뉴야 코인 룰렛`에서 뒤에 아무것도 입력하지 않았을 때 나던 오류 수정\n오목에서 '
                                                    '대각선이 포함된 쌍삼은 잡지 못하던 오류 수정', inline=False)
            embed.set_footer(text='이전 업데이트 hs16\n다음 업데이트 hs18')
            await ctx.send(embed=embed)
        elif extra1 == 'hs16':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 07월 17일)')
            embed.add_field(name='1. 새로운 기능', value='로그 기능에서 멤버가 차단되는 로그, 채널이 만들어지거나 삭제되는 로그, 역할이 만들어지거나 삭제되는 로그도 표시', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 뮤트`명령어에서 뮤트 기간을 단순히 초로 입력하지 않아도 됨\n로그 기능에서 멤버가 나가는 로그에 나간 '
                                                    '멤버가 언제 서버에 들어왔는지도 표시\n`커뉴야 서버사진`을 `커뉴야 서버프사`로도 되도록 변경\n리더보드에서 '
                                                    '경험치 부스트도 함께 표시\n리더보드에서 `커뉴야 리더보드 서버강화`처럼 리더보드가 있는 다른 명령어를 붙이면 그 '
                                                    '기능의 리더보드를 출력\n퀴즈 정답률을 소수점 이하 세자리수까지만 표시', inline=False)
            embed.add_field(name='3. 수정된 버그', value='초대 추적기능이 나오기 전이라든가에 들어온 사람이 나가면 환영채널에 메세지가 출력되지 않던 오류 수정', inline=False)
            embed.set_footer(text='이전 업데이트 hs15\n다음 업데이트 hs17')
            await ctx.send(embed=embed)
        elif extra1 == 'hs15':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 07월 13일)')
            embed.add_field(name='1. 새로운 기능', value='이번엔 없네요... 다만 추후 생길 떡밥을 숨겨놓긴 했는데 아마 아무도 못찾을거임', inline=False)
            embed.add_field(name='2. 개선된 기능', value='봇 커맨드 사용할 때의 응답 시간 최적화 (안되면 다음번패치때 다시 시도해볼 예정)\n도전과제 목록에서 임베드 밑에 '
                                                    '일부 도전과제는 표시되지 않는다는 내용이 이제는 맞지 않아 표기를 수정\n`커뉴야 차단`에서 멤버 이름들을 띄어쓰기'
                                                    ' 구분으로 여러 개 나열할 시 한 번에 여러 명 밴 가능', inline=False)
            embed.add_field(name='3. 수정된 버그', value='오목에서 시간초과로 인해 경기가 끝나면 점수가 바뀌지 않던 오류 수정\n`커뉴야 처벌내역`명령어에 있던 오타 수정', inline=False)
            embed.set_footer(text='이전 업데이트 hs14\n다음 업데이트 hs16')
            await ctx.send(embed=embed)
        elif extra1 == 'hs14':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 07월 11일)')
            embed.add_field(name='1. 새로운 기능', value='커뉴야 커맨드금지기능 추가: 특정 채널에서 사용할 수 있는 커맨드에 제한을 둘 수 있음\n`커뉴야 오목`에도 '
                                                    '목찌빠처럼 점수제도 추가, 등급 제도나 리더보드는 점수 분포 보고 추후 결정 예정', inline=False)
            embed.add_field(name='2. 개선된 기능', value='들낙퇴치같은 일부 관리 명령어에서 설정 말고 조회는 관리자권한이 없더라도 가능\n메세지 삭제, 메세지 수정 로그에서 '
                                                    '어느 채널에서 해당 일이 일어났는지도 표시\n코인 중 `화력코인`의 변동성을 증가\n데이터베이스 관련되어 최적화 '
                                                    '진행 -> 일부 커맨드 처리 속도 향상\n새로운 도전과제 추가 (앞으로 새 도전과제는 매 패치마다 추가될 예정이므로 '
                                                    '추후 이곳에는 기록하지 않겠음)', inline=False)
            embed.add_field(name='3. 수정된 버그', value='몇몇 오탈자나 도움말에 빼먹은 내용을 다시 추가\n코인 리셋이나 공식서버의 실시간 리더보드가 멈추던 현상 '
                                                    '해결\n누군가가 나갈 때 해당 메세지가 보내져야 할 채널에 메세지가 보내지지 않던 오류 수정\n오목에서 `현재 '
                                                    '차례`의 유저가 반대로 표시되던 버그 수정', inline=False)
            embed.add_field(name='4. 공식서버 전용 패치', value='"신고함"채널의 작동 시작\n피겅한 내용이긴 한데 이 내용은 나도 잘 모르겠으니 알아서 확인해 '
                                                        '보셈\n"커뉴봇 베타 실험실"채널에서 봇이 서버에 들어가는 로그가 표시 안되던 버그를 수정',
                            inline=False)
            embed.set_footer(text='이전 업데이트 hs13\n다음 업데이트 hs15')
            await ctx.send(embed=embed)
        elif extra1 == 'hs13':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 06월 16일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 도전과제 목록` 기능 추가: 도전과제들의 목록을 볼 수 있음\n새로운 도전과제 및 이스터에그 추가', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 강화`에서 한 번에 강화할 수 있는 아이템 개수를 공식서버 돈으로 늘릴 수 있음, 그에 따라 강화목록, '
                                                    '파괴 명령어 코드도 수정\n`커뉴야 코인 시세`에서 가격을 컴마로 구분\n일부 명령어의 축약형 추가',
                            inline=False)
            embed.add_field(name='3. 수정된 버그', value='공식서버 레벨 달성하는 도전과제를 달성해도 메세지가 안 보내지던 오류 수정\n`커뉴야 도전과제 리더보드`명령어 사용 '
                                                    '시 나던 에러 수정', inline=False)
            embed.add_field(name='4. 공식서버 전용 패치', value='상점 아이템에 강화 슬롯 추가권 생성', inline=False)
            embed.set_footer(text='이전 업데이트 hs12\n다음 업데이트 hs14')
            await ctx.send(embed=embed)
        elif extra1 == 'hs12':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 06월 02일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 코인`명령어 수학 모듈 재구성 후 재출시\n`커뉴야 퀴즈 뮤트` 추가: 랜덤 주제로 문제를 풀 때 보고 '
                                                    '싶지 않은 주제 설정\n`커뉴야 퀴즈 목록` 추가: 주요 주제 목록 표시\n`커뉴야 슬로우모드` 추가: 채널 관리 '
                                                    '명령어\n`커뉴야 코인 룰렛`기능 추가: 코인으로 도박 가능\n`커뉴야 초대당경부` 추가: 초대할 때마다 '
                                                    '경험치부스트를 줄 수 있음\n`커뉴야 권한진단` 추가: 현재 권한에서 사용할 수 없는 명령어들을 진단\n`커뉴야 '
                                                    '파이값`명령어 추가\n도전 과제 시스템 추가, 프로필 명령어 리메이크: 봇의 다양한 명령어를 쓰면서 도전 과제를 '
                                                    '해금 가능 (자세한 도움말은 `커뉴야 도움말 도전과제` 및 `커뉴야 도움말 프로필`)', inline=False)
            embed.add_field(name='2. 개선된 기능', value='퀴즈를 틀렸을 때 신고하는 기능 개편\n어느 서버에서 사용됐는지가 중요하지 않은 일부 커맨드는 디엠에서도 사용 '
                                                    '가능\n`커뉴야 서버추천`에서 명령어가 실행되는 서버는 나오지 않음\n코인 시세 변동 주기가 10분으로 변경',
                            inline=False)
            embed.add_field(name='3. 수정된 버그', value='도움말 글자가 이상하게 표기되던 것을 수정\n랜덤채팅 매칭이 안되던 오류 수정\n화력코인 값 표기 오류 수정', inline=False)
            embed.set_footer(text='이전 업데이트 hs11\n다음 업데이트 hs13')
            await ctx.send(embed=embed)
        elif extra1 == 'hs11':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 05월 20일)')
            embed.add_field(name='1. 새로운 기능', value='로그 기능 추가 - 멤버가 오고가는, 메세지가 수정되고 삭제되는, 멤버가 닉변하거나 멤버 역할이 바뀌는 것만 지원, '
                                                    '다른 것들은 추후 업데이트 예정\n`커뉴야 코인` 명령어 추가 및 베타 시작 - 자세한 도움말은 `커뉴야 도움 '
                                                    '코인`', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 오목`에서 어떠한 금수도 없는 규칙인 자유룰 추가 - 4500번~5999번방에서 이용 가능\n몇 가지 '
                                                    '명령어에 대한 축약형 추가\n들낙퇴치로 차단될 때 처벌내역에 쓰는 사유 개선, 차단된 시각도 표시\n퀴즈 출제 시 '
                                                    '주제를 같이 입력해도 인식\n10분마다 봇상메를 자동으로 업데이트\n`커뉴야 홍보`에서 초대링크 판별 알고리즘을 '
                                                    '개선', inline=False)
            embed.add_field(name='3. 수정된 버그', value='`커뉴야 기원목록 서버`에서 닉네임이 아닌 숫자가 뜨던 오류 수정\n사람이 나갈 때 초대한 사람이 커뉴봇이라고 뜨던 '
                                                    '오류 수정\n계정정보 명령어에서 True나 False라고 보내던 버그 수정\n출석체크 시 오늘의 1등이 이상하게 '
                                                    '표시되던 버그 수정', inline=False)
            embed.set_footer(text='이전 업데이트 hs10\n다음 업데이트 hs12')
            await ctx.send(embed=embed)
        elif extra1 == 'hs10':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 05월 05일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 오목 관전` 기능 추가: 커뉴야 오목 관전 (방번호)로 방번호 방에서 진행 중인 게임을 관전 가능', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 오목`에서 게임 중 UI 수정', inline=False)
            embed.add_field(name='3. 수정된 버그', value='레벨 시스템에서 나던 오류 수정, 커뉴야 오목에서 착수할 수 끝에 ""이라는 문자가 붙어있으면 봇이 뻗던 오류를 수정', inline=False)
            embed.set_footer(text='이전 업데이트 hs9\n다음 업데이트 hs11')
            await ctx.send(embed=embed)
        elif extra1 == 'hs9':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 05월 01일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 오목` 기능 추가: 자세한 내용은 `커뉴야 오목`명령어 실행을 통해 확인', inline=False)
            embed.add_field(name='2. 개선된 기능', value='~~`커뉴야 레벨`명령어에서 1등이 아니라면 다음 등수까지 더 필요한 경험치도 표시~~없음', inline=False)
            embed.add_field(name='3. 수정된 버그', value='`커뉴야 뮤트`명령어를 처음 실행할 때 나던 오류 수정', inline=False)
            embed.add_field(name='4. 공식서버 전용 패치', value='없음 :zany_face:', inline=False)
            embed.set_footer(text='이전 업데이트 hs8\n다음 업데이트 hs10')
            await ctx.send(embed=embed)
        elif extra1 == 'hs8':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 04월 29일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 추천인`기능 추가 (서버에 봇을 데려갈 때 누가 추천했는지 입력하는 기능)\n`커뉴야 봇메세지무시`시스템 '
                                                    '추가 (숫자채널, 세로채널 등에서 봇들이 보낸 메세지는 삭제하지 않도록 하는 기능)', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 랜덤숫자` 명령어를 `커뉴야 주사위`로도 가능하게 변경, 숫자를 두 개 설정해서 최소, 최대값을 설정하는 '
                                                    '것도 가능하게 변경\n실시간 묵찌빠가 끝났을 때 점수 차이가 많이 나도 얻거나 잃는 점수가 50에 가까워지도록 '
                                                    '변경', inline=False)
            embed.add_field(name='3. 수정된 버그', value='사람이 들어올 때 가끔 초대 횟수가 올라가지 않던 오류 수정\n서버에서 누군가가 나갈 때 메세지가 전송되지 않던 '
                                                    '오류 수정\n`커뉴야 강화`명령어 처음 실행 시 나던 오류 수정\n들낙 퇴치 시스템에서 "a분 b초만에 나감" '
                                                    '부분이 이상하게 출력되던 오류 수정', inline=False)
            embed.add_field(name='4. 공식서버 전용 패치', value='`커뉴야 잡키` 보상 버프\n`커뉴야 출첵`시 주는 돈을 좀 더 랜덤하게 변경', inline=False)
            embed.set_footer(text='이전 업데이트 hs7\n다음 업데이트 hs9')
            await ctx.send(embed=embed)
        elif extra1 == 'hs7':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 04월 20일)')
            embed.add_field(name='1. 새로운 기능', value='대화 명령어 다수 추가\n`커뉴야 퀴즈 주제` 명령어 추가: 주제별 문제 수를 알 수 있음\n(공식서버 전용) '
                                                    '원하는 사람 채널 뮤트권 추가', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 묵찌빠` 에서 점수가 좀 더 많이 차이나도 매칭이 가능하도록 변경\n세로채널에서 커스텀 이모지 하나만 '
                                                    '보내는 것도 메세지를 삭제하지 않음\n`커뉴야 퀴즈 풀기`에서 문제 수가 너무 적은 주제는 고를 수 없도록 '
                                                    '변경\n(공식서버 전용) 상점 아이템들의 가격들을 전반적으로 변경', inline=False)
            embed.add_field(name='3. 수정된 버그', value='출석체크 진행 시 가끔 2명의 등수가 똑같던 버그 수정, `커뉴야 골라`에서 아무것도 안 고르면 나던 에러를 '
                                                    '수정\n사용 권한이 없는 명령어에 대해서 더 이상 에러가 났다고 출력하지 않음\n`커뉴야 퀴즈 내점수` 명령어에서 '
                                                    '나던 에러 수정, 인터페이스를 고침', inline=False)
            embed.set_footer(text='이전 업데이트 hs6\n다음 업데이트 hs8')
            await ctx.send(embed=embed)
        elif extra1 == 'hs6':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 04월 06일)')
            embed.add_field(name='1. 새로운 기능', value='뮤트, 밴, 킥, 들낙퇴치 등을 기록하는 처벌 로그 추가\n레벨업문구, 들어오거나 나갈 때 문구를 서버별로 다르게 '
                                                    '설정하는 기능 추가\n`커뉴야 랜덤채팅 만나지않기`로 특정 사용자를 만나지 않도록 하는 기능 추가\n특정한 '
                                                    '조건에서만 발동되는 대화 명령어들을 추가', inline=False)
            embed.add_field(name='2. 개선된 기능', value="`커뉴야 퀴즈 풀기`에서 주제를 고를 수 있게 변경\n`커뉴야 묵찌빠` 에서 '묵', '찌', '빠' 말고 "
                                                    "'ㅁㅁㅁㅁ' 처럼 초성만 도배해도 인식\n같이 반응해주기 시스템(ㅋ -> ㅋㅋ 등)을 선택사항으로 변경\n(공식서버 "
                                                    "전용) `커뉴야 우주탐험` 패치\n실행할 권한이 없는 관리 명령어에 대해서 에러가 나는 대신 권한이 없다고 "
                                                    "출력\n세로채널을 원래 채널으로 롤백시킬 수 있도록 변경\n`커뉴야 도움`에서 축약형도 인식하도록 변경 (개발자가 "
                                                    "바보라서 빠진 명령어 있을 수도 있음)", inline=False)
            embed.add_field(name='3. 수정된 버그', value='묵찌빠 관련 버그들을 수정\n다른 사람을 뮤트할 때 나던 에러 수정\n(공식서버 전용) 잡초키우기를 처음에 하면 나던 에러 수정\n(공식서버 전용) `커뉴야 구매`에서 아이템 이름을 인식하지 못하던 오류 수정\n`커뉴야 기원목록 서버`명령어 실행 시 기원이 없으면 에러 나던 것을 수정\n모바일에서 `커뉴야 올려`명령어 실행 시 조금 올라가던 오류 롤백', inline=False)
            embed.set_footer(text='이전 업데이트 hs5\n다음 업데이트 hs7')
            await ctx.send(embed=embed)
        elif extra1 == 'hs5':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 03월 22일)')
            embed.add_field(name='1. 새로운 기능', value='칭호 역할 시스템 추가, 자세한 내용은 `커뉴야 도움 칭호`로 확인\n문의 사항이 있을 때 `커뉴야 문의` 명령어 '
                                                    '추가\n아무 쓸모없는 `커뉴야 입력해` 명령어 추가\n`커뉴야 뮤트`, `커뉴야 추방`, `커뉴야 차단`등 관리 '
                                                    '명령어 추가\n`커뉴야 서버시간`명령어 추가\n초대 관리 기능 추가: 누가 몇 명을 데려왔는가 등을 관리 (자세한 '
                                                    '정보는 `커뉴야 도움 초대횟수`)', inline=False)
            embed.add_field(name='2. 개선된 기능', value='`커뉴야 도움 (명령어이름)` 으로도 자세한 명령어 도움말을 확인할 수 있도록 변경\n`커뉴야 기원목록` 명령어에서 '
                                                    '`커뉴야 기원목록`이라고만 쳐도 전체 기원 목록이 표시되도록 변경\n`커뉴야 퀴즈 출제`명령어에서 퀴즈 정답을 '
                                                    '말했을 때 그 메세지를 삭제하도록 변경\n`커뉴야 퀴즈 풀기`명령어에서 틀리면 잃는 점수의 공식을 변경\n`커뉴야 '
                                                    '이름색역할 수정`추가\n`커뉴야 출첵`에서 임베드에 알면 좋은 팁을 출력\n들낙퇴치 UI 개선\n퀴즈를 풀 때 '
                                                    '대소문자를 구별하지 않음\n`커뉴야 파괴`를 `커뉴야 강화삭제`로도 되도록 변경\n여러 명령어의 쿨타임 '
                                                    '변\n`커뉴야 랜덤채팅`에서 서버 홍보를 못하도록 변경\n(공식서버 전용)`커뉴야 잡초키우기`, '
                                                    '`커뉴야 우주탐험` 패치', inline=False)
            embed.add_field(name='3. 수정된 버그', value='출석체크에서 12시가 지났는데도 내일 다시 해 달라는 문구가 뜨는 문제를 아마도 수정(조금 두고봐야할듯)\n`커뉴야 '
                                                    '퀴즈` 등의 명령어 최초 실행 시 나던 에러를 수정\n`커뉴야 삭제`명령어 실행 시 나던 에러 수정\n`커뉴야 퀴즈 '
                                                    '풀기`사용시 가끔 나던 에러 수정\n(공식서버 전용) `커뉴야 구매`명령어 관련 문제 해결', inline=False)
            embed.set_footer(text='이전 업데이트 hs4\n다음 업데이트 hs6')
            await ctx.send(embed=embed)
        elif extra1 == 'hs4':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 03월 12일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 골라` 명령어 추가, `커뉴야 말해` 명령어 추가, `커뉴야 퀴즈 풀기` 명령어 추가', inline=False)
            embed.add_field(name='2. 개선된 기능', value='모든 명령어: 접두사를 `커뉴야` 대신 `ㅋ`으로 대체 가능\n`커뉴야 서버강화`를 `커뉴야 섭강`으로 줄일 수 '
                                                    '있도록 변경\n`커뉴야 공식서버`를 `커뉴야 공섭`으로 줄일 수 있도록 변경', inline=False)
            embed.add_field(name='3. 수정된 버그', value='(공식서버 전용) `커뉴야 잡초키우기` 에서 물을 줬는데 비료를 줬다고 표기되는 오류 수정\n`커뉴야 '
                                                    '공식서버`명령어에서 링크가 만료됐다고 뜨던 오류 수정', inline=False)
            embed.set_footer(text='이전 업데이트 hs3\n다음 업데이트 hs5')
            await ctx.send(embed=embed)
        elif extra1 == 'hs3':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 03월 09일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 명령어` 추가: 명령어별 자세한 도움말\n채널부스트 기능 추가: 경부의 채널 버전', inline=False)
            embed.add_field(name='2. 개선된 기능', value='들낙 퇴치 시스템에서 들어온 지 10분도 안 지나서 나가도 들낙으로 간주 차단, (공식서버 전용)`커뉴야 '
                                                    '잡초키우기` 게임 업데이트', inline=False)
            embed.add_field(name='3. 수정된 버그', value='(공식서버 전용) 돈 명령어 표기오류 수정', inline=False)
            embed.set_footer(text='이전 업데이트 hs2\n다음 업데이트 hs4')
            await ctx.send(embed=embed)
        elif extra1 == 'hs2':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 03월 08일)')
            embed.add_field(name='1. 새로운 기능', value='`커뉴야 서버사진` 명령어 추가: 서버의 아이콘을 보여주는 명령어\n(공식서버 전용) 거울수 알림 추가: '
                                                    '숫자채널에서 센 숫자가 거울수에 임박했을 때 자동으로 알림을 줌', inline=False)
            embed.add_field(name='2. 개선된 기능', value='일부 명령어들의 줄임말 버전을 추가 (혼동의 여지가 없는 줄임말은 건의해 주세요)', inline=False)
            embed.add_field(name='3. 수정된 버그', value='출석체크 버그 수정 시도 2트: 내일 다시 출석체크를 하라는 답이 와도 일단은 시간 값은 수집하도록 변경, '
                                                   '일시적으로 쿨타임 줄임', inline=False)
            embed.set_footer(text='이전 업데이트 hs1\n다음 업데이트 hs3')
            await ctx.send(embed=embed)
        elif extra1 == 'hs1':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 03월 06일)')
            embed.add_field(name='1. 새로운 기능', value='세로 채널 기능 추가(메세지당 한 글자씩만 입력 가능한 채널)', inline=False)
            embed.add_field(name='2. 개선된 기능', value='(공식서버 전용) 잡초키우기, 우주탐험 미니게임 각각 업데이트', inline=False)
            embed.add_field(name='3. 버그 수정', value='봇이 온 이후로 메세지를 하나도 안 보낸 사람이 서버에서 나갈 경우 에러가 나며 나갔다는 메세지가 출력되지 않던 오류 '
                                                   '수정\n(공식서버 전용) 잡초키우기, 우주탐험, 강화 명령어를 처음 실행할 때 나는 에러 수정\n출석체크 명령어 오류'
                                                   ' 수정 시도 시작 (출석체크 시 시간을 내부에 기록함)', inline=False)
            embed.set_footer(text='이전 업데이트 ms10\n다음 업데이트 hs2')
            await ctx.send(embed=embed)
        elif extra1 == 'ms10':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 02월 26일)')
            embed.add_field(name='1. 새로운 기능', value='1)`커뉴야 업다운` 미니게임 명령어 추가: 업다운 게임 진행 가능\n2) `커뉴야 강화` 리메이크 (이제부터 '
                                                    '아이템 이름을 지정할 수 있고, 강화 레벨이 하나씩만 오르지 않으며, 세 아이템까지 동시에 강화 가능)\n3) '
                                                    '`커뉴야 강화` 명령어의 유틸성 명령어인 `커뉴야 파괴`, `커뉴야 강화목록` 명령어 추가', inline=False)
            embed.add_field(name='2. 편의성 개선', value='1)사람을 타겟으로 하는 많은 명령어들과 기원 명령어에서 띄어쓰기가 있어도 인식하도록 개선\n2)(공식서버 전용) '
                                                    '`커뉴야 상점` 명령어에서 돈 이모지가 이상하게 표시되던 점을 수정', inline=False)
            embed.add_field(name='3. 버그 수정', value='커뉴야 선물 명령어에서 네라고 대답하지 않았는데도 선물이 완료되었다고 표시되던 버그 수정', inline=False)
            embed.set_footer(text='이전 업데이트 ms9\n다음 업데이트 hs1')
            await ctx.send(embed=embed)
        elif extra1 == 'ms9':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 02월 20일)')
            embed.add_field(name='업데이트', value='1.`커뉴야 출첵목록` 명령어 추가: 명령어 실행으로 누가 몇 등으로 출석체크 했는지 확인 가능\n2. 새로운 퀴즈 기능 '
                                               '추가: `커뉴야 퀴즈` 로 도움말을 볼 수 있음, 현재는 데이터량이 부족해 출제만 가능, 퀴즈가 쌓이면 푸는 기능도 추가할 '
                                               '예정\n3. (커뉴서버 전용) `커뉴야 잡초키우기` 버프: 잡초 레벨업 보상 상향, 잡초가 더욱 고르게 레벨이 올라감\n4. '
                                               '`커뉴야 레벨` 커맨드의 인터페이스 개선: 이제 현재 레벨에서 경험치를 몇% 정도 모았나가 표시됨\n5. `커뉴야 기원삭제` '
                                               '명령어 추가: 서버 관리자가 자신의 서버에 등록되어 있는 기원을 지울 수 있음\n6. `커뉴야 기원목록` 명령어 추가: '
                                               '`커뉴야 기원목록 <전체/서버>` 로 등록되어 있는 기원들의 목록을 볼 수 있음\n7. `커뉴야 기원` 명령어 패치: '
                                               '기원추가 명령어로 서버 내에서만 쓰는 기원이 아닌 기원에서는 부적절한 단어가 들어갔거나 너무 긴 기원은 설정할 수 '
                                               '없음\n8. `커뉴야 도움`, `커뉴야 관리` 명령어에서 신기능들을 반영')
            embed.set_footer(text='이전 업데이트 ms8\n다음 업데이트 ms10')
            await ctx.send(embed=embed)
        elif extra1 == 'ms8':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 02월 15일)')
            embed.add_field(name='업데이트', value='1.`커뉴야 출첵` 명령어가 봇이 꺼졌다 켜져도 출석체크 정보를 저장하도록 변경(지금 켜졌던 건 적용 안될거에요)\n2. '
                                               '커뉴야 이름색목록 명령어를 통해 보는 이름색이 색깔순으로 정렬됨')
            embed.set_footer(text='이전 업데이트 ms7\n다음 업데이트 ms9')
            await ctx.send(embed=embed)
        elif extra1 == 'ms7':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 02월 04일)')
            embed.add_field(name='업데이트', value='1. 커뉴야 우주탐험, 커뉴야 기원 명령어를 실행하면 났던 에러를 고침\n2. 랜덤채팅 기능 추가: `커뉴야 랜덤채팅` 또는 '
                                               '`커뉴야 랜챗`으로 이용 가능\n3. 홍보 기능 추가: 서버강화 레벨이 50 이상인 서버는 홍보 가능\n4. 관리 명령어 더 '
                                               '추가: `커뉴야 레벨업메시지 설정`, `커뉴야 환영메시지 설정`, `커뉴야 나갈때메시지 설정`\n5. 커뉴봇 설 기념 이벤트 '
                                               '진행! 커뉴봇을 널리 퍼트리자는 취지에서 연 이벤트로 서버 관리자가 `커뉴야 이벤트`를 입력해 참여')
            embed.set_footer(text='이전 업데이트 ms6\n다음 업데이트 ms8')
            await ctx.send(embed=embed)
        elif extra1 == 'ms6':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 01월 27일)')
            embed.add_field(name='업데이트', value='1. 2차 데이터베이스 안정화\n2. 잡초키우기, 우주탐험 미니게임을 커뉴서버에서만 실행할 수 있도록 변경\n3. 커뉴야 '
                                               '서버강화 명령어 에러 수정\n4. 커뉴봇 강화, 서버강화 명령어에 대한 리더보드도 추가\n5. ~~정말 오랜만의~~ 도움말 '
                                               '수정\n6. 들낙 퇴치 시스템을 선택적으로 켜고 끌 수 있도록 변경\n7. 출석체크 메커니즘 변경 - 출첵을 봇이 들어간 '
                                               '모든 서버의 사람들과 등수 공유')
            embed.set_footer(text='이전 업데이트 ms5\n다음 업데이트 ms7')
            await ctx.send(embed=embed)
        elif extra1 == 'ms5':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 01월 25일)')
            embed.add_field(name='업데이트', value='1. 각종 리더보드 추가! 잡초키우기, 우주탐험, 묵찌빠(멀티플레이어)의 리더보드를 추가했어요.\n2. 출첵 난이도 버프! '
                                               '이제 12시 직전에 도배하는 건 안 먹혀요.\n3. 멀티서버 준비 패치 #3 - 말투 통일, 서버에 사람들이 들어오거나 나갈 '
                                               '때 메세지 설정 가능, 레벨업 보상도 자동으로 관리 가능\n4. 데이터베이스 안정화! 이제 레벨 롤백되는 현상 없습니다')
            embed.set_footer(text='이전 업데이트 ms4\n다음 업데이트 ms6')
            await ctx.send(embed=embed)
        elif extra1 == 'ms4':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 01월 09일)')
            embed.add_field(name='업데이트', value='1. 우주탐험 미니게임 추가! 새로운 미니게임이 추가됐어요. 여태껏 없었던 보상도 여기엔 있으니 한번 해보세요!\n2. '
                                               '`커뉴야 내가나가면`명령어 업데이트! 이제 내 레벨에 따라서 답변이 달라져요.\n3. `커뉴야 프사` 명령어 업데이트! '
                                               '커뉴야 프사 (사람이름)뒤에 임베드, 링크 라는 말을 붙이면 프사를 임베드에 넣어서 보내거나 프사의 링크롤 보내요.\n4. '
                                               '서버강화 명령어 업데이트! 서버강화를 시도하면 에러가 나는 버그를 고치고 쿨타임을 줄였어요.')
            embed.set_footer(text='이전 업데이트 ms3\n다음 업데이트 ms5')
            await ctx.send(embed=embed)
        elif extra1 == 'ms3':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2021년 01월 05일)')
            embed.add_field(name='업데이트', value='1. 잡초키우기 게임 업데이트: 비료 가격이 감소했어.\n2. 묵찌빠 멀티플레이어 모드 추가: `커뉴야 묵찌빠 매칭`으로 '
                                               '다른 사람과 실시간으로 묵찌빠를 할 수 있게 됐어.\n3. 각종 버그 수정: 레벨업하기 직전에 다음 레벨까지 필요한 경험치가 '
                                               '0이나 마이너스로 표시되고 한 번 더 채팅을 쳐야 레벨업이 되던 버그가 없어졌어.')
            embed.set_footer(text='이전 업데이트 ms2\n다음 업데이트 ms4')
            await ctx.send(embed=embed)
        elif extra1 == 'ms2':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2020년 12월 30일)')
            embed.add_field(name='2021년 새해맞이 업데이트', value='1.커뉴야 잡초키우기 게임 업데이트\n2. 초대 역할에 대한 경험치 부스트 버프')
            embed.set_footer(text='이전 업데이트 ms1\n다음 업데이트 ms3')
            await ctx.send(embed=embed)
        elif extra1 == 'ms1':
            embed = Embed(color=0xffd6fe, title='커뉴봇 업데이트 (날짜: 2020년 12월 28일)')
            embed.add_field(name='2021년 새해맞이 업데이트', value='1. `커뉴야 프사` 명령어 부활! 오류가 고쳐져서 다시 프사 명령어를 쓸 수 있어.\n2. 새로운 게임 '
                                                          '추가! ~~3가지라고하긴애매하지만~~ 새로운 게임이 추가됐어. `커뉴야 도움`으로 확인해봐.\n3. '
                                                          '`커뉴야 명령어` 명령어 추가! 명령어들의 사용법을 알아볼 수 있어.\n4. 출석 보상 상향! 이제 출석 '
                                                          '보상을 더 많이 받아.\n5. `커뉴야 가위바위보` 명령어 추가! 커뉴봇과 가위바위보 게임을 '
                                                          '즐겨봐.\n6. <#743339107731767366>채널에서 틀린 숫자를 입력할 시 자동 삭제 기능 '
                                                          '추가! 이제 힘들게 :weary:반응 달 필요 없어.\n7. `커뉴야 가위바위보`와 `커뉴야 묵찌빠` '
                                                          '명령어 추가! 커뉴봇과 게임을 즐겨봐.')
            embed.set_footer(text='이전 업데이트 initial_release\n다음 업데이트 ms2')
            await ctx.send(embed=embed)
        elif extra1 == 'initial_release':
            embed = Embed(color=0xffd6fe, title='커뉴봇 뼈대 완성 (날짜 2020년 11월 28일)')
            embed.set_footer(text='11월은 커뉴봇 개발 기간이어서 이 동안 수많은 변화가 있었겠지만 `커뉴야 업데이트`는 이것보다 더 나중에 나왔대요. 비록 이 기간 동안 업데이트 '
                                  '내용을 정확히 알 수는 없지만 이날부터 커뉴봇이 레벨 시스템을 관리하기 시작했어요.\n이전 업데이트 birth\n다음 업데이트 ms1')
            await ctx.send(embed=embed)
        elif extra1 == 'birth':
            embed = Embed(color=0xffd6fe, title='커뉴봇 출시 (날짜 2020년 11월 1일)')
            embed.set_footer(text='이날은 커뉴봇이 처음으로 출시된 날이에요! 출시일을 기념하기 위해 업데이트는 아니지만 이곳에 실어 두었어요.\n이전 업데이트 없음\n다음 업데이트 '
                                  'initial_release')
            await ctx.send(embed=embed)
        elif extra1:
            await ctx.send(embed=Embed(color=0xffd6fe, title='커뉴봇 업데이트 명령어 도움', description='`커뉴야 업데이트`: 최근에 이루어진 업데이트 정보를 알려줍니다.\n`커뉴야 업데이트 (기능)`: yonsei1 또는 그 이후 버전에 대해 특정한 기능이 버전별로 어떻게 업데이트됐는지를 보여줍니다.\n`커뉴야 업데이트 (버전)`: 최신 버전이 아닌 버전을 같이 입력한다면 해당 버전의 업데이트 내용을 알려줍니다. 24_seol보다 먼저 이루어진 업데이트의 버전명은 임의로 부여되었으며 일부 버전의 경우 해당 업데이트 출시 당시 공지가 대신 출력되기도 합니다 (당시 업데이트 명령어 출력 결과가 유실된 경우). 또한 첫 출시 때의 버전명은 birth로 설정해 두었습니다.\n언급된 값이 아닌 값이 입력된다면, 이 도움말을 표시합니다.'))

    @command(name="없뎃")
    async def no_update(self, ctx):
        await ctx.send("없뎃: since 2024-3-18")

    @command(name="나중업뎃")
    async def future_updates(self, ctx):
        l = grant_check("업뎃을 기대하시는 거에요?", ctx.author.id)
        if l == 1:
            await grant(ctx, "업뎃을 기대하시는 거에요?", "2024년이나 그 이후에 `커뉴야 나중업뎃` 명령어를 실행하세요.\n그런데, 업데이트를 원하시면 새로운 기능을 제안해 보시는 게 어떨까요?")
        await ctx.send("예정된 나중 업데이트 내용(바로 다음 업데이트라는 보장은 없음)\n뀨 상점에 `클오클 클랜 운영 도우미`, `레벨역할 최대치 증가`, `초대역할 기능 해금` 추가\nCOC 운영 알고리즘에서 클랜 컨텐츠만을 반영하면 중복값이 발생하므로 공격 성공 횟수나 홀 대비 트로피 개수 등으로 총점을 약간씩 변경\n고질병이던 쿨타임 이슈 해결\n`커뉴야 투표`, `커뉴야 계산` 명령어 추가")

    @command(name="정지먹여")
    async def addban_command(self, ctx, target: Optional[int]):
        if ctx.author.id != 724496900920705045: return
        if not target:
            await ctx.send("지정된 멤버가 없어요.")

        else:
            self.bot.banlist.extend([target])
            await ctx.send("정지를 성공적으로 먹였어요.")

    @command(name="정지풀어")
    async def delban_command(self, ctx, targets: Greedy[Member]):
        if ctx.author.id != 724496900920705045: return
        if not targets:
            await ctx.send("지정된 멤버가 없어요.")

        else:
            for target in targets:
                self.bot.banlist.remove(target.id)
            await ctx.send("정지를 성공적으로 풀었어요.")

    @command(name='문의')
    async def moon_doctor(self, ctx):
        embed = Embed(color=0xffd6fe, title="문의하기 전 주의사항", description="문의하기 전, 다음 사항들을 충분히 숙지하시고 문의해 주세요:\n0. 공식서버에서 "
                                                                       "문의하지 않는 한 답변은 당신의 DM으로 옵니다. 적어도 한 개의 서버에서 커뉴봇과 "
                                                                       "같이 있어야 하며 디엠이 켜져 있어야 합니다.문의에 대한 답변이 오지 않는 것은 "
                                                                       "개발자 책임이 아닙니다.\n\n1. 민감한 내용이라면 DM에서 문의하는 것을 "
                                                                       "권장합니다.\n\n2. 먼저 권한 설정이 제대로 되었는지 확인하고 `커뉴야 "
                                                                       "권한진단`명령어로 설정해놓고 권한을 안 준 건 아닌지 생각해봅니다.\n\n3. 문의는 "
                                                                       "보통 공식서버에서 하는 문의가 답변속도가 더 빠릅니다. 공식서버는 들낙퇴치가 켜져 "
                                                                       "있기 때문에 들낙할거면 여기서 하는 게 낫지만 공식서버에 가서 하는 것을 "
                                                                       "권장드립니다.\n\n4. 공식서버 차단 해제 문의나 봇 정지 해제 문의는 아는 사람 중 "
                                                                       "공식서버에 있는 사람에게 먼저 물어보고 문의해야 합니다. 어지간한 로그는 다 그곳에 "
                                                                       "써있습니다.\n\n5. 봇이 응답을 안 하는 현상 등은 점검 중이어서 그럴 때가 "
                                                                       "다수입니다. 그런 현상이 발생하면 우선 봇공지에 해당 내용이 있었나 보고 그 다음 "
                                                                       "문의해야 합니다.\n\n6. 지금 문의를 취소하려면 `취소`를 입력하세요")
        embed.set_footer(text="답변은 개발자가 바쁘거나 문의가 너무 복잡하지 않으면 하루 안에는 옵니다. 그동안은 0번 항목을 주의해주세요")
        await ctx.send(embed=embed)
        try:
            nae_yong = await self.bot.wait_for(
            "message",
            timeout=600,
            check=lambda message: message.author == ctx.author and ctx.channel == message.channel
            )
        except asyncio.TimeoutError:
            await ctx.send("문의를 취소했어요.")
            return
        if nae_yong.content == "취소":
            await ctx.send("문의를 취소했어요.")
            return
        await ctx.send("문의를 완료했어요!")
        await self.bot.get_channel(822461129384525824).send(f"{str(ctx.author)} (아이디 {ctx.author.id}의 문의: {nae_yong.content}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")

    @Cog.listener()
    async def on_guild_join(self, guild):
        humans = set(filter(lambda m: not m.bot, guild.members))
        if len(humans) <= 3:
            for g in self.bot.guilds:
                hc = set(filter(lambda m: not m.bot, g.members))
                if len(humans & hc) >= 2:
                    if guild.system_channel is not None:
                        try:
                            await guild.system_channel.send("커뉴봇은 과하게 많은 수의 개인용 서버에 들어오는 것을 원치 않습니다. 다른 서버들도 봇을 자유롭게 사용할 수 있도록 협조 바랍니다.")
                        except:
                            pass
                    await self.bot.get_channel(817335216133111838).send(f"{guild.name}: 과한 개인 서버로 판별되어 자동으로 나감")
                    await guild.leave()
                    return
        await self.bot.get_channel(817335216133111838).send(f"새로운 서버에 들어감\n이름: {guild.name}, 멤버수: {guild.member_count}")
        if guild.system_channel is not None:
            try:
                embed = Embed(color=0xffd6fe, title="커뉴봇을 서버에 데려와 주셔서 감사드려요!",
                          description="** **\n\t\n커뉴봇은 레벨 기능, 관리 기능, 게임 기능 등을 가진 종합 봇이에요!\n\t\n`커뉴야 도움` 명령어로 봇의 사용 방법을 알아보실 수 있어요.\n\t\n커뉴봇은 기능들에 있어서 자유도가 높으니 원하시는 대로 봇을 활용해 보세요!")
                await guild.system_channel.send(embed=embed)
            except:
                pass
        db.execute("INSERT INTO guilds (GuildID) VALUES (?)", guild.id)
        try:
            guild_invites = await guild.invites()
        except errors.Forbidden:
            db.commit()
            return
        for invite in guild_invites:
            db.execute("INSERT INTO invites (invite_code, uses, guildid) VALUES (?, ?, ?)", invite.code, invite.uses,
                       guild.id)
        db.commit()

    @Cog.listener()
    async def on_guild_remove(self, guild):
        db.execute("DELETE FROM guilds WHERE GuildID = ?", guild.id)
        db.execute("DELETE FROM invites WHERE guildid = ?", guild.id)
        db.execute("DELETE FROM exp WHERE GUildID = ?", guild.id)
        db.execute("DELETE FROM mutes WHERE GuildID = ?", guild.id)
        db.execute("DELETE FROM roles WHERE GuildID = ?", guild.id)
        db.commit()
        await self.bot.get_channel(817335216133111838).send(
            f"있던 서버가 삭제되거나 봇이 추방됨\n이름: {guild.name}, 멤버수: {guild.member_count}")


def setup(bot):
    bot.add_cog(Misc(bot))