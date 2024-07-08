import asyncio
from random import randint
from typing import Optional
from discord import Embed, DMChannel

from .achieve import grant_check, grant
from discord.ext.commands import Cog, command
import base64
from json import dumps, loads
from ..db import db
from time import time

quarkgen_coefficients = [0, 20000, 100000, 400000, 2000000]
alpha_centauri = [52776.49, ]
trade_item_visual = ['5000 아니 씨밧을 알데바락의 조각 하나와 거래합니다.', '특가 상품! 3000 아니 씨밧을 알데바락의 조각 하나와 거래합니다.',
                     '알데바락의 조각 20개를 주고 한 번에 두 아이템까지 거래할 수 있도록 합니다.', '50000 아니 씨밧을 주고 거래 새로고침 쿨타임을 7시간으로 줄입니다.',
                     '100000 아니 씨밧을 주고 거래 새로고침 쿨타임을 6시간으로 줄입니다.', '100000 아니 씨밧과 알데바락의 조각 50개를 주고 거래 새로고침 쿨타임을 5시간으로 줄입니다.',
                     '5000 아니 씨밧을 주고 0 아니 씨밧이나 10000 아니 씨밧을 받습니다. (동일한 확률로)', '알데바락의 조각 10개를 주고 상점에 별 지도를 입고시킵니다.',
                     '알데바락의 조각 10개를 주고 폴룩스의 조각 하나를 받습니다.', '7000 아니 씨밧을 주고 우주선에 전력 1,000,000만큼을 충전합니다.',
                     '알데바락의 조각 250개를 주고 한 번에 세 아이템까지 거래할 수 있도록 합니다.']


def trade_refresh(stats):
    slot = stats['trading_slot']
    cooldown = stats['trading_cooldown']
    trades = []
    for i in range(slot):
        while True:
            x = randint(1, 222)
            if x <= 87:
                trades.append(0)
                break
            elif x <= 97:
                trades.append(1)
                break
            elif 98 <= x <= 100 and slot == 1:
                trades.append(2)
                break
            elif 101 <= x <= 120 and slot >= 2 and cooldown == 3600 * 8:
                trades.append(3)
                break
            elif 121 <= x <= 135 and slot >= 2 and cooldown == 3600 * 7:
                trades.append(4)
                break
            elif 136 <= x <= 145 and slot >= 2 and cooldown == 3600 * 6:
                trades.append(5)
                break
            elif 146 <= x <= 160 and slot >= 2:
                trades.append(6)
                break
            elif 161 <= x <= 165 and slot >= 2 and 'trading_progress' not in stats:
                trades.append(7)
                break
            elif 166 <= x <= 200 and slot >= 2:
                trades.append(8)
                break
            elif 201 <= x <= 220 and slot >= 2:
                trades.append(9)
                break
            elif (x == 221 or x == 222) and slot == 2 and stats['trading_count'] >= 200:
                trades.append(10)
                break
    return trades


class Alpha(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="ㅇ프로필")
    async def profile(self, ctx):
        if ctx.channel.category.id != 916323967248248892:
            return
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        stats = loads(base64.b64decode(stats))
        embed = Embed(color=0xffd6fe)
        tjfaud = ''
        asdf = ''
        if stats['personal_setting'] & 256:
            stats['cvat_per_message'] *= 2
            stats['cvat_per_second'] *= 2
        for stat in stats:
            s = ''
            if stat == "ani_cvat":
                s = "보유 중인 아니 씨밧"
            elif stat == 'cvat_per_message':
                s = "채팅 시 획득 아니 씨밧"
            elif stat == 'cvat_per_second':
                s = '초당 벌어들이는 아니 씨밧'
            elif stat == 'cvat_gather_max':
                s = '한 번에 벌어들일 수 있는 최대 아니 씨밧'
            elif stat == 'electric_saving_max':
                s = '최대 전력 비축량'
            elif stat == 'trading_count':
                s = '알데바락 우주센터와의 거래 횟수'
            if s:
                tjfaud += f"\n{s}: {stats[stat]}"
            if stat == 'personal_setting':
                if stats['personal_setting'] != 0:
                    asdf = "\n구매한 상품들: "
                    if stats['personal_setting'] & 1 == 1:
                        asdf += "오타 연구소"
                    if 'quarkgen_level' in stats:
                        if stats['quarkgen_level'] == 1:
                            asdf += ', 쿼크 추출기'
                        elif stats['quarkgen_level'] == 2:
                            asdf += ', 쿼크 뭉탱태 추출기 ver. 1'
                        elif stats['quarkgen_level'] == 3:
                            asdf += ', 쿼크 뭉탱태 추출기 ver. 2'
                        elif stats['quarkgen_level'] == 4:
                            asdf += ', 쿼크 유링겟ㅍㅇ 추출기'
                    if 'trading_level' in stats and stats['trading_level']:
                        asdf += ", 알데바락 언어 번역기"
                    if stats['personal_setting'] & 512:
                        asdf += ', 별 지도'
        tjfaud += asdf
        embed.add_field(name='게임 정보', value=tjfaud)
        await ctx.send(embed=embed)

    @command(name='ㅇ상점')
    async def shop(self, ctx):
        if ctx.channel.category.id != 916323967248248892:
            return
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        stats = loads(base64.b64decode(stats))
        embed = Embed(color=0xffd6fe, title="아니 씨밧 상점")
        embed.add_field(name='채팅 시 획득 아니 씨밧 증가 (줄여서 1)',
                        value=f"채팅 시 획득하는 아니 씨밧을 2배로 증가시킵니다.\n비용: {stats['cvat_gain_upgrade_cost']} 아니 씨밧")
        l = grant_check("연구 입문자", ctx.author.id)
        if l == 0:
            if 'personal_setting' not in stats or stats["personal_setting"] & 1 == 0:
                embed.add_field(name='오타 연구소 (줄여서 2)',
                                value=f"우주의 신비를 파악하는 데 도움을 주는 오타를 연구합니다. 1번만 구매 가능합니다.\n비용: 1500 아니 씨밧")
        if 'cvat_per_second' in stats:
            embed.add_field(name='초당 획득 아니 씨밧 증가 (줄여서 3)',
                            value=f'오타 연구의 시작으로 자동생산하게 된 아니 씨밧의 생산 효율을 증가시킵니다.\n비용: {stats["cvatgen_efficiency_cost"]} 아니 씨밧')
            embed.add_field(name='미접속 중 아니 씨밧 최대치 증가 (줄여서 4)',
                            value=f'오타 연구의 시작으로 자동생산하게 된 아니 씨밧을 더 오랫동안 생산할 수 있게 됩니다.\n비용: {stats["cvatgen_gather_cost"]} 아니 씨밧')
        if 'personal_setting' in stats:
            if stats['personal_setting'] & 4 == 4 and ('quarkgen_level' not in stats or not stats['quarkgen_level']):
                embed.add_field(name='쿼크 추출기 (줄여서 5)',
                                value='우주 어딘가에는 존재하는 쿼크를 끌어모읍니다. 업 쿼크와 다운 쿼크를 자동으로 만들어내기 시작합니다.\n비용: 6969 아니 씨밧')
            if stats['personal_setting'] & 8 == 8:
                embed.add_field(name=':fireworks:를 이용한 핵융합 발전소 (줄여서 6)',
                                value='어떻게 불꽃놀이와 토륨으로 핵융합 발전을 하겠다는 건지는 정말 모르겠습니다. 그러나 이곳에서는 그런 게 가능하다네요;;\n비용: 500000 토륨')
            if stats['typo_research'] & 64 == 64 and stats['research_doing'] != '뭉탱태':
                if stats['quarkgen_level'] == 1:
                    embed.add_field(name='쿼크 뭉탱태 추출기 ver.1 (줄여서 7)',
                                    value='쿼크를 뭉탱이로 끌어모으는 고급 쿼크 추출기입니다. 업 쿼크와 다운 쿼크를 이전보다 더 빠른 속도로 만들어내기 시작합니다.\n비용: 12000 아니 씨밧')
                elif stats['quarkgen_level'] == 2:
                    embed.add_field(name='쿼크 뭉탱태 추출기 ver.2 (줄여서 8)',
                                    value='쿼크를 뭉탱이로 끌어모으는 고급 쿼크 추출기입니다. 업 쿼크와 다운 쿼크를 v1 때보다도 더 빠른 속도로 만들어내기 시작합니다.\n비용: 30000 아니 씨밧')
            if stats['personal_setting'] & 32 == 32:
                embed.add_field(name='최대 전력 비축량 증가 (줄여서 9)',
                                value=f'`ㅋㅇ발전` 명령어로 전력을 생산할 때 최대로 비축될 수 있는 전력의 양을 증가시킵니다.\n비용: {stats["elecgen_capacity_cost"]} 아니 씨밧')
            if stats['personal_setting'] & 16 and not stats['personal_setting'] & 256:
                embed.add_field(name='자동 획득 아니 씨밧 부스트 (줄여서 10)',
                                value='초당 획득 아니 씨밧과 미접속 중 아니 씨밧 최대치가 모두 2배로 증가하고, 앞으로 구매하는 초당 획득 아니 씨밧 증가와 미접속 중 아니 씨밧 최대치 증가의 효율이 2배로 늘어납니다. 한 번만 구매 가능합니다.\n비용: 40000 아니 씨밧')
            if 'aldebarak_shard' in stats and stats['trading_level'] == 0:
                embed.add_field(name='알데바락 언어 번역기 (줄여서 11)',
                                value='알데바락 우주센터와 거래할 때 그들의 언어를 알아듣게 되어, 더 수월한 거래를 할 수 있게 됩니다.\n비용: 알데바락의 조각 1개')
            if 'trading_progress' in stats and not stats['personal_setting'] & 512:
                embed.add_field(name='별 지도 (줄여서 12)',
                                value='알데바락 우주센터에서 상점 주인에게 남기고 간 주변 별 지도를 획득합니다. 알파 센타우리의 위치와 프록시마b 주변 소행성들의 평균적인 분포를 알 수 있다네요!\n비용: 폴룩스의 조각 1개')
            if stats['personal_setting'] & 1024 and stats['quarkgen_level'] == 3:
                embed.add_field(name='쿼크 유링겟ㅍㅇ 추출기 (줄여서 13)',
                                value='쿼크 뭉탱태 추출기를 강화해 쿼크를 유링겟ㅍㅇ으로 끌어오는 초고급 쿼크 추출기입니다. 업 쿼크와 다운 쿼크를 매우 빠른 속도로 만들어내며 아마 받았을 30% 속도 보너스까지 생각한다면 굉장하네요!\n비용: 90000 아니 씨밧')
        await ctx.send(embed=embed)

    @command(name='ㅇ구매')
    async def purchase(self, ctx, *, item):
        if ctx.channel.category.id != 916323967248248892:
            return
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        stats = loads(base64.b64decode(stats))
        if item in ['채팅 시 획득 아니 씨밧 증가', "1"]:
            if stats['ani_cvat'] < (cost := stats['cvat_gain_upgrade_cost']):
                await ctx.send(f"이 아이템의 가격인 {cost}만큼의 아니 씨밧을 가지고 있지 않아요!")
                return
            stats['ani_cvat'] -= cost
            stats['cvat_per_message'] *= 2
            stats['cvat_gain_upgrade_cost'] *= 5
        elif item in ['오타 연구소', '2']:
            l = grant_check('연구 입문자', ctx.author.id)
            if l == 1:
                return
            if stats['ani_cvat'] < 1500:
                await ctx.send("이 아이템의 가격인 1500만큼의 아니 씨밧을 가지고 있지 않아요!")
                return
            if 'personal_setting' not in stats:
                stats['personal_setting'] = 0
            if stats['personal_setting'] & 1 == 1:
                await ctx.send("이미 구매한 아이템이에요!")
                return
            stats['ani_cvat'] -= 1500
            stats['personal_setting'] += 1
            await ctx.author.send("오타 연구소를 구매하셨습니다! 이제 다양한 오타를 연구하실 수 있습니다.")
        elif item in ['초당 획득 아니 씨밧 증가', '3']:
            if stats['ani_cvat'] < stats['cvatgen_efficiency_cost']:
                await ctx.send(f"이 아이템의 가격인 {stats['cvatgen_efficiency_cost']}만큼의 아니 씨밧을 가지고 있지 않아요!")
                return
            stats['ani_cvat'] -= stats['cvatgen_efficiency_cost']
            stats['cvat_per_second'] += 0.25
            stats['cvatgen_efficiency_cost'] += 1500
        elif item in ['미접속 중 아니 씨밧 최대치 증가', '4']:
            if stats['ani_cvat'] < stats['cvatgen_gather_cost']:
                await ctx.send(f"이 아이템의 가격인 {stats['cvatgen_gather_cost']}만큼의 아니 씨밧을 가지고 있지 않아요!")
                return
            stats['ani_cvat'] -= stats['cvatgen_gather_cost']
            stats['cvat_gather_max'] += 1000
            stats['cvatgen_gather_cost'] += 1500
        elif item in ['쿼크 추출기', '5']:
            if stats['personal_setting'] & 4 == 0:
                return
            if 'quarkgen_level' not in stats:
                stats['quarkgen_level'] = 0
            if stats['quarkgen_level']:
                return
            if stats['ani_cvat'] < 6969:
                await ctx.send('이 아이템의 가격인 6969 아니 씨밧을 가지고 있지 않아요!')
                return
            stats['ani_cvat'] -= 6969
            stats['quarkgen_level'] = 1
            stats['cvat_gather_start'] = time()
        elif item in [':fireworks:를 이용한 핵융합 발전소', '6']:
            if stats['personal_setting'] & 64:
                return
            stats['90th'] = 500000
            stats['personal_setting'] += 56
            stats['electric_gen'] = 0
            stats['electric_usage'] = 0
            stats['electric_saving'] = 0
            stats['electric_saving_max'] = 1000000
            await ctx.send('ㅋㅇ발전 명령어를 사용해 보세요!')
        elif item in ['쿼크 뭉탱태 추출기 ver.1', '7']:
            if stats['personal_setting'] & 64 == 0 or stats['research_doing'] == '뭉탱태':
                return
            if stats['ani_cvat'] < 12000:
                await ctx.send('이 아이템의 가격인 12000 아니 씨밧을 가지고 있지 않아요!')
                return
            stats['ani_cvat'] -= 12000
            stats['quarkgen_level'] = 2
        elif item in ['쿼크 뭉탱태 추출기 ver.2', '8']:
            if stats['personal_setting'] & 64 == 0 or stats['research_doing'] == '뭉탱태':
                return
            if stats['ani_cvat'] < 30000:
                await ctx.send('이 아이템의 가격인 30000 아니 씨밧을 가지고 있지 않아요!')
                return
            stats['ani_cvat'] -= 30000
            stats['quarkgen_level'] = 3
        elif item in ['최대 전력 비축량 증가', '9']:
            if stats['personal_setting'] & 32 == 0:
                return
            if stats['ani_cvat'] < stats['elecgen_capacity_cost']:
                await ctx.send(f'이 아이템의 가격인 {stats["elecgen_capacity_cost"]} 아니 씨밧을 가지고 있지 않아요!')
                return
            stats['ani_cvat'] -= stats['elecgen_capacity_cost']
            stats['electric_saving_max'] += 500000
            stats['elecgen_capacity_cost'] += 5000
        elif item in ['자동 획득 아니 씨밧 부스트', '10']:
            if stats['personal_setting'] & 16 == 0 or stats['personal_setting'] & 256:
                return
            if stats['ani_cvat'] < 40000:
                await ctx.send(f'이 아이템의 가격인 40000 아니 씨밧을 가지고 있지 않아요!')
                return
            stats['ani_cvat'] -= 40000
            stats['personal_setting'] += 256
        elif item in ['알데바락 언어 번역기', '11']:
            if 'aldebarak_shard' not in stats or stats['trading_level']:
                return
            stats['aldebarak_shard'] = 0
            stats['trading_level'] = 1
            stats['trading_cooldown'] = 28800
            stats['trading_next_refresh'] = time() + 28800
            await ctx.author.send('다시 한번 `ㅋㅇ거래`를 사용해 보라는 소리가 어딘가에서 들려옵니다.')
        elif item in ['별 지도', '12']:
            if 'trading_progress' not in stats or stats['personal_setting'] & 512:
                return
            if 'pollux_shard' not in stats or not stats['pollux_shard']:
                await ctx.send('이 아이템의 가격인 폴룩스의 조각 1개를 가지고 있지 않아요!')
                return
            stats['pollux_shard'] -= 1
            stats['personal_setting'] += 512
        elif item in ['쿼크 유링겟ㅍㅇ 추출기', '13']:
            if not stats['personal_setting'] & 1024:
                return
            if stats['ani_cvat'] < 90000:
                await ctx.send('이 아이템의 가격인 90000 아니 씨밧을 가지고 있지 않아요!')
                return
            stats['ani_cvat'] -= 90000
            stats['quarkgen_level'] = 4
        await end_purchase(stats, ctx)

    @command(name='ㅇ연구')
    async def typo_research(self, ctx):
        if ctx.channel.category.id != 916323967248248892:
            return
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        stats = loads(base64.b64decode(stats))
        if 'research_doing' in stats and stats['research_doing'] != '없음':
            await ctx.send('이미 어떤 오타를 연구중이에요!')
            return
        if 'personal_setting' in stats and stats['personal_setting'] & 1 == 1:
            if 'typo_research' not in stats:
                stats['typo_research'] = 0
            embed = Embed(color=0x36393f, title='우주를 알아보는 오타 연구')
            if stats['typo_research'] == 0:
                embed.add_field(name="아니 씨밧 연구하기",
                                value="이 게임의 돈 이름이기도 하고 가장 기본적이면서 가장 대중적이고 가장 유명한 아니 씨밧을 연구합니다.\n\n연구를 완료하면 느린 속도로 아니 씨밧을 생산하기 시작합니다.\n\n연구비용: 69 아니 씨밧, 소요 시간: 0초")
            else:
                if not stats['typo_research'] & 2:
                    embed.add_field(name="피겅 연구하기",
                                    value="가장 오래된 오타 중 하나인 피겅을 연구하게 됩니다.\n\n연구를 완료하면 아주 오래된 오타인 만큼 우주 탄생의 진실을 조금이나마 연구해 쿼크와 전자를 추출하는 방법을 알아내게 됩니다.\n\n연구비용: 1000 아니 씨밧, 소요 시간: 10분")
                if not stats['typo_research'] & 4:
                    embed.add_field(name="피곦 연구하기",
                                    value="피겅만큼은 아니지만 피곤의 상당히 오래된 오타들 중 하나인 피곦을 연구하게 됩니다.\n\n연구를 완료하면 우주 초기의 상황을 조금이나마 연구해 쿼크를 합성하는 방법을 알아내게 됩니다.\n\n연구비용: 1500 아니 씨밧, 소요 시간: 40분")
            if stats['typo_research'] & 4:
                if not stats['typo_research'] & 8:
                    embed.add_field(name="h 연구하기",
                                    value="어쩌다가 한영키가 바뀜으로 인해 ㅗ가 h가 되었고 h가 대문자로 바뀌었더니 수소 원자의 기호가 되어버렸습니다.\n\n연구를 완료하면 전자(e-)의 성질을 탐구하고 전자를 자유롭게 다룰 수 있게 되며 양성자와 전자를 합쳐 경수소(1H), 중수소(2H), 삼중수소(3H)를 만들 수 있게 됩니다.\n\n연구비용: 양성자, 중성자 각각 1억 개, 소요 시간: 2시간")
            if stats['typo_research'] & 4:
                if not stats['typo_research'] & 16:
                    embed.add_field(name=":fireworks: 연구하기",
                                    value=":weary:를 치려다가 어떻게 나오게 되었는지 정말 모르겠는 :fireworks:로 바뀌게 된 이 오타를 연구합니다.\n\n연구를 완료하면 섭씨 10억 도까지 온도를 올릴 수 있는 미핀 불꽃놀이를 할 수 있게 되어 핵융합 발전이 가능해질까요?\n\n연구비용: 경수소 2억 개, 소요 시간: 3시간")
            if stats['typo_research'] & 16:
                if not stats['typo_research'] & 32:
                    embed.add_field(name=';TH 연구하기',
                                    value='생각을 하려 했는지 어쨌는지는 모르지만, :thinking:이 ;TH로 변했습니다!\n\n연구를 완료하면 실제로 불꽃놀이 화약을 가열시킬 수 있는 토륨을 추출해낼 방법을 알게 됩니다.\n\n연구비용: 5000 아니 씨밧, 소요 시간: 1시간')
            if stats['personal_setting'] & 64 == 64 and not stats['typo_research'] & 64:
                embed.add_field(name='뭉탱태 연구하기',
                                value='스트리머 "케인"님의 밈 중 하나인 뭉탱이 밈을 채팅에 치려다가 ㅇ 받침이 없어져 버렸습니다.\n\n연구를 완료하면 더 높은 성능의 쿼크 추출기를 구매해 쿼크를 뭉탱이로 추출해낼 수 있게 됩니다.\n\n연구비용: 10000 아니 씨밧, 소요 시간: 6시간')
            if stats['personal_setting'] & 32 == 32 and not stats['typo_research'] & 128:
                embed.add_field(name='메타벗 연구하기',
                                value='무언가 심오한 것을 연구합니다. 이것을 연구하기만 한다면 어디론가 갈 수 있을지도 모릅니다.\n\n연구를 완료하면 가까운 거리 정도는 이동할 수 있는 우주선을 만들게 되지만, 무언가 더 남아 있을 수 있습니다.\n\n연구비용: 100000 아니 씨밧, 소요 시간: 2일')
            if stats['personal_setting'] & 32 == 32 and not stats['typo_research'] & 256:
                embed.add_field(name='뇌저 연구하기',
                                value='뇌절 이라고 말하려다가 뇌저 라고 오타를 낸 다음 갑자기 대화 주제를 트는 모습을 볼 수 있습니다.\n\n이런 식으로 뇌전탑이 아무데도 아닌 곳에서 튀어나오게 된 오타를 연구하다 보니 연구를 완료하면 이때까지는 비축만 해 놓던 전력을 다른 곳으로 옮길 수 있게 됩니다.\n\n연구비용: 2000000 비축된 전기, 소요 시간 3시간')
            if stats['personal_setting'] & 16 == 16 and not stats['typo_research'] & 512:
                embed.add_field(name='알데바락이 뭔가요? 연구하기',
                                value='거성 알데바란의 이름을 말하려다가 알데바락이 됐어요 ㅠㅠ 그런데 어떻게 ㄴ이 ㄱ으로 오타난 걸까요? 비록 우리가 연구하는 것은 어떻게 ㄴ이 ㄱ으로 바뀌었는지는 아니지만, 이것도 연구할 재밌어 보이는 주제네요!\n\n연구를 완료하면 커뉴서버 안에 숨겨져 있는 세력인 알데바락 우주센터에 관한 것들을 조금이나마 알게 됩니다.\n\n연구비용: 25000 아니 씨밧, 1000000 비축된 전기, 소요 시간 8시간')
            if (not stats['typo_research'] & 1024) and 'trading_slot' in stats and stats['trading_slot'] == 2:
                embed.add_field(name='ㅍ 연구하기',
                                value='저런. 아마 복붙을 하고 싶었던 거였겠죠?\n\n컨트롤 v마저 제대로 누르지 못하는 서준을 본받아 연구를 완료하면 지금은 좀 느리다 싶은 것들이 빨라지는 것을 느낄 수 있습니다.\n\n연구비용: 100000 아니 씨밧, 25 알데바락의 조각, 3000000 비축된 전기, 소요 시간 1일')
            if stats['typo_research'] & 3072 == 1024:
                embed.add_field(name='유링겟ㅍㅇ 연구하기',
                                value='스트리머 "케인"님의 밈 중 하나인 뭉탱이 밈의 일부인 "유링게슝"을 채팅에 치려다가 ㅠ가 ㅍ으로 변했나 봅니다.\n\n연구를 완료하면 쿼크 뭉탱태로 있다가 유링겟ㅍㅇ 추출기가 상점에 입고되는데, 이 추출기는 쿼크만 추출하는 게 아니라고 하더라고요?\n\n연구비용: 400000 아니 씨밧, 소요 시간 1일 12시간')
            await ctx.send("어떤 연구를 하시겠습니까? 연구할 오타의 이름을 말해 주세요", embed=embed)
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
            except TimeoutError:
                await ctx.send("연구를 취소했어요.")
                return
            if msg.content == "아니 씨밧":
                if stats['ani_cvat'] < 69:
                    await ctx.send(f"이 오타를 연구할 수 있는 69만큼의 아니 씨밧을 가지고 있지 않아요!")
                    return
                if stats['typo_research'] & 1:
                    await ctx.send("이미 연구한 오타에요!")
                    return
                stats['typo_research'] = 1
                await ctx.send("아니 씨밧 연구 시작 완료!")
                await ctx.author.send(
                    "아니 씨밧 연구 완료!\n알파 센타우리 주변의 자기장 형성에 대해 일부분 알 것 같습니다...\n이제부터 `ㅋㅇ획득`을 입력하시면 모아진 아니 씨밧이 지급됩니다.")
                stats['cvat_per_second'] = 0.5
                stats['cvatgen_efficiency_cost'] = 3000
                stats['cvat_gather_start'] = time()
                stats['cvatgen_gather_cost'] = 3000
                stats['cvat_gather_max'] = 2000
            elif msg.content == "피겅":
                if stats['ani_cvat'] < 1000:
                    await ctx.send("이 오타를 연구할 수 있는 1000만큼의 아니 씨밧을 가지고 있지 않아요!")
                    return
                if stats['typo_research'] & 2:
                    await ctx.send("이미 연구한 오타에요!")
                    return
                stats['ani_cvat'] -= 1000
                stats['typo_research'] += 2
                stats['research_end'] = time() + 600
                stats['research_doing'] = '피겅'
            elif msg.content == '피곦':
                if stats['ani_cvat'] < 1500:
                    await ctx.send("이 오타를 연구할 수 있는 1500만큼의 아니 씨밧을 가지고 있지 않아요!")
                    return
                if stats['typo_research'] & 4:
                    await ctx.send("이미 연구한 오타에요!")
                    return
                stats['ani_cvat'] -= 1500
                stats['typo_research'] += 4
                stats['research_end'] = time() + 2400
                stats['research_doing'] = '피곦'
            elif msg.content == 'h':
                if stats['proton'] < 100000000 or stats['neutron'] < 100000000:
                    await ctx.send("이 오타를 연구할 때 쓰이는 양성자 1억 개와 중성자 1억 개를 가지고 있지 않아요!")
                    return
                if stats['typo_research'] & 8:
                    await ctx.send("이미 연구한 오타에요!")
                    return
                stats['proton'] -= 100000000
                stats['neutron'] -= 100000000
                stats['typo_research'] += 8
                stats['research_end'] = time() + 7200
                stats['research_doing'] = 'h'
            elif msg.content == '🎆':
                if stats['1h'] < 200000000:
                    await ctx.send("이 오타를 연구할 때 쓰이는 경수소 2억 개를 가지고 있지 않아요!")
                    return
                if stats['typo_research'] & 16:
                    await ctx.send("이미 연구한 오타에요!")
                    return
                stats['1h'] -= 200000000
                stats['typo_research'] += 16
                stats['research_end'] = time() + 10800
                stats['research_doing'] = '🎆'
            elif msg.content == ';TH':
                if stats['ani_cvat'] < 5000:
                    await ctx.send('이 오타를 연구할 때 쓰이는 5000만큼의 아니 씨밧을 가지고 있지 않아요!')
                    return
                if stats['typo_research'] & 32:
                    await ctx.send('이미 연구한 오타에요!')
                    return
                stats['ani_cvat'] -= 5000
                stats['typo_research'] += 32
                stats['research_end'] = time() + 3600
                stats['research_doing'] = ';TH'
            elif msg.content == '뭉탱태':
                if stats['ani_cvat'] < 10000:
                    await ctx.send('이 오타를 연구할 때 쓰이는 10000만큼의 아니 씨밧을 가지고 있지 않아요!')
                    return
                if stats['typo_research'] & 64:
                    await ctx.send('이미 연구한 오타에요!')
                    return
                stats['ani_cvat'] -= 10000
                stats['typo_research'] += 64
                stats['research_end'] = time() + 21600
                stats['research_doing'] = '뭉탱태'
            elif msg.content == '메타벗':
                if stats['ani_cvat'] < 100000:
                    await ctx.send('이 오타를 연구할 때 쓰이는 100000만큼의 아니 씨밧을 가지고 있지 않아요!')
                    return
                if stats['typo_research'] & 128:
                    await ctx.send('이미 연구한 오타에요!')
                    return
                stats['ani_cvat'] -= 100000
                stats['typo_research'] += 128
                stats['research_end'] = time() + 172800
                stats['research_doing'] = '메타벗'
            elif msg.content == '뇌저':
                if 'electric_saving' not in stats:
                    return
                if stats['electric_saving'] < 2000000:
                    await ctx.send('이 오타를 연구할 때 쓰이는 2000000만큼의 비축된 전력을 가지고 있지 않아요!')
                    return
                if stats['typo_research'] & 256:
                    await ctx.send('이미 연구한 오타에요!')
                    return
                stats['electric_saving'] -= 2000000
                stats['typo_research'] += 256
                stats['research_end'] = time() + 10800
                stats['research_doing'] = '뇌저'
            elif msg.content == '알데바락이 뭔가요?':
                if stats['personal_setting'] & 16 == 0:
                    return
                if stats['typo_research'] & 512:
                    await ctx.send('이미 연구한 오타에요!')
                    return
                if stats['ani_cvat'] < 25000 or stats['electric_saving'] < 1000000:
                    await ctx.send('이 오타를 연구할 때 쓰이는 25000만큼의 아니 씨밧과 1000000만큼의 비축된 전력을 가지고 있지 않아요!')
                    return
                stats['ani_cvat'] -= 25000
                stats['electric_saving'] -= 1000000
                stats['typo_research'] += 512
                stats['research_end'] = time() + 28800
                stats['research_doing'] = '알데바락이 뭔가요?'
            elif msg.content == 'ㅍ':
                if 'trading_slot' not in stats or stats['trading_slot'] == 1:
                    return
                if stats['typo_research'] & 1024:
                    await ctx.send('이미 연구한 오타에요!')
                    return
                if stats['ani_cvat'] < 100000 or stats['aldebarak_shard'] < 25 or stats['electric_saving'] < 3000000:
                    await ctx.send('이 오타를 연구할 때 쓰이는 100000 아니 씨밧, 25 알데바락의 조각, 3000000 비축된 전기를 가지고 있지 않아요!')
                    return
                stats['ani_cvat'] -= 100000
                stats['aldebarak_shard'] -= 25
                stats['electric_saving'] -= 3000000
                stats['typo_research'] += 1024
                stats['research_end'] = time() + 86400
                stats['research_doing'] = 'ㅍ'
            elif msg.content == '유링겟ㅍㅇ':
                if not stats['typo_research'] & 1024:
                    return
                if stats['typo_research'] & 2048:
                    await ctx.send('이미 연구한 오타에요!')
                    return
                if stats['ani_cvat'] < 400000:
                    await ctx.send('이 오타를 연구할 때 쓰이는 400000만큼의 아니 씨밧을 가지고 있지 않아요!')
                    return
                stats['ani_cvat'] -= 400000
                stats['typo_research'] += 2048
                stats['research_end'] = time() + 129600
                stats['research_doing'] = '유링겟ㅍㅇ'
            else:
                await ctx.send("존재하지 않거나 연구가 불가능한 오타에요!")
                return
            await ctx.send('오타 연구를 시작했어요! 정해진 시간이 지난 뒤에 아니 씨밧 카테고리의 아무 채널에나 메세지를 보내면 커뉴봇이 DM으로 오타 연구가 완료됐다고 알려줄 거에요.')
            stats = base64.b64encode(dumps(stats).encode("ascii"))
            db.record("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", stats, ctx.author.id)
            db.commit()
        else:
            return

    @command(name='ㅇ획득')
    async def gather_cvat(self, ctx):
        if ctx.channel.category.id != 916323967248248892:
            return
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        stats = loads(base64.b64decode(stats))
        if 'cvat_per_second' not in stats:
            return
        earned = int(min(stats['cvat_per_second'] * (time() - stats['cvat_gather_start']), stats['cvat_gather_max']))
        if stats['personal_setting'] & 256:
            earned *= 2
        stats['ani_cvat'] += earned
        tjfaud = f"{earned}만큼의 아니 씨밧을 벌어 현재 {stats['ani_cvat']} 만큼의 아니 씨밧을 가지게 되었어요!"
        check1 = 0
        if 'quarkgen_level' in stats:
            x = quarkgen_coefficients[stats['quarkgen_level']]
            if stats['typo_research'] & 1024 and stats['research_doing'] != 'ㅍ':
                x = x * 13 // 10
            if 'electric_gen' in stats:
                x -= 2000 * stats['electric_gen']
                stats['electric_saving'] += (time() - stats['cvat_gather_start']) * stats['electric_gen']
                if stats['electric_saving'] >= stats['electric_saving_max']:
                    stats['electric_saving'] = stats['electric_saving_max']
                    tjfaud += f' 또한 전력 비축량이 {stats["electric_saving"]}(저장할 수 있는 최댓값)까지 늘어났어요!'
                    if stats['electric_saving_max'] == 1e6:
                        stats['personal_setting'] += 32
                        check1 = 1
                        l = grant_check("피카츄?", ctx.author.id)
                        if l == 1:
                            await grant(ctx, "피카츄?", "처음으로 전력을 1000000까지 생산하세요\n\n`인게임 도전과제입니다.`", 1)
                else:
                    tjfaud += f' 또한 전력 비축량이 {stats["electric_saving"]}까지 늘어났어요!'
            stats['up_quark'] += (earned := min(x * (time() - stats['cvat_gather_start']), x * 10000) + max(0, x // 100000 * (time() - stats['cvat_gather_start'] - 10000)))
            stats['down_quark'] += earned
            tjfaud += f' 또한 업 쿼크와 다운 쿼크를 각각 {earned} 만큼 벌어 현재 업 쿼크와 다운 쿼크를 각각 {stats["up_quark"]}, {stats["down_quark"]} 만큼 가지게 됐어요!'
        if check1:
            tjfaud += '\n전력 1000000을 채웠으므로 우선 최대로 비축할 수 있는 전력의 양이 1500000까지 늘어나고, 오타 연구소에 새로운 연구들이 해금되는 데다가, 상점에도 새로운 아이템이 입고됩니다!'
            stats['electric_saving_max'] = 1500000
            stats['elecgen_capacity_cost'] = 20000
        await ctx.send(tjfaud)
        stats['cvat_gather_start'] = time()
        stats = base64.b64encode(dumps(stats).encode("ascii"))
        await asyncio.sleep(0.2)
        db.record("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", stats, ctx.author.id)
        db.commit()

    @command(name='ㅇ쿼크')
    async def quark(self, ctx):
        if ctx.channel.category.id != 916323967248248892:
            return
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        stats = loads(base64.b64decode(stats))
        if 'up_quark' not in stats:
            return
        tjfaud = ''
        for stat in stats:
            s = ''
            if stat == 'up_quark':
                s = '보유 중인 업 쿼크'
            elif stat == 'down_quark':
                s = '보유 중인 다운 쿼크'
            if s:
                tjfaud += f'\n{s}: {stats[stat]}'
        await ctx.send(embed=Embed(color=0xffd6fe, title='쿼크 정보', description=tjfaud))

    @command(name='ㅇ디버그')
    async def debug(self, ctx):
        if ctx.channel.category.id != 916323967248248892 or ctx.author.id != 724496900920705045:
            return
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        stats = base64.b64decode(stats)
        await ctx.send(stats.replace(b"'", b'"'))
        stats = loads(stats)
        stats['trading_next_refresh'] = time()
        stats = base64.b64encode(dumps(stats).encode("ascii"))
        db.record("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", stats, ctx.author.id)
        db.commit()

    @command(name='ㅇ합성')
    async def synthesize(self, ctx, a: Optional[str], amount: Optional[int]):
        if ctx.channel.category.id != 916323967248248892:
            return
        if not a:
            await ctx.send("합성할 물질을 정해주세요...")
            return
        if ctx.channel.category.id != 916323967248248892:
            return
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        stats = loads(base64.b64decode(stats))
        if stats['personal_setting'] & 2 == 0:
            return
        if a == '양성자':
            if (stats['up_quark'] < 2 * amount) or (stats['down_quark'] < amount):
                await ctx.send('양성자 하나는 업 쿼크 2개와 다운 쿼크 1개로 구성돼요...')
                return
            if 'proton' not in stats:
                stats['proton'] = amount
            else:
                stats['proton'] += amount
            stats['up_quark'] -= 2 * amount
            stats['down_quark'] -= amount
            await ctx.send(f'보유 중인 양성자의 개수를 {stats["proton"]}까지 늘렸어요')
        elif a == '중성자':
            if (stats['down_quark'] < 2 * amount) or (stats['up_quark'] < amount):
                await ctx.send('중성자 하나는 다운 쿼크 2개와 업 쿼크 1개로 구성돼요...')
                return
            if 'neutron' not in stats:
                stats['neutron'] = amount
            else:
                stats['neutron'] += amount
            stats['down_quark'] -= 2 * amount
            stats['up_quark'] -= amount
            await ctx.send(f'보유 중인 중성자의 개수를 {stats["neutron"]}까지 늘렸어요')
        elif a == '수소':
            if stats['proton'] < amount or stats['electron'] < amount:
                await ctx.send('수소 원자 하나는 양성자 하나와 전자 하나로 구성돼요...가끔 중수소가 나오는 건 보너스래요.')
                return
            h2 = amount // 6400
            h1 = amount - h2
            if '1h' not in stats:
                stats['1h'] = h1
            else:
                stats['1h'] += h1
            if '2h' not in stats:
                stats['2h'] = h2
            else:
                stats['2h'] += h2
            stats['proton'] -= amount
            stats['electron'] -= amount
            await ctx.send(f'보유 중인 경수소의 개수를 {stats["1h"]}, 중수소의 개수를 {stats["2h"]}까지 늘렸어요.')
        stats = base64.b64encode(dumps(stats).encode("ascii"))
        db.record("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", stats, ctx.author.id)
        db.commit()

    @command(name='ㅇ발전')
    async def make_electricity(self, ctx, rate: Optional[int] = -1):
        if ctx.channel.category.id != 916323967248248892:
            return
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        stats = loads(base64.b64decode(stats))
        if not stats['personal_setting'] & 64:
            return
        if stats['quarkgen_level'] == 0:
            return
        quarkgen_speed = quarkgen_coefficients[stats['quarkgen_level']]
        if stats['typo_research'] & 1024 and stats['research_doing'] != 'ㅍ':
            quarkgen_speed = quarkgen_speed * 13 // 10
        if rate < 0:
            embed = Embed(color=0xffff33, title='핵융합 발전',
                          description='핵융합 발전을 할 수 있어요. 1초당 업 쿼크와 다운 쿼크 각각 2000개를 사용해 전력 1만큼을 생산할 수 있어요.')
            embed.add_field(name='현재 초당 쿼크 증감량과 전력 생산량',
                            value=f'쿼크: 쿼크 추출기에 의해 +{quarkgen_speed}, 전력 생산에 의해 -{stats["electric_gen"] * 2000} -> 총합 {quarkgen_speed - stats["electric_gen"] * 2000}\n전기: 핵융합 발전소에 의해 {stats["electric_gen"]}')
            embed.set_footer(text='새로 얼만큼 발전할지를 정하려면 `ㅋㅇ발전 (초당전력)`\n처음으로 비축 가능한 전력을 가득 채웠을 때 좋은 일이 일어날 거에요!')
            await ctx.send(embed=embed)
        else:
            if rate * 2000 > quarkgen_speed:
                await ctx.send("아직은 쿼크 생산량을 초과할 정도로 많은 전력을 생산할 수 없어요! yonsei6 업데이트에서 만나요.")
                return
                # await ctx.send("이 정도로 많은 전력을 생산한다면 쿼크가 부족해질 수도 있어요. 그래도 이만큼의 전력을 생산하고 싶으시면 `설정`이라고 말해주세요.")
                # try:
                #     _ = await self.bot.wait_for(
                #         "message",
                #         timeout=30,
                #         check=lambda message: message.author == ctx.author and ctx.channel == message.channel and message.content == '설정'
                #     )
                # except asyncio.TimeoutError:
                #     await ctx.send("설정을 취소했어요.")
                #     return
            stats['electric_gen'] = rate
            stats_ = base64.b64encode(dumps(stats).encode("ascii"))
            db.execute("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", stats_, ctx.author.id)
            db.commit()
            await ctx.send('발전에 의한 전력 생산량을 바꿨어요!')

    @command(name='ㅇ업뎃', aliases=['ㅇ최근업뎃'])
    async def alpha_update(self, ctx):
        embed = Embed(color=0xffd6fe, title='yonsei1')
        embed.add_field(name='1. 새로운 기능',
                        value='더 나중 컨텐츠가 열리지만 스포이므로 말하지 않을게요',
                        inline=False)
        embed.add_field(name='2. 개선된 기능', value='`ㅋㅇ프로필` 명령어에서 자동 획득 아니 씨밧 부스트에 대한 보너스를 반영\n`ㅋㅇ거래` 명령어에서 거래 품목 개수가 1일 때 추가 거래 품목을 늘리는 거래를 제안할 확률 증가', inline=False)
        embed.add_field(name='3. 수정된 버그', value='`ㅋㅇ프로필` 명령어에서 일부 스탯이 표시되지 않던 버그 수정\n메타벗과 뇌저를 연구해도 `ㅋㅇ우주선`명령어가 제대로 작동하지 않던 버그 수정\n우주여행 도중 우주선의 남은 전력 값이 이상하게 표기되던 버그 수정',
                        inline=False)
        embed.set_footer(text='이전 업데이트 정보도 알고 싶다면 `커뉴야 업데이트 알파센타우리` (yonsei1 또는 그 이후의 업데이트만 알려줍니다)')
        await ctx.send(embed=embed)

    @command(name='ㅇ우주선')
    async def ani_cvat_spaceship(self, ctx, activity: Optional[str], activity2: Optional[str]):
        if ctx.channel.category.id != 916323967248248892:
            return
        activity = activity or '정보'
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        stats = loads(base64.b64decode(stats))
        if 'spaceship_level' not in stats:
            return
        if activity == '정보':
            embed = Embed(color=0x0f0f19, title='우주선 정보')
            if stats['spaceship_velocity'] == -1:
                embed.add_field(name='연료를 넣는 방법을 모르겠다!', value='아직 지식이 부족한데 음... 오타에 대해서 좀만 더 잘 알았어도...')
                await ctx.send(embed=embed)
                return
            else:
                destination = None
                if stats['spaceship_traveling']:
                    location = '우주 어딘가'
                    destination = stats['destination']
                else:
                    location = stats['location']
                embed.add_field(name='우주선 레벨', value=str(stats['spaceship_level']))
                embed.add_field(name='현재 위치', value=location)
                if destination:
                    embed.add_field(name='출발지', value=stats['location'])
                    embed.add_field(name='목적지', value=stats['destination'])
                embed.add_field(name='남은 전력', value=stats['spaceship_electricity'])
                embed.add_field(name='설정된 속력', value=f"{stats['spaceship_velocity']}v")
                embed.add_field(name='초당 소모하는 전력', value=stats['spaceship_elec_consumption'])
                await ctx.send(embed=embed)
        else:
            if stats['spaceship_velocity'] == -1:
                return
            elif activity == '충전':
                if not activity2 or not activity2.isdigit():
                    await ctx.send("`ㅋㅇ우주선 충전 (충전할 전기)`")
                    return
                activity2 = int(activity2)
                if activity2 > stats['electric_saving']:
                    activity2 = stats['electric_saving']
                stats['electric_saving'] -= activity2
                stats['spaceship_electricity'] += activity2
                await ctx.send(f'우주선에 전력을 {activity2}만큼 충전해 {stats["spaceship_electricity"]}만큼이 됐어요!')
            elif activity == '속력':
                if not activity2 or not activity2.isdigit():
                    await ctx.send('`ㅋㅇ우주선 속력 (속력)`')
                    return
                activity2 = int(activity2)
                stats['spaceship_velocity'] = activity2
                if stats['typo_research'] & 1024 and stats['research_doing'] != 'ㅍ':
                    stats['spaceship_velocity'] = stats['spaceship_velocity'] * 6 // 5
                stats['spaceship_elec_consumption'] = round((activity2 / 50) ** 2.5)
                await ctx.send(
                    f'속력을 {stats["spaceship_velocity"]}v로 변경했어요! 그에 따라 우주선을 운행하는 도중 초당 소모하는 전력이 {round((activity2 / 50) ** 2.5)}로 바뀌었어요!')
            elif activity == '출발':
                if not stats['spaceship_traveling']:
                    if not activity2:
                        if 'known_locations' not in stats:
                            destination = 'proxima_b'
                        else:
                            await ctx.send('`ㅋㅇ우주선 출발 (목적지)`')
                            return
                    else:
                        return  # todo 목적지를 직접 설정할 때 코드는 여기로
                    if stats['spaceship_velocity'] == 0:
                        await ctx.send('먼저 `ㅋㅇ우주선 속력 (속력)`으로 우주선의 속력을 결정해 주세요!')
                        return
                    if 'known_locations' in stats:
                        embed = Embed(color=0x0f0f19, title='우주선 출발 예정',
                                      description=f'{destination} 지역으로 출발할 예정이에요. 이번 여행에 관한 정보를 표시할테니 꼼꼼히 확인하세요.\n\n설정된 우주선 속력: {stats["spaceship_velocity"]}, 초당 소모하는 전력 {stats["spaceship_elec_consumption"]}\n\n목적지까지의 거리: 10000000, 걸리는 시간 {10000000 / stats["spaceship_velocity"]} -> 총 소모 전력 {stats["spaceship_elec_consumption"] * 10000000 / stats["spaceship_velocity"]}\n\n`출발`이라고 입력해 출발하세요\n만약 가는 도중 전력이 바닥난다면, 우주선은 그래도 나아가지만 속력이 매우 느려질 거에요...')
                    else:
                        embed = Embed(color=0x0f0f19, title='우주선 출발 예정',
                                      description=f'다른 곳으로 출발할 예정이에요. 이번 여행에 관한 정보를 표시할테니 꼼꼼히 확인하세요.\n\n설정된 우주선 속력: {stats["spaceship_velocity"]}, 초당 소모하는 전력 {stats["spaceship_elec_consumption"]}\n\n목적지까지의 거리: ?, 걸리는 시간 ? -> 총 소모 전력 ?\n\n`출발`이라고 입력해 출발하세요\n최소 수백만 전력 정도는 모아서 출발하시는 걸 추천드려요..')
                    await ctx.send(embed=embed)
                    try:
                        go = await self.bot.wait_for(
                            "message",
                            timeout=60,
                            check=lambda
                                message: message.author == ctx.author and ctx.channel == message.channel and message.content == '출발'
                        )
                    except asyncio.TimeoutError:
                        await ctx.send("출발하지 않기로 했어요.")
                        return
                    await ctx.send('성공적으로 출발했어요!')
                    stats['destination'] = destination
                    stats['spaceship_traveling'] = True
                    stats['spaceship_electricity'] -= int(
                        stats["spaceship_elec_consumption"] * 10000000 / stats["spaceship_velocity"])
                    stats['arrival_time'] = time() + 10000000 / stats["spaceship_velocity"]
                    if stats['spaceship_electricity'] < 0:
                        excess_time = -stats['spaceship_electricity'] / stats["spaceship_elec_consumption"]
                        stats['arrival_time'] += excess_time * 99
                else:
                    await ctx.send('이미 어딘가를 향해 가는 중이에요...')
                    return
            stats_ = base64.b64encode(dumps(stats).encode("ascii"))
            db.execute("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", stats_, ctx.author.id)
            db.commit()

    @command(name='ㅇ거래')
    async def aldebarak_trade(self, ctx, activity: str = ''):
        if ctx.channel.category.id != 916323967248248892:
            return
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        stats = loads(base64.b64decode(stats))
        if 'trading_level' not in stats:
            return
        if stats['trading_level'] == 0:
            embed = Embed(title='dHJhZGU=',
                          description='633256755A4342446232355649487071633249675A47316B625738676447686C6269424A49486470624777675A326C325A534235623355674D79427261336C314C69424A5A694235623355675A326C325A5342745A5341314D444177494746756156396A646D46304C4342306147567549456B6764326C736243426E61585A6C49486C7664584967633268766343426849484E775A574E70595777676158526C62534268626D51675A326C325A534235623355675953427A614746795A4342765A6942686247526C596D46795957733D')
            await ctx.send('`거래`라고 입력해 거래를 진행하세요.', embed=embed)
            try:
                go = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda
                        message: message.author == ctx.author and ctx.channel == message.channel and message.content == '거래'
                )
            except asyncio.TimeoutError:
                await ctx.send("거래하지 않기로 했어요.")
                return
            if stats['trading_level'] == 0:
                if stats['ani_cvat'] < 5000:
                    await ctx.send('거래에 필요한 5000 아니 씨밧을 가지고 있지 않아요!')
                    return
            stats['ani_cvat'] -= 5000
            stats['aldebarak_shard'] = 1
            await ctx.send('거래를 완료했어요!')
        else:
            if not activity:
                check = 1
                if 'trading_current' not in stats:
                    await ctx.author.send('인사가 늦었습니다! 알데바락 우주센터와 당신을 이어 줄 거래상입니다. 알데바락 우주센터 세력과 저는 엄청 큰 연관이 있는 관계는 '
                                          '아니지만, 알데바락 우주센터에서 저에게 월급을 줄 테니 프록시마b에 오는 방문객에게 물건을 팔아달라고 부탁했어요. 우선 저희 상점을 '
                                          '소개할게요.\n`ㅋㅇ거래`를 사용하시면, 보다시피 지금 팔고 있는 거래 상품을 볼 수 있어요.\n`ㅋㅇ거래 정보`를 사용하시면, '
                                          '거래에 관련된 여러 가지 정보를 확인하실 수 있어요.\n`ㅋㅇ거래 n`을 사용하시면, n번으로 라벨링되어 있는 아이템을 구매하실 수 '
                                          '있어요.\n`ㅋㅇ거래 새로고침`을 사용하시면, 거래 품목을 바꿀 수 있어요. 다만 명령어를 사용하실 때마다 바뀌는 건 아니고 상당히 '
                                          '긴 쿨타임을 가지고 있어요.\n왜 `ㅋㅇ거래 구매`가 아니라 `ㅋㅇ거래 n`이냐고요? 저와 거래를 많이 하면 알려드리죠.')
                    stats['trading_current'] = trade_refresh(stats)
                    stats['trading_count'] = 0
                    check = 0
                embed = Embed(color=0xffd6fe, title='거래 가능한 품목', description='`ㅋㅇ거래 n`으로 n번 아이템을 거래하세요')
                for i in range(1, stats['trading_slot'] + 1):
                    try:
                        embed.add_field(name=str(i), value=trade_item_visual[stats['trading_current'][i-1]])
                    except TypeError:
                        embed.add_field(name=str(i), value='이미 거래 완료된 아이템이에요!')
                await ctx.send(embed=embed)
                if check:
                    return
            elif activity == '새로고침':
                refresh_cool = stats['trading_next_refresh'] - time()
                if refresh_cool > 0:
                    h, m, s = int(refresh_cool) // 3600, (int(refresh_cool) % 3600) // 60, int(refresh_cool) % 60
                    await ctx.send(f'다음 새로고침은 약 {h}시간 {m}분 {s}초 뒤에 할 수 있어요!')
                    return
                stats['trading_current'] = trade_refresh(stats)
                stats['trading_next_refresh'] = time() + stats['trading_cooldown']
                await ctx.send('새로고침을 완료했어요!')
            elif activity == '정보':
                embed = Embed(color=0xffd6fe, title='거래 정보')
                embed.add_field(name='현재까지 거래한 횟수', value=stats['trading_count'])
                refresh_cool = stats['trading_next_refresh'] - time()
                if refresh_cool > 0:
                    h, m, s = int(refresh_cool) // 3600, (int(refresh_cool) % 3600) // 60, int(refresh_cool) % 60
                    embed.add_field(name='다음 새로고침까지 남은 시간', value=f'약 {h}시간 {m}분 {s}초')
                else:
                    embed.add_field(name='다음 새로고침까지 남은 시간', value='지금 새로고침 가능')
                embed.add_field(name='거래 레벨', value=stats['trading_level'])
                embed.add_field(name='새로고침당 얻을 수 있는 거래 품목 개수', value=stats['trading_slot'])
                await ctx.send(embed=embed)
                return
            elif activity.isdigit():
                activity = int(activity)
                if activity > stats['trading_slot']:
                    await ctx.send('잘못된 번호를 입력했어요!')
                    return
                activity -= 1
                item = stats['trading_current'][activity]
                if item is None:
                    await ctx.send('이미 진행한 거래에요! 할 수 있는 거래를 다 한 상태라면 `ㅋㅇ거래 새로고침`으로 새로운 거래 아이템을 받으셔야 돼요.')
                    return
                if item == 0:
                    if stats['ani_cvat'] < 5000:
                        await ctx.send('제가 가져갈 5000 아니 씨밧은 어디 있죠?')
                        return
                    stats['ani_cvat'] -= 5000
                    stats['aldebarak_shard'] += 1
                    await ctx.send('알데바락의 조각이에요. 가져가세요!')
                elif item == 1:
                    if stats['ani_cvat'] < 3000:
                        await ctx.send('제가 가져갈 3000 아니 씨밧은 어디 있죠?')
                        return
                    stats['ani_cvat'] -= 3000
                    stats['aldebarak_shard'] += 1
                    await ctx.send('알데바락 조각이에요. 가져가세요!')
                elif item == 2:
                    if stats['aldebarak_shard'] < 20:
                        await ctx.send('제가 가져갈 20 알데바락의 조각은 어디 있죠?')
                        return
                    stats['aldebarak_shard'] -= 20
                    stats['trading_slot'] += 1
                    await ctx.send('좋아요! 다음 새로고침 때부터는 한 번에 두 아이템을 제시해 드릴게요. 거기에다가 새로운 오타 하나를 연구하실 수도 있어요!')
                elif item == 3:
                    if stats['ani_cvat'] < 50000:
                        await ctx.send('제가 가져갈 50000 아니 씨밧은 어디 있죠?')
                        return
                    stats['ani_cvat'] -= 50000
                    stats['trading_cooldown'] = 3600 * 7
                    await ctx.send('좋아요! 다음 새로고침 때부터는 새로고침에 필요한 쿨타임을 줄여 드릴게요.')
                elif item == 4:
                    if stats['ani_cvat'] < 100000:
                        await ctx.send('제가 가져갈 100000 아니 씨밧은 어디 있죠?')
                        return
                    stats['ani_cvat'] -= 100000
                    stats['trading_cooldown'] = 3600 * 6
                    await ctx.send('좋아요! 다음 새로고침 때부터는 새로고침에 필요한 쿨타임을 줄여 드릴게요.')
                elif item == 5:
                    if stats['ani_cvat'] < 100000 or stats['aldebarak_shard'] < 50:
                        await ctx.send('제가 가져갈 100000 아니 씨밧과 50 알데바락의 조각은 어디 있죠?')
                        return
                    stats['ani_cvat'] -= 100000
                    stats['aldebarak_shard'] -= 50
                    stats['trading_cooldown'] = 3600 * 5
                    await ctx.send('좋아요! 다음 새로고침 때부터는 새로고침에 필요한 쿨타임을 줄여 드릴게요.')
                elif item == 6:
                    if stats['ani_cvat'] < 5000:
                        await ctx.send('제가 가져갈 5000 아니 씨밧은 어디 있죠?')
                        return
                    x = randint(0, 1)
                    if not x:
                        await ctx.send('5000 아니 씨밧 감사합니다!')
                        stats['ani_cvat'] -= 5000
                    else:
                        await ctx.send('운이 좋으신데요? 5000 아니 씨밧을 가져가세요!')
                        stats['ani_cvat'] += 5000
                elif item == 7:
                    if stats['aldebarak_shard'] < 10:
                        await ctx.send('제가 가져갈 10 알데바락의 조각은 어디 있죠?')
                        return
                    stats['aldebarak_shard'] -= 10
                    stats['trading_progress'] = 0
                    await ctx.send('좋아요! 상점에 방문해 보세요.')
                elif item == 8:
                    if stats['aldebarak_shard'] < 10:
                        await ctx.send('제가 가져갈 10 알데바락의 조각은 어디 있죠?')
                        return
                    stats['aldebarak_shard'] -= 10
                    if 'pollux_shard' not in stats:
                        stats['pollux_shard'] = 1
                    else:
                        stats['pollux_shard'] += 1
                    await ctx.send('폴룩스의 조각이에요. 귀한 거니까 조심히 가져가세요!')
                elif item == 9:
                    if stats['ani_cvat'] < 7000:
                        await ctx.send('제가 가져갈 7000 아니 씨밧은 어디 있죠?')
                        return
                    if stats['destination'] is not None:
                        await ctx.send('우주여행 도중에는 저희도 거래하기가 힘들어요... 내려서 거래해 주시면 충전해 드릴게요!')
                        return
                    stats['ani_cvat'] -= 7000
                    stats['spaceship_electricity'] += 1000000
                    await ctx.send('좋아요! 제대로 충전했어요.')
                elif item == 10:
                    if stats['aldebarak_shard'] < 250:
                        await ctx.send('제가 가져갈 250 알데바락의 조각은 어디 있죠?')
                        return
                    stats['aldebarak_shard'] -= 250
                    stats['trading_slot'] += 1
                    await ctx.send('250 알데바락의 조각은 저희에게도 큰 돈이에요! 다음 새로고침 때부터 한 번에 세 개의 아이템이나 거래할 수 있게 돼요.')
                stats['trading_current'][activity] = None
                stats['trading_count'] += 1
                if stats['trading_count'] == 100:
                    l = grant_check("활발한 거래자", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "활발한 거래자", "알데바락 우주센터와 100회 이상 성공적으로 거래하세요\n\n`인게임 도전과제입니다.`", 1)
            else:
                await ctx.send('올바르지 않은 명령어에요!')
                return
        stats_ = base64.b64encode(dumps(stats).encode("ascii"))
        db.execute("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", stats_, ctx.author.id)
        db.commit()

    @command(name='ㅇ도움')
    async def ani_cvat_help(self, ctx, *, content: Optional[str]):
        try:
            stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", ctx.author.id)[0]
        except:
            return
        stats = loads(base64.b64decode(stats))
        available_commands = ['프로필', '상점', '구매']
        available_features = ['알파 센타우리', '아니 씨밧']
        if 'personal_setting' in stats and stats['personal_setting'] & 1 == 1:
            available_commands.append('연구')
            available_features.append('오타 연구소')
        if 'cvat_per_second' in stats:
            available_commands.append('획득')
        if 'up_quark' in stats:
            available_commands.append('쿼크')
            available_features.append('업 쿼크')
            available_features.append('다운 쿼크')
        if stats['personal_setting'] & 2:
            available_commands.append('합성')
            available_features += ['양성자', '중성자', '수소']
        if stats['personal_setting'] & 4 == 4:
            available_features.append('쿼크 추출기')
        if stats['personal_setting'] & 64:
            available_commands.append('발전')
            available_features.append('토륨')
            available_features.append('전력')
        if 'spaceship_level' in stats:
            available_commands.append('우주선')
        if 'known_location' in stats:
            available_features.append('프록시마b')
        if stats['typo_research'] & 512:
            available_features.append('알데바락 우주센터')
        if 'trading_level' in stats:
            available_commands.append('거래')
        if 'aldebarak_shard' in stats:
            available_features.append('알데바락의 조각')
        if 'pollux_shard' in stats:
            available_features.append('폴룩스의 조각')
        if not content:
            embed = Embed(color=0xffd6fe, title='알파 센타우리 도움',
                          description='게임을 진행해나갈수록 더 많은 것들이 여기에 표시됩니다. `ㅋㅇ도움 (컨텐츠)`로 자세히 알아보세요!')
            if ctx.channel.category.id != 916323967248248892:
                embed.set_footer(
                    text='채널 안에서만 실행 가능한 명령어이므로 이곳에서는 아무것도 뜨지 않습니다. 바깥 분들께 컨텐츠를 스포하면 안 되죠.\n게임 구입은 `커뉴야 뀨 구매 알파 센타우리`')
                await ctx.send(embed=embed)
                return
            embed.add_field(name='사용 가능한 명령어', value=', '.join(available_commands), inline=False)
            embed.add_field(name='명령어는 아닌 게임 요소들', value=', '.join(available_features), inline=False)
            await ctx.send(embed=embed)
        else:
            if content in available_commands:
                embed = Embed(color=0xffd6fe, title=f'알파 센타우리 명령어 도움')
            elif content in available_features:
                embed = Embed(color=0xffd6fe, title=f'알파 센타우리 게임 요소 도움')
            else:
                return
            helps = {'프로필': '현재 자신의 게임 진행도를 알아볼 수 있는 명령어입니다.\n사용법: `ㅋㅇ프로필`',
                     '상점': '아니 씨밧을 비롯한 다양한 재화로 아이템들을 구매합니다. 구매 가능한 아이템만 표시됩니다.\n사용법: `ㅋㅇ상점`',
                     '구매': '상점에서 구매 가능한 아이템을 구매합니다.\n사용법: `ㅋㅇ구매 (아이템명)`',
                     '알파 센타우리': '적경: 14h 39m 36.49s, 적위: –60° 50′ 02.37, 지구로부터 거리: 대략 4.4ly\n게임은 이곳을 공전하는 한 천체에서 시작됩니다.',
                     '아니 씨밧': '알파 센타우리의 가장 기본적인 재화이자 가장 쓰임새가 많은 재화이기도 합니다. 아니 씨밧!',
                     '연구': '오타 연구소에서 연구할 수 있는 오타들을 확인하고 연구합니다.\n사용법: `ㅋㅇ연구`, 명령어 실행 이후 연구하고자 하는 오타의 이름을 말해 주시면 됩니다.',
                     '오타 연구소': '우주의 비밀을 풀어나가는 오타 연구소로, 우주 구석구석에 숨어 있던 오타들을 발굴하며 연구하는 곳입니다. 오타를 발굴한다는 게 무슨 말인지 의아해하실 수도 있지만, 최근에도 몇 년 전 오타들이 우연히 발견된다네요.',
                     '획득': '처음에는 아니 씨밧을, 게임을 진행할수록 아니 씨밧에 더해 다른 것들까지, 당신이 없는 동안 자동으로 생산된 것들을 획득하는 명령어입니다.\n사용법: `ㅋㅇ획득`',
                     '쿼크': '우주를 이루는 정말, 정말 작은 입자들입니다. 쿼크는 총 6종류가 있다고 하네요. 이 입자들을 얼마나 쌓아 놓고 있는지를 확인합니다.\n사용법: `ㅋㅇ쿼크`',
                     '업 쿼크': '6종류의 쿼크들 중 하나로 +2/3의 전하량을 가지고 있습니다.',
                     '다운 쿼크': '6종류의 쿼크들 중 하나로 -1/3의 전하량을 가지고 있습니다.',
                     '합성': '`ㅋㅇ발전`등의 명령어가 해금되면 쓸 일이 없어지겠지만, 자신이 직접 입자들을 합성할 수 있는 명령어입니다.\n사용법: `ㅋㅇ합성 (합성할것) (합성할양)`',
                     '양성자': '원자핵을 이루는 입자로, 원자 번호는 양성자의 개수에 따라 정해집니다. 양성자 하나는 업 쿼크 2개와 다운 쿼크 1개로 이루어져 있습니다.',
                     '중성자': '원자핵을 이루는 입자로, 같은 수의 양성자를 가지고 있어도 중성자의 개수가 다를 수 있습니다. 그런 것들을 동위원소라고 부릅니다. 중성자 하나는 업 쿼크 1개와 다운 쿼크 2개로 이루어져 있습니다.',
                     '수소': '우주에서 가장 흔히 볼 수 있는 원소입니다. 가장 흔한 경수소는 양성자 하나와 중성자 하나와 전자 하나로 이루어져 있습니다.',
                     '쿼크 추출기': '최소한 이곳에서는 우주를 돌아다니는 쿼크들이 많이 존재한다고 합니다. 이 쿼크들을 그대로 놔두지 않고 포집하겠다는 것이 쿼크 추출기의 목표입니다. 초기 모델은 속도도 느리고 쿼크만 가져오지만, 발전된 모델은 그렇지 않습니다.',
                     '발전': '발전소를 돌려 전기를 만들 수 있는 명령어입니다.\n`ㅋㅇ발전`: 현재 상태를 확인합니다.\n`ㅋㅇ발전 (초당전력)`: 초당 얼마의 전력을 생산할지를 바꿉니다. 자신의 현재 상태에 따라 초당 최대로 생산할 수 있는 전력의 양이 달라집니다.',
                     '토륨': '원자 번호 90번의 무거운 원소입니다. 이곳의 핵융합 발전소는 특이하게도 토륨을 분열시켜 나오는 열로 미핀 불꽃놀이를 가동해 온도를 10억 도까지 올려 핵융합 발전을 한다고 합니다.',
                     '전력': '앞으로 많은 것들에 쓰이겠지만, 계속 만들어주어야 합니다.',
                     '우주선': 'cosmic ray가 아닌 spaceship입니다.\n`ㅋㅇ우주선` 또는 `ㅋㅇ우주선 정보`: 현재 우주선의 정보를 확인합니다. 지식이 부족할 경우 일부 정보만 확인될 수도 있습니다.\n스포는 "뇌저"연구 이후 확인하는 것을 추천합니다. ||`ㅋㅇ우주선 충전`: 우주선에 전력을 충전합니다. `ㅋㅇ우주선 출발 (목적지)`: (목적지)로 출발합니다. `ㅋㅇ우주선 속력 (속력)`: 우주선이 얼마나 빠르게 움직일지 정합니다. 빠르게 움직일수록 더 많은 전력을 소모합니다.||',
                     '프록시마b': '프록시마 센타우리 별을 공전하는 한 행성으로, 생명체 거주 가능성이 있다고 판단되는 곳입니다. 과연 실제로 이곳에서 생명체를 찾을 수 있을까요?',
                     '알데바락 우주센터': '메타벗에 상당한 영향을 미치고 있는 것으로 알려진 세력입니다. 메타벗과 그 비밀을 푸는 서준의 오타를 발견하고 연구하는 데 상당히 큰 공을 세운 곳이라고 하네요. 센터 본부는 알데바락 주변에 위치한다고 알려져 있는데, 언젠가 그곳에 찾아가볼 수 있지 않을까요?',
                     '거래': '알데바락 우주센터와 거래합니다. 그런데 정말로 알데바락 우주센터와 거래하는 걸까요?',
                     '알데바락의 조각': '알데바락 우주센터에서 흔하게 발견되는 물건입니다. 그러나 알데바락 우주센터 바깥에서는 그리 흔하게 발견되지는 않는 것 같네요. 알데바락의 조각 자체가 무언가 대단한 걸 하지는 않지만, 알데바락의 조각은 우주 곳곳에서 화폐로 쓰인다고 합니다! 심지어 커뉴핑크에서도...',
                     '폴룩스의 조각': '알데바락 우주센터에서 희귀하게 취급되는 물건입니다. 저 먼 곳에 폴룩스라는 별이 있다네요. 이 물건은 알데바락의 조각과 다르게 무언가 대단한 걸 한다고 알려져 있습니다.'}
            embed.add_field(name=content, value=helps[content])
            await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("alpha")

    @Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel,
                      DMChannel) or message.author.bot or not message.channel.category or message.channel.category.id != 916323967248248892:
            return
        l = grant_check("알파 센타우리 접근자", message.author.id)
        if l == 1:
            await grant(message, "알파 센타우리 접근자", "게임을 시작하세요...\n\n`인게임 도전과제입니다.`", 1)
            initial_data = base64.b64encode(dumps({'ani_cvat': 0, 'next_cvat_gain': time(), 'cvat_per_message': 30,
                                                   'cvat_gain_upgrade_cost': 100}).encode("ascii"))
            db.execute("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", initial_data, message.author.id)
            db.commit()
            await message.author.send("**아니 씨밧**\n아니 씨밧 월드에 오신 걸 환영합니다.\n이곳에 처음 오셨을 때의 목표는 2000 아니 씨밧을 모으는 것입니다. 채팅을 "
                                      "치고 상점의 업그레이드를 구매해 2000 아니 씨밧을 모아 보세요!")
        await self.gain_cvat(message.author.id, message)

    async def gain_cvat(self, uid, message):
        stats = db.record("SELECT alpha_centauri FROM games WHERE UseriD = ?", uid)[0]
        stats = loads(base64.b64decode(stats))
        if time() > stats["next_cvat_gain"]:
            stats["ani_cvat"] += (s := stats["cvat_per_message"]) + randint(-int(s / 5), int(s / 5))
            stats["next_cvat_gain"] = time() + 60
            stats_ = base64.b64encode(dumps(stats).encode("ascii"))
            db.execute("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", stats_, uid)
            db.commit()
            if stats["ani_cvat"] >= 2000:
                l = grant_check("연구 입문자", message.author.id)
                if l == 1:
                    await grant(message, "연구 입문자", "2000 아니 씨밧을 모아 연구를 시작하세요\n\n`인게임 도전과제입니다.`", 1)
                    await message.author.send("2000 아니 씨밧을 모아 연구를 시작할 수 있게 되었습니다.\n `ㅋㅇ상점` 명령어에 오타ㅏ 연구소가 새로 입고되었습니다!")
        if 'research_end' in stats and time() > stats['research_end']:
            if stats['research_doing'] == "피겅":
                await message.author.send(
                    "피겅 연구 완료! 이제부터 쿼크를 만들 수 있게 됩니다. `ㅋㅇ쿼크`로 확인하세요\nhttps://media.discordapp.net/attachments/815416004480860160/898010435419246612/VLRJD.png")
                stats['up_quark'] = 2000000000
                stats['down_quark'] = 2000000000
            elif stats['research_doing'] == "피곦":
                await message.author.send(
                    "피곦 연구 완료! 이제부터 쿼크를 모아 양성자와 중성자로 만들 수 있게 됩니다. `ㅋㅇ합성`으로 확인하세요\nhttps://media.discordapp.net/attachments/770644244658389022/898013788190670908/unknown.png")
                stats['personal_setting'] += 2
                l = grant_check("진정한 시작", message.author.id)
                if l == 1:
                    await grant(message, "진정한 시작", "오타 연구소에서 피곦을 연구하세요\n\n`인게임 도전과제입니다.`", 1)
            elif stats['research_doing'] == 'h':
                await message.author.send(
                    "h 연구 완료! 이제 전자와 수소를 자유자재로 다룰 수 있게 됩니다. `ㅋㅇ합성 수소`가 해금됩니다.\nhttps://media.discordapp.net/attachments/773409630125817887/939138519534817390/weary_-_we_2_weary_-_4_-_h.png?width=854&height=670")
                stats['electron'] = 1000000000
            elif stats['research_doing'] == '🎆':
                await message.author.send(
                    "🎆 연구 완료! 이제 핵융합 발전을 할 수 있게 될까요?\n상점에 핵융합 발전소를 비롯한 다양한 것들이 입고됩니다...\nhttps://media.discordapp.net/attachments/749224990209212419/941988129194254377/fireworks.png?width=596&height=670")
                stats['personal_setting'] += 4
            elif stats['research_doing'] == ';TH':
                await message.author.send(
                    ";TH 연구 완료! 이제 토륨을 다룰 수 있게 되어 진짜로 핵융합 발전을 할 수 있게 됩니다. 또한 토륨 원자 1000000개를 획득합니다.\n도대체 양성자 90개짜리 원소로 핵융합 발전을 한다는 게 뭔 개소리\nhttps://cdn.discordapp.com/attachments/773409630125817887/1003196775374524426/thinking_-_TH.png")
                stats['personal_setting'] += 8
                stats['90th'] = 1000000
            elif stats['research_doing'] == '뭉탱태':
                await message.author.send(
                    "뭉탱태 연구 완료! 이제 더욱 발전된 쿼크 추출기가 상점에 입고됩니다.\nhttps://cdn.discordapp.com/attachments/749224990209212419/1203978395009163274/-_.png?ex=65d30f42&is=65c09a42&hm=e976aeca0ba3f4fd41bd6c757a686fd7ff8e529f8a22f064962fd0fa33f07c5b&")
                stats['research_end'] = 2147483647
            elif stats['research_doing'] == '메타벗':
                await message.author.send(
                    "메타벗 연구 완료! 음... 저 옆에 큰 게 설마 우주선인가요? `ㅋㅇ우주선`이라는 명령어도 있는 것 같네요!\nhttps://cdn.discordapp.com/attachments/749224990209212419/1204007058819780618/-_.png?ex=65d329f4&is=65c0b4f4&hm=28adccaa2b50df562710716a592ee20e463b0524cbe57235dca080e6390672dc&")
                stats['personal_setting'] += 128
                stats['location'] = 'alpha_centauri'
                stats['spaceship_level'] = 1
                if not stats['personal_setting'] & 256:
                    stats['spaceship_velocity'] = -1
                stats['spaceship_traveling'] = False
            elif stats['research_doing'] == '뇌저':
                await message.author.send(
                    "뇌저 연구 완료! 그런데 이런 기술을 어디에 쓸까요...?\nhttps://cdn.discordapp.com/attachments/749224990209212419/1204062227137691729/-_.png?ex=65d35d55&is=65c0e855&hm=d8a5d3e12b13d4aee038757e458f800a3500c7006e2a0a1a700bf15706217453&\n사진에 이상한 게 숨어 있다고요? 느가 카가 다가 니기 마가3")
                stats['spaceship_velocity'] = 0
                stats['spaceship_electricity'] = 0
                stats['spaceship_elec_consumption'] = 0
            elif stats['research_doing'] == '알데바락이 뭔가요?':
                await message.author.send(
                    "알데바락이 뭔가요? 연구 완료! 왜인지 알데바락 우주센터에서 당신에게 신호를 보내는 것 같습니다.\n`ㅋㅇ거래` 명령어를 새로 사용해 보라는데요...?\nhttps://cdn.discordapp.com/attachments/794563329560674344/1008294851340668998/Screenshot_20220814-174340_Discord.jpg?ex=65d1c341&is=65bf4e41&hm=3345f18f78dbb15e0656fe488286feb495fdec10048323a7c123c607ea0a3213&")
                stats['trading_level'] = 0
                stats['trading_slot'] = 1
                stats['trading_cooldown'] = 9999999
                stats['trading_next_refresh'] = time() + stats['trading_cooldown']
            elif stats['research_doing'] == 'ㅍ':
                await message.author.send(
                    "ㅍ 연구 완료! 컨트롤 v의 마인드를 담아 앞으로 쿼크 생산량이 30%만큼 늘어나며 우주선의 속도가 20%만큼 늘어납니다. 게다가 새로운 오타에 대한 지식도 알 것 같네요!\nhttps://cdn.discordapp.com/attachments/749224990209212419/1218918653983195146/weary_-_.png?ex=66096975&is=65f6f475&hm=d6c0b813f492d96c27e50ce68f7088319bec5b7be9fa6d2ec84f8b3beb6a9fd6&"
                )
            elif stats['research_doing'] == '유링겟ㅍㅇ':
                await message.author.send(
                    "유링겟ㅍㅇ 연구 완료! 이제 더더욱 발전된 쿼크 추출기가 상점에 입고됩니다.\nhttps://cdn.discordapp.com/attachments/770644244658389022/898016831997104209/unknown.png?ex=6604c559&is=65f25059&hm=952d0afc1bde2ba905449ecaa5af0e9330a8b07618d3d81dd74897e3b620ce6a&"
                )
                stats['personal_setting'] += 1024
            stats['research_doing'] = '없음'
            stats['research_end'] = 2147483647
            stats_ = base64.b64encode(dumps(stats).encode("ascii"))
            db.execute("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", stats_, uid)
            db.commit()
        if 'arrival_time' in stats and time() > stats['arrival_time']:
            embed = Embed(color=0xffd6fe, title='우주선이 도착했습니다!')
            embed.add_field(name='도착 장소', value=stats['destination'], inline=False)
            if stats['spaceship_electricity'] < 0:
                stats['spaceship_electricity'] = 0
                embed.add_field(name='남은 전력', value='우주선이 자동으로 전력 절약 모드에 들어가서 이 정보는 표시되지 않아요!', inline=False)
            embed.add_field(name='남은 전력', value='약' + str(stats['spaceship_electricity'] + int(stats['arrival_time'] - time()) * stats['spaceship_elec_consumption']), inline=False)
            l = grant_check("프록시마b", message.author.id)
            if l == 1:
                await grant(message, "프록시마b", "프록시마b에 도착하세요\n\n`인게임 도전과제입니다.`", 1)
                await self.bot.get_channel(918505828716265472).set_permissions(message.author, read_messages=True)
                await message.author.send(
                    '우주선이 새로운 곳에 도착했어요. <#918505828716265472>에 가 보세요!\n\n프록시마b에 도착하니까 상점에서 새로운 것들을 팔기 시작했어요. 얼른 사 보세요!')
                stats['known_locations'] = ['alpha_centauri', 'proxima_b']
                stats['personal_setting'] += 16
            stats['arrival_time'] = 2147483647
            stats['location'] = stats['destination']
            stats['destination'] = None
            stats['spaceship_traveling'] = False
            await message.channel.send(embed=embed)
            stats_ = base64.b64encode(dumps(stats).encode("ascii"))
            db.execute("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", stats_, uid)
            db.commit()


async def end_purchase(stats, ctx):
    stats = base64.b64encode(dumps(stats).encode("ascii"))
    db.record("UPDATE games SET alpha_centauri = ? WHERE UserID = ?", stats, ctx.author.id)
    db.commit()
    await ctx.send("구매 완료!")
    return


def setup(bot):
    bot.add_cog(Alpha(bot))