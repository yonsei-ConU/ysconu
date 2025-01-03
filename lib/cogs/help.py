from typing import Optional
from discord import Embed
from discord.ext.commands import Cog, command
from discord.app_commands import command as slash, choices, Choice
from ..utils.send import send


# -*- coding: utf-8 -*-

class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    @command(name="도움", aliases=["도움말", "도와줘", "명령어"])
    async def help(self, ctx, command_to_know: Optional[str] = "12430987"):
        embed = Embed(color=0xffd6fe)
        if command_to_know == "공지":
            embed.add_field(name="명렁어 도움: 공지",
                            value="봇 개발자가 최근에 전송한 공지를 보여주는 명령어에요. 봇이 켜진 후 공지가 보내지지 않았다면 에러가 나지만 그럴 일은 없을 거에요.\n사용법: `커뉴야 공지`")
        elif command_to_know in ["업데이트", "업뎃"]:
            embed.add_field(name="명령어 도움: 업데이트",
                            value="`커뉴야 업데이트`: 최근에 이루어진 업데이트 정보를 알려줍니다.\n`커뉴야 업데이트 (기능)`: yonsei1 또는 그 이후 버전에 대해 특정한 기능이 버전별로 어떻게 업데이트됐는지를 보여줍니다.\n`커뉴야 업데이트 (버전)`: 최신 버전이 아닌 버전을 같이 입력한다면 해당 버전의 업데이트 내용을 알려줍니다. 24_seol보다 먼저 이루어진 업데이트의 버전명은 임의로 부여되었으며 일부 버전의 경우 해당 업데이트 출시 당시 공지가 대신 출력되기도 합니다 (당시 업데이트 명령어 출력 결과가 유실된 경우). 또한 첫 출시 때의 버전명은 birth로 설정해 두었습니다.\n언급된 값이 아닌 값이 입력된다면, 이 도움말을 표시합니다.'")
        elif command_to_know == '나중업뎃':
            embed.add_field(name='명령어 도움: 나중업뎃', value='개발자가 나중에 업데이트하려고 하는 사항을 보여 주는 명령어에요.\n사용법: `커뉴야 나중업뎃`')
        elif command_to_know in ["레벨", "렙"]:
            embed.add_field(name="명령어 도움: 레벨",
                            value="서버 안에서의 레벨을 보여 주는 명령어에요. 레벨 명령어 뒤에 사람 이름을 덧붙이면 다른 사람의 레벨도 확인할 수 있어요.\n사용법: `커뉴야 레벨 <사람>`")
        elif command_to_know in ["경험치부스트", "경부"]:
            embed.add_field(name="명령어 도움: 경부",
                            value="서버 안에서 현재 적용되고 있는 경험치 부스트를 보여주는 명령어에요. 기본값은 1이에요.\n사용법: `커뉴야 경부 <사람>")
        elif command_to_know in ["리더보드", "레벨순위"]:
            embed.add_field(name="명령어 도움: 리더보드",
                            value="다양한 기능들에 대한 리더보드를 보는 명령어에요.\n`커뉴야 리더보드`: 서버 안의 모든 사람들의 레벨과 경험치를 높은 순으로 보여줍니다.. 이모지로 반응해서 페이지를 넘길 수 있습니다.\n`커뉴야 리더보드 돈`: 공식서버 안에서만, 가진 돈의 순위를 보여줍니다.\n`커뉴야 리더보드 <잡초키우기/우주탐험/묵찌빠/서버강화/경부/퀴즈/오목/도전과제>`: 각각에 기준에 대해 순위를 출력합니다.")
        elif command_to_know in ["도움", "도움말", "도와줘"]:
            embed.add_field(name="명령어 도움: 도움",
                            value="종합적인 봇 도움말을 출력하는 명령어에요. 관리 명령어는 너무 많아 다른 명령어로 분리했어요.\n사용법: `커뉴야 도움`")
        elif command_to_know == "관리":
            embed.add_field(name="명령어 도움: 관리", value="관리자 분들이 사용하면 좋은 명령어들만 모아 놓은 목록을 출력하는 명령어에요.\n사용법: `커뉴야 관리`")
        elif command_to_know == "운빨테스트":
            embed.add_field(name="명령어 도움: 운빨테스트",
                            value="말 그래도 운빨을 테스트해주는 명령어에요. 10%, 1%, 0,1%, 0,01% 확률에 당첨된다면 n% 확률에 당첨되셨네요! 라고 출력하고 아니면 평범한 운빨이라고 출력해요.\n사용법: `커뉴야 운빨테스트`")
        elif command_to_know == "강화":
            embed.add_field(name="명령어 도움: 강화",
                            value="원하는 아이템을 강화시켜주는 명령어에요. 기본적으로는 `커뉴야 강화 아이템이름` 으로 강화할 수 있어요. (아이템은 한 번에 3개까지만 강화 가능해요!)\n`커뉴야 강화 아이템이름`: 원하는 아이템을 강화해요. 확률에 따라 레벨이 오르거나 내려요.\n`커뉴야 강화목록`: 현재 자신의 아이템들과 레벨을 볼 수 있어요.\n`커뉴야 파괴`: `커뉴야 파괴 아이템이름` 으로 자기가 강화 중인 아이템을 파괴할 수 있어요. `커뉴야 강화삭제`로도 사용할 수 있는 명령어에요.")
        elif command_to_know in ["서버강화", "섭강"]:
            embed.add_field(name="명령어 도움: 서버강화",
                            value="서버별로 진행되는 게임이에요! `커뉴야 서버강화`를 입력하면 확률에 따라 서버 레벨이 올라가요. 50레벨이 넘어간다면 자기 서버를 홍보할 수도 있어요!\n`커뉴야 서버강화`: 서버 강화를 시도해요.\n`커뉴야 서버강화 리더보드`: 서버강화를 한 적이 있는 서버들의 강화 레벨 랭킹을 출력해요.\n`커뉴야 홍보`: (관리자만 사용할 수 있어요!) 서버강화 레벨이 50이 넘었다면 `커뉴야 홍보`로 여러분의 서버를 홍보하실 수 있어요. 서버강화 레벨이 더 높아지면 더 긴 홍보글을 작성할 수 있어요.")
        elif command_to_know in ["가위바위보", "가바보"]:
            embed.add_field(name="명령어 도움: 가위바위보",
                            value="봇과 가위바위보를 하는 명령어에요. `커뉴야 가바보` 로 줄일 수 있어요. `커뉴야 가위바위보 (가위/바위/보)` 로 봇과 가위바위보를 해보세요.")
        elif command_to_know in ["묵", "묵찌빠"]:
            embed.add_field(name="명령어 도움: 묵찌빠",
                            value="봇 또는 다른 사람과 묵찌빠를 할 수 있어요. `커뉴야 묵`으로 줄일 수 있어요.\n`커뉴야 묵찌빠 (묵/찌/빠)`: 봇과 묵찌빠를 진행해요.\n`커뉴야 묵찌빠 매칭`: 실시간 대전 매칭을 잡아요. 봇과의 DM으로 하는 기능이에요!\n`커뉴야 묵찌빠 매칭취소`: 잡는 중인 매칭 대기열에서 빠져나와요.\n`커뉴야 묵찌빠 티어`: 현재 자신의 MMR과 티어를 확인해요.\n`커뉴야 묵찌빠 리더보드`: `커뉴야 묵찌빠 리더보드 (페이지)`로 점수 순위를 출력해요. 한 페이지당 10명씩 나와요.")
        elif command_to_know in ["랜덤채팅", "랜챗"]:
            embed.add_field(name="명령어 도움: 랜덤채팅",
                            value="다른 사람과 실시간으로 랜덤채팅을 할 수 있어요. `커뉴야 랜챗`으로 줄일 수 있어요.\n`커뉴야 랜덤채팅 시작`: 랜덤채팅 대기열에 들어가요. 봇과의 DM으로 하는 기능이에요!\n`커뉴야 랜덤채팅 종료`: 진행 중인 랜덤채팅을 끝내거나 대기열에서 빠져나와요.\n`커뉴야 랜덤채팅 만나지않기`: 만나기 싫은 유저를 3명까지 등록해 만나지 않게 할 수 있어요. `커뉴야 랜덤채팅 만나지않기 <추가/삭제/조회>로 사용할 수 있어요.\n`커뉴야 랜덤채팅 도움`: 간략한 도움말을 보여줘요.")
        elif command_to_know == "기원":
            embed.add_field(name="명령어 도움: 기원",
                            value="꼭 이루었으면 하는 것을 기원할 수 있어요.\n`커뉴야 기원 (기원할항목)`: 기원하고 싶은 사항을 기원해요.\n`커뉴야 기원목록`: 기원들의 목록을 볼 수 있어요. 자세한 내용은 `커뉴야 도움 기원목록`으로 확인해 주세요.\n`커뉴야 기원추가`: (관리자만 사용할 수 있어요!) `커뉴야 기원추가 (대상)`으로 기원을 해서 서버 안에서만 보이는 기원을 추가해요. 하루에 한 번 기원을 할 때마다 기원 대상의 닉네임이 자동으로 변경돼요.\n`커뉴야 기원삭제`: (관리자만 사용할 수 있어요!) `커뉴야 기원삭제 (삭제할기원)` 으로 이 서버 안에서 관리되는 기원을 삭제할 수 있어요.")
        elif command_to_know == "서버추천":
            embed.add_field(name="명령어 도움: 서버추천",
                            value="들어갈만 한 서버를 추천해 주는 명령어에요. `커뉴야 홍보` 명령어로 글이 등록된 서버 중에서 보여줘요.\n사용법: `커뉴야 서버추천`")
        elif command_to_know == "퀴즈":
            embed.add_field(name="명령어 도움: 퀴즈",
                            value="! 𝓦𝓱𝔂 𝓷𝓸𝓽?/ 위너#8329 의 아이디어로 만들어진 퀴즈게임이에요.\n`커뉴야 퀴즈 도움`: 이 도움말을 표시해요.\n`커뉴야 퀴즈 출제`: 내고 싶은 퀴즈를 낼 수 있어요. 다만 이상한 퀴즈는 안 되기 때문에 등록까지 시간이 좀 걸릴 수 있어요.\n`커뉴야 퀴즈 풀기`: 누군가에 의해 출제된 퀴즈를 풀 수 있어요. 맞으면 점수를 얻고 틀리면 약간의 점수를 잃어요. 만약 `커뉴야 퀴즈 풀기`뒤에 원하는 주제를 입력하면 그 주제의 퀴즈를 풀 수 있어요.\n`커뉴야 퀴즈 내점수`: 자신의 퀴즈 점수를 조회할 수 있어요.\n`커뉴야 퀴즈 주제`: 선택한 주제에 문제가 몇 개나 있나를 확인할 수 있어요.\n`커뉴야 퀴즈 뮤트`: 특정한 주제의 문제는 안나오도록 설정할 수 있어요.\n`커뉴야 퀴즈 주제`: 한 주제의 문제수를 확인할 수 있어요.\n`커뉴야 퀴즈 목록`: 주요한 주제의 목록을 표시해요.")
        elif command_to_know == "업다운":
            embed.add_field(name="명령어 도움: 업다운",
                            value="업다운 게임을 할 수 있는 명령어에요. 숫자를 예측하면 그거보다 큰지 작은지 알려주면서 숫자가 몇인지 맞히는 그 게임 맞아요.\n사용법: `커뉴야 업다운 (숫자)`")
        elif command_to_know == "소개":
            embed.add_field(name="명령어 도움: 소개", value="봇의 소개를 보여주는 명령어에요.\n사용법: `커뉴야 소개`")
        elif command_to_know == "프사":
            embed.add_field(name="명령어 도움: 프사",
                            value="원하는 사람의 프사를 출력하는 명령어에요. 명령어를 실행하는 서버에 있는 사람만 대상이 될 수 있어요.\n사용법: `커뉴야 프사 (대상)`")
        elif command_to_know == "서버사진":
            embed.add_field(name="명령어 도움: 서버사진", value="명령어를 실행하는 서버의 서버 사진을 출력하는 명령어에요.\n사용법: `커뉴야 서버사진`")
        elif command_to_know in ["출석체크", "출첵", "ㅊㅊ"]:
            embed.add_field(name="명령어 도움: 출첵",
                            value="하루에 한 번 출석체크를 하는 명령어에요. `커뉴야 ㅊㅊ`으로 줄일 수 있어요.\n`커뉴야 출첵`: 출석체크를 할 수 있어요. 쓰는 건 자유지만 하루에 한 번만 답장해요.\n`커뉴야 출첵목록`: `커뉴야 출첵목록 (사람수)` 로 1등부터 (사람수) 등까지 오늘 출석체크를 한 사람들의 목록을 출력해요.")
        elif command_to_know == "이름색":
            embed.add_field(name="명령어 도움: 이름색",
                            value="서버 관리자가 지정한 이름색을 가질 수 있는 명령어에요.\n`커뉴야 이름색` 또는 `커뉴야 이름색목록`: 현재 서버에서 쓸 수 있는 이름색 역할의 목록을 표시해요.\n`커뉴야 이름색 (색깔)`: 이름색을 장착하거나 해제해요. 역할 순서 때문에 두 개 이상의 이름색을 동시에 장착하면 다른 하나를 해제해야 할 수도 있어요.\n`커뉴야 이름색역할`: (관리자만 사용할 수 있어요!) 이름색 역할들을 추가하거나 삭제해요. `커뉴야 명령어 이름색역할`로 알아보세요.")
        elif command_to_know == "돈":
            embed.add_field(name="명령어 도움: 돈", value="(공식 커뮤니티 전용 명령어에요!) 자기가 가지고 있는 돈을 보여주는 명령어에요.\n사용법: `커뉴야 돈`")
        elif command_to_know == "상점":
            embed.add_field(name="명령어 도움: 상점",
                            value="(공식 커뮤니티 전용 명령어에요!) 번 돈을 가지고 살 수 있는 아이템 목록을 보여주는 명령어에요.\n`커뉴야 상점`: 상점을 표시해요.\n`커뉴야 구매 (아이템이름)`: 아이템을 구매할 수 있어요. 축약할 수 있는 아이템들의 목록은 다음과 같아요:\n```프리미엄 티켓: 프\n원하는 사람 강제닉변권: 원\n강제 닉변 방지권: 강\n닉네임 변경권: 닉\n고속 레벨업 티켓: 고\n커스텀 커맨드 생성권: 커\n공지 홍보권: 공\n강화 슬롯 추가권: 슬```")
        elif command_to_know in ["잡초키우기", "잡키"]:
            embed.add_field(name="명령어 도움: 잡초키우기",
                            value="공식 커뮤니티 전용 명령어에요!) vecchio#9762의 아이디어로 만들어진 자기의 잡초를 키우는 게임 명령어에요. `커뉴야 잡키`로 줄일 수 있어요.\n`커뉴야 잡초키우기 가입`: 게임 진행을 위한 계정을 만들어요.\n`커뉴야 잡초키우기 도움`: 세부적으로 사용 가능한 명령어들의 목록을 출력해요.")
        elif command_to_know in ["우주탐험", "우탐"]:
            embed.add_field(name="명령어 도움: 우주탐험",
                            value="(공식 커뮤니티 전용 명령어에요!) 우주를 탐험하는 게임 명령어에요. `커뉴야 우탐`으로 줄일 수 있어요.\n`커뉴야 우주탐험 튜토리얼`: 우주탐험 튜토리얼을 출력해요. 굳이 이 명령어가 아니어도 `커뉴야 우주탐험`을 처음으로 친다면 튜토리얼이 나와요.\n`커뉴야 우주탐험 도움`: 세부적으로 사용 가능한 명령어들의 목록을 출력해요.")
        elif command_to_know in ["나는?", "프로필"]:
            embed.add_field(name="명령어 도움: 프로필",
                            value="도전과제와 관련된 프로필을 보여주는 명령어에요.\n`커뉴야 프로필`: 프로필을 표시해요.\n`커뉴야 소개작성`: 프로필에 쓸 소개글을 작성해요.\n도전과제와 관련된 정보는 `커뉴야 도움 도전과제`를 확인해보세요")
        elif command_to_know in ["경험치범위", "경범위"]:
            embed.add_field(name="명령어 도움: 경험치범위",
                            value="(관리자만 사용할 수 있어요!) 명령어가 실행되는 서버에서 받을 수 있는 경험치 범위를 관리하는 명령어에요.`커뉴야 경범위`로 줄일 수 있어요.\n`커뉴야 경험치범위 조회`: 현재 서버에서 받는 경험치의 범위를 출력해요.\n`커뉴야 경험치범위 설정`: 받을 수 있는 경험치의 범위를 설정해요. 최소 경험치가 최대보다 크거나 두 값 중 하나가 음수일 수 없어요.")
        elif command_to_know in ["경험치쿨타임", "경쿨"]:
            embed.add_field(name="명령어 도움: 경험치쿨타임",
                            value="(관리자만 사용할 수 있어요!) 명령어가 실행되는 서버에서 경험치를 얼마마다 한 번 받냐를 관리하는 명령어에요. `커뉴야 경쿨`으로 줄일 수 있어요.\n`커뉴야 경험치쿨타임 조회`: 현재 서버에서 경험치를 받을 수 있는 주기를 출력해요.\n`커뉴야 경험치쿨타임 설정`: 경험치를 받는 주기를 설정해요. 자연수로만 설정할 수 있어요.")
        elif command_to_know == "레벨업채널":
            embed.add_field(name="명령어 도움: 레벨업채널",
                            value="(관리자만 사용할 수 있어요!) 누군가의 레벨이 오르면 레벨업 메세지를 출력할 채널을 관리하는 명령어에요.\n`커뉴야 레벨업채널 조회`: 현재 서버에서 레벨업을 하면 어느 채널에 알림이 가는지를 확인해요.\n`커뉴야 레벨업채널 설정`: 레벨업을 하면 어느 채널에 알림을 보낼지 설정해요.\n`커뉴야 레벨업채널 초기화`: 레벨업 문구를 특정 채널이 아닌 메세지가 보내진 채널에 보내게 설정해요.\n`커뉴야 레벨업채널 끔`: 레벨업을 해도 아무 알림을 보내지 않도록 설정해요.")
        elif command_to_know == "경험치설정":
            embed.add_field(name="명령어 도움: 경험치설정",
                            value="(관리자만 사용할 수 있어요!) 원하는 사람의 경험치를 원하는 값으로 설정할 수 있는 명령어에요.\n사용법: `커뉴야 경험치설정 (대상) (경험치)` (마지막 경험치 항목은 입력하지 않아도 돼요)")
        elif command_to_know in ["경험치부스트설정", "경부설정"]:
            embed.add_field(name="명령어 도움: 경부설정",
                            value="(관리자만 사용할 수 있어요!) 원하는 사람의 경험치 부스트를 원하는 값으로 설정할 수 있는 명령어에요.\n사용법: `커뉴야 경부설정 (대상) (부스트)` (마지막 부스트 항목은 입력하지 않아도 돼요)")
        elif command_to_know == "숫자채널":
            embed.add_field(name="명령어 도움: 숫자채널",
                            value="(관리자만 사용할 수 있어요!) 명령어가 실행된 채널을 숫자 세기 채널로 지정할 수 있는 명령어에요. 그런 채널들에서는 사람들이 순서대로 숫자를 세고 틀린 숫자를 세면 지워져요.\n사용법: `커뉴야 숫자채널`")
        elif command_to_know == "환영채널":
            embed.add_field(name="명령어 도움: 환영채널",
                            value="(관리자만 사용할 수 있어요!) 서버에 들어오거나 나가는 사람이 있을 때 알림을 보내는 채널을 관리하는 명령어에요.\n`커뉴야 환영채널 조회`: 현재 오고가는 알림 채널이 어딘지 확인해요.\n`커뉴야 환영채널 설정`: 사람이 오고가면 어느 채널에 알림을 보낼지 설정해요.\n`커뉴야 환영채널 초기화`: 사람이 들어오거나 나가도 알림을 보내지 않도록 설정해요.")
        elif command_to_know == "공지채널":
            embed.add_field(name="명령어 도움: 공지채널",
                            value="(관리자만 사용할 수 있어요!) 봇이 공지를 보낼 때 받는 채널을 관리하는 명령어에요.\n`커뉴야 공지채널 조회`: 현재 봇 공지 알림 채널이 어딘지 확인해요.\n`커뉴야 공지채널 설정`: 봇 공지가 오면 어느 채널에 알림을 보낼지 설정해요.\n`커뉴야 공지채널 초기화`: 봇 공지가 있어도 알림을 보내지 않도록 설정해요.")
        elif command_to_know == "무규방":
            embed.add_field(name="명령어 도움: 무규방",
                            value="(관리자만 사용할 수 있어요!) 채널을 무규방으로 설정하는 명령어에요. 무규방으로 설정되면 `커뉴야 올려` 대화 명령어가 먹히지 않아요. ~~사실 19기능이 없는봇이라 쓸데없는 기능~~\n사용법: `커뉴야 무규방")
        elif command_to_know == "세로채널":
            embed.add_field(name="명령어 도움: 세로채널",
                            value="(관리자만 사용할 수 있어요!) 채널을 세로 채널로 지정할 수 있는 명령어에요. 그런 채널들에서는 두 글자 이상의 메세지는 전부 지워져요.\n`커뉴야 새로채널`: 해당 채널을 세로 채널로 지정해요.\n`커뉴야 세로채널 해제`: 세로채널으로 지정된 채널을 해제해요.")
        elif command_to_know == "들낙퇴치":
            embed.add_field(name="명령어 도움: 들낙퇴치",
                            value="(관리자만 사용할 수 있어요!) 명령어가 실행되는 서버에서 들낙러를 자동 밴 시키는 들낙 퇴치 시스템을 관리하는 명령어에요.\n`커뉴야 들낙퇴치 조회`: 현재 서버에서 들낙 퇴치 시스템이 켜져 있는지를 조회해요.\n`커뉴야 들낙퇴치 (켜/꺼)`: 들낙퇴치 시스템을 켜거나 꺼요.")
        elif command_to_know == "레벨역할":
            embed.add_field(name="명령어 도움: 레벨역할",
                            value="(관리자만 사용할 수 있어요!) 레벨업 보상으로 얻는 역할을 관리하는 명령어에요.\n`커뉴야 레벨역할 목록`: 이 서버에서 받을 수 있는 레벨업 보상 역할의 목록을 한 페이지당 10개 역할씩 표시해요.\n`커뉴야 레벨역할 추가`: 새로운 레벨업 보상 역할을 만들어요.\n`커뉴야 레벨역할 삭제`: 레벨업 보상으로 주던 역할을 더 이상 보상으로 주지 않아요. 역할 자체가 지워지지는 않아요.")
        elif command_to_know == "이름색역할":
            embed.add_field(name="명령어 도움: 이름색역할",
                            value="(관리자만 사용할 수 있어요!) 마음대로 장착하거나 해제할 수 있는 이름색 역할을 관리하는 명령어에요.\n`커뉴야 이름색역할 목록`: 가질 수 있는 이름색 역할의 목록을 표시해요.\n`커뉴야 이름색역할 추가`: 새로운 이름색 역할을 만들어요.\n`커뉴야 이름색역할 삭제`: 마음대로 장착할 수 있던 역할을 더 이상 그럴 수 없게 해요. 역할 자체가 지워지지는 않아요.\n`커뉴야 이름색역할 수정`: 봇이 인식하는 역할 이름을 변경해요.")
        elif command_to_know == "홍보":
            embed.add_field(name="명령어 도움: 홍보",
                            value="(관리자만 사용할 수 있어요!) `커뉴야 서버강화` 명령어로 서버 레벨이 50 이상이 되었다면 이 명령어를 사용해 자신의 서버를 홍보할 수 있는 명령어에요.\t사용법: `커뉴야 홍보`")
        elif command_to_know in ["채널부스트", "채부"]:
            embed.add_field(name="명령어 도움: 채널부스트",
                            value="(관리자만 사용할 수 있어요!) 이 채널에서 경험치를 얼마나 더 받나를 보여 주는 명령어에요. `커뉴야 채부`로 줄일 수 있어요.\n사용법: `커뉴야 채널부스트")
        elif command_to_know in ["채널부스트설정", "채부설정"]:
            embed.add_field(name="명령어 도움: 채널부스트설정",
                            value="(관리자만 사용할 수 있어요!) 채널의 채널부스트를 설정하는 명령어에요. `커뉴야 채부설정`으로 줄일 수 있어요.\n사용법: `커뉴야 채부설정 (부스트)`")
        elif command_to_know == "골라":
            embed.add_field(name="명령어 도움: 골라",
                            value="`커뉴야 골라 (단어1) (단어2) ...... `으로 커뉴봇이 여러 개의 단어들 중 하나를 랜덤으로 고르게 하는 명령어에요. 단어 개수에는 제한이 없지만 띄어쓰기를 하면 다른 단어로 인식되므로 한 단어를 쓸 거면 붙여서 써 주세요.")
        elif command_to_know == "말해":
            embed.add_field(name="명령어 도움: 말해", value="커뉴봇이 해당 채널에 메세지를 보내도록 하는 명령어에요. *핑은 못해요*\n사용법: `커뉴야 말해 (할말)`")
        elif command_to_know == "문의":
            embed.add_field(name="명령어 도움: 문의",
                            value="`커뉴야 문의 (문의할내용)으로`각종 사항들을 개발자에게 문의할 수 있어요. 답변이 DM으로 오기 때문에 DM 수신을 꼭 켜야 해요!")
        elif command_to_know == "뮤트":
            embed.add_field(name="명령어 도움: 뮤트",
                            value="(관리자만 사용할 수 있어요!)원하는 사람을 뮤트시킬 수 있어요. 아직은 기간 설정을 시간 단위로만 할 수 있지만 추후 패치로 분 등의 단위로도 뮤트할 수 있도록 바꿀 예정이에요. 만약 몇 시간을 뮤트할지 쓰지 않는다면 무기한으로 처리돼요.\n사용법: `커뉴야 뮤트 (사람이름) (시간)`")
        elif command_to_know == "언뮤트":
            embed.add_field(name="명령어 도움: 언뮤트", value="(관리자만 사용할 수 있어요!) 뮤트당했던 사람을 뮤트 해제시킬 수 있어요.\n사용법: `커뉴야 언뮤트 (사람)")
        elif command_to_know in ["추방", "킥"]:
            embed.add_field(name="명령어 도움: 추방",
                            value="(관리자만 사용할 수 있어요!) 원하는 사람을 추방시킬 수 있어요. `커뉴야 킥` 이나 `커뉴야 강퇴`로도 사용할 수 있는 명령어에요.\n사용법: `커뉴야 추방 (사람)`")
        elif command_to_know in ["차단", "밴"]:
            embed.add_field(name="명령어 도움: 차단",
                            value="(관리자만 사용할 수 있어요!) 원하는 사람을 차단시킬 수 있어요. `커뉴야 밴`으로도 사용할 수 있는 명령어에요.\n사용법: `커뉴야 차단 (사람)`")
        elif command_to_know == "서버시간":
            embed.add_field(name="명령어 도움: 서버시간", value="봇이 돌아가고 있는 서버 컴퓨터의 시간을 출력하는 명령어에요.\n사용법: `커뉴야 서버시간`")
        elif command_to_know == "초대횟수":
            embed.add_field(name="명령어 도움: 초대횟수", value="내가 이 서버에서 몇 명을 불렀는지 알려주는 명령어에요.\n사용법: `커뉴야 초대횟수`")
        elif command_to_know == "초대설정":
            embed.add_field(name="명령어 도움: 초대설정",
                            value="(관리자만 사용할 수 있어요!) 원하는 사람의 초대 횟수를 설정할 수 있는 명령어에요.\n사용법: `커뉴야 초대설정 (사람) (횟수)`")
        elif command_to_know == "처벌로그":
            embed.add_field(name="명령어 도움: 처벌로그",
                            value="(관리자만 사용할 수 있어요!) 뮤트, 밴, 킥 등을 기록하는 처벌 내역 채널을 설정하는 명령어에요.\n`커뉴야 처벌로그 조회`: 현재 서버의 처벌 로그를 조회해요.\n`커뉴야 처벌로그 설정`: 처벌 로그를 변경해요.")
        elif command_to_know == "레벨업문구":
            embed.add_field(name="명령어 도움: 레벨업문구",
                            value="(관리자만 사용할 수 있어요!) 누군가가 레벨업을 하면 레벨업채널에 표시되는 문구를 변경하는 명령어에요.\n`커뉴야 레벨업문구 조회`: 현재 서버의 레벨업 문구를 조회해요.\n`커뉴야 레벨업문구 설정`: 레벨업 문구를 변경해요.")
        elif command_to_know == "환영문구":
            embed.add_field(name="명령어 도움: 환영문구",
                            value="(관리자만 사용할 수 있어요!) 누군가가 서버에 들어오면 환영채널에 표시되는 문구를 변경하는 명령어에요.\n`커뉴야 환영문구 조회`: 현재 서버의 환영 문구를 조회해요.\n`커뉴야 환영문구 설정`: 환영 문구를 변경해요.")
        elif command_to_know == "나갈때문구":
            embed.add_field(name="명령어 도움: 나갈때문구",
                            value="(관리자만 사용할 수 있어요!) 누군가가 서버에서 나가면 환영채널에 표시되는 문구를 변경하는 명령어에요.\n`커뉴야 나갈때문구 조회`: 현재 서버의 나갈때 문구를 조회해요.\n`커뉴야 나갈때문구 설정`: 나갈때 문구를 변경해요.")
        elif command_to_know == "같이반응":
            embed.add_field(name="명령어 도움: 같이반응",
                            value="(관리자만 사용할 수 있어요!) 명령어가 실행되는 서버에서 `ㅋㅋ`등의 말에 커뉴봇이 반응하는 것을 관리하는 명령어에요.\n`커뉴야 같이반응 조회`: 현재 서버에서 같이 반응 시스템이 켜져 있는지를 조회해요.\n`커뉴야 같이반응 (켜/꺼)`: 같이 반응 시스템을 켜거나 꺼요.")
        elif command_to_know == "추천인":
            embed.add_field(name="명령어 도움: 추천인",
                            value="서버에 봇을 데려갈 때 누가 추천했는지를 관리하는 명령어에요. 많은 서버에 봇을 추천한 분이라면 가끔 개발자기 니트로를 뿌리기도 한다는 소문이 있어요.\n`커뉴야 추천인 발급`: 추천인 코드를 발급해요. 코드가 없는 사람만 발급할 수 있어요.\n`커뉴야 추천인 조회`: 자기가 만든 추천인 코드를 조회해요.\n`커뉴야 추천인 사용 (사용할 코드)`: 봇이 들어간 서버의 관리자가 받은 추천인 코드를 사용하는 명령어에요. 서버당 여러 번 쓸 수는 있지만 여러 번 카운트되진 않으니 한 번만 쓰세요.")
        elif command_to_know in ["봇메세지무시", "봇무시", "봇메시지무시"]:
            embed.add_field(name="명령어 도움: 봇메세지무시",
                            value="(관리자만 사용할 수 있어요!) 명령어가 실행되는 서버의 숫자채널, 세로채널 등 특수한 채널에서 봇이 보낸 메세지는 삭제하지 않도록 하는 기능이에요.\n`커뉴야 봇메세지무시 조회`: 현재 서버에서 봇메세지 무시 시스템이 켜져 있는지를 조회해요.\n`커뉴야 봇메세지무시 (켜/꺼)`: 봇메세지 무시 시스템을 켜거나 꺼요.")
        elif command_to_know in ["랜덤숫자", "주사위"]:
            embed.add_field(name="명령어 도움: 랜덤숫자",
                            value="원하는 범위에서 랜덤한 숫자를 보내는 명령어에요.\n`커뉴야 랜덤숫자 (수)`: 1부터 (수)까지의 수 중에서 아무거나 선택해요.\n`커뉴야 랜덤숫자 (수) (수)` 두 수 사이의 수 중에서 아무거나 선택해요.")
        elif command_to_know == "슬로우모드":
            embed.add_field(name="명령어 도움: 슬로우모드",
                            value="(관리자만 사용할 수 있어요!) 명령어가 실행되는 채널의 슬로우모드를 설정할 수 있어요.\n사용법: `커뉴야 슬로우모드 (초)`")
        elif command_to_know == "권한진단":
            embed.add_field(name="명령어 도움: 권한진단",
                            value="(관리자만 사용할 수 있어요!) 명령어가 실행되는 서버에서 봇 권한에 따라 사용할 수 없는 기능을 보여 줘요.\n사용법: `커뉴야 권한진단`")
        elif command_to_know == "초대당경부":
            embed.add_field(name="명령어 도움: 초대당경부",
                            value="(관리자만 사용할 수 있어요!) 명령어가 실행되는 서버에서 사람을 데려오면 주는 경험치부스트를 설정할 수 있어요.\n`커뉴야 초대당경부 설정 (%)`: 한 명을 데려오면 경험치 부스트를 얼마나 줄지 설정해요.")
        elif command_to_know in ["코인"]:
            embed.add_field(name="명령어 도움: 코인",
                            value="가상의 커뉴봇 코인 게임을 진행할 수 있어요.\n`커뉴야 코인`: 현재 가진 코인 정보를 표시해요.\n`커뉴야 코인 투자`: 공식서버 가입자라면 공식서버 돈과 환전하거나, 코인들에 투자할 수 있어요.\n`커뉴야 코인 시세`: 현재 코인들의 시세를 확인해요.\n`커뉴야 코인 룰렛`: 코인을 가지고 룰렛 도박을 할 수 있어요.\n`커뉴야 코인 블랙잭`: 코인을 가지고 블랙잭을 할 수 있어요.\n`커뉴야 코인 지원금`: 30분에 한 번씩 약간의 지원금을 받을 수 있어요.\n`커뉴야 코인 자산`: 현재 가지고 있는 모든 코인 가치를 포함한 자산을 확인해요.\n`커뉴야 코인 그래프`: 실험 중인 기능이에요. 현재는 최근 10일간의 화력코인 가격만 출력해요. **yonsei1 업데이트 이전의 화력코인 가격이 그래프에 포함됐다면 그 부분은 오차가 있을 수 있어요.**")
        elif command_to_know == "로그채널":
            embed.add_field(name="명령어 도움: 로그채널",
                            value="(관리자만 사용할 수 있어요!) 메세지 삭제 등의 로그를 출력하는 채널을 관리하는 명령어에요.\n`커뉴야 로그채널 조회`: 현재 서버 로그 채널이 어딘지 확인해요.\n`커뉴야 로그채널 설정`: 로그에 뜰 사건이 발생하면 어느 채널에 로그를 보낼지 설정해요.")
        elif command_to_know == "오목":
            embed.add_field(name="명령어 도움: 오목",
                            value="`커뉴야 오목 도움`: 이 도움말을 표시해요.\n`커뉴야 오목 규칙`: 커뉴봇 오목에 적용되는 규칙을 설명해요.\n`커뉴야 오목 테스트`: 지금 오목을 실행해도 되는지 판단해요.\n`커뉴야 오목 입장`: 오목 게임에 입장할 수 있어요. `커뉴야 오목 입장 (방번호)`로 입장해 주세요.\n`커뉴야 오목 목록`: 현재 비어 있지 않은 방들의 목록을 표시해요.\n`커뉴야 오목 관전`: `커뉴야 오목 관전 (방번호)` 로 게임 중인 방을 관전할 수 있어요.\n`커뉴야 오목 자동매칭`: 자동으로 오목 매칭을 잡을 수 있어요.")
        elif command_to_know == "도전과제":
            embed.add_field(name="명령어 도움: 도전과제",
                            value="봇 도전 과제를 확인할 수 있어요.\n`커뉴야 도전과제`: 현재 달성한 도전과제들을 표시해요.\n`커뉴야 도전과제 리더보드`: 사람들의 도전과제 개수 순위를 표시해요.\n`커뉴야 도전과제 장착 (자리) (도전과제)`: 달성한 도전과제 중에서 프로필에 장착할 도전과제를 골라요.\n`커뉴야 도전과제 목록`: 존재하는 도전과제들의 목록을 표시해요.\n`커뉴야 도전과제 설명 (도전과제)`: (도전과제) 에 대한 설명을 출력해요.\n`커뉴야 도전과제 페이지순`: `커뉴야 도전과제`와 효과가 같지만 도전과제들을 페이지순으로 정리해요.")
        elif command_to_know == "커맨드금지":
            embed.add_field(name="명령어 도움: 커맨드금지",
                            value="(관리자만 사용할 수 있어요!)특정 채널에서 사용하는 커맨드를 제한할 수 있는 명령어에요.\n`커뉴야 커맨드금지`: 현재 이 채널의 커맨드금지 레벨이 몇인지와 각 레벨이 무엇을 의미하는지를 확인해요.\n`커뉴야 커맨드금지 <레벨>`: 커맨드금지 레벨을 선택한 레벨로 바꿔요.")
        elif command_to_know == "닉홍보금지":
            embed.add_field(name="명령어 도움: 닉홍보금지",
                            value="(관리자만 사용할 수 있어요!)닉네임에 디스코드 서버 초대 링크가 들어가 있는 사람의 닉네임을 되돌려 놓는 시스템 명령어에요.\n`커뉴야 닉홍보금지`: 명령어가 실행되는 서버에서 닉네임 홍보가 금지되었는지 확인해요.\n`커뉴야 닉홍보금지 <켜/켬/꺼/끔>`: 닉네임 홍보 금지 시스템을 켜거나 꺼요.")
        elif command_to_know == "스펙":
            embed.add_field(name="명령어 도움: 스펙",
                            value="자신이 커뉴봇을 이때까지 어떻게 사용해 왔는지를 간략하게 보여 주는 명령어에요. 봇 도전과제 중 일부는 이 명령어를 실행할 때 달성 여부를 판단해요.\n`커뉴야 스펙`: 종합적인 스펙을 확인해요.\n`커뉴야 스펙 커맨드`: 많이 쓴 명령어 순서대로 25개가 무슨 명령어이고 몇 번 사용했는지를 확인해요.")
        elif command_to_know == "지분":
            embed.add_field(name="명령어 도움: 지분",
                            value="특정한 명령어에서 총 사용 횟수 대비 자신의 사용 횟수를 출력하는 명령어에요.\n사용법: `커뉴야 지분 (커맨드)`\n여기에 나온 커맨드는 커맨드의 축약형도 인식해요.")
        elif command_to_know == "타이머":
            embed.add_field(name="명령어 도움: 타이머",
                            value="설정한 시간 동안 타이머를 작동시키는 명령어에요. 예를 들어 `커뉴야 타이머 2분 30초 뀨우?!`라고 입력하면 2분 30초 후에 커뉴봇이 DM으로 `뀨우?`라고 보내요!")
        elif command_to_know == "스톱워치":
            embed.add_field(name="명령어 도움: 스톱워치",
                            value="스톱워치를 작동시키는 명령어에요.\n`커뉴야 스톱워치 시작`: 스톱워치 기록을 시작해요.\n`커뉴야 스톱워치 종료`: 돌아가고 있는 스톱워치가 있다면 그것을 종료해요.\n`커뉴야 스톱워치 기록`: 스톱워치가 돌아가는 도중 중간에 기록을 할 수 있어요.\n`커뉴야 스톱워치 일시정지`: 스톱워치가 돌아가는 도중 중간에 일시정지를 할 수 있어요. 만약 일시정지 중이라면 아랫줄의 재개와 같은 효과를 내요.\n`커뉴야 스톱워치 재개`: 일시정지 중인 스톱워치를 다시 돌아가게 해요.\n`커뉴야 스톱워치 내역`: 이전에 자신이 설정했던 스톱워치의 기록들을 살펴봐요.\n일시정지와 재개가 아닌 명령어들은 뒤에 아무 말이나 덧붙이면 스톱워치 제목이나 기록 제목, 내역은 특정 제목으로 돼 있는 기록만 검색하는 기능이 추가돼요!")
        elif command_to_know == "뀨":
            embed.add_field(name="명령어 도움: 뀨",
                            value="애교를 부리는 명령어일까요?\n`커뉴야 뀨`: 애교를 부립니다.\n`커뉴야 뀨 도움`: 도움말을 표시합니다.\n`커뉴야 뀨 가격`: 뀨를 구매할 수 있는 결제 수단과 가격, 기타 정보 등을 알려줍니다.\n`커뉴야 뀨 상점`: 뀨로 구매할 수 있는 것들의 목록을 보여줍니다.\n`커뉴야 뀨 구매 (아이템명)`: (아이템명) 을 구매합니다.\n`커뉴야 뀨 설명 (아이템명)`: (아이템명)에 대한 설명을 봅니다.")
        elif command_to_know == "기원목록":
            embed.add_field(name="명령어 도움: 기원목록",
                            value="존재하는 기원들의 목록을 보여주는 명령어에요. `커뉴야 기원목록 (필터)` 로 확인할 수 있고 필터는 다음과 같아요.\n'전체' 또는 '랜덤' 또는 빈칸: 모든 곳에서 진행되는 기원들의 목록을 랜덤하게 표시해요.\n'서버': 서버 내에서 진행되는 기원들의 목록을 표시해요.\n'신규': 최근에 기원된 것 순서대로 목록을 표시해요.\n'오늘기원됨': 오늘 기원된 것들만을 표시해요.\n'오랫동안기원됨': 가장 오랫동안 기원되고 있는 순서대로 목록을 표시해요.")
        elif command_to_know in ["할거", "할일"]:
            embed.add_field(name="명령어 도움: 할거",
                            value="자신이 할 일을 등록하고 그걸 진행하게 할 수 있는 명령어에요.\n`커뉴야 할거 추가`: 할 일을 추가해요.\n`커뉴야 할거 진행`: 이전에 등록해 놓은 할 일을 진행해요.\n`커뉴야 할거 초기화`: 만들어 놓았던 할 일들을 초기화해요.\n`커뉴야 할거 중간목표`: 진행 중인 할 일 중에서 중간 목표를 설정해요.\n`커뉴야 할거 현재`: 현재 설정해둔 할 일들의 목록을 표시해요.\n`커뉴야 할거 도움`: 명령어에 대한 도움말을 표시해요.\n자세한 인수 입력법 같은 내용은 `커뉴야 할거 도움`에 자세히 실어 놓았으니 명령어를 사용하시기 전에 꼭 도움말을 먼저 참고하세요.")
        elif command_to_know == '날짜차이':
            embed.add_field(name='명령어 도움: 날짜차이',
                            value='두 날짜 간의 차이를 계산합니다.\n`커뉴야 날짜차이 (날짜1)`: 오늘과 날짜1 간의 차이를 계산합니다.\n`커뉴야 날짜차이 (날짜1) (날짜2)`: 날짜1과 날짜2간의 차이를 계산합니다. 날짜들은 20240128과 같은 형식으로 입력받습니다.')
        elif command_to_know == '소수판정':
            embed.add_field(name='명령어 도움: 소수판정',
                            value='어떤 자연수가 소수인지 합성수인지를 판별합니다.\n사용법: `커뉴야 소수판정 (자연수)`\n자연수 값은 2 이상 1e1900 미만만 입력할 수 있으며, 수가 318665857834031151167461보다 커질 경우 정확도가 99.999994%까지 떨어집니다.')
        elif command_to_know == '소인수분해':
            embed.add_field(name='명령어 도움: 소인수분해',
                            value='어떤 자연수를 소인수분해합니다.\n사용법: `커뉴야 소인수분해 (자연수)`\n너무 큰 수를 입력할 경우 너무 오래 걸린다며 답변을 거부할 수도 있고, 그렇지 않을 수도 있습니다. 수가 클수록 답변을 거부할 확률이 올라가지만 아마도 비례하는 것은 아니며, 같은 수를 소인수분해하라고 여러 번 던져 준다 해도 언제는 받아주고 언제는 거절할 확률은 아마도 0에 매우 가깝습니다.\n또한 수가 커지면 커질수록 뒤에 ?가 붙을 확률이 생기며, ?가 있을 경우에는 가장 큰 소인수라고 출력한 수가 약 0.000006% 확률로 소수가 아닐 수 있습니다.')
        elif command_to_know == '글자수':
            embed.add_field(name='명령어 도움: 글자수',
                            value='글자 수를 세어 줍니다.\n사용법: `커뉴야 글자수 (할말)`')
        elif command_to_know == '다음거울수':
            embed.add_field(name='명령어 도움: 다음거울수',
                            value='주어진 수가 거울수인지를 확인해 주고, 주어진 수보다 큰 수 중 가장 작은 거울수를 알려줍니다. 거울수는 숫자들의 배열을 뒤집어도 값이 같은 수를 말합니다.\n사용법: `커뉴야 다음거울수 (자연수)`')
        elif command_to_know == '심심해':
            embed.add_field(name='명령어 도움: 심심해',
                            value='심심한 분들을 위해 공식서버 또는 커뉴봇과 관련된 다양한 TMI들을 보여줍니다.\n`커뉴야 심심해`: 랜덤한 TMI를 출력합니다.\n이 아래는 아이템 구매자 전용입니다.\n`커뉴야 심심해 리스트`: 지금까지 발견한 TMI들의 목록을 보여줍니다.\n`커뉴야 심심해 (번호)`: 발견한 TMI에 대해 해당 번호의 TMI를 출력합니다.')
        elif command_to_know == '계산':
            embed.add_field(name='명령어 도움: 계산',
                            value='주어진 식을 계산하는 명령어로 만들고 싶은 명령어입니다. yonsei1 버전에 처음 출시되어 업데이트를 할수록 더 강한 명령어가 됐으면 좋겠네요.\n`커뉴야 계산 도움`: 조금 더 자세한 도움말을 출력합니다.\n`커뉴야 계산 (계산식)`: 입력된 식을 계산해 결과를 보여줍니다. 현재 버전에서 봇이 알아들을 수 있는 계산식의 범위는 `커뉴야 계산 도움`을 참고하세요')
        elif command_to_know == '공부':
            embed.add_field(name='명령어 세트 도움: 공부',
                            value='커뉴봇 산하의 고성능 공부 챗봇 커뉴스터디에 오신 걸 환영합니다. 이 명령어 세트 안에는 유저의 공부를 도울'
                                  '많은 명령어들이 존재하므로, 최대한 활용해 보시는 것을 추천드립니다. '
                                  '또한, 대부분의 명령어는 슬래시 커맨드 전용으로 돌아갑니다. 이 점 유의하세요.\n\n'
                                  '이 기능 아래에 있는 명령어는 /공부정보, /할일추가, /할일진행, /할일현재, /오늘내일할일, /달력, /할일단축, '
                                  '/분류트리, /공부시작, /공부기록, /공부설정, /공부일지, /이벤트, /성적그래프, /공부시간그래프 가 있습니다.'
                                  '`커뉴야 출첵`은 커뉴스터디 명령어는 아니지만, 커뉴스터디가 추가된 yonsei6버전에서 리워크되었습니다. '
                                  '커뉴스터디 아래의 많은 명령어들은 우선 해당 날의 출석체크를 필요로 합니다.')
        elif command_to_know == '공부정보':
            embed.add_field(name='명령어 도움: 공부정보',
                            value='커뉴스터디에 속한 명령어로, 오늘까지 할 일들과 오늘 공부한 시간을 간략하게 보여 줍니다.')
        elif command_to_know == '할일추가':
            embed.add_field(name='명령어 도움: 할일추가',
                            value='커뉴스터디에 속한 명령어로, 해야 될 일이 있으면 이 명령어로 할 일을 추가할 수 있습니다. '
                                  '모든 파라미터에 적절한 값을 넣으면 되지만, 참고할 만한 사항은 몇 가지 있습니다. '
                                  '기간 에는 n일, n시간, n분 의 형식이 지원되며, 얼마마다 에는 n일, 매일, 요일들이 지원됩니다. (금, 월수금 등)'
                                  '또한 분량 뒤에 단위를 붙일 수도 있습니다. (50문제, 3뭉탱이 등등) 얼마마다 값에 아무 것도 없다면 '
                                  '1회성 할일, 있다면 반복할일로 인식됩니다. 이전 명령어 `커뉴야 할거 추가`에 대응.')
        elif command_to_know == '할일진행':
            embed.add_field(name='명령어 도움: 할일진행',
                            value='커뉴스터디에 속한 명령어로, 등록해 놓은 할 일들을 진행합니다. 어떤 할 일을 했는지를 내용에, 얼마나 많이 했는지를 '
                            '진행할분량에, 혹시 공부 시간을 기록하고 싶다면 공부한시간_기록용 에 채우시면 됩니다. 이전 명령어 '
                                  '`커뉴야 할거 진행`에 대응.')
        elif command_to_know == '할일현재':
            embed.add_field(name='명령어 도움: 할일현재',
                            value='커뉴스터디에 속한 명령어로, 현재 남은 할 일들과 그 할 일들을 얼마나 진행했는지와 그 할 일들이 언제까지인지'
                                  '를 보여줍니다. 이전 명령어 `커뉴야 할거 현재`에 대응.')
        elif command_to_know == '오늘내일할일':
            embed.add_field(name='명령어 도움: 오늘내일할일',
                            value='커뉴스터디에 속한 명령어로, 핸드폰 해상도의 **사진**으로 얼마 남지 않은 할 일들을 출력해 줍니다.'
                                  'yonsei6 버전에서 바로 작동할지는 미지수입니다.')
        elif command_to_know == '달력':
            embed.add_field(name='명령어 도움: 달력',
                            value='커뉴스터디에 속한 명령어로, 컴퓨터 해상도의 **사진**으로 이번달 동안 할 일들을 출력해 줍니다.'
                                  'yonsei6 버전에서 바로 작동할지는 미지수입니다.')
        elif command_to_know == '할일단축':
            embed.add_field(name='명령어 도움: 할일단축',
                            value='커뉴스터디에 속한 명령어로, 할일추가, 공부시작 등의 명령어를 사용할 때 단축 경로를 지정할 수 있습니다.\n\n'
                                  '`키워드`에는 원하는 것 아무거나 들어갈 수 있고, `넣을영역`은 네 가지 카테고리 중 하나를 선택할 수 있습니다.\n\n'
                                  '이런 식으로 단축 경로를 지정하고 나면, 다음번에 `/할일추가` 또는 `/공부시작` 등의 명령어를 사용했을 때 '
                                  '매번 `큰분류` 파라미터에 `수학`이라고 입력한다다든지 할 필요 없이 `내용` 파라미터에 `수학` 이라는 말이 '
                                  '포함되기만 하면 자동으로 `큰분류` 파라미터에 `수학`이라고 입력된 것처럼 행동합니다.')
        elif command_to_know == '분류트리':
            embed.add_field(name='명령어 도움: 분류트리',
                            value='커뉴스터디에 속한 명령어로, 큰분류, 중간분류, 작은분류 간에 포함 관계를 설정할 수 있습니다.\n\n'
                                  '예를 들어 분류트리 명령어를 이용해 `수학` 아래에 `해석학`, `선형대수학`, `집합론`을 넣었다고 합시다. '
                                  '그러면 나중에 `할일추가` 나 `공부시작` 등의 명령어를 사용했을 때 `중간분류` 파라미터에 `집합론`을 넣는다면 '
                                  '자동으로 `큰분류` 파라미터에 `수학`을 넣은 것처럼 행동합니다. `/할일단축` 명령어 세팅과 동시에 적용될 수 있고,'
                                  ' 이 경우 할일단축 명령어 설정의 우선순위가 더 높습니다.')
        elif command_to_know == '공부시작':
            embed.add_field(name='명령어 도움: 공부시작',
                            value='커뉴스터디에 속한 명령어로, 실시간 공부 기록을 지원하는 명령어입니다. 약 15초마다 한 번씩 UI가 업데이트되며, '
                                  '공부 그만하기 버튼을 눌러 공부를 종료하게 되면 자동으로 오늘 한 공부에 기록됩니다.')
        elif command_to_know == '공부기록':
            embed.add_field(name='명령어 도움: 공부기록',
                            value='커뉴스터디에 속한 명령어로, `공부시작` 명령어 외에 따로 기록할 만한 공부 내용이 있을 때 그것을 기록하는'
                                  ' 명령어입니다. `성적`과 `공부한시간` 파라미터가 따로 있다는 것에 주의하세요.')
        elif command_to_know == '공부일지':
            embed.add_field(name='명령어 도움: 공부일지',
                            value='커뉴스터디에 속한 명령어로, 원하는 날짜에 공부한/했던 것들의 일지를 텍스트로 보여 주는 명령어입니다. '
                                  '`분류기준`에 들어가는 값은 했던 공부들을 얼마나 자세하게 나눌까입니다.')
        elif command_to_know == '공부설정':
            embed.add_field(name='명령어 도움: 공부설정',
                            value='커뉴스터디에 속한 명령어로, 커뉴스터디 기능에 대한 몇 가지 설정들을 관리하는 명령어입니다.')
        elif command_to_know == '이벤트':
            embed.add_field(name='명령어 도움: 이벤트',
                            value='커뉴스터디에 속한 명령어로, 미래에 일어날 중요할 일을 기록하는 명령어입니다. '
                                  '이벤트에 들어가는 값을 바꾸고 나면 매 출석체크마다 이벤트가 얼마 남았는지를 보여줍니다.')
        elif command_to_know == '성적그래프':
            embed.add_field(name='명령어 도움: 성적그래프',
                            value='커뉴스터디에 속한 명령어로, 성적을 기록한 공부 데이터에 대해 성적을 그래프로 그려 줍니다.')
        elif command_to_know == '공부시간그래프':
            embed.add_field(name='명령어 도움: 공부시간그래프',
                            value='커뉴스터디에 속한 명령어로, 공부 시간을 기록한 공부 데이터에 대해 공부 시간을 그래프로 그려 줍니다.')
        else:
            embed.add_field(name="커뉴봇 일반 명령어 도움! (관리 명령어 도움말은 `커뉴야 관리`)",
                            value="커뉴봇에서 사용할 수 있는 명령어의 목록을 보여줘요! 대화형 명령어들은 굳이 도움말에 넣지는 않았으니 한 번 찾아 보세요!", inline=False)
            embed.add_field(name="최신 소식들을 알아보고 유저분들과 소통해 봐요!",
                            value="`커뉴야 공지`, `커뉴야 업데이트`, `커뉴야 나중업뎃`, `커뉴야 소개`, `커뉴야 공식서버`, `커뉴야 초대`\n​", inline=False)
            embed.add_field(name="이 명령어들은 꼬박꼬박 써 보세요!",
                            value="`커뉴야 출석체크`, `커뉴야 출첵내역`, `커뉴야 출첵목록`, `커뉴야 연속출석`, `커뉴야 기원`, `커뉴야 기원목록`\n​",
                            inline=False)
            embed.add_field(name="여러 가지 게임들을 즐겨보세요!",
                            value="`커뉴야 강화`, `커뉴야 강화목록`, `커뉴야 강화삭제`, `커뉴야 서버강화`, `커뉴야 가위바위보`, `커뉴야 묵찌빠`, `커뉴야 퀴즈`, `커뉴야 오목`, `커뉴야 커뉴핑크`\n​",
                            inline=False)
            embed.add_field(name="사용 통계를 알아보고 도전 과제를 달성해봐요!",
                            value="`커뉴야 스펙`, `커뉴야 지분`, `커뉴야 도전과제`, `커뉴야 프로필`, `커뉴야 소개작성`\n​", inline=False)
            embed.add_field(name="서버 내 레벨과 관련된 정보를 알아보세요!", value="`커뉴야 레벨`, `커뉴야 경험치부스트`, `커뉴야 리더보드`, `커뉴야 채널부스트`\n​",
                            inline=False)
            embed.add_field(name="서버 내에서의 다른 정보들을 알아보세요!", value="`커뉴야 초대횟수`, `커뉴야 이름색`, `커뉴야 커맨드금지`, `커뉴야 올려금지`\n​",
                            inline=False)
            embed.add_field(name="공부하시거나 일정 등을 관리하시는 걸 도와드릴게요!",
                            value="`커뉴야 타이머`, `커뉴야 스톱워치`, `/공부정보`, `/할일추가`, `/할일진행`, `/할일현재`, `/오늘내일할일`, `/달력`, `/할일단축`, `/분류트리`, `/공부시작`, `/공부기록`, `/공부설정`, `/공부일지`, `/이벤트`, `/성적그래프`, `/공부시간그래프` (**커뉴스터디에 대한 자세한 설명은 `커뉴야 도움 공부` 및 각각 명령어 도움을 참고해주세요.**)\n​", inline=False)
            embed.add_field(name="이 봇이나 서버들 또는 사람들에 대한 정보를 얻어가세요!",
                            value="`커뉴야 프사`, `커뉴야 유저정보`, `커뉴야 서버사진`, `커뉴야 서버정보`, `커뉴야 스탯`, `커뉴야 서버시간`, `커뉴야 핑`\n​",
                            inline=False)
            embed.add_field(name="개발자와 연락하거나 디버그를 진행하세요!",
                            value="`커뉴야 문의`, `커뉴야 개인정보처리방침`, `커뉴야 끼임해제`, `커뉴야 어디`, `커뉴야 디엠테스트`\n​", inline=False)
            embed.add_field(name="이 명령어들은 공식서버에서만 사용할 수 있어요!",
                            value="`커뉴야 잡초키우기`, `커뉴야 우주탐험`, `커뉴야 돈`, `커뉴야 구매`, `커뉴야 상점`, `커뉴야 설명`, 그 외에 `ㅋㅇ`으로 시작하는 명령어들...\n​",
                            inline=False)
            embed.add_field(name="그리고 아주 많은 유용한 기능들... (공식서버 내 밈 명령어 일부 포함)",
                            value="`커뉴야 운빨테스트`, `커뉴야 올려`, `커뉴야 서바준보`, `커뉴야 오타원본`, `커뉴야 심심해`, `커뉴야 골라`, `커뉴야 말해`, `커뉴야 섞어`, `커뉴야 서버추천`, `커뉴야 업다운`, `커뉴야 지건`, `커뉴야 색깔`, `커뉴야 날짜차이`, `커뉴야 소수판정`, `커뉴야 소인수분해`, `커뉴야 글자수`, `커뉴야 다음거울수`, `커뉴야 계산`\n​",
                            inline=False)
            embed.set_footer(
                text=f"자세한 도움은 '커뉴야 도움 (명령어)'\n모든 명령어는 ㅋ도움 처럼 줄일 수 있으며, 명령어가 yonsei1 또는 그 이후 버전에 업데이트됐다면 `커뉴야 업데이트 (명령어)`를 사용해 해당 명령어의 업데이트 상황을 알아볼 수 있습니다.")
        await send(ctx, embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print('("help")')


async def setup(bot):
    await bot.add_cog(Help(bot))
