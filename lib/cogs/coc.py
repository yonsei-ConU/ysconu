import asyncio
from typing import Optional

from discord import Embed
from discord.ext.commands import Cog, command, cooldown, BucketType, max_concurrency
from ..db import db
import requests
from math import ceil, tan, pi, e, sqrt
from collections import deque, defaultdict
from datetime import datetime

headers = {
    'Authorization': 'Bearer '
                     'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjQxZWUzY2I3LWQwNjItNGMzMC1hYzJkLTMzNWMwZjYxMGY5OSIsImlhdCI6MTcwMjg3MzM3Mywic3ViIjoiZGV2ZWxvcGVyLzBiMDQ3MGY5LWUxODEtNTg2YS0zNjdkLWUzZGY3YWNjYmRlMyIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjIxMC4yMjEuMTcuMTMiXSwidHlwZSI6ImNsaWVudCJ9XX0.8rap51PWgENKDetjCr-yaz7_mfWttRe3tH2UttbZdm9tOrJonAp2NWyZHs3lX9AMKnHqWEbu89d-JVDNrizfXQ '
}
yonseiblue = 0x003876


def sgn(x):
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def get_clan(tag):
    return requests.get(f'https://api.clashofclans.com/v1/clans/%23{tag}', headers=headers).json()


def get_clan_members(tag):
    return requests.get(f'https://api.clashofclans.com/v1/clans/%23{tag}/members', headers=headers).json()


def get_clan_war(tag):
    return requests.get(f'https://api.clashofclans.com/v1/clans/%23{tag}/currentwar', headers=headers).json()


def get_clan_raid(tag):
    return requests.get(f'https://api.clashofclans.com/v1/clans/%23{tag}/capitalraidseasons?limit=1',
                        headers=headers).json()


def clan_member_refresh(clan_tag):
    clan_members = get_clan_members(clan_tag)
    temp = db.records("SELECT user_tag FROM clash_of_clans WHERE clan_tag = ?", clan_tag)
    deleted_members = []
    tag_to_name = dict()
    for t in temp:
        deleted_members.append(t[0])
    for clan_member in clan_members['items']:
        if clan_member['tag'] not in deleted_members:
            db.execute("INSERT INTO clash_of_clans (user_tag, clan_tag) VALUES (?, ?)", clan_member['tag'], clan_tag)
        else:
            deleted_members.remove(clan_member['tag'])
        tag_to_name[clan_member['tag']] = clan_member['name']
    for deleted_member in deleted_members:
        db.execute("DELETE FROM clash_of_clans WHERE user_tag = ? AND clan_tag = ?", deleted_member, clan_tag)
    return tag_to_name, clan_members


def calculate_final_kv(war_kv, raid_kv, donation_kv, ldt, league_dkv, member_time, clan_game_dkv):
    if ldt > 3000:
        ldt = 1000
    elif ldt < -3000:
        ldt = -1000
    else:
        ldt //= 3
    if member_time < 10 and donation_kv == 2500:
        donation_kv = 500
    nal_meok = sum(1 for element in [war_kv, raid_kv, donation_kv] if element >= 2500)
    kv = 4 * war_kv // 3 + 2 * raid_kv // 3 + 2 * donation_kv // 3 + \
         league_dkv + ldt + clan_game_dkv
    if nal_meok:
        kv += 1500 * nal_meok - 500
    # if t < 30 and kv > 2000:
    #     kv = int(newbie_kv(newbie_adjust(t), kv))
    if kv < 0:
        kv = 0
    return kv


# with open(r"C:/Users/namon/PycharmProjects/beta_client_temp/lib/utils/coc_auth.txt", "r") as f:
#     coc_auth_info = f.readlines()


class Coc(Cog):
    def __init__(self, bot):
        self.bot = bot

    # @command(name='클오클')
    # async def clash_of_clans_cmd_help(self, ctx, page: Optional[str] = '도움'):
    #     embed = Embed(color=yonseiblue, title='클래시 오브 클랜 운영 도우미')
    #     check = 0
    #     if page.isdigit():
    #         page = int(page)
    #         check = 1
    #     if page == '도움':
    #         check = 1
    #         desc = '무려 연세대학교 학생이 만든' * 0 + '`커뉴야 클오클`명령어 도움입니다.\n\n`커뉴야 클오클 도움`: 이 도움말을 표시합니다.\n`커뉴야 클오클 0~7`: 뀨 상품 클래시 오브 클랜 운영 도우미에 대한 도움말들을 표시합니다. 0부터 7까지 순서대로 읽는 것을 추천드립니다.\n`커뉴야 클오클 인증`: `커뉴야 클오클 6`의 도움말에서 언급된 바 있는 인증을 하고, 자신의 명령어 사용 권한을 확인하는 명령어입니다.\n`커뉴야 클오클 설정`: (명령어 사용 권한이 있는 사람만 사용할 수 있어요) 초기 설정을 했을 때 설정했던 값들을 바꿀 수 있는 명령어입니다.'
    #     elif page == 0:
    #         desc = '이 시스템은 어떤 멤버가 얼마나 열심히 활동하는지를 계산하면서 클랜 운영을 정확하게 도와주는 시스템입니다.\n\n친구들끼리 즐겜할 목적으로 만든 클랜이라면 이 시스템 사용을 ' \
    #                '추천드리지 **않고**, 열심히 활동하지 않는 사람을 쳐내야 하는 클랜의 경우 사용을 추천합니다.\n\n매우 정교한 방식으로 동작하는 알고리즘에 의해 값이 계산되기 때문에, ' \
    #                '아래와 같이 도움말 페이지를 나누었습니다.\n\n`커뉴야 클오클 0`: 이 도움말\n\n`커뉴야 클오클 1`: 아이템 구매 시 사용 가능한 명령어들의 목록\n\n`커뉴야 클오클 2, ' \
    #                '3, 4, 5`: 알고리즘의 동작방식 간단 설명\n\n`커뉴야 클오클 6`: 구매 직후 해야 될 것들\n\n`커뉴야 클오클 7`: 사용 전 주의사항\n\n읽는 걸 싫어하신다면 1,6,' \
    #                '7정도만 읽어주셔도 됩니다.'
    #     elif page == 1:
    #         desc = '`커뉴야 추방정산`: 클랜 멤버들의 무기여 지수를 무기여 지수가 큰 순서대로 정렬해 보여줍니다.\n\n`커뉴야 클전정산`, `커뉴야 습격전정산` (또는 `커뉴야 습격정산`), ' \
    #                '`커뉴야 지원정산`, `커뉴야 리그정산 (리그일)`, `커뉴야 클겜정산`: 각각의 컨텐츠에 대해 무기여 지수를 정산합니다. 리그정산의 경우 리그전 매칭이 잡힌 직후 `커뉴야 ' \
    #                '리그정산 0`을 사용하시면 더 정확한 결과를 얻으실 수 있습니다.\n\n또한 `정산`이 들어간 모든 명령어는 마지막에 1을 붙임으로 (예시: `커뉴야 클전정산 1`) 결과를 ' \
    #                '출력하지만 데이터에 반영하지 않도록 할 수 있습니다. '
    #     elif page == 2:
    #         desc = '**무기여 지수**가 이 알고리즘의 핵심으로, 특정 인물이 얼마나 클랜 안에서 날로 먹으려고 하는지를 0에서 10000 사이의 값으로 매기는 지수입니다. 이름이 무기여 지수인 ' \
    #                '만큼 값이 높을수록 활동하지 않는 멤버라는 의미입니다.\n\n무기여 지수를 산출하는 알고리즘은 구현되어 있지만 무기여 지수의 분포는 당연히 클랜마다 다르게 나올 것이기 때문에, ' \
    #                '운영하고 계시는 클랜이 얼마나 빡센 클랜인지를 기준으로 지수를 해석하시면 도움이 되실 겁니다.\n\n그래도 헷갈리실 수 있으니 해석의 가이드라인을 조금 제시해 ' \
    #                '드리겠습니다.\n\n무기여 지수가 10000점이라면, 수상할 정도로 아무것도 안 한다는 뜻입니다. 대부분의 컨텐츠에 참여하지 않으며, 참여하는 컨텐츠가 있다고 해도 많아야 한 ' \
    #                '종류, 그 컨텐츠마저 열심히 할 가능성은 낮습니다.\n\n무기여 지수가 8000점 전후라면, 10000점보다는 낫지만 별 차이는 없는 수준입니다. 가끔 클랜 컨텐츠에 참여하긴 ' \
    #                '하지만 정말로 가끔일 뿐입니다.\n\n무기여 지수가 5000점 전후라면, 이런저런 컨텐츠를 필수로 지정해두는 빡센 클랜이 아닌 상당수의 클랜에서는 열심히 하는 건 확실히 아닌데 ' \
    #                '그래도 자기가 할 일은 묵묵히 하는 정도의 포지션일 겁니다. *5000점*인 만큼, 열심히 참여하는 컨텐츠도 있지만 손을 놓는 컨텐츠 또한 있을 겁니다.\n\n무기여 지수가 ' \
    #                '2500점 전후라면, 소위 말하는 일반인클에서는 열심히 하는 편에 속한 멤버일 가능성이 큽니다. 참여하지 않는 컨텐츠는 보통 하나 정도밖에 없으며, 실력이 눈을 뜨고 봐줄 수 ' \
    #                '없는 컨텐츠도 딱히 없을 가능성이 큽니다.'
    #     elif page == 3:
    #         desc = '무기여 지수는 클랜전, 습격전, 지원, 클랜전 리그, 클랜 게임에 관련된 무기여 지수로 세분화됩니다.\n\n클랜전, 습격전, 지원과 관련된 무기여 지수는 0점부터 ' \
    #                '3000점까지의 값을 가질 수 있습니다.\n\n클랜전에 관한 무기여 지수는, 클랜전 참여 여부, 참여했을 경우 공격 여부, 총 획득한 별과 총 파괴율, 클랜전 지도에서 공격한 ' \
    #                '사람과 당한 사람의 상대적 위치에 따라 무기여 지수 변화를 결정합니다. 클랜전에 참가했지만 공격을 가지 않았을 경우 무기여 지수가 가장 큰 폭으로 증가하고, ' \
    #                '애초에 클랜전에 참가하지 않을 경우 얼마나 오랫동안 불참했는지에 따라 무기여 지수가 올라갑니다. 또한, 클랜에 가입한 지 얼마 되지 않은 멤버가 불참할 경우에도 무기여 지수가 ' \
    #                '큰 폭으로 올라갑니다. 이외의 경우에도 알고리즘의 평가에 의해 무기여 지수가 변동됩니다.\n\n습격전에 관한 무기여 지수는, 습격전 공격 횟수와 얻은 캐피탈 골드의 총합으로 ' \
    #                '무기여 지수를 정산합니다. 단, 짬처리를 일부러 해준 경우 등 얻은 골드가 적다고 반드시 실력이 낮다고 말할 수는 없기 때문에 좋지 않은 성과로 인해 무기여 지수가 올라가는 ' \
    #                '정도는 매우 적습니다. 다만, 비정상적인 행보가 의심되지만 실제로 무슨 일이 있었는지 봇이 알 방법이 없는 일부 경우 봇이 정산할 때 무언가를 물어보기도 할 ' \
    #                '겁니다.\n\n지원에 관한 무기여 지수는, 지원한 유닛 수와 지원받은 유닛 수에 의해 결정됩니다. 당연히 지원을 받기만 하는 사람이 가장 높은 무기여 지수를 가져가지만, ' \
    #                '지원 컨텐츠에 전혀 참여하지 않는 사람들에게도 높은 무기여 지수가 부여됩니다. '
    #     elif page == 4:
    #         desc = '클랜전 리그와 클랜 게임은 1개월을 주기로 일어나기 때문에 신규 가입자에 관한 지수를 정산하기가 어렵습니다. 그러므로 이 컨텐츠들과 관련된 무기여 지수들은 ' \
    #                '-1600점에서 +1600점까지 있으며 먼저 언급한 세 컨텐츠에 관한 무기여 지수를 바탕으로 점수를 우선 구한 뒤 거기다가 이 두 컨텐츠에 관한 무기여 지수를 더하는 방식으로 ' \
    #                '정산됩니다. 자세한 얘기는 `커뉴야 클오클 5`를 참고하세요. 1600이라는 값은 설정에서 바꿀 수 있습니다.\n\n클랜전 리그와 관련된 무기여 지수는 매 전쟁마다 클랜전과 ' \
    #                '관련된 무기여 지수와 비슷한 방식으로 정산하지만, 7일차까지 정산이 끝나기 전에는 임시 무기여 지수가 부여됩니다. 7일차까지 정산을 모두 완료한다면 임시값이 아닌 실제값이 ' \
    #                '들어가게 됩니다.\n\n클랜 게임에 관련된 무기여 지수는 정말 아쉽지만 편하게 정산해 드릴 방법을 찾지 못해, 명령어를 실행한 후 멤버의 이름과 점수를 직접 적고 나서 그 ' \
    #                '데이터를 바탕으로 정산해드립니다. 당연히 클랜 게임에서 높은 점수를 얻었을수록 낮은 무기여 지수를 부여하지만, 예외적으로 0점을 받은 멤버보다 100점같은 매우 낮은 점수를 ' \
    #                '받은 멤버에게 더 높은 무기여 지수를 부여합니다. 클랜 게임에서 0점으로 끝났다면 아무 보상을 받지 못하지만 50점만 받아도 보상을 얻을 수 있기 때문에 해둔 조치입니다. '
    #     elif page == 5:
    #         desc = '다섯 종류의 무기여 지수를 바탕으로 실제 추방정산에 표시되는 지수를 구하는 방법을 알아보겠습니다.\n\n우선 클랜전, 습격전, 지원과 관련된 무기여 지수를 모두 합하지만, ' \
    #                '이 세 지수에 미리 정해진 가중치를 곱해서 합합니다.\n\n이후에는 클랜전, 습격전, 지원과 관련된 무기여 지수 중에 만약 2500을 넘는 값이 있다면 그 컨텐츠를 전혀 ' \
    #                '참여하지 않는 것으로 간주하고 무기여 지수를 추가로 더합니다.\n\n이 값에다가 클랜전 리그, 클랜 게임과 관련된 무기여 지수를 더한 후 직접 설정 가능한 멤버별 추가 무기여 ' \
    #                '지수를 더하면 진짜 무기여 지수가 완성됩니다. '
    #     elif page == 6:
    #         desc = '상품을 구매한 직후에는 두 종류의 초기 설정을 하게 됩니다.\n\n먼저 하는 설정은 운영 도우미가 실제로 운영을 도울 클랜이 어디인지, 운영 권한을 가질 사람이 누구인지를 ' \
    #                '설정하는 것입니다. 혼선을 막기 위해, **대표 또는 공동 대표임이 인증된 후에 서비스를 이용하실 수 있습니다.**인증 방법은 `커뉴야 클오클 인증`으로 하시면 되고, ' \
    #                '상품을 구매하시기 전에 인증을 요청하셔도 받아 드립니다.\n\n클랜에서 지위가 대표일 경우 자신이 아닌 다른 사람에게도 원하면 명령어 사용권을 부여할 수 있지만, ' \
    #                '공동 대표일 경우 자신만 쓸 수 있습니다.\n\n명령어 사용권 관련 설정이 끝나게 되면, 알고리즘의 세부적인 수치를 직접 설정할 수 있습니다. 얼마나 빡센 클랜인지와 클랜 ' \
    #                '컨텐츠들 중 어떤 것을 얼만큼이나 중요하게 생각하는지를 봇이 물어보면 대답해 주시면 됩니다. 이후에는 늦어도 24시간이 되기 전에 봇으로부터 DM으로 명령어 사용이 가능하다는 ' \
    #                '사실을 전달받으실 겁니다.\n\n당연히 위에서 언급한 모든 설정들은 원하는 때 바꿀 수 있습니다. '
    #     elif page == 7:
    #         desc = '이 기능은 클랜 운영 `도우미` 이고 클랜 운영을 대신 해주는 무언가는 아닙니다. 뭐 잘못된 설정으로 인해 엄한 사람을 보내버리는 것보단 낫지 않겠어요?\n\n클랜 컨텐츠와 ' \
    #                '관련된 데이터만 명령어로 수집하고 이런 클랜 컨텐츠들은 어쨌거나 적어도 며칠을 주기로 일어납니다. 그렇기 때문에 명령어를 사용한 지 오래 지나지 않았을 때는 멤버별 무기여 ' \
    #                '지수가 정확하지 않을 수 있습니다. 그러나, 이 정확성은 1주 정도만 지나도 쓸만한 수준이 되며 한 달이 지나면 알고리즘이 추구하는 최대의 정확도를 뽑을 수 있게 됩니다. '
    #
    #     if check:
    #         embed.add_field(name=str(page), value=desc)
    #     embed.set_footer(text='`커뉴야 뀨 구매 클오클 클랜 운영 도우미`로 구매 가능한 상품이고, 구매하셨다면 여기에 포함된 모든 명령어들을 기간 제한 없이 사용하실 수 있습니다.')
    #     await ctx.send(embed=embed)

    @command(name='클전정산')
    async def clan_war(self, ctx, clan_tag: str, check: int = 0):
        if ctx.author.id != 724496900920705045:
            return
        tag_to_name, _ = clan_member_refresh(clan_tag)
        cw = get_clan_war(clan_tag)
        attack_score = dict()
        opponent_position = [''] * cw['teamSize']
        for opp in cw['opponent']['members']:
            opponent_position[opp['mapPosition'] - 1] = opp['tag']
        for mem in cw['clan']['members']:
            if 'attacks' not in mem:
                attack_score[mem['tag']] = 0
            else:
                stars = sum(atk['stars'] for atk in mem['attacks'])
                percent = sum(atk['destructionPercentage'] for atk in mem['attacks'])
                position = mem['mapPosition']
                pos_delta = 50
                for atk in mem['attacks']:
                    if atk['stars']:
                        pos = opponent_position.index(atk['defenderTag']) - position + 1
                    else:
                        pos = 50
                    pos_delta = min(pos_delta, pos)
                if pos_delta == 50:
                    pos_delta = 0
                if stars == 0 and percent < 50:
                    attack_score[mem['tag']] = 0
                elif stars <= 1:
                    attack_score[mem['tag']] = percent // 6
                elif stars <= 2:
                    attack_score[mem['tag']] = percent * 5 // 9
                elif stars == 3 and percent < 150:
                    attack_score[mem['tag']] = percent
                elif stars >= 5 and percent >= 180:
                    attack_score[mem['tag']] = percent * 5 // 2 * (stars - 4)
                else:
                    attack_score[mem['tag']] = percent * 2 // 5 * stars
                attack_score[mem['tag']] /= ceil((x := max(pos_delta - cw['teamSize'] // 10, 0) + 1) ** x)
                if 0.1 < attack_score[mem['tag']] < 1:
                    attack_score[mem['tag']] = 1
        members = db.records(
            "SELECT user_tag, war_ban, war_kv, war_inactive_streak, member_time FROM clash_of_clans WHERE clan_tag = ?",
            clan_tag)
        # 공격간사람, 안간사람, 불참한 사람 등등 정산
        to_kick = []
        not_attacked = []
        cnt = 0
        result_strings = []
        result_string = ''
        for member in members:
            kv_delta_past_cap = 0
            ban_check = 0
            if member[0] not in attack_score:  # 불참
                s = -1
                if member[1]:
                    ban_check = 1
                    kv_delta = 0
                    if not check: db.execute("UPDATE clash_of_clans SET war_ban = ? WHERE user_tag = ?", member[1] - 1,
                                             member[0])
                    inactive_streak_delta = 0
                else:
                    today_in_month = datetime.now().day
                    days_since_league_end = max(0, today_in_month - 9)
                    if member[4] > today_in_month:  # 이번달에 들어온 사람이 아니다
                        normal_war_time = member[4] * 10000
                    else:
                        normal_war_time = min(member[4], days_since_league_end)
                    kv_delta = 100 * (member[3] + 1)
                    if normal_war_time <= 2:
                        kv_delta = 0
                        inactive_streak_delta = 0
                    elif normal_war_time <= 8:
                        kv_delta = 1000
                        inactive_streak_delta = 1
                    elif normal_war_time < 15:
                        kv_delta = kv_delta * 7 // 5
                        inactive_streak_delta = 1
                    else:
                        inactive_streak_delta = 1
                    if member[2] + kv_delta >= 3000:
                        kv_delta_past_cap = 50
            else:  # 참여
                s = int(attack_score[member[0]])
                if s == 0:  # 미공이거나 미공으로 간주
                    not_attacked.append(tag_to_name[member[0]])
                    if member[2] < 1000:
                        kv_delta = 1000
                        if not check:
                            db.execute("UPDATE clash_of_clans SET war_ban = 1 WHERE user_tag = ?", member[0])
                    elif member[2] < 2500:
                        kv_delta = 2500
                        if not check:
                            db.execute("UPDATE clash_of_clans SET war_ban = 2 WHERE user_tag = ?", member[0])
                    else:
                        to_kick.append(member[0])
                        kv_delta = 9999
                    inactive_streak_delta = 0
                else:
                    if s <= 100:
                        kv_delta = (100 - s) ** 1.5 // 4
                    elif s <= 150:
                        kv_delta = -((s - 100) ** 2 // 100)
                    elif s <= 400:
                        kv_delta = -((s - 100) ** 2 // 300)
                    elif s <= 500:
                        kv_delta = - s
                    else:
                        kv_delta = -750
                    if s <= 50:
                        inactive_streak_delta = -1
                    elif s <= 440:
                        inactive_streak_delta = -2
                    else:
                        inactive_streak_delta = -3
            kv_delta = int(kv_delta)
            if not ban_check:
                if min(member[2], 3000) + kv_delta > 3000:
                    kv_delta = 3000 - min(member[2], 3000)
                elif member[2] + kv_delta < 0:
                    kv_delta = -member[2]
                result_string += f'{tag_to_name[member[0]]}: {s}점, {member[2]} -> {member[2] + kv_delta + kv_delta_past_cap} (Δ={kv_delta + kv_delta_past_cap})\n'
                cnt += 1
                if cnt == 10:
                    result_strings.append(result_string)
                    result_string = ''
                    cnt = 0
            if not check:
                db.execute("UPDATE clash_of_clans SET war_kv = ?, war_inactive_streak = ? WHERE user_tag = ?",
                           member[2] + kv_delta + kv_delta_past_cap, max(-1, min(7, member[3] + inactive_streak_delta)),
                           member[0])
        embed = Embed(color=yonseiblue, title='클랜전 정산 완료')
        for i in range(len(result_strings)):
            if i == 0:
                embed.add_field(name='클랜전 관련 무기여 지수 변화', value=result_strings[i], inline=False)
            else:
                embed.add_field(name='​', value=result_strings[i], inline=False)
        if result_string:
            embed.add_field(name='​', value=result_string, inline=False)
        embed.add_field(name='추방할 사람', value=', '.join(list(map(lambda y: tag_to_name[y], to_kick))), inline=False)
        war_banned = db.records("SELECT user_tag FROM clash_of_clans WHERE clan_tag = ? AND war_ban != 0", clan_tag)
        embed.add_field(name='다음번 클랜전에서 뺄 사람', value=', '.join(list(map(lambda y: tag_to_name[y[0]], war_banned))),
                        inline=False)
        await ctx.send(embed=embed)
        if not check:
            db.commit()

    @command(name='습격전정산', aliases=['습격정산'])
    async def clan_raid(self, ctx, clan_tag: str, check: int = 0):
        tag_to_name, _ = clan_member_refresh(clan_tag)
        ra = get_clan_raid(clan_tag)['items'][0]
        loots = dict()
        for mem in ra['members']:
            loots[mem['tag']] = [mem['capitalResourcesLooted'], mem['attacks']]
        member_data = db.records("SELECT user_tag, raid_kv, member_time FROM clash_of_clans WHERE clan_tag = ?",
                                 clan_tag)
        members = []
        six_attack_len = 0
        six_attack_sum = 0
        for m in member_data:
            members.append(m[0])
        for sc in loots:
            try:
                members.remove(sc)
            except ValueError:
                pass
            if loots[sc][1] == 6:
                six_attack_len += 1
                six_attack_sum += loots[sc][0]
        six_attack_mean = six_attack_sum // six_attack_len
        ask_tolerance = deque()
        low_loot = []
        kv_dict = dict()
        dkv_dict = dict()
        for mem, rkv, mtime in member_data:
            kv_dict[mem] = rkv
            if mem not in loots:
                if mtime >= 25:
                    dkv = 1000
                elif mtime >= 14:
                    dkv = 1200
                else:
                    dkv = 1500
                loots[mem] = [0, 0]
            elif loots[mem][1] < 5:
                dkv = 900
            elif loots[mem][1] == 5:
                dkv = 700
            else:
                ratio = loots[mem][0] / six_attack_mean
                if 1.25 <= ratio <= 1.5:
                    dkv = -500 - 300 * tan(pi * (ratio - 1.25))
                elif ratio > 1.5:
                    dkv = -800
                elif ratio < 0.5:
                    low_loot.append(mem)
                    dkv = sqrt(1 - 2 * ratio) * 1000
                    ask_tolerance.append(
                        f'{tag_to_name[mem]}: 6공 평균에 비해 {round(ratio, 3)}배로 kv {rkv} -> {rkv + dkv} 예정, 이 사람이 일부러 '
                        f'짬처리를 해준 것이라면 1, 아니라면 0을 입력해주세요 (리플레이들에서 처음 시작할 때 털 수 있는 자원 양만 확인하면 될 겁니다!)')
                else:
                    dkv = -200 * (ratio ** 0.4)
            dkv_dict[mem] = int(dkv)
        possible_nal_meok = []
        attacker = ''
        for raid in ra['attackLog']:
            for district in raid['districts']:
                try:
                    for attack in district['attacks'][::-1]:
                        if attack['destructionPercent'] < 90:
                            continue
                        elif attack['destructionPercent'] < 100:
                            attacker = attack['attacker']['tag']
                        else:
                            if attacker and attacker != attack['attacker']['tag']:
                                if attacker not in possible_nal_meok:
                                    ask_tolerance.append(
                                        f'{tag_to_name[attacker]}: 짬처리를 다른 사람에게 돌린 게 아닌지 의심됨. 이 사람이 공격권을 다 써서 어쩔 수 없는 상황에 '
                                        f'있었다면 1, 아니라면 0을 입력해주세요 (마지막 리플레이만 확인하면 될 겁니다!)')
                                    possible_nal_meok.append(attacker)
                            attacker = ''
                except KeyError:
                    pass
        a = len(low_loot)
        b = len(possible_nal_meok)

        actual_nal_meok = []
        if a + b != 0:
            await ctx.send(
                f"{a + b}명이 비정상적인 습격전 기록을 가진 것으로 확인되었습니다. 지금부터 {a}명의, 자원을 너무 적게 턴 자들과, {b}명의, 짬처리를 다른 사람에게 돌림이 의심되는 "
                f"사람들에 대한 정보를 입력해주세요.")
            ask_tolerance.rotate(b)
            for i in range(b):
                await ctx.send(ask_tolerance[i])
                try:
                    tolerate = await self.bot.wait_for(
                        "message",
                        timeout=600,
                        check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                    )
                except asyncio.TimeoutError:
                    await ctx.send("습격전 정산을 취소했어요")
                    return
                if tolerate.content != '1':
                    actual_nal_meok.append(possible_nal_meok[i])
            for i in range(a):
                await ctx.send(ask_tolerance[b + i])
                try:
                    tolerate = await self.bot.wait_for(
                        "message",
                        timeout=600,
                        check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                    )
                except asyncio.TimeoutError:
                    await ctx.send("습격전 정산을 취소했어요")
                    return
                if tolerate == '1':
                    dkv_dict[low_loot[i]] = 400 * (low_loot[i] in actual_nal_meok)
        for nalmeok in actual_nal_meok:
            ratio = loots[nalmeok][0] / six_attack_mean
            dkv_dict[nalmeok] = int(400 + 4000 * ((ratio - 1) ** 2))
        embed = Embed(color=yonseiblue, title='주말 습격전 정산 완료')
        cnt = 0
        result_strings = []
        result_string = ''
        for dkv_info in dkv_dict:
            if kv_dict[dkv_info] + dkv_dict[dkv_info] > 3000:
                dkv_dict[dkv_info] = 3000 - kv_dict[dkv_info]
            elif kv_dict[dkv_info] + dkv_dict[dkv_info] < 0:
                dkv_dict[dkv_info] = -kv_dict[dkv_info]
            result_string += f'{tag_to_name[dkv_info]}: {kv_dict[dkv_info]} -> {kv_dict[dkv_info] + dkv_dict[dkv_info]} (Δ={dkv_dict[dkv_info]})\n'
            cnt += 1
            if cnt == 10:
                cnt = 0
                result_strings.append(result_string)
                result_string = ''
            if not check:
                db.execute("UPDATE clash_of_clans SET raid_kv = raid_kv + ? WHERE user_tag = ?", dkv_dict[dkv_info],
                           dkv_info)
        for i in range(len(result_strings)):
            if i == 0:
                embed.add_field(name='습격전 관련 무기여 지수 변화', value=result_strings[i], inline=False)
            else:
                embed.add_field(name='​', value=result_strings[i], inline=False)
        if result_string:
            embed.add_field(name='​', value=result_string, inline=False)
        if not a + b:
            embed.set_footer(text='아무도 비정상적인 행보를 보이지 않았어요!')
        await ctx.send(embed=embed)
        if not check:
            db.commit()

    @command(name='지원정산')
    async def donations(self, ctx, clan_tag: str, check: int = 0):
        clan_member_refresh(clan_tag)
        members = get_clan_members(clan_tag)['items']
        result_strings = []
        result_string = ''
        cnt = 0
        for member in members:
            tag, give, take = member['tag'], member['donations'], member['donationsReceived']
            if give == 0:
                if take == 0:
                    kv = 2000
                else:
                    kv = min(3000, 1500 + take * 3)
            else:
                try:
                    ratio = give / take
                except ZeroDivisionError:
                    ratio = 99999999
                if ratio >= 10 and give >= 100:
                    kv = max(0, 550 - give // 2)
                elif ratio >= 4 and give >= 2000:
                    kv = 0
                elif ratio >= 3 and give >= 1500:
                    kv = 1000 - 250 * ratio
                elif ratio >= 1.5 and give >= 1000:
                    kv = 1250 - 1000 * ratio / 3
                elif ratio < 1 / 9:
                    kv = min(3000, 1250 + take * 2)
                elif ratio < 1 / 3 and take >= 1000:
                    kv = min(3000, 800 + 7 * take // 5)
                elif ratio < 1 / 2 and take >= 500:
                    kv = min(3000, 1000 + 6 * take // 5)
                elif ratio < 0.8:
                    kv = (-3500 * ratio + 6550) // 3
                else:
                    kv = 1250 - min((give - take) // 10, 200)
                kv = min(3000, max(0, int(kv)))
            print(give, take, kv)
            if not check: db.execute("UPDATE clash_of_clans SET donation_kv = ? WHERE user_tag = ?", kv, member['tag'])
            result_string += f'{member["name"]}: {kv}\n'
            cnt += 1
            if cnt == 10:
                cnt = 0
                result_strings.append(result_string)
                result_string = ''
        if not check: db.commit()
        embed = Embed(color=yonseiblue, title='지원 정산 완료')
        for i in range(len(result_strings)):
            if i == 0:
                embed.add_field(name='설정된 지원 관련 무기여 지수', value=result_strings[i], inline=False)
            else:
                embed.add_field(name='​', value=result_strings[i], inline=False)
        if result_string:
            embed.add_field(name='​', value=result_string, inline=False)
        await ctx.send(embed=embed)

    @command(name='추방정산')
    @max_concurrency(1, BucketType.default)
    async def measure_kv(self, ctx, clan_tag: str):
        # newbie_adjust = lambda x: 1.7 - 0.7 / (1 + e ** (5 - x / 2)) + e ** (-(x - 15) ** 2 / 50) / 14
        # newbie_kv = lambda a, x: (a ** 1.5) * ((x - 2000) ** 1.02) + 2000
        tag_to_name, clan_members = clan_member_refresh(clan_tag)
        # clan_members = clan_members['items']
        member_kv_data = db.records(
            "SELECT user_tag, war_kv, raid_kv, donation_kv, league_dkv_temp, league_dkv, member_time, clan_game_dkv FROM clash_of_clans WHERE clan_tag = ?",
            clan_tag)
        member_kv = [[0, '', ''] for _ in range(len(member_kv_data))]
        league_temp_included = 0
        for i in range(len(member_kv_data)):
            member_kv_data[i] = list(member_kv_data[i])
            if member_kv_data[i][4] != 0:
                league_temp_included = 1
            kv = calculate_final_kv(*member_kv_data[i][1:])
            member_kv[i] = [kv, tag_to_name[member_kv_data[i][0]], member_kv_data[i][0]]
        member_kv = sorted(member_kv, reverse=True)
        result_text = ''
        for i in range(1, min(50, len(member_kv)) + 1):
            result_text += f'{i}. {member_kv[i - 1][1]} ({member_kv[i - 1][2]}): {member_kv[i - 1][0]}\n'
        await ctx.send(embed=Embed(color=yonseiblue, title='무기여 지수' + '(클랜전 리그로 인한 임시값 반영됨)' * league_temp_included,
                                   description=result_text))

    @command(name='리그정산')
    async def clan_war_league(self, ctx, clan_tag: str, war_day: int, just_show: int = 0):
        tag_to_name, _ = clan_member_refresh(clan_tag)
        ct = '#' + clan_tag
        league_data = requests.get(f'https://api.clashofclans.com/v1/clans/%23{clan_tag}/currentwar/leaguegroup',
                                   headers=headers).json()
        max_war_day = len(league_data['clans']) - 1
        if war_day == 0:
            for league_clan_data in league_data['clans']:
                if league_clan_data['tag'] == '#' + clan_tag:
                    league_participants = [mem['tag'] for mem in league_clan_data['members']]
                    break
            all_members = db.records("SELECT user_tag FROM clash_of_clans WHERE clan_tag = ?", clan_tag)
            voluntary_no_participate = []
            for member in all_members:
                if member[0] not in league_participants:
                    voluntary_no_participate.append(member[0])
            for vnp in voluntary_no_participate:
                db.execute("UPDATE clash_of_clans SET league_dkv_temp = 1600 WHERE user_tag = ?", vnp)
            embed = Embed(color=yonseiblue, title='클랜전 리그 불참 요청자 정산 완료')
            embed.add_field(name='리그전 멤버에서 빠진 사람들 (이들은 리그전이 다 끝난 이후 클랜전 리그 관련 무기여 지수 1600점이 일괄 부여됩니다)',
                            value=','.join([tag_to_name[tag] for tag in voluntary_no_participate]))
            await ctx.send(embed=embed)
            if not just_show:
                db.commit()
            return
        for war_tag in league_data['rounds'][war_day - 1]['warTags']:
            war_data = requests.get(f'https://api.clashofclans.com/v1/clanwarleagues/wars/%23{war_tag[1:]}',
                                    headers=headers).json()
            if war_data['clan']['tag'] == ct:
                check = 0
                break
            elif war_data['opponent']['tag'] == ct:
                check = 1
                break
            else:
                continue
        if check == 0:
            cw = war_data['clan']
        elif check == 1:
            cw = war_data['opponent']
        dkv_dict = dict()
        opponent_position = [''] * 50
        broken = [False] * 15
        attack_info = [dict() for _ in range(30)]
        if check == 0:
            for opp in war_data['opponent']['members']:
                opponent_position[opp['mapPosition'] - 1] = opp['tag']
        else:
            for opp in war_data['clan']['members']:
                opponent_position[opp['mapPosition'] - 1] = opp['tag']
        opponent_position = list(filter(lambda x: x != "", opponent_position))
        today_participant = []
        clan_position = [''] * 50
        for mem in cw['members']:
            clan_position[mem['mapPosition'] - 1] = mem['tag']
        clan_position = list(filter(lambda x: x != "", clan_position))
        for mem in cw['members']:
            try:
                today_participant.append(tag_to_name[mem['tag']])
            except KeyError:
                pass
            if 'attacks' not in mem:
                dkv = 1200
            else:
                atk = mem['attacks'][0]
                stars = atk['stars']
                percent = atk['destructionPercentage']
                position = clan_position.index(mem['tag']) + 1
                order = atk['order']
                pos_delta = opponent_position.index(atk['defenderTag']) - position + 1
                attack_info[order - 1]['pos_delta'] = pos_delta
                attack_info[order - 1]['position'] = position
                attack_info[order - 1]['defender'] = opponent_position.index(atk['defenderTag']) + 1
                attack_info[order - 1]['stars'] = stars
                attack_info[order - 1]['percent'] = percent
                attack_info[order - 1]['attacker'] = mem['tag']
                if pos_delta < 0:
                    if stars == 3:
                        dkv = 2
                    elif stars == 2:
                        dkv = 500
                    else:
                        dkv = 1000
                elif pos_delta > 0:
                    if stars == 3:
                        dkv = 300 * pos_delta
                    elif stars:
                        dkv = 500 * pos_delta
                    else:
                        dkv = 1000 * pos_delta
                else:
                    if stars == 0:
                        dkv = 500 - (percent // 10)
                    elif stars == 1:
                        dkv = 100 - (percent // 2)
                    elif stars == 2:
                        dkv = -200 - percent
                    else:
                        dkv = -500
            dkv_dict[mem['tag']] = dkv
        for attack in attack_info:
            if not attack:
                continue
            else:
                if broken[attack['position'] - 1]:
                    if attack['pos_delta'] > 0:
                        for i in range(attack['position'], attack['defender'] - 1):
                            if not broken[i]:
                                break
                        else:
                            if attack['stars'] == 0:
                                dkv = 500 - (attack['percent'] // 10)
                            elif attack['stars'] == 1:
                                dkv = 100 - (attack['percent'] // 2)
                            elif attack['stars'] == 2:
                                dkv = -200 - attack['percent']
                            else:
                                dkv = -500
                            dkv_dict[attack['attacker']] = dkv * 4
                        dkv_dict[attack['attacker']] //= 4
                    elif attack['pos_delta'] < 0:
                        if attack['stars'] == 0:
                            dkv = 500 - (attack['percent'] // 8)
                        elif attack['stars'] == 1:
                            dkv = 100 - (attack['percent'] // 1.6)
                        elif attack['stars'] == 2:
                            dkv = -200 - attack['percent']
                        else:
                            dkv = -500
                        dkv_dict[attack['attacker']] = int(dkv)
                if attack['stars']:
                    broken[attack['defender'] - 1] = True
        members = db.records("SELECT user_tag, league_dkv_temp FROM clash_of_clans WHERE clan_tag = ?", clan_tag)
        embed = Embed(color=yonseiblue, title=f'클랜전 리그 {war_day}일차 정산 완료')
        embed.add_field(name='오늘 참가자 목록', value=', '.join(today_participant), inline=False)
        result_string = ''
        for dkv_info in dkv_dict:
            try:
                old_dkv = 0
                for member in members:
                    if member[0] == dkv_info:
                        old_dkv = member[1]
                        break
                result_string += f'{tag_to_name[dkv_info]}: {old_dkv} -> {old_dkv + dkv_dict[dkv_info]} (Δ={dkv_dict[dkv_info]})\n'
            except KeyError:
                pass
        embed.add_field(name='클랜전 리그 관련 임시 무기여 지수 변화', value=result_string, inline=False)
        if war_day == max_war_day:
            embed.set_footer(text='이번 정산이 마지막 일차 정산이므로, 바로 이어서 클랜전 리그 전체 정산이 진행됩니다')
        await ctx.send(embed=embed)
        if not just_show:
            for user_tag in dkv_dict:
                db.execute("UPDATE clash_of_clans SET league_dkv_temp = league_dkv_temp + ? WHERE user_tag = ?",
                           dkv_dict[user_tag], user_tag)
            db.commit()
        if war_day != max_war_day:
            return

        await asyncio.sleep(2)

        league_dkv_data = db.records(
            "SELECT user_tag, league_dkv_temp, league_dkv FROM clash_of_clans WHERE clan_tag = ?", clan_tag)
        league_dkv_final = []
        for member, dkv_temp, dkv in league_dkv_data:
            league_dkv_final.append([dkv_temp, dkv, member])
        league_dkv_final.sort(reverse=True)
        hard_work_cnt = 0
        result_strings = []
        result_string = ''
        cnt = 0
        for dkv_temp, dkv, member in league_dkv_final:
            if dkv_temp <= -2500:
                hard_work_cnt += 1
            if dkv_temp >= 1600:
                actual_dkv = 1600
            elif dkv_temp > 1000:
                actual_dkv = 1500
            elif dkv_temp > 500:
                actual_dkv = 800
            elif dkv_temp > 300:
                actual_dkv = 500
            elif dkv_temp <= -2500:
                actual_dkv = -1490 - 10 * hard_work_cnt
            else:
                actual_dkv = sgn(dkv_temp) * int(dkv_temp ** 2 / (2500 ** 2 / 1500))
            if actual_dkv != dkv:
                result_string += f'{tag_to_name[member]}: {dkv} -> {actual_dkv} (임시 무기여 지수는 {dkv_temp}(이)었고, Δ={actual_dkv - dkv})\n'
                cnt += 1
                if cnt == 5:
                    result_strings.append(result_string)
                    result_string = ''
                    cnt = 0
                if not just_show:
                    db.execute("UPDATE clash_of_clans SET league_dkv = ? WHERE user_tag = ?",
                               actual_dkv, member)
        embed = Embed(color=yonseiblue, title=f'클랜전 리그 {league_data["season"]}시즌 정산 완료')
        for i in range(len(result_strings)):
            if i == 0:
                embed.add_field(name='클랜전 리그 관련 무기여 지수 변화 (변한 사람만 표시함)', value=result_strings[i], inline=False)
            else:
                embed.add_field(name='​', value=result_strings[i], inline=False)
        if result_string:
            embed.add_field(name='​', value=result_string, inline=False)
        embed.set_footer(text='이 정산이 완료되었으므로, 모든 멤버의 클랜전 리그 관련 임시 무기여 지수는 0으로 초기화됩니다.')
        await ctx.send(embed=embed)
        if not just_show:
            db.execute("UPDATE clash_of_clans SET league_dkv_temp = 0 WHERE clan_tag = ?", clan_tag)
            db.commit()

    @command(name='클겜정산')
    async def clan_game(self, ctx, clan_tag: str, just_show: int = 0):
        tag_to_name, _ = clan_member_refresh(clan_tag)
        clan_game_dkv = defaultdict(lambda: 1200)
        score_sum = 0
        await ctx.send(
            '클랜 게임 정산은 API로 받을 방법이 없어 수동으로 해야 돼요 ㅠㅠ 이걸 자동으로 받는 방법이 있다면 문의해 주세요!\n지금부터 정확히 여기 나온 대로 입력해주세요!\n첫 번째 줄에는, 만점을 빨리 기록하신 분들에게 약간의 보너스를 줄지를 입력합니다. 준다면 1 아니면 0을 입력해주세요. 다만, 클랜 게임이 끝난 이후 정산하고 계신다면 0을 입력하셔야 합니다.\n두 번째 줄에는 이번 클랜 게임에서 1인당 얻을 수 있는 최대 점수, 모든 보상을 얻기 위해 필요한 클랜 총점을 입력합니다. 보통은 `4000 50000` 일 겁니다.\n세 번째 줄부터는, 보이는 등수대로 `닉네임 점수` 형식으로 입력해주시면 됩니다. 0점인 멤버는 굳이 입력하지 않으셔도 됩니다.\n\n아래는 좋은 예시입니다.\n1\n4000 50000\n으으ㅐ 4000\n으으ㅐ2 4000\n으으ㅐ느느 ㅏ 3000')
        try:
            response = await self.bot.wait_for(
                "message",
                timeout=1000,
                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
            )
        except asyncio.TimeoutError:
            await ctx.send("클랜 게임 정산을 취소했어요.")
            return
        response = response.content.split('\n')
        for i in range(len(response)):
            data = response[i]
            if i == 0:
                try:
                    x = int(data)
                except ValueError:
                    await ctx.send(f"{i + 1}번째 줄 입력이 잘못됐어요!")
                    return
                if x not in [0, 1]:
                    await ctx.send(f"{i + 1}번째 줄 입력이 잘못됐어요!")
                    return
            elif i == 1:
                try:
                    max_score, max_clan_score = map(int, data.split())
                except ValueError:
                    await ctx.send(f"{i + 1}번째 줄 입력이 잘못됐어요!")
                    return
            else:
                data = data.split(' ')
                try:
                    member_name = ' '.join(data[:-1])
                    member_score = int(data[-1])
                    score_ratio = member_score / max_score
                    if member_score == max_score:
                        if x == 1:
                            if score_sum < max_clan_score:
                                member_dkv = -1600
                            else:
                                member_dkv = -1500
                            score_sum += member_score
                        else:
                            member_dkv = -1500
                    elif member_score >= max_score // 2:
                        member_dkv = int(-1200 * score_ratio)
                    elif member_score >= max_score // 4:
                        member_dkv = int(-2400 * score_ratio) + 600
                    elif member_score >= max_score // 8:
                        member_dkv = int(-4000 * score_ratio) + 1000
                    elif member_score != 0:
                        member_dkv = int(-10000 * score_ratio) + 1750
                    else:
                        member_dkv = 1200
                    for tag in tag_to_name:
                        if tag_to_name[tag] == member_name:
                            clan_game_dkv[tag] = member_dkv
                except ValueError:
                    await ctx.send(f"{i + 1}번째 줄 입력이 잘못됐어요!")
                    return
        result_strings = []
        result_string = ''
        cnt = 0
        for tag in tag_to_name:
            result_string += f'{tag_to_name[tag]}: {clan_game_dkv[tag]}\n'
            cnt += 1
            if cnt == 10:
                cnt = 0
                result_strings.append(result_string)
                result_string = ''
            if not just_show:
                db.execute("UPDATE clash_of_clans SET clan_game_dkv = ? WHERE user_tag = ?", clan_game_dkv[tag], tag)
        embed = Embed(color=yonseiblue, title='클랜 게임 정산 완료')
        for i in range(len(result_strings)):
            if i == 0:
                embed.add_field(name='클랜 게임 관련 무기여 지수', value=result_strings[i], inline=False)
            else:
                embed.add_field(name='​', value=result_strings[i], inline=False)
        if result_string:
            embed.add_field(name='​', value=result_string, inline=False)
        await ctx.send(embed=embed)
        if not just_show:
            db.commit()

    @command(name='멤버정보')
    async def clan_member_info(self, ctx, clan_tag: str, user_name: str):
        tag_to_name, _ = clan_member_refresh(clan_tag)
        name_to_tag = {tag_to_name[k]: k for k in tag_to_name}
        if user_name not in name_to_tag:
            await ctx.send('존재하지 않는 이름이에요!')
            return
        user_tag = name_to_tag[user_name]
        war_kv, raid_kv, donation_kv, league_dkv_temp, league_dkv, member_time, clan_game_dkv = db.record(
            "SELECT war_kv, raid_kv, donation_kv, league_dkv_temp, league_dkv, member_time, clan_game_dkv FROM clash_of_clans WHERE user_tag = ? AND clan_tag = ?",
            user_tag, clan_tag)
        embed = Embed(color=yonseiblue, title=f'멤버 정보: {user_name} (태그 {user_tag})')
        embed.add_field(name='클랜에 있었던 시간', value=f'{member_time}일')
        embed.add_field(name='클랜전 관련 무기여 지수 (0~4000)', value=str(war_kv))
        embed.add_field(name='주말 습격전 관련 무기여 지수 (0~3000)', value=str(raid_kv))
        embed.add_field(name='지원 관련 무기여 지수 (0~3000)', value=str(donation_kv))
        embed.add_field(name='클랜전 리그 관련 임시 무기여 지수 (리그전 기간이 아니면 0임)', value=str(league_dkv_temp))
        embed.add_field(name='클랜전 리그 관련 무기여 지수 (-1500~1600)', value=str(league_dkv))
        embed.add_field(name='클랜 게임 관련 무기여 지수 (-1500~1500)', value=str(clan_game_dkv))
        embed.add_field(name='총 무기여 지수 (0~?????)', value=str(calculate_final_kv(war_kv, raid_kv, donation_kv, league_dkv_temp, league_dkv, member_time, clan_game_dkv)))
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("coc")


def setup(bot):
    bot.add_cog(Coc(bot))