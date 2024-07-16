import asyncio
import os
from collections import defaultdict
from random import *
from time import time
from typing import Optional
from json import dumps, loads
from PIL import Image, ImageDraw
from discord import Embed, File
from discord.ext.commands import Cog, BucketType, command, cooldown
from .achieve import grant_check, grant
from ..db import db
from discord.app_commands import command as slash, choices, Choice
from ..utils.send import send

# 원래 3,칸 불투명도 가격 = [0] * 2 + [15000] * 47 + list(range(15000, 20001, 100)) + [20000] * 49 + list(range(20000, 25001, 100)) + list(range(25200, 30001, 200)) + [30000] * 25 + [40000, 40000, 40000, 40000, 100000]
level_thresholds = [0,
                    5, 100, 2000, 3000, 5000,
                    7500, 10000, 12000, 16000, 20000,
                    25000, 30000, 35000, 40000, 45000,
                    50000, 60000, 80000, 100000, 120000,
                    160000, 200000, 300000, 1000000000000000000]
opacity_costs = [[0],
                 [0] * 2 + [50] * 49 + [100] * 50 + [200] * 154 + [10000],
                 [0] * 2 + list(range(300, 1001, 50)) + [1000] * 32 + list(range(1000, 2000, 5)) + [2000, 2000, 2000,
                                                                                                    2000, 2000, 20000],
                 [0] * 2 + list(range(500, 2000, 10)) + list(range(2000, 5001, 30)) + [10000, 100000],
                 [0] * 2 + list(range(1500, 2000, 50)) + [2000] * 87 + list(range(2000, 5000, 60)) + [5000] * 51 + list(
                     range(5000, 8000, 60)) + [10000, 10000, 10000, 10000, 150000],
                 [0] * 2 + list(range(2000, 5001, 50)) + [5000] * 87 + list(range(5100, 10000, 100)) + [10000] * 51 + [
                     15000, 20000, 25000, 30000, 200000],
                 [0] * 2 + list(range(5000, 10001, 500)) + [10000] * 137 + list(range(10050, 15000, 50)) + [20000,
                                                                                                            20000,
                                                                                                            20000,
                                                                                                            20000,
                                                                                                            20000,
                                                                                                            300000],
                 [0] * 2 + list(range(10000, 20000, 100)) + [20000] * 26 + [21000, 22000, 23000, 24000] + [
                     25000] * 18 + list(range(25000, 35001, 100)) + [40000, 40000, 40000, 400000],
                 [0] * 2 + list(range(500000, 5000000, 500000)) + [5000000] * 39 + list(range(5000000, 10000000, 25000)) + [12345678, 12345678, 12345678, 23456789, 34567890],
                 [0] * 2 + list(range(8000000, 10000000, 100000)) + list(range(10000000, 20000000, 50000)) + list(range(20000000, 30000000, 400000)) + [30000000] * 7 + [50000000],
                 [0] * 2 + [77777777] * 252 + [123456789]]
# for oc in opacity_costs:
#     print(len(oc), sum(oc))
SimpleWhite = (255, 255, 255)
SimpleRed = (255, 0, 0)
SimpleYellow = (255, 255, 0)
SimpleGreen = (0, 255, 0)
SimpleCyan = (0, 255, 255)
SimpleBlue = (0, 0, 255)
SimpleMagenta = (255, 0, 255)
SimpleBlack = (0, 0, 0)
MintCream = (0xf5, 0xff, 0xfa)
Ivory = (0xff, 0xff, 0xf0)
CobaltBlue = (0xd, 0x4a, 0xbc)
RaisinBlack = (0x21, 0x20, 0x27)
ClassicCopper = (0xce, 0x7c, 0x56)
DullCopper = (0xb4, 0x73, 0x60)
MetallicCopper = (0x71, 0x29, 0x1d)
Scarlet = (0xff, 0x2f, 0)
Madder = (0xa2, 0, 0x21)
Pewter = (0xe9, 0xea, 0xec)
Purgatori = (0x89, 0x57, 0x61)
Congregation = (0xa0, 0x21, 3)
SpringGreen = (0, 255, 0x7f)
BabyBlue = (0xb1, 0xc5, 0xd4)
EarthYellow = (255, 0xb2, 0x57)
PastelPink = (0xfe, 0x57, 0x79)
to_visual_bonus_name = {'money_per_command': '`커뉴야 커뉴핑크` 실행 1회당 획득하는 돈',
                        'exp_per_command': '`커뉴야 커뉴핑크` 실행 1회당 획득하는 경험치', 'money_per_hour': '시간당 획득하는 돈',
                        'Copper_per_hour': '시간당 획득하는 구리', 'Copper_per_command': '`커뉴야 커뉴핑크` 실행 1회당 획득하는 구리',
                        'Iron_per_command': '`커뉴야 커뉴핑크` 실행 1회당 획득하는 철', 'Pewter_per_hour': '시간당 획득하는 퓨터'}
to_visual_currency_name = {'Money': '돈', 'Copper': '구리', 'Pewter': '퓨터'}
SIZE_OF_ONE_TILE = 40
mpc_default_upgrade_cost = [10000, 15000, 20000, 25000, 30000, 40000, 50000, 50000, 50000, 50000, 50000, 50000, 50000,
                            50000, 50000, 50000, 50000, 50000, 50000, 50000, 1, 1, 1, 1, 1, 1000, 1000, 1000, 1000,
                            1000, 10000, 10000, 10000, 10000, 10000, 10000, 20000, 30000, 40000, 50000, 60000, 60000,
                            60000, 60000, 60000]
epc_default_upgrade_cost = [20000, 30000, 40000, 50000, 60000, 80000, 100000, 120000, 140000, 160000, 165000, 170000,
                            175000, 180000, 185000, 190000, 195000, 200000, 200000, 200000, 20000, 30000, 50000, 70000,
                            100000]
preset_name_prefix = ['', 'L', 'P', 'A']
extend_costs = [0, 0, 0, 30000, 100000, 500000, 2000000, 100000000, 1000000000, 5000000000]
pick_upgrade_costs = [[0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]]
mineral_KtoE = {'구리': 'Copper', '퓨터': 'Pewter', '철': 'Iron', '은': 'Silver', '금': 'Gold', '백금': 'Platinum'}
mineral_EtoK = {'Copper': '구리', 'Pewter': '퓨터', 'Iron': '철', 'Silver': '은', 'Gold': '금', 'Platinum': '백금'}
mineral_prices_default = {'Copper': 1000, 'Pewter': 200, 'Iron': 2500, 'Silver': 5000, 'Gold': 8000, 'Platinum': 10000}
premium_boosted = dict()


def check_current_level(exp):
    assert len(level_thresholds) > 1
    low, high = 0, len(level_thresholds) - 1

    while low <= high:
        actual_lvl = (low + high) // 2
        if level_thresholds[actual_lvl] <= exp < level_thresholds[actual_lvl + 1]:
            return actual_lvl
        elif exp <= level_thresholds[actual_lvl]:
            high = actual_lvl - 1
        else:
            low = actual_lvl + 1

    return actual_lvl


def make_tutorial_embed(username):
    embed = Embed(color=0xffffff, title=username, description='커뉴핑크 색깔 시스템 튜토리얼')
    embed.add_field(name='기본 정보',
                    value='위 사진은 현재 색깔 정보인데, `투명한 SimpleWhite`로 가득 채워져 있습니다. 앞으로 당신은 이곳에다가 여러 가지 색깔을 채워 각종 보너스를 받게 됩니다.',
                    inline=False)
    embed.add_field(name='칸을 업그레이드하는 방법',
                    value='색깔을 칠하기 전에 우선 `불투명도`를 업그레이드해야 합니다. 불투명도를 업그레이드한다는 것은 특정한 칸을 활성화시킨다는 느낌입니다.\n\n불투명도를 완전히 업그레이드하게 되면 그 칸에 원하는 색을 칠할 수 있게 됩니다.\n초기에는 3x3 크기이므로 채울 수 있는 칸이 9칸밖에 없지만, 특정 조건을 만족시키면 확장 기능이 해금되어 더 많은 칸을 채울 수 있게 됩니다!',
                    inline=False)
    embed.add_field(name='칸에 색을 칠하면?',
                    value='어떤 칸에 색깔을 칠하게 되면 어떤 색을 칠했느냐에 따라 다양한 효과가 나타납니다.\n예를 들어 기본으로 칠해져 있는 SimpleWhite의 경우 `커뉴야 커뉴핑크`를 실행할 때마다 얻을 수 있는 돈과 경험치를 특정한 값만큼 증가시키고, 머지않아 해금할 다른 색의 경우 `커뉴야 커뉴핑크`를 실행할 때마다 얻을 수 있는 돈을 일정한 비율로 증가시킵니다.\n보통 비슷한 효과를 가진 색깔들은 색깔 자체도 비슷합니다. 예를 들어, 명령어 실행 당 주는 돈을 늘리는 색깔들은 전체적으로 매우 밝은 색들입니다.\n게임을 진행해 나갈수록, 이것보다 더 복합적이고 다양한 보너스를 주는 여러 종류의 색깔들이 점차 잠금해제되어 갈 것입니다!',
                    inline=False)
    return embed


def calculate_total_bonus_from_colors(im, default_bonuses):
    default_bonuses = loads(default_bonuses)
    w, h = im.size
    base_values = [[defaultdict(int) for __ in range(w // SIZE_OF_ONE_TILE)] for _ in range(h // SIZE_OF_ONE_TILE)]
    multipliers = [[1] * (w // SIZE_OF_ONE_TILE) for _ in range(h // SIZE_OF_ONE_TILE)]
    ivory = 0
    earthyellow = 0
    uid = int(im.filename.split('\\')[-1].split('_')[0])
    for x in range(w // SIZE_OF_ONE_TILE):
        for y in range(h // SIZE_OF_ONE_TILE):
            pixel = im.getpixel((SIZE_OF_ONE_TILE * x + 1, SIZE_OF_ONE_TILE * y + 1))
            # todo 큐브로 칸 강화하면 여기에 반영
            enchant_pixel = im.getpixel((SIZE_OF_ONE_TILE * x + 1, SIZE_OF_ONE_TILE * y + 2))
            if pixel[2] != enchant_pixel[2]:
                multipliers[x][y] *= 1.1
            col = pixel[:3]
            opacity = pixel[3]
            if col == SimpleWhite:
                base_values[x][y]['money_per_command_add'] += min(250, opacity - 1)
            elif col == MintCream:
                base_values[x][y]['money_per_command_mult1'] += 0.16
            elif col == Ivory:
                ivory = 1
            elif col == SimpleBlack:
                base_values[x][y]['money_per_hour_add'] += 5000
            elif col == SimpleRed:
                nx = x + 1
                if 0 <= nx < w // SIZE_OF_ONE_TILE:
                    multipliers[x + 1][y] *= 2.5
            elif col == SimpleBlue:
                base_values[x][y]['money_per_command_mult2'] += round(default_bonuses['exp_per_command'] / 100, 3)
            elif col == CobaltBlue:
                base_values[x][y]['money_per_command_add'] += [200, 350, 500, 700, 850, 1000][w // SIZE_OF_ONE_TILE - 3]
            elif col == RaisinBlack:
                base_values[x][y]['money_per_hour_mult1'] += 0.2
            elif col == ClassicCopper:
                base_values[x][y]['Copper_per_command'] += 0.4
            elif col == DullCopper:
                base_values[x][y]['Copper_per_hour'] += 30
            elif col == MetallicCopper:
                base_values[x][y]['Copper_per_command'] += 0.2
                base_values[x][y]['Iron_per_command'] += 0.1
            elif col == Scarlet:
                dx = [1, -1, 0, 0]
                dy = [0, 0, 1, -1]
                for i in range(4):
                    nx, ny = x + dx[i], y + dy[i]
                    if 0 <= nx < w // SIZE_OF_ONE_TILE and 0 <= ny < w // SIZE_OF_ONE_TILE:
                        multipliers[nx][ny] *= 1.25
            elif col == Madder:
                dx = [1, 1, -1, -1]
                dy = [1, -1, 1, -1]
                for i in range(4):
                    nx, ny = x + dx[i], y + dy[i]
                    if 0 <= nx < w // SIZE_OF_ONE_TILE and 0 <= ny < w // SIZE_OF_ONE_TILE:
                        multipliers[nx][ny] *= 1.25
            elif col == Pewter:
                base_values[x][y]['Pewter_per_hour'] += 30
            elif col == SimpleYellow:
                base_values[x][y]['mine_income_mult1'] += 0.2
            elif col == SimpleGreen:
                base_values[x][y]['exp_per_command_add'] += 3
            elif col == SimpleMagenta:
                meta_level = db.record("SELECT Level FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", uid)
                if not meta_level:
                    continue
                meta_level = meta_level[0]
                ach_levels = [1, 5, 16, 30, 62, 100]
                for i in range(6):
                    if meta_level >= ach_levels[i]:
                        base_values[x][y]['money_per_command_add'] += 25 * (i + 1)
                        base_values[x][y]['money_per_command_mult1'] += 0.008
            elif col == Congregation:
                base_values[x][y]['scary_cube'] += 0.05
            elif col == SpringGreen:
                xpb = db.record("SELECT XPBoost FROM exp WHERE UserID = ? AND GUildID = 743101101401964647", uid)
                if not xpb:
                    continue
                xpb = xpb[0]
                if xpb > 2:
                    base_values[x][y]['exp_per_command_mult1'] += min(0.45, 0.2 + xpb / 10)
                elif xpb > 1.25:
                    base_values[x][y]['exp_per_command_mult1'] += xpb / 5
                else:
                    base_values[x][y]['exp_per_command_mult1'] += xpb - 1
            elif col == BabyBlue:
                t = db.record("SELECT count(distinct col_name) FROM conupink_color_info WHERE UserId = ?", uid)
                base_values[x][y]['money_per_command_mult1'] += \
                    [0, 0, 0, 0, 0, 0.05, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27,
                     0.28,
                     0.29, 0.3, 0.305, 0.31, 0.315, 0.32, 0.325, 0.33, 0.335, 0.34, 0.345, 0.35][t]
            elif col == EarthYellow:
                earthyellow = 1
            elif col == PastelPink:
                base_values[x][y]['money_per_command_mult1'] -= 0.05
                base_values[x][y]['money_per_command_mult3'] += 0.05

    total_bonus = defaultdict(int)
    for x in range(w // SIZE_OF_ONE_TILE):
        for y in range(h // SIZE_OF_ONE_TILE):
            for value in base_values[x][y]:
                total_bonus[value] += base_values[x][y][value] * multipliers[x][y]
    total_bonus['money_per_command'] = total_bonus['money_per_command_add'] + default_bonuses[
        'money_per_command'] + 1000 * ivory
    if earthyellow:
        total_bonus['mine_sell_mult'] = 1.25
    total_bonus['exp_per_command'] = default_bonuses['exp_per_command'] + total_bonus['exp_per_command_add']
    try:
        total_bonus['money_per_hour'] = default_bonuses['money_per_hour']
    except KeyError:
        total_bonus['money_per_hour'] = 0
    total_bonus['money_per_hour'] += total_bonus['money_per_hour_add']
    for bonus in ['money_per_command', 'exp_per_command', 'money_per_hour']:
        for i in range(1, 11):
            if f'{bonus}_mult{i}' in total_bonus:
                total_bonus[bonus] *= 1 + total_bonus[f'{bonus}_mult{i}']
                del total_bonus[f'{bonus}_mult{i}']
        if f'{bonus}_add' in total_bonus:
            del total_bonus[f'{bonus}_add']

    return total_bonus


def find_color_from_pixel_value(red, green, blue):
    for color in ['SimpleWhite', 'MintCream', 'Ivory', 'SimpleBlack', 'SimpleRed', 'SimpleBlue', 'CobaltBlue',
                  'RaisinBlack', 'ClassicCopper', 'DullCopper', 'MetallicCopper', 'Scarlet', 'Madder', 'Pewter',
                  'SimpleYellow', 'SimpleGreen', 'SimpleMagenta', 'Purgatori', 'Congregation', 'SpringGreen',
                  'BabyBlue', 'EarthYellow', 'PastelPink']:
        if eval(color) == (red, green, blue):
            return color


def random_round(x):
    return 100 * (x - int(x)) > randint(0, 100)


def check_valid_coordinate(uid, preset, x, y):
    im = Image.open(rf'C:\Users\namon\PycharmProjects\discordbot\lib\images\{uid}_{preset}.png')
    w, h = im.size
    im.close()
    if not (1 <= x <= w // SIZE_OF_ONE_TILE and 1 <= y <= h // SIZE_OF_ONE_TILE):
        return 0
    return 1


def f(im, ctx, preset, embed, default_bonuses):
    total_bonus = calculate_total_bonus_from_colors(im, default_bonuses)
    im.save(u := rf"C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{preset}.png")
    bonus_string = ''
    for bonus in total_bonus:
        if bonus.startswith('Copper') or bonus.startswith('Iron') or bonus.startswith('Pewter'):
            bonus_ = bonus.split('_')
            t = db.execute(
                f"UPDATE conupink_mine_info SET {'_'.join(bonus_[1:])} = {total_bonus[bonus]} WHERE UserID = {ctx.author.id} AND mineral_name = '{bonus_[0]}'")
            if not t:
                db.execute(
                    f"INSERT INTO conupink_mine_info (UserID, mineral_name, {'_'.join(bonus_[1:])}) VALUES ({ctx.author.id}, {bonus_[0]}, {total_bonus[bonus]})")
        elif bonus.startswith('mine'):
            pass
        else:
            db.execute(f"UPDATE conupink_user_info SET {bonus} = ? WHERE USERID = ?", total_bonus[bonus], ctx.author.id)
        bonus_string += f'{to_visual_bonus_name[bonus]}: +{total_bonus[bonus]}\n'
    default_bonus_string = '\n'.join(
        [f'{to_visual_bonus_name[bonus]}: +{default_bonuses[bonus]}' for bonus in default_bonuses])
    embed.add_field(name='현재 보너스', value=bonus_string, inline=False)
    embed.add_field(name='기본 보너스', value=default_bonus_string, inline=False)
    return u, embed


def pick_level_to_info(pick_level):
    levels = list(map(int, list(str(pick_level))))
    level_text = ''
    materials = ['구리', '철', '은', '금']
    for i in range(len(levels)):
        level_text += f'\n{materials[i]} 곡괭이: {levels[i]}레벨'
    return levels, level_text, materials[:len(levels)]


def make_new_preset(uid, preset_number):
    with Image.open(r"C:\Users\namon\PycharmProjects\discordbot\lib\images\initial_image.png") as im:
        draw = ImageDraw.Draw(im, 'RGBA')
        draw.rectangle(((0, 0), (SIZE_OF_ONE_TILE * 3, SIZE_OF_ONE_TILE * 3)), (255, 255, 255, 1))
        im.save(u := rf"C:\Users\namon\PycharmProjects\discordbot\lib\images\{uid}_{preset_number}.png")
    return u


class ConUPink(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def purchase_kkyu(self, ctx, kkyu, item, cost, tjfaud):
        if kkyu < cost:
            await send(ctx, "이 아이템을 살 만큼의 뀨를 가지고 있지 않습니다.")
            return 0
        embed = Embed(color=0x00b2ff, title=f"{item} 을(를) 구매합니다.")
        embed.add_field(name="아이템 정보",
                        value=tjfaud,
                        inline=False)
        embed.add_field(name="차감되는 뀨 정보", value=f"{kkyu} -> {kkyu - cost}")
        await send(ctx, f"{item} 을(를) 구매하려고 합니다. `구매`라고 입력해서 구매를 확정지으세요", embed=embed)
        msg = await self.bot.wait_for(
            "message",
            check=lambda message: message.author == ctx.author and ctx.channel == message.channel
        )
        if msg.content == "구매":
            await send(ctx, "구매 완료! 구매해 주셔서 감사합니다.")
            await self.bot.get_channel(823393077376581654).send(f"{ctx.author.id} 님이 뀨 아이템 {item}을 구매하셨습니다.")
            kkyu -= cost
            db.execute("UPDATE games SET kkyu = ? WHERE UserID = ?", kkyu, ctx.author.id)
            db.commit()
            return 1
        return 0

    async def check_level_up(self, ctx, exp, level):
        actual_lvl = check_current_level(exp)
        level_up = actual_lvl - level
        if not level_up:
            return actual_lvl
        embed = Embed(color=0xffd6fe, title=ctx.author.name, description=f'{actual_lvl}로 레벨 업!')
        if actual_lvl == 1:
            embed.add_field(name='레벨업 보상', value='`커뉴야 커뉴핑크 프로필` 기능 해금')
            embed.add_field(name='​',
                            value='잘하셨어요! 이렇게 특정한 양의 경험치를 모으면 레벨업을 할 수 있고, 레벨업할 때마다 특정한 보상을 받을 수 있어요.\n\n특정한 보상은 지금처럼 기능일 수도 있고, 살 수 있는 아이템의 최대 레벨을 확장하는 것일 수도 있고, 아니면 자원을 더 잘 벌 수 있도록 하는 버프일 수도 있어요.\n\n우선 `커뉴야 커뉴핑크 프로필`을 확인해 보시고, 2레벨 달성까지 조금만 더 힘내요!')
        elif actual_lvl == 2:
            embed.add_field(name='레벨업 보상', value='`커뉴야 커뉴핑크 색깔` 기능 해금')
            embed.add_field(name='​', value='커뉴핑크는 색깔의 게임이라고 했죠? 이제부터가 진정한 시작이에요.\n새로 해금된 `커뉴야 커뉴핑크 색깔`을 확인해보세요!')
            l = grant_check("커뉴핑크 사용자", ctx.author.id)
            if l == 1:
                await grant(ctx, "커뉴핑크 사용자", "커뉴핑크에서 2레벨을 달성하세요. 게임은 이제 시작입니다!")
        elif actual_lvl == 3:
            embed.add_field(name='레벨업 보상', value='새로운 색깔 MintCream, Ivory, SimpleBlack 해금')
            embed.add_field(name='​',
                            value='이제까지는 SimpleWhite만 사용할 수 있었지만 새로운 색 몇 가지를 더 사용할 수 있게 됐어요. `커뉴야 커뉴핑크 도감`을 확인해보세요!')
        elif actual_lvl == 4:
            embed.add_field(name='레벨업 보상', value='명령어 실행당 기본 돈 획득량 +10, 상점에 기본 돈, 경험치 획득량 업그레이드 추가')
            embed.add_field(name='​',
                            value='특정한 색을 칠해야만 획득 돈이 늘어나는 효과가 있지만, 상점에 새로 추가된 업그레이드를 사면 칠해진 색깔과 관계없는 보너스를 받으실 수 있어요.')
            default_bonuses = \
                db.record("SELECT default_bonuses FROM conupink_user_info WHERE UserID = ?", ctx.author.id)[0]
            default_bonuses = loads(default_bonuses)
            default_bonuses['money_per_command'] += 10
            default_bonuses = dumps(default_bonuses)
            db.execute("UPDATE conupink_user_info SET default_bonuses = ? WHERE UserID = ?", default_bonuses,
                       ctx.author.id)
        elif actual_lvl == 5:
            embed.add_field(name='레벨업 보상', value='새로운 색깔 SimpleRed, SimpleBlue 해금')
            embed.add_field(name='​',
                            value='이전까지 해금한 색깔들과는 또 다른 효과를 가진 색깔을 사용할 수 있게 됐어요. `커뉴야 커뉴핑크 도감`을 확인해보세요!')
        elif actual_lvl == 6:
            embed.add_field(name='레벨업 보상', value='`커뉴야 커뉴핑크 확장` 기능 해금')
            embed.add_field(name='​',
                            value='이제까지는 3x3 그리드에만 색을 칠할 수 있었지만, 지금부터는 모든 칸의 불투명도가 끝까지 업그레이드되었을 때에 한해 더 많은 칸에 색을 칠할 수 있게 돼요.')
        elif actual_lvl == 7:
            embed.add_field(name='레벨업 보상', value='`커뉴야 커뉴핑크 프리셋` 기능 해금, L1번 프리셋 해금')
            embed.add_field(name='​',
                            value='용도에 따라 다른 색깔들의 조합을 사용해야 할 때가 올 거에요. 그럴 경우를 대비해 완전히 다른 프리셋을 사용할 수 있도록 해 드릴게요!')
            make_new_preset(ctx.author.id, 1000001)
        elif actual_lvl == 8:
            embed.add_field(name='레벨업 보상', value='시간당 획득 돈 기본값 5000 증가')
            embed.add_field(name='​',
                            value='진행을 약간 더 수월하게 만들기 위해 큰 보너스는 아니지만 시간당 약간의 돈을 드릴게요!')
            default_bonuses = \
                db.record("SELECT default_bonuses FROM conupink_user_info WHERE UserID = ?", ctx.author.id)[0]
            default_bonuses = loads(default_bonuses)
            if 'money_per_hour' in default_bonuses:
                default_bonuses['money_per_command'] += 5000
            else:
                default_bonuses['money_per_command'] = 5000
            default_bonuses = dumps(default_bonuses)
            db.execute(
                "UPDATE conupink_user_info SET default_bonuses = ?, money_per_hour = money_per_hour + 5000 WHERE UserID = ?",
                default_bonuses, ctx.author.id)
            db.commit()
        elif actual_lvl == 9:
            embed.add_field(name='레벨업 보상', value='새로운 색깔 CobaltBlue, RaisinBlack 해금')
            embed.add_field(name='​',
                            value='나중엔 예외가 생기지만, 비슷한 계통의 색깔들은 비슷한 느낌의 효과를 가지고 있어요!')
        elif actual_lvl == 10:
            embed.add_field(name='레벨업 보상', value='새로운 색깔 ClassicCopper, DullCopper 해금, `커뉴야 커뉴핑크 광산` 해금, L2번 프리셋 해금')
            embed.add_field(name='​',
                            value='첫 번째 서브 컨텐츠가 열렸어요. 이 색깔은 새로운 프리셋 하나를 파서 칠하시는 걸 추천할게요! 참고로, L으로 시작하는 프리셋은 레벨업 보상으로 주어지는 프리셋이에요.')
            make_new_preset(ctx.author.id, 1000002)
            db.execute("INSERT INTO conupink_mine_info (UserID, mineral_name) VALUES (?, 'Copper')", ctx.author.id)
            db.commit()
            l = grant_check("커뉴핑크 초보 탈출", ctx.author.id)
            if l == 1:
                await grant(ctx, "커뉴핑크 초보 탈출", "커뉴핑크에서 10레벨을 달성하세요.")
        elif actual_lvl == 11:
            embed.add_field(name='레벨업 보상', value='새로운 색깔 MetallicCopper 해금, 상점에서 파는 기본 돈과 경험치 업그레이드 최대 레벨 확장')
            embed.add_field(name='​',
                            value='기본 돈, 경험치 업그레이드 가격이 너무 빠르게 오른다고요? 지금 풀린 업그레이드에서는 전보단 느리게 오를 거에요.')
        elif actual_lvl == 12:
            embed.add_field(name='레벨업 보상', value='새로운 색깔 Scarlet, Madder, Pewter 해금')
            embed.add_field(name='​',
                            value='광산을 확장하는 데 필요한 퓨터를 얻을 수 있는 색깔이 해금됐어요! 나머지 두 색도 인접한 칸들을 버프시켜주는 색이므로 잘 생각해서 칠해 보세요.')
            db.execute("INSERT INTO conupink_mine_info (UserID, mineral_name) VALUES (?, 'Pewter')", ctx.author.id)
            db.commit()
        elif actual_lvl == 13:
            embed.add_field(name='레벨업 보상', value='상점에서 프리셋과 특정한 색깔 물감 사용권을 판매하기 시작')
            await send(ctx, 
                '`커뉴야 커뉴핑크 도감`과 관련된 기술적 문제로 인해 현재 25개가 넘는 색깔을 등록할 수 없는 상태에요. 도감 명령어를 우선 리워크하고 yonsei3이나 yonsei4버전 정도에 오시면 상점에 물감 사용권이 정말로 올라와 있을 거에요. 죄송해요 ㅠㅠ')
        elif actual_lvl == 14:
            embed.add_field(name='레벨업 보상', value='새로운 색깔 SimpleYellow, SimpleGreen, SimpleMagenta 해금')
            embed.add_field(name='​',
                            value='노란색 계통의 색깔은 광물을 주지 않으면서 광산과 관련된, 초록색 계통의 색깔은 경험치와 관련된, 마젠타나 핑크 계통의 색깔은 공식서버와 관련된 효과를 가지고 있어요.')
        elif actual_lvl == 15:
            embed.add_field(name='레벨업 보상', value='시간당 퓨터 생산량 기본값 12 추가, 상점에서 프리미엄 프리셋을 판매하기 시작')
            embed.add_field(name='​',
                            value='퓨터는 광산을 확장하고 새로운 광물을 만나는 데 중요해요. 이 12라는 수치는 SimpleYellow 등의 보너스도 받아가므로 잘 활용해 보세요!')
            db.execute(
                'UPDATE conupink_mine_info SET per_hour_default = per_hour_default + 12 WHERE UserID = ? AND mineral_name = "Pewter"',
                ctx.author.id)
            db.commit()
        elif actual_lvl == 16:
            embed.add_field(name='레벨업 보상', value='새로운 색깔 Purgatori, Congregation 해금, `커뉴야 커뉴핑크 큐브`와 색깔 강화 시스템 해금')
            embed.add_field(name='​',
                            value='두 번째 서브 컨텐츠가 열렸어요. 이제 새로 열린 재화인 큐브를 이용해 존재하는 색깔을 강화시킬 수 있어요!\n지금도 물론 사용할 수 있는 재화이지만, yonsei2 버전이 되면서부터 사용처가 조금씩 조금씩 확대될 거에요!')
            l = grant_check("커뉴핑크 중수", ctx.author.id)
            if l == 1:
                await grant(ctx, "커뉴핑크 중수", "커뉴핑크에서 16레벨을 달성하세요.")
        elif actual_lvl == 17:
            embed.add_field(name='레벨업 보상', value='새로운 색깔 SpringGreen, BabyBlue 해금')
        elif actual_lvl == 18:
            embed.add_field(name='레벨업 보상', value='상점에서 파는 기본 돈과 경험치 업그레이드 최대 레벨 확장, 상점을 통해 퓨터를 구매할 수 있게 됨')
            embed.add_field(name='​',
                            value='기본 돈, 경험치 업그레이드 가격이 너무 비싸다고요? 그동안 열심히 올렸다면 그에 대한 보상을 이제 받을 거에요.')
        elif actual_lvl == 19:
            embed.add_field(name='레벨업 보상', value='새로운 색깔 EarthYellow, PastelPink 해금')
        elif actual_lvl == 20:
            embed.add_field(name='레벨업 보상', value='A1번, L3번 프리셋 해금, `커뉴야 커뉴핑크` 명령어 실행당 주는 돈 기본값 25 추가')
            embed.add_field(name='​',
                            value='참된 커뉴핑크 유저시군요...\nA번 프리셋은 특수한 프리셋으로, 다음과 같은 효과를 가지고 있어요.\n- 불투명도 업그레이드 가격 -100%\n- '
                                  '색칠에 필요한 물감 개수 × 0\n자신보다 크기가 큰 프리셋이 존재한다면 확장 가격 -100%, 그렇지 않다면 확장 가격을 원래의 '
                                  '16766718제곱으로 바꿈\n- 모든 보너스 -100% (레이어 12)\n윗줄 계산 이후 이 프리셋을 장착하기 직전에 장착한 프리셋에 해당하는 '
                                  '보너스 전부를 지급\n용도는 알아서 생각하는 겁니다.')
            with Image.open(r"C:\Users\namon\PycharmProjects\discordbot\lib\images\initial_image.png") as im:
                draw = ImageDraw.Draw(im, 'RGBA')
                draw.rectangle(((0, 0), (SIZE_OF_ONE_TILE * 3, SIZE_OF_ONE_TILE * 3)), (255, 255, 255, 255))
                im.save(rf"C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_3000001.png")
            make_new_preset(ctx.author.id, 1000003)
            default_bonuses = \
                db.record("SELECT default_bonuses FROM conupink_user_info WHERE UserID = ?", ctx.author.id)[0]
            default_bonuses = loads(default_bonuses)
            default_bonuses['money_per_command'] += 25
            default_bonuses = dumps(default_bonuses)
            db.execute("UPDATE conupink_user_info SET default_bonuses = ? WHERE UserID = ?", default_bonuses,
                       ctx.author.id)
            db.commit()
        elif actual_lvl == 21:
            embed.add_field(name='레벨업 보상',
                            value='광산의 3번째, 4번째 확장 가능, 상점에서 10번 프리셋까지 구매할 수 있게 됨')
            embed.add_field(name='​',
                            value='아직은 도감을 확인해도 변했다는 게 보이지 않을 거에요. 하지만 효과 자체는 정상적으로 작동하기 때문에 버그제보를 하지 않으셔도 돼요! (이후 업데이트에서 도감이 리워크되면 정상적으로 효과가 보일 거에요)')
        elif actual_lvl == 22:
            embed.add_field(name='레벨업 보상', value='새로운 색깔 TidalWave 해금')
        elif actual_lvl == 23:
            embed.add_field(name='레벨업 보상', value='기존 7*7을 넘어서, 10*10까지의 확장이 가능해짐')
            embed.add_field(name='​',
                            value='난이도가 어려워지는 시작점이 이곳 23레벨입니다.')
        await send(ctx, embed=embed)
        return actual_lvl

    @command(name='커뉴핑크', aliases=['커핑'])
    @cooldown(1, 7, BucketType.user)
    async def conupink_game(self, ctx, activity: Optional[str], *args):
        activity = activity or '돈벌기'
        cur_stat = db.record("SELECT USERID FROM conupink_user_info WHERE USERID = ?", ctx.author.id)
        if not cur_stat:
            embed = Embed(color=0xffd6fe, title='커뉴핑크에 오신 걸 환영합니다!',
                          description='커뉴핑크는 색깔의 게임입니다.\n처음에는 아무것도 없이 시작하지만, 가능성은 무궁무진하죠.\n하지만 적당한 튜토리얼으로 게임에 빨리 적응하도록 돕겠습니다.\n\n우선 `커뉴야 커뉴핑크` 명령어로 돈부터 벌어 봅시다!')
            db.execute("INSERT INTO conupink_user_info (USERID, default_bonuses) VALUES (?, ?)", ctx.author.id,
                       '{"money_per_command": 10, "exp_per_command": 5}')
            db.commit()
            await send(ctx, embed=embed)
            return

        if activity == '돈벌기':
            cur_money, money_delta, cur_exp, exp_delta, cur_level = db.record(
                "SELECT money, money_per_command, total_exp, exp_per_command, exp_level FROM conupink_user_info WHERE USERID = ?",
                ctx.author.id)
            money_delta += random_round(money_delta)
            exp_delta += random_round(exp_delta)
            embed = Embed(color=0xffd6fe, title=ctx.author.name)
            if ctx.author.id in premium_boosted:
                if time() > premium_boosted[ctx.author.id]:
                    del premium_boosted[ctx.author.id]
                else:
                    money_delta *= 5
                    exp_delta *= 5
                    embed.set_footer(text='애교 부스터 적용중!')
            embed.add_field(name='가진 돈 변화', value=f'{cur_money:,} -> {int(cur_money + money_delta):,}')
            embed.add_field(name='획득한 경험치', value=f'{cur_exp:,} -> {int(cur_exp + exp_delta):,}')
            cur_level = await self.check_level_up(ctx, cur_exp + exp_delta, cur_level)
            mineral_per_command_info = db.records(
                "SELECT mineral_name, per_command FROM conupink_mine_info WHERE USERID = ? AND per_command != 0",
                ctx.author.id)
            if mineral_per_command_info:
                mineral_gain_text = []
                for mineral_name, per_command in mineral_per_command_info:
                    if premium_boosted:
                        per_command *= 5
                        mineral_gain_text.append(f'{mineral_EtoK[mineral_name]}: {per_command}')
                        db.execute("UPDATE conupink_mine_info SET amount = amount + ? WHERE UserID = ?", per_command,
                                   ctx.author.id)
            await send(ctx, embed=embed)
            db.execute(
                "UPDATE conupink_user_info SET money = money + ?, net_money = net_money + ?, total_exp = total_exp + ?, exp_level = ? WHERE USERID = ?",
                int(money_delta), int(money_delta), int(exp_delta), cur_level, ctx.author.id)
            db.commit()

        elif activity == '도움':
            level, progress = db.record("SELECT exp_level, progress FROM conupink_user_info WHERE USERID = ?",
                                        ctx.author.id)
            embed = Embed(color=0xffd6fe, title='커뉴핑크 도움! | ver beta', description='현재 사용할 수 있는 기능만 도움말에 표시돼요!')
            help_text = '`커뉴야 커뉴핑크 도움`: 이 도움말을 표시합니다.\n`커뉴야 커뉴핑크`: 돈과 경험치를 획득합니다.'
            if level >= 1:
                help_text += '\n`커뉴야 커뉴핑크 프로필`: 현재 당신의 다양한 스탯들을 표시합니다.'
            if level >= 2:
                help_text += '\n`커뉴야 커뉴핑크 색깔`: 당신의 색 현황을 확인합니다.'
            if os.path.exists(
                    os.path.join(r'C:\Users\namon\PycharmProjects\discordbot\lib\images', f'{ctx.author.id}_1.png')):
                help_text += '\n`커뉴야 커뉴핑크 튜토리얼 (색깔, 레이어)`: 입력된 기능의 튜토리얼을 표시합니다.\n`커뉴야 커뉴핑크 업글 x y z`: 왼쪽에서 x번째, ' \
                             '위에서 y번째 칸의 불투명도를 z번 업그레이드합니다. z가 주어지지 않았을 경우 z는 1입니다.\n`커뉴야 커뉴핑크 칸정보 x y`: 왼쪽에서 x번째, ' \
                             '위에서 y번째 칸의 정보를 확인합니다.\n`커뉴야 커뉴핑크 도감`: 지금까지 해금한 색깔들의 목록과 색깔들 각각의 효과를 표시합니다.'
            if progress >= 1:
                help_text += '\n`커뉴야 커뉴핑크 상점`: 구매 가능한 아이템들의 목록을 표시합니다.'
                help_text += '\n`커뉴야 커뉴핑크 구매 item`: 상점에서 구매 가능한 아이템들 중 원하는 것을 구매합니다.'
                help_text += '\n`커뉴야 커뉴핑크 색칠 x y color`: 왼쪽에서 x번째, 위에서 y번째 칸의 색을 color(으)로 칠합니다. 주의: 원래 칠해져 있던 색의 효과는 더 이상 받을 수 없고 물감도 돌려받지 못합니다. 다만 올라간 물감 가격은 다시 내려갑니다.'
                help_text += '\n`커뉴야 커뉴핑크 물감`: 가지고 있는 물감 개수를 보여줍니다. SimpleWhite의 경우 언제든 칠할 수 있으므로 표시하지 않습니다. (물감을 구매한 적이 있어야 작동)'
                help_text += '\n`커뉴야 커뉴핑크 획득`: 시간당 보너스를 주는 색깔이 있을 경우 그 보너스를 받습니다.'
            if level >= 6:
                help_text += '\n`커뉴야 커뉴핑크 확장`: 모든 칸의 불투명도가 끝까지 업그레이드되었을 때 칸을 확장합니다.'
            if level >= 7:
                help_text += '\n`커뉴야 커뉴핑크 프리셋`: 당신의 프리셋 현황을 확인합니다.\n장착은 `커뉴야 커뉴핑크 프리셋 (장착할프리셋)`'
            if level >= 10:
                help_text += '\n`커뉴야 커뉴핑크 광산`: 광산 컨텐츠를 진행합니다.'
            if level >= 16:
                help_text += '\n`커뉴야 커뉴핑크 큐브`: 가지고 있는 큐브 정보를 확인합니다.\n`커뉴야 커뉴핑크 강화 x y`: 왼쪽에서 x번째, 위에서 y번째 칸을 강화합니다.'
            embed.add_field(name='​', value=help_text)
            await send(ctx, embed=embed)

        elif activity == '프로필':
            embed = Embed(color=0xffd6fe, title=ctx.author.name)
            cur_stat = db.record("SELECT * FROM conupink_user_info WHERE USERID = ?", ctx.author.id)
            _, money, progress, net_money, money_per_command, money_per_hour, exp_level, total_exp, exp_per_command, current_preset, kkyu_preset_amount, last_gained, mpc_default_level, epc_default_level, default_bonuses, pick_level, scary_cube, red_cube, purple_cube, crimson_cube, blue_cube, cyan_cube, sunset_cube, cute_cube = cur_stat
            if exp_level == 0:
                return
            embed.add_field(name='가진 돈', value=f'현재 돈: {money:,}, 현재까지 번 돈 총량: {net_money:,}')
            embed.add_field(name='레벨',
                            value=f'현재 레벨: {exp_level}, 총 경험치 {total_exp} (다음 레벨까지 {level_thresholds[exp_level + 1] - total_exp})')
            embed.add_field(name='돈 획득량',
                            value=f'`커뉴야 커뉴핑크` 1회 실행 당 {money_per_command}' + f', 시간당 {money_per_hour} (최대 24시간까지)' * int(
                                bool(money_per_hour)))
            embed.add_field(name='경험치 획득량', value=f'`커뉴야 커뉴핑크` 1회 실행 당 {exp_per_command}')
            embed.set_footer(text='값이 정수면 그대로 받아들이시면 되고, 정수가 아니면 정수부분 + (소수부분 확률로 1 추가) 라고 받아들이시면 됩니다.')
            await send(ctx, embed=embed)

        elif activity == '색깔':
            level = db.record("SELECT exp_level FROM conupink_user_info WHERE USERID = ?", ctx.author.id)[0]
            if level < 2:
                return
            if not os.path.exists(
                    os.path.join(r'C:\Users\namon\PycharmProjects\discordbot\lib\images', f'{ctx.author.id}_1.png')):
                u = make_new_preset(ctx.author.id, 1)
                embed = make_tutorial_embed(ctx.author.name)
                embed.add_field(name='해금된 기능',
                                value='`커뉴야 커뉴핑크 튜토리얼`: 지금 보고 계신 화면을 출력합니다. 이 부분 빼고요.\n`커뉴야 커뉴핑크 업글 x y (z)`: 왼쪽에서 x번째, 위에서 y번째 칸의 불투명도를 z번 업그레이드합니다.\n`커뉴야 커뉴핑크 칸정보 x y`: 왼쪽에서 x번째, 위에서 y번째 칸의 정보를 표시합니다.\n`커뉴야 커뉴핑크 도감`: 지금까지 해금한 색깔들의 목록과 색깔들 각각의 효과를 표시합니다.')
                embed.set_footer(text='`커뉴야 커뉴핑크 업글 1 1 1`을 먼저 시도해보세요. 이 칸을 먼저 업그레이드하는 것이 가장 좋을 겁니다!')
                await ctx.channel.send(embed=embed, file=File(u))
            else:
                preset = db.record("SELECT current_preset FROM conupink_user_info WHERE USERID = ?", ctx.author.id)[0]
                await send(ctx, 
                    file=File(rf'C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{preset}.png'))

        elif activity == '튜토리얼':
            if os.path.exists(
                    os.path.join(r'C:\Users\namon\PycharmProjects\discordbot\lib\images', f'{ctx.author.id}_1.png')):
                if not args or args[0] == '색깔':
                    await send(ctx, embed=make_tutorial_embed(ctx.author.name))
                elif args[0] == '레이어':
                    embed = Embed(color=0xffd6fe, title='커뉴핑크 레이어 시스템 튜토리얼',
                                  description='**+1%p** 와 같은 보너스를 **곱연산** 보너스라고 합니다.\n\n예를 들어, 명령어 실행당 획득 돈이 10인 상태에서 MintCream으로 색칠된 칸 하나에 의해 +16%p 보너스를 얻으면 최종 계산 결과 명령어 실행당 획득 돈은 11.6입니다.\n\n**레이어**는 여러 가지 곱연산 보너스를 동시에 받고 있을 때 그것들을 어떤 순서로 계산할지 알려줍니다.\n\nMintCream은 **레이어 1**의 보너스를 주기 때문에, 만약 MintCream을 세 칸에 칠했다면 그때의 명령어 실행당 획득 돈은 10 × (1 + 0.16) × (1 + 0.16) × (1 + 0.16) = 약 15.6**이 아니고** 10 × (1 + 0.16 + 0.16 + 0.16) = 14.8이 됩니다.\n\n만약 이 상태에서 어떻게든 **레이어 2**의 보너스 10%p를 받게 된다면, 그때의 명령어 실행당 획득 돈은 10 × (1 + 0.16 + 0.16 + 0.16) × (1 + 0.1) = 약 16.3이 됩니다.\n\n다른 레이어의 보너스들이 있다면 그것도 비슷하게 적용됩니다.\n\n그렇다면 명령어 실행당 획득 돈이 10 × (1 + 0.16) × (1 + 0.16) × (1 + 0.16)으로 계산된다면 어떤 보너스를 받고 있을까요?\n\n||레이어 1,2,3에 각각 +16%p를 받고 있다||는 대답이 나오셨다면, 잘 이해하신 겁니다!')
                    await send(ctx, embed=embed)

        elif activity == '칸정보':
            if not os.path.exists(
                    os.path.join(r'C:\Users\namon\PycharmProjects\discordbot\lib\images', f'{ctx.author.id}_1.png')):
                return
            try:
                x, y = map(int, args)
            except:
                await send(ctx, "`커뉴야 커뉴핑크 칸정보 x y`")
                return
            preset = db.record("SELECT current_preset FROM conupink_user_info WHERE USERID = ?", ctx.author.id)[0]
            with Image.open(
                    rf"C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{preset}.png") as im:
                red, green, blue, opacity = im.getpixel(
                    (SIZE_OF_ONE_TILE * (x - 1) + 1, SIZE_OF_ONE_TILE * (y - 1) + 1))
                color = find_color_from_pixel_value(red, green, blue)
                embed = Embed(color=red * 0x10000 + green * 0x100 + blue, title=ctx.author.name)
                embed.add_field(name=f'({x}, {y})칸 정보', value=f'색깔: {color}, 불투명도 레벨: {opacity}')
                await send(ctx, embed=embed)

        elif activity == '업글':
            if not os.path.exists(
                    os.path.join(r'C:\Users\namon\PycharmProjects\discordbot\lib\images', f'{ctx.author.id}_1.png')):
                return
            if len(args) == 2:
                try:
                    x, y = map(int, args)
                except ValueError:
                    x = 0
                    y = 0
                z = 1
            elif len(args) == 3:
                try:
                    x, y, z = map(int, args)
                except ValueError:
                    x = 0
                    y = 0
                    z = 1
            else:
                await send(ctx, "`커뉴야 커뉴핑크 업글 x y (z)`")
                return
            preset = db.record("SELECT current_preset FROm conupink_user_info WHERE UserID = ?", ctx.author.id)[0]
            if not check_valid_coordinate(ctx.author.id, preset, x, y):
                await send(ctx, "올바르지 않은 값을 입력했어요!")
                return
            cost_scale = opacity_costs[max(x, y)]
            im = Image.open(rf'C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{preset}.png')
            red, green, blue, opacity = im.getpixel((SIZE_OF_ONE_TILE * (x - 1) + 1, SIZE_OF_ONE_TILE * (y - 1) + 1))
            if opacity == 255:
                await send(ctx, "이 칸은 이미 불투명도 업그레이드를 완료했어요!")
                return
            elif opacity + z > 255:
                z = 255 - opacity
            total_cost = sum(cost_scale[opacity + 1:opacity + z + 1])
            money, default_bonuses = db.record("SELECT money, default_bonuses FROM conupink_user_info WHERE USERID = ?",
                                               ctx.author.id)
            if money < total_cost:
                await send(ctx, f"업그레이드를 위한 돈이 부족해요! 원하시는 만큼 업그레이드하기 위해서는 돈이 {total_cost}만큼 필요해요.")
                return
            new_opacity = opacity + z
            embed = Embed(color=red * 0x10000 + green * 0x100 + blue, title=ctx.author.name)
            embed.add_field(name=f'({x}, {y})칸 불투명도 업그레이드 완료',
                            value=f'돈을 {total_cost}만큼 소모해 불투명도 레벨을 {z}만큼 올려 {new_opacity}레벨이 됐어요!', inline=False)
            db.execute("UPDATE conupink_user_info SET money = money - ? WHERE USERID = ?", total_cost, ctx.author.id)
            draw = ImageDraw.Draw(im, 'RGBA')
            draw.rectangle(((SIZE_OF_ONE_TILE * (x - 1), (SIZE_OF_ONE_TILE * (y - 1))),
                            (SIZE_OF_ONE_TILE * x - 1, SIZE_OF_ONE_TILE * y - 1)), (red, green, blue, new_opacity))
            u, embed = f(im, ctx, preset, embed, default_bonuses)
            await send(ctx, embed=embed, file=File(u))
            db.commit()
            if x == y == 1 and opacity + z == 255:
                embed = Embed(color=0xffffff, title=ctx.author.name)
                embed.add_field(name='불투명도를 끝까지 업그레이드했어요!', value='불투명도를 끝까지 업그레이드한 칸들은 다른 색으로 칠할 수 있어요.\n특정한 색으로 칠할 '
                                                                  '때 어떤 효과가 나타나는지는 `커뉴야 커뉴핑크 도감`에서 확인할 수 있어요.\n만약 도감에 '
                                                                  'SimpleWhite밖에 없다면, 경험치를 2000까지 벌어서 3레벨로 승급하시면 다른 색깔을 '
                                                                  '해금하실 수 있을 거에요.\n\n그렇기 때문에, 새로 `커뉴야 커뉴핑크 색칠 x y '
                                                                  'color`라는 명령어가 해금됐어요. 이 명령어는 왼쪽에서 x번째, 위에서 y번째에 위치한 '
                                                                  '칸을 color 색으로 칠하는 명령어에요. 칠해진 색을 바꾸면 원래 색이 가진 효과를 더 '
                                                                  '이상 얻지 못하게 되기 때문에 신중히 결정하셔야 돼요!')
                await send(ctx, embed=embed)
                db.execute("UPDATE conupink_user_info SET progress = 1 WHERE USERID = ?", ctx.author.id)
                db.commit()

        elif activity == '도감':
            if not os.path.exists(
                    os.path.join(r'C:\Users\namon\PycharmProjects\discordbot\lib\images', f'{ctx.author.id}_1.png')):
                return
            '''if not args:
                embed = Embed(color=0xffd6fe, title='리뉴얼된 색깔 도감 안내', description='이 도움말 중 도감이 어떻게 변했는지에 관련된 항목은 yonsei5버전 정도에 사라잘 예정이에요.')
                embed.add_field(name='도감이 리뉴얼된 이유', value='이전 시스템은 기술적인 한계상 서로 다른 25가지가 넘는 색을 표시할 수 없었고, 그에 따라 리뉴얼이 필요한 상황.')
                embed.add_field(name='변경 사항', value='이제 뀨 상점 페이지나 도전과제 목록 페이지처럼 색깔들이 카테고리로 나누어져 보입니다. 다만 그 기능들보다는 조금 더 유연한 검색을 지원합니다.')
                embed.add_field(name='특정한 색깔만 보기', value='`커뉴야 커뉴핑크 도감 (색이름)`을 입력하면, 잠금해제된 색깔에 한해 해당 색깔에 대한 자세한 정보를 알려줍니다.')
                embed.add_field(name='비슷한 색깔들을 보기', value='`커뉴야 커뉴핑크 도감 (색종류)`를 입력하면, 잠금해제된 색깔에 한해 해당 카테고리의 색깔 목록을 알려줍니다. 예시로, `초록`, `밝은` 등을 색종류에 넣을 수 있습니다.')
                embed.set_footer(text='다른 검색 필터 아이디어 받아요')
                await send(ctx, embed=embed)
            elif args[0] == '밝은':
                col_name, val, coloring_cost, unlock_level, misc, unlock_currency, description, effect = db.record("SELECT col_name, val, coloring_cost, unlock_level, misc, unlock_currency, description, effect FROM colors WHERE col_name = ?", args[0])
'''
            exp_level = db.record("SELECT exp_level FROM conupink_user_info WHERE USERID = ?", ctx.author.id)[0]
            embed = Embed(color=0xffd6fe, title=ctx.author.name)
            embed.add_field(name='SimpleWhite 0xffffff', value='`커뉴야 커뉴핑크`명령어 실행당 획득 돈 250 증가', inline=False)
            if exp_level >= 3:
                embed.add_field(name='MintCream  0xf5fffa', value='`커뉴야 커뉴핑크`명령어 실행당 획득 돈 16%p 증가 (레이어 1)',
                                inline=False)
                embed.add_field(name='Ivory 0xfffff0',
                                value='`커뉴야 커뉴핑크`명령어 실행당 획득 돈 1000 증가, 그러나 여러 칸을 이 색으로 칠해도 한 칸에만 칠한 것으로 간주',
                                inline=False)
                embed.add_field(name='SimpleBlack 0x000000', value='시간당 획득 돈 5000 증가', inline=False)
            if exp_level >= 5:
                embed.add_field(name='SimpleRed 0xff0000', value='바로 오른쪽 칸이 자신을 부스트하며 제약조건이 없는 경우, 그 칸의 효과를 2.5배로 만듦',
                                inline=False)
                embed.add_field(name='SimpleBlue 0x0000ff',
                                value='`커뉴야 커뉴핑크`명령어 실행당 경험치 획득량 **기본값**이 x일 때, `커뉴야 커뉴핑크`명령어 실행당 획득 돈 x%p 증가 (레이어 2)',
                                inline=False)
            if exp_level >= 9:
                embed.add_field(name='CobaltBlue 0x0d4abc',
                                value='현재 프리셋의 크기 (얼마나 확장했는지)에 따라 `커뉴야 커뉴핑크`명령어 실행당 획득 돈 증가 (3×3일 경우 300, 4×4일 경우 500, 5×5일 경우 1200, ...)',
                                inline=False)
                embed.add_field(name='RaisinBlack 0x212027', value='시간당 획득 돈 20%p 증가 (레이어 1)', inline=False)
            if exp_level >= 10:
                embed.add_field(name='ClassicCopper 0xce7c56', value='`커뉴야 커뉴핑크`명령어 실행당 구리 획득량 기댓값 0.4 증가',
                                inline=False)
                embed.add_field(name='DullCopper 0xb47360', value='시간당 획득 구리 30 증가', inline=False)
            if exp_level >= 11:
                embed.add_field(name='MetallicCopper 0x71291d',
                                value='`커뉴야 커뉴핑크`명령어 실행당 구리 획득량 기댓값 0.2 증가, `커뉴야 커뉴핑크`명령어 실행당 철 획득량 기댓값 0.1 증가',
                                inline=False)
            if exp_level >= 12:
                embed.add_field(name='Scarlet 0xff2f00',
                                value='상하좌우로 맞붙어 있는 칸들이 자신을 부스트하며 제약조건이 없는 경우, 그 칸의 효과를 25%만큼 증폭', inline=False)
                embed.add_field(name='Madder 0xa20021',
                                value='대각선으로 맞붙어 있는 칸들이 자신을 부스트하며 제약조건이 없는 경우, 그 칸의 효과를 25%만큼 증폭', inline=False)
                embed.add_field(name='Pewter 0xe9eaec', value='시간당 획득 퓨터 30 증가', inline=False)
            if exp_level >= 14:
                embed.add_field(name='SimpleYellow 0xffff00', value='모든 광산 관련 보너스를 20%만큼 증폭', inline=False)
                embed.add_field(name='SimpleGreen 0x00ff00', value='`커뉴야 커뉴핑크`명령어 실행당 획득 경험치 3 증가', inline=False)
                embed.add_field(name='SimpleMagenta 0xff00ff',
                                value='공식서버 레벨과 관련된 도전과제 달성 개수에 따라 `커뉴야 커뉴핑크`명령어 실행당 돈 획득량 증가 (합연산 + 레이어 1 곱연산)',
                                inline=False)
            if exp_level >= 16:
                # embed.add_field(name='Purgatori 895761', value='상하좌우 또는 대각선으로 인접해 있는 칸 중 Congregation으로 칠해진 칸이 있다면 그 칸의 효과를 2배로, 이외의 `큐브 획득 기댓값 증가`를 효과로 가지는 색이 칠해진 칸이 있다면 그 칸의 효과를 1.3배로 만듦', inline=False)
                embed.add_field(name='Purgatori 895761', value='??????', inline=False)
                embed.add_field(name='Congregation a02103', value='`커뉴야 커뉴핑크` 명령어 실행당 무서운 큐브 획득량 기댓값 0.05 증가',
                                inline=False)
            if exp_level >= 17:
                embed.add_field(name='SpringGreen 0x00ff7f',
                                value='공식서버의 경험치 부스트에 따라 `커뉴야 커뉴핑크`명령어 실행당 경험치 증가, 경험치 부스트가 1.25 이하라면 그대로 레이어 1에 적용, 1.25를 넘는다면 증가하지만 위로 볼록한 함수에 대입해 나온 만큼의 보너스를 레이어 1에 적용 (경험치 부스트가 2라면 40% 정도 늘리는 효과)',
                                inline=False)
                embed.add_field(name='BabyBlue 0xb1c5d4',
                                value='한 번이라도 물감을 구매한 적이 있는 색깔의 개수에 따라 `커뉴야 커뉴핑크`명령어 실행당 획득 돈 증가 (레이어 1)', inline=False)
            if exp_level >= 19:
                embed.add_field(name='EarthYellow 0xffb257',
                                value='모든 광물의 판매 가격 25% 증가, 그러나 여러 칸을 이 색으로 칠해도 한 칸에만 칠한 것으로 간주', inline=False)
                embed.add_field(name='PastelPink 0xfe5779',
                                value='`커뉴야 커뉴핑크`명령어 실행당 획득 돈 5%p 감소 (레이어 1), `커뉴야 커뉴핑크`명령어 실행당 획득 돈 5%p 증가 (레이어 3)',
                                inline=False)
            await send(ctx, embed=embed)

        elif activity == '상점':
            progress, exp_level, kkyu_preset_amount = db.record(
                "SELECT progress, exp_level, kkyu_preset_amount FROM conupink_user_info WHERE UserID = ?",
                ctx.author.id)
            if not progress:
                return
            embed = Embed(color=0xffd6fe, title=ctx.author.name)
            embed.add_field(name='색깔 물감',
                            value='도감에 있는 색깔에 대하여 `커뉴야 커뉴핑크 구매 (색이름)`을 입력하면 해당 색깔 물감을 구매할 수 있어요. 같은 색의 물감을 많이 가지고 있을수록, 그 색이 많이 칠해져 있을수록 가격이 올라요. 단, 상점에 따로 표시된 색깔들은 이 규칙을 적용받지 않아요.')
            if exp_level >= 4:
                embed.add_field(name='명령어 시행당 기본 돈 증가',
                                value='돈을 주면 `커뉴야 커뉴핑크` 명령어 사용 1회당 획득하는 돈의 기본값을 2만큼 증가시켜요. `커뉴야 커뉴핑크 구매 명령어 실행당 기본 돈 증가` 또는 `커뉴야 커뉴핑크 구매 기본돈`으로 구매할 수 있어요.')
                embed.add_field(name='명령어 시행당 기본 경험치 증가',
                                value='돈을 주면 `커뉴야 커뉴핑크` 명령어 사용 1회당 획득하는 경험치의 기본값을 1만큼 증가시켜요. `커뉴야 커뉴핑크 구매 명령어 실행당 기본 경험치 증가` 또는 `커뉴야 커뉴핑크 구매 기본경험치`로 구매할 수 있어요.')
            if exp_level >= 11:
                embed.add_field(name='애교 부스터',
                                value='3뀨를 주면 `명령어 실행당` 관련된 모든 보너스를 5분간 5배로 만들어요. `커뉴야 커뉴핑크 구매 애교`로 구매할 수 있어요.')
                embed.add_field(name='더 귀여운 애교 부스터',
                                value='9뀨를 주면 `명령어 실행당` 관련된 모든 보너스를 20분간 5배로 만들어요. `커뉴야 커뉴핑크 구매 애교2`로 구매할 수 있어요.')
                embed.set_footer(text='뀨와 관련된 시간제 부스트들은 도중에 봇이 꺼질 경우 남은 시간만큼의 부스트에 해당하는 뀨가 환불돼요.')
            if exp_level >= 13:
                embed.add_field(name='FakeConU 물감',
                                value='3뀨를 주면 구매할 수 있으며, yonsei2 정도의 버전부터 도감에 표시될 예정이에요. 모든 보너스 계산이 끝난 뒤, 이 색이 칠해진 칸은 `명령어 실행당 획득 돈 3.5% 증가`를 받아요. 이해, 수학, 커뉴핑크를 잘하신다면...')
                if exp_level < 21:
                    embed.add_field(name='다음 프리셋',
                                value='돈 250000만큼을 내면 2~5번 프리셋을 살 수 있어요. 무조건 2번부터 5번까지 순서대로 사야 하는 것은 아니고, 그렇기 때문에 구매한 프리셋 개수만큼 다음 프리셋의 가격이 오르지도 않아요. `커뉴야 커뉴핑크 구매 프리셋 (2~5)`로 구매할 수 있어요.')
            if exp_level >= 15:
                embed.add_field(name=f'P{kkyu_preset_amount + 1}번 프리셋',
                                value=f'{kkyu_preset_amount * 2 + 8}뀨를 주면 다음 프리미엄 프리셋을 열 수 있어요. `커뉴야 커뉴핑크 구매 P{kkyu_preset_amount + 1}`로 구매할 수 있어요.')
            if exp_level >= 21:
                embed.add_field(name='다음 프리셋',
                                value='2번부터 5번까지는 250000, 6번부터 10번까지는 1500000의 돈을 내면 `커뉴야 커뉴핑크 구매 프리셋 (2~10)`으로 다음 프리셋을 구매할 수 있어요.')
            await send(ctx, embed=embed)

        elif activity == '구매':
            if not args:
                await send(ctx, '`커뉴야 커뉴핑크 구매 (구매할아이템)`')
                return
            cur_stat = db.record("SELECT * FROM conupink_user_info WHERE USERID = ?", ctx.author.id)
            _, money, progress, net_money, money_per_command, money_per_hour, exp_level, total_exp, exp_per_command, current_preset, kkyu_preset_amount, last_gained, mpc_default_level, epc_default_level, default_bonuses, pick_level, scary_cube, red_cube, purple_cube, crimson_cube, blue_cube, cyan_cube, sunset_cube, cute_cube = cur_stat
            if not progress:
                return
            if exp_level >= 4:
                default_bonuses = loads(default_bonuses)
                if args[0] == '기본돈' or (len(args) == 5 and ' '.join(args) == '명령어 실행당 기본 돈 증가'):
                    if mpc_default_level >= 45:
                        await send(ctx, '현재 버전에서 설정된 최대 레벨을 달성했어요!')
                        return
                    elif (mpc_default_level >= 10 and exp_level < 11) or (mpc_default_level >= 20 and exp_level < 18):
                        await send(ctx, '경험치 레벨을 더 올려서 이 업그레이드를 계속하세요!')
                        return
                    else:
                        cost = mpc_default_upgrade_cost[mpc_default_level]
                        if money < cost:
                            await send(ctx, f'해당 업그레이드를 하려면 돈이 {cost}만큼 필요해요!')
                            return
                        default_bonuses['money_per_command'] += 2
                        db.execute(
                            "UPDATE conupink_user_info SET mpc_default_level = mpc_default_level + 1, money = money - ?, default_bonuses = ?, money_per_command = money_per_command + 2 WHERE UserID = ?",
                            cost, dumps(default_bonuses), ctx.author.id)
                        db.commit()
                        await send(ctx, '구매 완료!')
                        return
                if args[0] == '기본경험치' or (len(args) == 5 and ' '.join(args) == '명령어 실행당 기본 경험치 증가'):
                    if epc_default_level >= 25:
                        await send(ctx, '현재 버전에서 설정된 최대 레벨을 달성했어요!')
                        return
                    elif (epc_default_level >= 10 and exp_level < 11) or (epc_default_level >= 20 and exp_level < 18):
                        await send(ctx, '경험치 레벨을 더 올려서 이 업그레이드를 계속하세요!')
                        return
                    else:
                        cost = epc_default_upgrade_cost[epc_default_level]
                        if money < cost:
                            await send(ctx, f'해당 업그레이드를 하려면 돈이 {cost}만큼 필요해요!')
                            return
                        default_bonuses['exp_per_command'] += 1
                        db.execute(
                            "UPDATE conupink_user_info SET epc_default_level = epc_default_level + 1, money = money - ?, default_bonuses = ?, exp_per_command = exp_per_command + 1 WHERE UserID = ?",
                            cost, dumps(default_bonuses), ctx.author.id)
                        db.commit()
                        await send(ctx, '구매 완료!')
                        return
            if exp_level >= 11:
                if args == ('애교',):
                    if ctx.author.id in premium_boosted:
                        await send(ctx, '이미 부스터 적용 중이에요. 나중에 다시 구매해 주세요!')
                        return
                    p = await self.purchase_kkyu(ctx,
                                                 db.record("SELECT kkyu FROM games WHERE UserID = ?", ctx.author.id)[0],
                                                 '애교 부스터', 3,
                                                 "구매 직후부터 5분간 `명령어 실행당` 관련된 모든 보너스를 5배로 만들어요.")
                    if p == 1:
                        premium_boosted[ctx.author.id] = time() + 300
                    return
                if args == ('애교2',):
                    if ctx.author.id in premium_boosted:
                        await send(ctx, '이미 부스터 적용 중이에요. 나중에 다시 구매해 주세요!')
                        return
                    p = await self.purchase_kkyu(ctx,
                                                 db.record("SELECT kkyu FROM games WHERE UserID = ?", ctx.author.id)[0],
                                                 '더 귀여운 애교 부스터', 9,
                                                 "구매 직후부터 20분간 `명령어 실행당` 관련된 모든 보너스를 5배로 만들어요.")
                    if p == 1:
                        premium_boosted[ctx.author.id] = time() + 1200
                    return
            if exp_level >= 13:
                if args == ['FakeConU']:
                    p = await self.purchase_kkyu(ctx,
                                                 db.record("SELECT kkyu FROM games WHERE UserID = ?", ctx.author.id)[0],
                                                 'FakeConU 물감', 3,
                                                 "FakeConU 물감을 하나 구매해요."
                                                 "**이 물감은 다른 물감들과 다르게 이 색이 칠해져 있던 칸에 다른 색을 칠하게 되면 물감을 그대로 돌려받을 수 있고,"
                                                 "물감을 구매한 개수에 따라 가격이 오르지도 않아요.**")
                    if p == 1:
                        t = db.execute(
                            "UPDATE conupink_color_info SET available = available + 1 WHERE UserID = ? AND col_name = 'FakeConU'")
                        if not t:
                            db.execute(
                                "INSERT INTO conupink_color_info (UserID, col_name, available) VALUES (?, 'FakeConU', 1)",
                                ctx.author.id)
                        db.commit()
                    return
            if exp_level >= 15:
                if args == [f'P{kkyu_preset_amount}']:
                    p = await self.purchase_kkyu(ctx,
                                                 db.record("SELECT kkyu FROM games WHERE UserID = ?", ctx.author.id)[0],
                                                 f'P{kkyu_preset_amount + 1}번 프리셋', kkyu_preset_amount * 2 + 8,
                                                 "프리미엄 프리셋을 하나 구매해요."
                                                 "yonsei3이나 그 근처 버전부터, 모든 프리미엄 프리셋에는 다음과 같은 효과가 부여될 예정이에요."
                                                 "\n- 1번 프리셋이 이 프리셋보다 많이 확장되었다면, 이 프리셋의 불투명도 업그레이드 비용 50% 감소")
                    if p == 1:
                        make_new_preset(ctx.author.id, 2000000 + kkyu_preset_amount + 1)
            if exp_level >= 13:
                if len(args) == 2 and args[0] == '프리셋' and args[1].isdigit():
                    preset_number = int(args[1])
                    if preset_number > 10:
                        await send(ctx, '구매할 수 없는 프리셋 번호에요!')
                        return
                    elif preset_number > 5 and exp_level < 21:
                        await send(ctx, '경험치 레벨을 21까지 높여야 해당 프리셋을 구매할 수 있어요!')
                        return
                    if preset_number < 5:
                        cost = 200000
                    else:
                        cost = 1500000
                    if money < cost:
                        await send(ctx, '프리셋 구매를 위한 돈이 부족해요!')
                        return
                    make_new_preset(ctx.author.id, preset_number)
                    await send(ctx, '새로운 프리셋을 만들었어요!')
                    db.execute("UPDATE conupink_user_info SET money = money - ? WHERE UserID = ?", cost, ctx.author.id)
                    db.commit()
                    return
            target_color = db.record("SELECT * FROM colors WHERE col_name = ?", args[0])
            if not target_color:
                await send(ctx, "올바르지 않은 색 이름이에요!")
                return
            col_name, val, coloring_cost, unlock_level, misc, unlock_currency, description, effect = target_color
            money, level = db.record("SELECT money, exp_level FROM conupink_user_info WHERE USERID = ?", ctx.author.id)
            if unlock_level > level:
                return
            exponent = db.record("SELECT used + available FROM conupink_color_info WHERE UserID = ? AND col_name = ?",
                                 ctx.author.id, col_name)
            if not exponent:
                db.execute("INSERT INTO conupink_color_info (UserID, col_name) VALUES (?, ?)", ctx.author.id, col_name)
                exponent = [0]
            coloring_cost *= (2 ** exponent[0])
            await send(ctx, 
                f'{col_name} 물감을 구매하려고 해요. 현재 1, 2, 3개를 구매하기 위한 가격은 각각 {to_visual_currency_name[unlock_currency]} {coloring_cost}, {coloring_cost * 3}, {coloring_cost * 7} 이에요. 아이템을 몇 개 구매할지 입력해주세요.')
            try:
                amount = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda
                        message: message.author == ctx.author and ctx.channel == message.channel and message.content.isdigit()
                )
            except asyncio.TimeoutError:
                await send(ctx, "구매하지 않기로 했어요.")
                return
            amount = int(amount.content)
            coloring_cost *= 2 ** amount - 1
            if unlock_currency == 'Money':
                if coloring_cost > money:
                    await send(ctx, 
                        f'돈이 부족해요! 해당 아이템을 구매하려면 {to_visual_currency_name[unlock_currency]} {coloring_cost}만큼이 필요해요.')
                    return
                else:
                    db.execute("UPDATE conupink_user_info SET money = money - ? WHERE USERID = ?", coloring_cost,
                               ctx.author.id)
            db.execute("UPDATE conupink_color_info SET available = available + ? WHERE UserID = ? AND col_name = ?",
                       amount, ctx.author.id, col_name)
            db.commit()
            await send(ctx, '구매 완료!')

        elif activity == '색칠':
            if not os.path.exists(
                    os.path.join(r'C:\Users\namon\PycharmProjects\discordbot\lib\images', f'{ctx.author.id}_1.png')):
                return
            if len(args) != 3:
                await send(ctx, "`커뉴야 커뉴핑크 색칠 x y color`")
                return
            try:
                x, y = map(int, args[:2])
            except ValueError:
                await send(ctx, "잘못된 값이 입력됐어요!")
                return
            preset, default_bonuses = db.record(
                "SELECT current_preset, default_bonuses FROM conupink_user_info WHERE UserID = ?", ctx.author.id)
            if not check_valid_coordinate(ctx.author.id, preset, x, y):
                await send(ctx, "올바르지 않은 좌표를 입력했어요!")
                return
            col_name = args[2]
            available = db.record("SELECT available FROM conupink_color_info WHERE UserID = ? AND col_name = ?",
                                  ctx.author.id, col_name)
            im = Image.open(rf'C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{preset}.png')
            if preset > 3000000:
                if not available:
                    await send(ctx, '아무리 A번 프리셋이라도 여태까지 물감을 구매한 적 없는 색을 칠할 수는 없어요...')
                    return
                draw = ImageDraw.Draw(im, 'RGBA')
                red, green, blue = eval(col_name)
                draw.rectangle(((SIZE_OF_ONE_TILE * (x - 1), (SIZE_OF_ONE_TILE * (y - 1))),
                                (SIZE_OF_ONE_TILE * x - 1, SIZE_OF_ONE_TILE * y - 1)), (red, green, blue, 255))
                embed = Embed(color=0x10000 * red + 0x100 * green + blue, title=ctx.author.name)
                embed.add_field(name='색칠 완료', value=f'({x}, {y}) 칸을 {col_name}으로 칠했어요!')
                embed.add_field(name='보너스', value='A번 프리셋을 장착한 상태이기 때문에, 이 프리셋을 장착하기 직전에 장착했던 프리셋의 보너스를 받고 있어요.')
                im.save(u := rf"C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{preset}.png")
                await send(ctx, embed=embed, file=File(u))
            if not available or available[0] == 0:
                await send(ctx, f'물감이 없어요! `커뉴야 커뉴핑크 구매 {args[2]}`로 물감을 구매해주세요. 물론 존재하는 색이라면...')
                return
            red, green, blue, opacity = im.getpixel(
                (SIZE_OF_ONE_TILE * (x - 1) + 1, SIZE_OF_ONE_TILE * (y - 1) + 1))
            if opacity != 255:
                await send(ctx, '색칠할 수 없는 칸이에요! 우선 이 칸의 불투명도를 255까지 업그레이드하고 나서 색칠하셔야 돼요.')
            before_color = find_color_from_pixel_value(red, green, blue)
            draw = ImageDraw.Draw(im, 'RGBA')
            red, green, blue = eval(col_name)
            draw.rectangle(((SIZE_OF_ONE_TILE * (x - 1), (SIZE_OF_ONE_TILE * (y - 1))),
                            (SIZE_OF_ONE_TILE * x - 1, SIZE_OF_ONE_TILE * y - 1)), (red, green, blue, opacity))
            embed = Embed(color=0x10000 * red + 0x100 * green + blue, title=ctx.author.name)
            embed.add_field(name='색칠 완료', value=f'({x}, {y}) 칸을 {col_name}으로 칠했어요!')
            u, embed = f(im, ctx, preset, embed, default_bonuses)
            await send(ctx, embed=embed, file=File(u))
            db.execute(
                "UPDATE conupink_color_info SET available = available - 1, used = used + 1 WHERE UserID = ? AND col_name = ?",
                ctx.author.id, col_name)
            db.execute("UPDATE conupink_color_info SET used = used - 1 WHERE UserID = ? AND col_name = ?",
                       ctx.author.id, before_color)
            db.commit()

        elif activity == '물감':
            paint_info = db.records("SELECT col_name, used, available FROM conupink_color_info WHERE UseriD = ?",
                                    ctx.author.id)
            if not paint_info:
                return
            fields = []
            field = ''
            cnt = 0
            embed = Embed(color=0xffd6fe, title=ctx.author.name, description='물감 정보')
            for col_name, used, available in paint_info:
                field += f'\n{col_name}: {used}개 칸에 칠해져 있음, {available}개의 물감 보유 중'
                cnt += 1
                if cnt == 10:
                    cnt = 0
                    fields.append(field)
                    field = ''
            if field:
                fields.append(field)
            for field in fields:
                embed.add_field(name='​', value=field)
            await send(ctx, embed=embed)

        elif activity == '획득':
            cur_stat = db.record("SELECT * FROM conupink_user_info WHERE USERID = ?", ctx.author.id)
            _, money, progress, net_money, money_per_command, money_per_hour, exp_level, total_exp, exp_per_command, current_preset, kkyu_preset_amount, last_gained, mpc_default_level, epc_default_level, default_bonuses, pick_level, scary_cube, red_cube, purple_cube, crimson_cube, blue_cube, cyan_cube, sunset_cube, cute_cube = cur_stat
            if not progress:
                return
            mineral_info = db.records(
                "SELECT mineral_name, per_hour FROM conupink_mine_info WHERE UserID = ? AND per_hour != 0",
                ctx.author.id)
            if money_per_hour == 0 and not mineral_info:
                await send(ctx, '아무것도 획득할 게 없어요...')
                return
            cur_time = int(time()) // 60
            if not last_gained:
                idle_time = 0
            else:
                idle_time = cur_time - last_gained
            moneydelta = idle_time * money_per_hour // 60
            mineral_gains = ''
            if mineral_info:
                im = Image.open(
                    rf'C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{current_preset}.png')
                default_bonuses = loads(default_bonuses)
                tb = calculate_total_bonus_from_colors(im, default_bonuses)
                if 'mine_income_mult' in tb:
                    multiplier = tb['mine_income_mult']
                else:
                    multiplier = 1
                mineral_gains = '또한 다음과 같은 광물들을 캤어요:'
                for mineral, ph in mineral_info:
                    d = idle_time * ph * multiplier // 60
                    mineral_gains += f'\n{mineral_EtoK[mineral]}, {d}'
                    db.execute(
                        "UPDATE conupink_mine_info SET amount = amount + ? WHERE userID = ? AND mineral_name = ?", d,
                        ctx.author.id, mineral)
            await send(ctx, f'{moneydelta}만큼의 돈을 획득했어요! {mineral_gains}')
            db.execute(
                "UPDATE conupink_user_info SET money = money + ?, net_money = net_money + ?, last_gained = ? WHERE UserID = ?",
                moneydelta, moneydelta, cur_time, ctx.author.id)
            db.commit()

        elif activity == '확장':
            await send(ctx, '만약 에러가 난다면 현재 버전에서 설정된 최대까지 확장했다는 뜻이에요!')
            cur_stat = db.record("SELECT * FROM conupink_user_info WHERE USERID = ?", ctx.author.id)
            _, money, progress, net_money, money_per_command, money_per_hour, exp_level, total_exp, exp_per_command, current_preset, kkyu_preset_amount, last_gained, mpc_default_level, epc_default_level, default_bonuses, pick_level, scary_cube, red_cube, purple_cube, crimson_cube, blue_cube, cyan_cube, sunset_cube, cute_cube = cur_stat
            if exp_level < 6:
                return
            if current_preset > 3000000:
                await send(ctx, 'A번 프리셋 확장은 구현 중이에요 ㅠㅠ yonsei4 업데이트에서 봅시다!')
                return
            im = Image.open(
                rf'C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{current_preset}.png')
            w, h = im.size
            w //= SIZE_OF_ONE_TILE
            h //= SIZE_OF_ONE_TILE
            check = 1
            for x in range(w):
                if not check:
                    break
                for y in range(h):
                    _, _, _, opacity = im.getpixel((SIZE_OF_ONE_TILE * x + 1, SIZE_OF_ONE_TILE * y + 1))
                    if opacity != 255:
                        check = 0
                        break
            if not check:
                await send(ctx, '현재 프리셋의 **모든** 칸의 불투명도를 255레벨까지 올려야 확장이 가능해요!')
                return
            if money < extend_costs[w]:
                await send(ctx, f'돈을 {extend_costs[w]}만큼 모아야 확장할 수 있어요!')
                return
            if w == 7 and exp_level < 23:
                await send(ctx, "아직은 이렇게 크게까지 확장할 수 없어요! 경험치 레벨을 올려서 더 넓게 확장할 수 있는 권한을 부여받으세요")
                return
            await send(ctx, 
                f'{w}×{w}에서 {w + 1}×{w + 1}으로 확장하려고 해요. 가격은 {extend_costs[w]}에요. `확장`이라고 다시 한 번 말해 칸을 확장하세요.')
            try:
                _ = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda
                        message: message.author == ctx.author and ctx.channel == message.channel and message.content == '확장'
                )
            except asyncio.TimeoutError:
                await send(ctx, "확장하지 않기로 했어요.")
                return
            initial_image = Image.open(rf'C:\Users\namon\PycharmProjects\discordbot\lib\images\initial_image.png')
            im_temp = initial_image.resize((SIZE_OF_ONE_TILE * (w + 1), SIZE_OF_ONE_TILE * (w + 1)))
            im_temp.paste(im)
            draw = ImageDraw.Draw(im_temp, 'RGBA')
            draw.rectangle(
                ((SIZE_OF_ONE_TILE * w, 0), (SIZE_OF_ONE_TILE * (w + 1) - 1, SIZE_OF_ONE_TILE * (w + 1) - 1)),
                (255, 255, 255, 1))
            draw.rectangle(((0, SIZE_OF_ONE_TILE * w), (SIZE_OF_ONE_TILE * w - 1, SIZE_OF_ONE_TILE * (w + 1) - 1)),
                           (255, 255, 255, 1))
            embed = Embed(color=0xffffff, title=ctx.author.name, description='확장을 완료해서 이제 새로운 칸을 쓸 수 있게 됐어요!')
            im_temp.save(
                u := rf"C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{current_preset}.png")
            db.execute("UPDATE conupink_user_info SET money = money - ? WHERE UserID = ?", extend_costs[w],
                       ctx.author.id)
            await send(ctx, embed=embed, file=File(u))

        elif activity == '프리셋':
            cur_stat = db.record("SELECT * FROM conupink_user_info WHERE USERID = ?", ctx.author.id)
            _, money, progress, net_money, money_per_command, money_per_hour, exp_level, total_exp, exp_per_command, current_preset, kkyu_preset_amount, last_gained, mpc_default_level, epc_default_level, default_bonuses, pick_level, scary_cube, red_cube, purple_cube, crimson_cube, blue_cube, cyan_cube, sunset_cube, cute_cube = cur_stat
            if exp_level < 7:
                return
            if not args:
                current_preset = \
                    db.record("SELECT current_preset FROM conupink_user_info WHERE UserID = ?", ctx.author.id)[0]
                await send(ctx, 
                    f'현재 {str(ctx.author)}님이 사용 중인 프리셋은 {preset_name_prefix[current_preset // 1000000]}{current_preset % 1000000}번이에요!\n\n새로운 프리셋을 사용하면 맨 처음 사진을 하나 더 받게 돼요. 그곳에다가 다른 조합으로 색을 칠할 수 있게 되는 거죠!')
            else:
                preset = args[0]
                try:
                    if preset[0].isdigit():
                        next_preset = int(preset[0])
                    else:
                        preset[0] = preset[0].upper()
                        next_preset = 1000000 * preset_name_prefix.index(preset[0]) + int(preset[1:])
                except TypeError:
                    await send(ctx, '올바르지 않은 프리셋 이름이에요!')
                    return
                if not os.path.exists(
                        os.path.join(r'C:\Users\namon\PycharmProjects\discordbot\lib\images',
                                     f'{ctx.author.id}_{next_preset}.png')):
                    await send(ctx, '해금하지 못한 프리셋이에요!')
                    return
                im = Image.open(
                    rf'C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{next_preset}.png')
                embed = Embed(color=0xffd6fe, title=ctx.author.name, description='프리셋 변경 완료')
                u, embed = f(im, ctx, next_preset, embed, default_bonuses)
                await send(ctx, embed=embed, file=File(u))
                db.execute("UPDATE conupink_user_info SET current_preset = ? WHERE UserID = ?", next_preset,
                           ctx.author.id)

        elif activity == '광산':
            mineral_info = db.records("SELECT mineral_name, amount, per_hour FROM conupink_mine_info WHERE UserID = ?",
                                      ctx.author.id)
            if not mineral_info:
                return
            if not args:
                pick_level = db.record("SELECT pick_level FROM conupink_user_info WHERE UserID = ?", ctx.author.id)[0]
                embed = Embed(color=0xce7c56, title=ctx.author.name)
                pick_levels, level_text, _ = pick_level_to_info(pick_level)
                embed.add_field(name='곡괭이 레벨', value=level_text)
                embed.add_field(name='광물 정보', value='\n'.join(
                    [f'{mineral_EtoK[mineral_name]}: {amount}개 보유, 시간당 {per_hour}개 획득' for
                     mineral_name, amount, per_hour in mineral_info]))
                embed.set_footer(
                    text='`커뉴야 커뉴핑크 광산`: 이 화면을 표시합니다.\n`커뉴야 커뉴핑크 광산 업글 (곡괭이)`: 특정 곡괭이를 업그레이드합니다.\n`커뉴야 커뉴핑크 광산 확장`: 퓨터를 이용해 광산을 더 넓혀 새로운 광물을 캘 수 있게 됩니다.\n`커뉴야 커뉴핑크 광산 판매 (광물) (개수)`: 광물을 판매해 돈을 얻습니다.\n자동으로 캐지는 광물은 `커뉴야 커뉴핑크 획득`으로 획득하세요')
                await send(ctx, embed=embed)
                return
            activity = args[0]
            mineral_info_dict = dict()
            for mn, a, ph in mineral_info:
                mineral_info_dict[mn] = a

            if activity == '업글':
                if len(args) == 1:
                    await send(ctx, '`커뉴야 커뉴핑크 광산 업글 (곡괭이)`')
                    return
                pick_level = db.record("SELECT pick_level FROM conupink_user_info WHERE UserID = ?", ctx.author.id)[0]
                pick_levels, _, materials = pick_level_to_info(pick_level)
                if args[1] not in materials:
                    if args[1] not in ['구리', '철', '은', '금', '백금']:
                        await send(ctx, '올바르지 않은 곡괭이에요!')
                        return
                else:
                    await send(ctx, '새로운 곡괭이를 만드는 것은 업데이트를 기다려 주세요 ㅠㅠ')
                    return
                material_id = materials.index(args[1])
                if pick_levels[material_id] == 9:
                    await send(ctx, '이 곡괭이는 이미 최대 레벨이에요!')
                    return
                else:
                    cost = pick_upgrade_costs[material_id][pick_levels[material_id]]
                    if mineral_info_dict[args[1]] < cost:
                        await send(ctx, f'광물이 부족해요! 곡괭이 업그레이드를 위해서는 {args[1]} {cost}개가 필요해요.')
                        return
                    db.execute(
                        "UPDATE conupink_mine_info SET per_hour_default = per_hour_default + 10, per_hour = per_hour + 10, amount = amount - ? WHERE UserID = ? AND mineral_name = ?",
                        cost, ctx.author.id, mineral_KtoE[args[1]])
                    db.execute(
                        "UPDATE conupink_mine_info SET per_hour_default = per_hour_default + 5, per_hour = per_hour + 5 WHERE UserID = ? AND mineral_name = ?",
                        cost, ctx.author.id, ['Copper', 'Iron', 'Silver', 'Gold', 'Platinum'][material_id + 1])
                    db.execute("UPDATE conupink_user_info SET pick_level = pick_level + ? WHERE UserID = ?",
                               10 ** material_id, ctx.author.id)
                    db.commit()
                    await send(ctx, '업그레이드 완료!')

            elif activity == '확장':
                if len(mineral_info_dict) == 1:
                    await send(ctx, '우선 광물 "퓨터"를 모아야 돼요! 퓨터는 12레벨이 된 이후에 획득할 수 있게 돼요.')
                    return
                mine_extend_costs = [0, 0, 1800, 5000, 10000, 1000000000]
                cost = mine_extend_costs[len(mineral_info_dict)]
                if mineral_info_dict['Pewter'] < cost:
                    await send(ctx, f'광물이 부족해요! 확장을 위해서는 퓨터 {cost}개가 필요해요.')
                    return
                new_mineral = ['구리', '철', '은', '금', '백금'][len(mineral_info_dict)]
                embed = Embed(color=0xce7c56, title=ctx.author.name,
                              description=f'광산을 더 뚫어, {new_mineral}이 나오는 광맥을 발견했어요!')
                await send(ctx, embed=embed)
                db.execute("INSERT INTO conupink_mine_info (UserID, mineral_name) VALUES (?, ?)", ctx.author.id,
                           ['Copper', 'Iron', 'Silver', 'Gold', 'Platinum'][len(mineral_info_dict)])
                db.commit()

            elif activity == '판매':
                if len(args) < 3 or not args[2].isdigit():
                    await send(ctx, '`커뉴야 커뉴핑크 광산 판매 (광물) (개수)`')
                    return
                mineral_amount = db.record(
                    "SELECT amount FROM conupink_mine_info WHERE UserID = ? AND mineral_name = ?", ctx.author.id,
                    mineral_KtoE[args[1]])
                if not mineral_amount:
                    await send(ctx, '올바르지 않은 광물 이름이에요!')
                    return
                mineral_amount = mineral_amount[0]
                sell_amount = int(args[2])
                if mineral_amount < sell_amount:
                    await send(ctx, '그만큼의 광물을 가지고 있지 않아요!')
                    return
                current_preset, default_bonuses = db.record(
                    "SELECT current_preset, default_bonuses FROM conupink_user_info WHERE UserID = ?", ctx.author.id)
                im = Image.open(
                    rf'C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{current_preset}.png')
                tb = calculate_total_bonus_from_colors(im, default_bonuses)
                if 'mine_sell_mult' in tb:
                    multiplier = tb['mine_sell_mult']
                else:
                    multiplier = 1
                money_delta = int(sell_amount * mineral_prices_default[mineral_KtoE[args[1]]] * multiplier)
                await send(ctx, f'{args[1]} {sell_amount}개를 팔아 돈을 {money_delta}만큼 얻었어요!')
                db.execute("UPDATE conupink_mine_info SET amount = amount - ? WHERE UserID = ? AND mineral_name = ?",
                           sell_amount, ctx.author.id, mineral_KtoE[args[1]])
                db.execute(
                    "UPDATE conupink_user_info SET money = money + ?, net_money = net_money + ? WHERE UserID = ?",
                    money_delta, money_delta, ctx.author.id)
                db.commit()

        elif activity == '큐브':
            exp_level, scary_cube = db.record("SELECT exp_level, scary_cube FROM conupink_user_info WHERE UserID = ?",
                                              ctx.author.id)
            if exp_level < 16:
                return
            embed = Embed(color=0xa02103, title=ctx.author.name, description='큐브 시스템 βeta')
            embed.add_field(name='무서운 큐브 보유량', value=str(scary_cube))
            embed.set_footer(text='`커뉴야 커뉴핑크 강화 x y`를 사용하면 해당 칸에 다른 색을 칠하기 전까지 큐브를 사용해 그 칸을 강화할 수 있어요!')
            await send(ctx, embed=embed)

        elif activity == '강화':
            exp_level, current_preset, default_bonuses, scary_cube = db.record(
                "SELECT exp_level, current_preset, default_bonuses, scary_cube FROM conupink_user_info WHERE UserID = ?",
                ctx.author.id)[0]
            if exp_level < 16:
                return
            im = Image.open(
                rf'C:\Users\namon\PycharmProjects\discordbot\lib\images\{ctx.author.id}_{current_preset}.png')
            try:
                x, y = map(int, args)
            except:
                await send(ctx, "`커뉴야 커뉴핑크 강화 x y`")
                return
            red, green, blue, opacity = im.getpixel(
                (SIZE_OF_ONE_TILE * (x - 1) + 1, SIZE_OF_ONE_TILE * (y - 1) + 1))
            color = find_color_from_pixel_value(red, green, blue)
            red_, green_, blue_, opacity_ = im.getpixel(
                (SIZE_OF_ONE_TILE * (x - 1) + 1, SIZE_OF_ONE_TILE * (y - 1) + 2))
            if blue_ != blue:
                await send(ctx, '이미 강화되어 있는 칸이에요! 다행히도 이후 버전에서는 같은 색깔을 여러 번 강화할 수 있게 될 거에요.')
                return
            embed = Embed(color=red * 0x10000 + green * 0x100 + blue, title=ctx.author.name,
                          description='칸을 강화하려고 합니다. 가격이나 효과를 잘 보고 결정하세요!')
            if color == SimpleWhite:
                embed.add_field(name='가격', value='5x 무서운 큐브')
                embed.add_field(name='효과', value='명령어 실행당 획득 돈 **250 증가** -> **275 증가**')
                cost_deduct = lambda c: c - 5
            else:
                await send(ctx, '업데이트로 더 많은 강화 요소가 추가될 예정이에요!')
                return
            embed.set_footer(text='`강화`라고 입력해 칸을 강화하세요')
            await send(ctx, embed=embed)
            try:
                _ = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author.id == ctx.author.id and message.content == '강화'
                )
            except asyncio.TimeoutError:
                await send(ctx, '칸을 강화하지 않기로 했어요.')
                return
            scary_cube = cost_deduct(scary_cube)
            if scary_cube < 0:
                await send(ctx, '그만큼의 큐브를 가지고 있지 않아요!')
                return
            draw = ImageDraw.Draw(im, 'RGBA')
            draw.point((SIZE_OF_ONE_TILE * (x - 1) + 1, SIZE_OF_ONE_TILE * (y - 1) + 2),
                       (red, green, blue - 1, opacity))
            embed = Embed(color=red * 0x10000 + green * 0x100 + blue, title=ctx.author.name, description='강화 완료')
            u, embed = f(im, ctx, current_preset, embed, default_bonuses)
            await send(ctx, embed=embed, file=File(u))
            db.execute("UPDATE conupink_user_info SET scary_cube = ? WHERE UserID = ?", scary_cube, ctx.author.id)
            db.commit()

        elif activity == '리더보드':
            score_info = db.records(
                "SELECT UserID, total_exp FROM conupink_user_info ORDER BY total_exp DESC LIMIT 10")
            tjfaud = ""
            ids = []
            scores = []
            for uid, score in score_info:
                ids.append(uid)
                scores.append(score)
            for uid in ids:
                a = ids.index(uid)
                b = scores[a]
                c = scores.index(b) + 1
                tjfaud += '\n' * (c != 1) + f"{c}. {self.bot.get_user(uid)} (총 경험치 {b})"
            embed = Embed(color=0xffd6fe, title=f"커뉴핑크 경험치 랭킹", description=tjfaud)
            await send(ctx, embed=embed)

        else:
            await send(ctx, '존재하지 않는 기능이에요!')
            return

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print('("conupink")')


async def setup(bot):
    await bot.add_cog(ConUPink(bot))
