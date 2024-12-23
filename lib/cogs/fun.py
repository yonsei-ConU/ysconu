import asyncio
import heapq
import math
import sqlite3
import re
from collections import defaultdict
from random import *
from time import time
from typing import Optional
import json
from datetime import datetime, timedelta
import os
from PIL import Image
from discord import Member, Embed, DMChannel, File, Forbidden
from discord.ext.commands import Cog, BucketType, max_concurrency, BadArgument
from discord.ext.commands import command, cooldown
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from fractions import Fraction
from decimal import *
from collections import deque
from ..db import db
from .achieve import grant, grant_check
from discord.app_commands import command as slash, choices, Choice
from ..utils.send import *
from time import sleep

global today
today = ((time() + 32400) // 86400)


def dijkstra(g, st, v):
    distances = [float('inf')] * (v + 1)
    distances[st] = 0
    heap = []
    heapq.heappush(heap, (0, st))

    while heap:
        dist, cur = heapq.heappop(heap)
        if distances[cur] < dist:
            continue
        for nextnum, nextdist in g[cur]:
            t = dist + nextdist
            if distances[nextnum] > t:
                distances[nextnum] = t
                heapq.heappush(heap, (t, nextnum))

    return distances


class vertex:
    def __init__(self, a: str, b: dict):
        self.name = a
        self.lines = b
        self.transfer = len(b) > 1


오금 = vertex('오금', {'3': '352', '5': 'P552'})
경찰병원 = vertex('경찰병원', {'3': '351'})
가락시장 = vertex('가락시장', {'3': '350', '8': '817'})
수서 = vertex('수서', {'3': '349', '수인분당': 'K221'})
일원 = vertex('일원', {'3': '348'})
대청 = vertex('대청', {'3': '347'})
학여울 = vertex('학여울', {'3': '346'})
대치 = vertex('대치', {'3': '345'})
도곡 = vertex('도곡', {'3': '344', '수인분당': 'K217'})
매봉 = vertex('매봉', {'3': '343'})
양재 = vertex('양재', {'3': '342', '신분당': 'D08'})
남부터미널 = vertex('남부터미널', {'3': '341'})
교대 = vertex('교대', {'2': '223', '3': '340'})
고속터미널 = vertex('고속터미널', {'3': '339', '7': '734', '9': '923'})
잠원 = vertex('잠원', {'3': '338'})
신사 = vertex('신사', {'3': '337', '신분당': 'D04'})
압구정 = vertex('압구정', {'3': '336'})
옥수 = vertex('옥수', {'3': '335', '경의중앙': 'K114'})
금호 = vertex('금호', {'3': '334'})
약수 = vertex('약수', {'3': '333', '6': '633'})
동대입구 = vertex('동대입구', {'3': '332'})
충무로 = vertex('충무로', {'3': '331', '4': '423'})
을지로3가 = vertex('을지로3가', {'2': '203', '3': '330'})
종로3가 = vertex('종로3가', {'1': '130', '3': '329', '5': '534'})
안국 = vertex('안국', {'3': '328'})
경복궁 = vertex('경복궁', {'3': '327'})
독립문 = vertex('독립문', {'3': '326'})
무악재 = vertex('무악재', {'3': '325'})
홍제 = vertex('홍제', {'3': '324'})
녹번 = vertex('녹번', {'3': '323'})
불광 = vertex('불광', {'3': '322', '6': '612'})
연신내 = vertex('연신내', {'3': '321', '6': '614'})
구파발 = vertex('구파발', {'3': '320'})
지축 = vertex('지축', {'3': '319'})
삼송 = vertex('삼송', {'3': '318'})
원흥 = vertex('원흥', {'3': '317'})
원당 = vertex('원당', {'3': '316'})
화정 = vertex('화정', {'3': '315'})
대곡 = vertex('대곡', {'3': '314', '경의중앙': 'K322', '서해': 'S11'})
백석 = vertex('백석', {'3': '313'})
마두 = vertex('마두', {'3': '312'})
정발산 = vertex('정발산', {'3': '311'})
주엽 = vertex('주엽', {'3': '310'})
대화 = vertex('대화', {'3': '309'})
강남 = vertex('강남', {'2': '222', '신분당': 'D07'})
서초 = vertex('서초', {'2': '224'})
방배 = vertex('방배', {'2': '225'})
사당 = vertex('사당', {'2': '226', '4': '433'})
낙성대 = vertex('낙성대', {'2': '227'})
서울대입구 = vertex('서울대입구', {'2': '228'})
봉천 = vertex('봉천', {'2': '229'})
신림 = vertex('신림', {'2': '230', '신림': 'S408'})
신대방 = vertex('신대방', {'2': '231'})
구로디지털단지 = vertex('구로디지털단지', {'2': '232'})
대림 = vertex('대림', {'2': '233', '7': '744'})
신도림 = vertex('신도림', {'1': '140', '2': '234'})
문래 = vertex('문래', {'2': '235'})
영등포구청 = vertex('영등포구청', {'2': '236', '5': '523'})
당산 = vertex('당산', {'2': '237', '9': '913'})
합정 = vertex('합정', {'2': '238', '6': '622'})
홍대입구 = vertex('홍대입구', {'2': '239', '경의중앙': 'K314', '공항철도': 'A03'})
신촌_지하 = vertex('신촌_지하', {'2': '240'})
이대 = vertex('이대', {'2': '241'})
아현 = vertex('아현', {'2': '242'})
충정로 = vertex('충정로', {'2': '243', '5': '531'})
시청 = vertex('시청', {'1': '132', '2': '201'})
을지로입구 = vertex('을지로입구', {'2': '202'})
을지로4가 = vertex('을지로4가', {'2': '204', '5': '535'})
동대문역사문화공원 = vertex('동대문역사문화공원', {'2': '205', '4': '422', '5': '536'})
신당 = vertex('신당', {'2': '206', '6': '635'})
상왕십리 = vertex('상왕십리', {'2': '207'})
왕십리 = vertex('왕십리', {'2': '2085', '540': '경의중앙', 'K116': '수인분당'})
한양대 = vertex('한양대', {'2': '209'})
뚝섬 = vertex('뚝섬', {'2': '210'})
성수 = vertex('성수', {'2': '211'})
용답 = vertex('용답', {'2': '211-1'})
신답 = vertex('신답', {'2': '211-2'})
용두 = vertex('용두', {'2': '211-3'})
신설동 = vertex('신설동', {'1': '126', '2': '211-4', '우이신설': 'S122'})
건대입구 = vertex('건대입구', {'2': '212', '7': '727'})
구의 = vertex('구의', {'2': '213'})
강변 = vertex('강변', {'2': '214'})
잠실나루 = vertex('잠실나루', {'2': '215'})
잠실 = vertex('잠실', {'2': '216', '8': '814'})
잠실새내 = vertex('잠실새내', {'2': '217'})
종합운동장 = vertex('종합운동장', {'2': '218', '9': '930'})
삼성 = vertex('삼성', {'2': '219'})
선릉 = vertex('선릉', {'2': '220', '수인분당': 'K215'})
역삼 = vertex('역삼', {'2': '221'})
도림천 = vertex('도림천', {'2': '234-1'})
양천구청 = vertex('양천구청', {'2': '234-2'})
신정네거리 = vertex('신정네거리', {'2': '234-3'})
까치산 = vertex('까치산', {'2': '234-4', '5': '518'})
응암 = vertex('응암', {'6': '610'})
역촌 = vertex('역촌', {'6': '611'})
독바위 = vertex('독바위', {'6': '613'})
구산 = vertex('구산', {'6': '615'})
새절 = vertex('새절', {'6': '616'})
증산 = vertex('증산', {'6': '617'})
디지털미디어시티 = vertex('디지털미디어시티', {'6': '618', '경의중앙': 'K316', '공항철도': 'A04'})
월드컵경기장 = vertex('월드컵경기장', {'6': '619'})
마포구청 = vertex('마포구청', {'6': '620'})
망원 = vertex('망원', {'6': '621'})
상수 = vertex('상수', {'6': '623'})
광흥창 = vertex('광흥창', {'6': '624'})
대흥 = vertex('대흥', {'6': '625'})
공덕 = vertex('공덕', {'5': '529', '6': '626', '경의중앙': 'K312', '공항철도': 'A02'})
효창공원앞 = vertex('효창공원앞', {'6': '627', '경의중앙': 'K311'})
삼각지 = vertex('삼각지', {'4': '428', '6': '628'})
녹사평 = vertex('녹사평', {'6': '629'})
이태원 = vertex('이태원', {'6': '630'})
한강진 = vertex('한강진', {'6': '631'})
버티고개 = vertex('버티고개', {'6': '632'})
청구 = vertex('청구', {'5': '537', '6': '634'})
동묘앞 = vertex('동묘앞', {'1': '127', '6': '636'})
창신 = vertex('창신', {'6': '637'})
보문 = vertex('보문', {'6': '638', '우이신설': 'S121'})
안암 = vertex('안암', {'6': '639'})
고려대 = vertex('고려대', {'6': '640'})
월곡 = vertex('월곡', {'6': '641'})
상월곡 = vertex('상월곡', {'6': '642'})
돌곶이 = vertex('돌곶이', {'6': '643'})
석계 = vertex('석계', {'1': '120', '6': '644'})
태릉입구 = vertex('태릉입구', {'6': '645', '7': '717'})
화랑대 = vertex('화랑대', {'6': '646'})
봉화산 = vertex('봉화산', {'6': '647'})
신내 = vertex('신내', {'6': '648', '경춘': 'P122'})
소요산 = vertex('소요산', {'1': '100'})
동두천 = vertex('동두천', {'1': '101'})
보산 = vertex('보산', {'1': '102'})
동두천중앙 = vertex('동두천중앙', {'1': '103'})
지행 = vertex('지행', {'1': '104'})
덕정 = vertex('덕정', {'1': '105'})
덕계 = vertex('덕계', {'1': '106'})
양주 = vertex('양주', {'1': '107'})
녹양 = vertex('녹양', {'1': '108'})
가능 = vertex('가능', {'1': '109'})
의정부 = vertex('의정부', {'1': '110'})
희룡 = vertex('희룡', {'1': '111', '의정부경전철': 'U111'})
망월사 = vertex('망월사', {'1': '112'})
도봉산 = vertex('도봉산', {'1': '113', '7': '710'})
도봉 = vertex('도봉', {'1': '114'})
방학 = vertex('방학', {'1': '115'})
창동 = vertex('창동', {'1': '116', '4': '412'})
녹천 = vertex('녹천', {'1': '117'})
월계 = vertex('월계', {'1': '118'})
광운대 = vertex('광운대', {'1': '119', '경춘': '119'})
신이문 = vertex('신이문', {'1': '121'})
외대앞 = vertex('외대앞', {'1': '122'})
회기 = vertex('회기', {'1': '123', '경의중앙': 'K118', '경춘': 'K118'})
청량리 = vertex('청량리', {'1': '124', '경의중앙': 'K117', '경춘': 'K117', '수인분당': 'K209'})
제기동 = vertex('제기동', {'1': '125'})
동대문 = vertex('동대문', {'1': '128', '4': '421'})
종로5가 = vertex('종로5가', {'1': '129'})
종각 = vertex('종각', {'1': '131'})
서울 = vertex('서울', {'1': '133', '4': '426', '경의중앙': 'P313', '공항철도': 'A01'})
남영 = vertex('남영', {'1': '134'})
용산 = vertex('용산', {'1': '135', '경의중앙': 'K110'})
노량진 = vertex('노량진', {'1': '136', '9': '917'})
대방 = vertex('대방', {'1': '137', '신림': 'S402'})
신길 = vertex('신길', {'1': '138', '5': '525'})
영등포 = vertex('영등포', {'1': '139'})
구로 = vertex('구로', {'1': '141'})
구일 = vertex('구일', {'1': '142'})
개봉 = vertex('개봉', {'1': '143'})
오류동 = vertex('오류동', {'1': '144'})
온수 = vertex('온수', {'1': '145', '7': '750'})
역곡 = vertex('역곡', {'1': '146'})
소사 = vertex('소사', {'1': '147', '서해': 'S16'})
부천 = vertex('부천', {'1': '148'})
중동 = vertex('중동', {'1': '149'})
송내 = vertex('송내', {'1': '150'})
부개 = vertex('부개', {'1': '151'})
부평 = vertex('부평', {'1': '152', '인천1': 'I120'})
백운 = vertex('백운', {'1': '153'})
동암 = vertex('동암', {'1': '154'})
간석 = vertex('간석', {'1': '155'})
주안 = vertex('주안', {'1': '156', '인천2': 'I218'})
도화 = vertex('도화', {'1': '157'})
제물포 = vertex('제물포', {'1': '158'})
도원 = vertex('도원', {'1': '159'})
동인천 = vertex('동인천', {'1': '160'})
인천 = vertex('인천', {'1': '161', '수인분당': 'K272'})
가산디지털단지 = vertex('가산디지털단지', {'1': 'P142', '7': '746'})
독산 = vertex('독산', {'1': 'P143'})
금천구청 = vertex('금천구청', {'1': 'P144'})
석수 = vertex('석수', {'1': 'P145'})
관악 = vertex('관악', {'1': 'P146'})
안양 = vertex('안양', {'1': 'P147'})
명학 = vertex('명학', {'1': 'P148'})
금정 = vertex('금정', {'1': 'P149', '4': '443'})
군포 = vertex('군포', {'1': 'P150'})
당정 = vertex('당정', {'1': 'P151'})
의왕 = vertex('의왕', {'1': 'P152'})
성균관대 = vertex('성균관대', {'1': 'P153'})
화서 = vertex('화서', {'1': 'P154'})
수원 = vertex('수원', {'1': 'P155', '수인분당': 'K245'})
세류 = vertex('세류', {'1': 'P156'})
병점 = vertex('병점', {'1': 'P157'})
서동탄 = vertex('서동탄', {'1': 'P157-1'})
세마 = vertex('세마', {'1': 'P158'})
오산대 = vertex('오산대', {'1': 'P159'})
오산 = vertex('오산', {'1': 'P160'})
진위 = vertex('진위', {'1': 'P161'})
송탄 = vertex('송탄', {'1': 'P162'})
서정리 = vertex('서정리', {'1': 'P163'})
평택지제 = vertex('평택지제', {'1': 'P164'})
평택 = vertex('평택', {'1': 'P165'})
성환 = vertex('성환', {'1': 'P166'})
직산 = vertex('직산', {'1': 'P167'})
두정 = vertex('두정', {'1': 'P168'})
천안 = vertex('천안', {'1': 'P169'})
봉명 = vertex('봉명', {'1': 'P170'})
쌍용 = vertex('쌍용', {'1': 'P171'})
아산 = vertex('아산', {'1': 'P172'})
탕정 = vertex('탕정', {'1': 'P173'})
배방 = vertex('배방', {'1': 'P174'})
온양온천 = vertex('온양온천', {'1': 'P176'})
신창 = vertex('신창', {'1': 'P177'})


getcontext().prec = 200
factorial_inv = [Decimal(1)] * 2
tmp = Decimal(1)
pi = Decimal("3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679")
γ = Decimal(
    "0.5772156649015328606065120900824024310421593359399235988057672348848677267776646709369470632917467495"
)

ln2 = Decimal(
    '0.6931471805599453094172321214581765680755001343602552541206800094933936219696947156058633269964186875420014810205706857336855202'
)


for i in range(2, 51):
    tmp /= Decimal(i)
    factorial_inv.append(tmp)


def simulate_quiz(time, num):
    result = []
    for i in range(time):
        result.append(randint(1, num))
    result = set(result)
    if time != len(result):
        return 1
    else:
        return 0


def miller_rabin(a, n):
    d = n - 1
    r = 0

    while not d % 2:
        d //= 2
        r += 1

    x = pow(a, d, n)

    if x == 1 or x == n - 1:
        return True

    for i in range(r - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True

    return False


def isprime(n):
    if n <= 71:
        if n in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]:
            return True
        else:
            return False
    else:
        for i in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
            if not miller_rabin(i, n):
                return False
        return True


def g(x, n, r):
    return (x ** 2 + r) % n


def pollard_rho(n, clock):
    if isprime(n):
        return n

    for i in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]:
        if not n % i:
            return i

    d = 1
    x = randint(2, n)
    y = x
    c = randint(1, n)

    while not d - 1:
        y = g(g(y, n, c), n, c)
        x = g(x, n, c)
        t = abs(x - y)
        d = math.gcd(t, n)

        clock_ = time()
        if clock_ - clock > 1 / 3:
            return

        if d == n:
            return pollard_rho(n, clock_)
    if isprime(d):
        return d
    return pollard_rho(d, clock_)


def check_tier(person):
    mmr = db.record("SELECT mook_chi_pa_mmr FROM games WHERE UserID = ?", person)
    mmr = mmr[0]
    if mmr < 2500:
        tier = "아이언"
        num = 0
    elif mmr < 3500:
        tier = "브론즈"
        num = ((mmr - 2500) // 250) + 1
        num = 5 - num
    elif mmr < 4500:
        tier = "실버"
        num = ((mmr - 3500) // 250) + 1
        num = 5 - num
    elif mmr < 5500:
        tier = "골드"
        num = ((mmr - 4500) // 250) + 1
        num = 5 - num
    elif mmr < 6500:
        tier = "플래티넘"
        num = ((mmr - 5500) // 250) + 1
        num = 5 - num
    elif mmr < 7500:
        tier = "다이아몬드"
        num = ((mmr - 6500) // 250) + 1
        num = 5 - num
    else:
        tier = "?"
        num = ((mmr - 7500) // 250) + 1
    return tier, num


def calc_card_value(values):
    ace_count = 0
    ans = 0
    for value in values:
        if value == 'A':
            ans += 11
            ace_count += 1
        elif value in ['J', 'Q', 'K']:
            ans += 10
        else:
            ans += int(value)
    if ans > 21:
        if ace_count == 0:
            return '버스트 ', ans
        else:
            while ans > 21 and ace_count:
                ace_count -= 1
                ans -= 10
            if ace_count == 0 and ans > 21:
                return '버스트 ', ans
            else:
                return '', ans
    elif ans == 21 and len(values) == 2:
        return '블랙잭 ', ans
    else:
        if ace_count:
            return '소프트 ', ans
        return '', ans


operators = ['+', '-', '*', '/', '**', '%']
operator_arity = {'add': 2, 'sub': 2, 'mul': 2, 'div': 2, 'mod': 2, 'pow': 2, 'sqrt': 1, 'ln': 1, 'exp': 1, 'sin': 1, 'cos': 1, 'tan': 1, 'harmonic': 1}


def div(a, b):
    try:
        return Fraction(a) / Fraction(b)
    except ZeroDivisionError:
        return ':weary:'


def twopi_mod(x):
    if isinstance(x, Fraction):
        x = Decimal(x.numerator) / Decimal(x.denominator)
    x %= pi
    if x < -pi:
        x += 2 * pi
    elif x > pi:
        x -= 2 * pi
    return x


def sin(x):
    x = twopi_mod(x)
    r = Decimal(0)
    sgn_tmp = Decimal(1)
    for power in range(1, 51, 2):
        r += sgn_tmp * (x ** Decimal(power)) * factorial_inv[power]
        sgn_tmp *= -1
    return r


def cos(x):
    x = twopi_mod(x)
    r = Decimal(1)
    sgn_tmp = Decimal(-1)
    for power in range(2, 52, 2):
        r += sgn_tmp * (x ** Decimal(power)) * factorial_inv[power]
        sgn_tmp *= -1
    return r


def tan(x):
    try:
        return sin(x) / cos(x)
    except ZeroDivisionError:
        return ':weary:'


def harmonic(n):
    try:
        if n == int(n):
            n = int(n)
    except ValueError:
        return 0
    if n < 1000:
        r = Decimal("0")
        for i in range(1, n + 1):
            r += Decimal("1") / Decimal(str(i))
        return r
    else:
        return Decimal(n).ln() + γ + (Decimal(1) / Decimal(2 * n)) - (
            Decimal(1) / Decimal(12 * n * n))


operator_functions = {
    'add': lambda a, b: a + b,
    'sub': lambda a, b: a - b,
    'mul': lambda a, b: a * b,
    'div': div,
    'mod': lambda a, b: a % b,
    'pow': lambda a, b: pow(a, b) if (len(str(a)) * len(str(b)) < 1000) else ":weary:",
    'sqrt': lambda a: a.sqrt(),
    'ln': lambda a: a.ln(),
    'exp': lambda a: a.exp(),
    'sin': sin,
    'cos': cos,
    'tan': tan,
    'harmonic': harmonic,
}


def infix_to_postfix(expression: str) -> list:
    stack = []
    operator_to_internal = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div', '%': 'mod', '**': 'pow', 'sqrt': 'sqrt', 'ln': 'ln', 'exp': 'exp', 'sin': 'sin', 'cos': 'cos', 'tan': 'tan', 'harmonic': 'harmonic'}
    precedence = {'add': 1, 'sub': 1, 'mul': 3, 'div': 3, 'mod': 2, 'pow': 4, 'sqrt': 1000, 'ln': 1000, 'exp': 1000, 'sin': 1000, 'cos': 1000, 'tan': 1000, 'harmonic': 1000}
    result = []

    def precedence_of(op):
        return precedence[op] if op in precedence else -1

    def is_operator(c):
        return c in operator_to_internal

    i = 0
    while i < len(expression):
        if expression[i].isdigit() or expression[i] == '.' or expression[i:i+2] == 'pi' or expression[i:i+5] == 'gamma':
            if expression[i:i+2] == 'pi':
                result.append(pi)
                i += 1
            elif expression[i:i+5] == 'gamma':
                result.append(γ)
                i += 1
            else:
                num = ''
                while i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
                    num += expression[i]
                    i += 1
                result.append(Decimal(num))
                i -= 1
        elif expression[i] == '(':
            stack.append(expression[i])
        elif expression[i] == ')':
            while stack and stack[-1] != '(':
                result.append(stack.pop())
            stack.pop()  # Remove '(' from stack
        elif expression[i:i+4] == 'sqrt':
            stack.append('sqrt')
            i += 3
        elif expression[i:i+2] == 'ln':
            stack.append('ln')
            i += 1
        elif expression[i:i+3] == 'exp':
            stack.append('exp')
            i += 2
        elif expression[i:i+3] == 'mod':
            stack.append('mod')
            i += 2
        elif expression[i:i+3] == 'sin':
            stack.append('sin')
            i += 2
        elif expression[i:i+3] == 'cos':
            stack.append('cos')
            i += 2
        elif expression[i:i+3] == 'tan':
            stack.append('tan')
            i += 2
        elif expression[i:i+8] == 'harmonic':
            stack.append('harmonic')
            i += 7
        elif is_operator(expression[i]):
            op = expression[i]
            if i + 1 < len(expression) and expression[i:i+2] == '**':  # Handle '**' operator
                op = '**'
                i += 1
            while (stack and stack[-1] != '(' and
                   precedence_of(operator_to_internal[op]) <= precedence_of(stack[-1])):
                result.append(stack.pop())
            stack.append(operator_to_internal[op])
        i += 1

    while stack:
        result.append(stack.pop())

    return result


def eval_postfix(expression: list):
    # param `expression` is a result of the function `infix_to_postfix`
    # param `operator_arity` is a dictionary that defines the number of operands each operator needs
    stack = []
    for e in expression:
        if check_numeric(e):
            stack.append(e)
        else:
            if e not in operator_arity:
                raise ValueError(f"Unsupported operator: {e}")
            arity = operator_arity[e]
            operands = [stack.pop() for _ in range(arity)][::-1]  # Pop operands in reverse order
            stack.append(operator_functions[e](*operands))

    return stack.pop()


def check_numeric(val):
    try:
        float(val)
        return True
    except ValueError:
        return False


def next_palindrome(n):
    n = str(n)
    if int(n) < 10:
        if int(n) == 9:
            p = 11
        else:
            p = int(n) + 1
    else:
        l = len(n)
        p = n[:l // 2]
        if l % 2:
            c = n[l // 2]
        else:
            c = '-1'
        s = n[math.ceil(l / 2):]

        if n == n[::-1]:
            s = str(int(s) + 1)

        if c == '-1':
            if int(s) >= int(p[::-1]):
                p = str(int(p) + 1)
            p = p + p[::-1]
            if l != len(p):
                p = list(p)
                p.remove('0')
                p = ''.join(p)
        else:
            pc = int(p + c)
            if int(s) >= int(p[::-1]):
                pc = str(pc + 1)
            else:
                pc = str(pc)
            p = pc[:len(pc) - 1]
            c = pc[-1]
            p = p + c + p[::-1]
            if l != len(p):
                p = list(p)
                p.remove('0')
                p = ''.join(p)
    return Decimal(p)
# getcontext().prec = 100
# factorial_inv = [Decimal(1)] * 2
# tmp = Decimal(1)
# for i in range(2, 51):
#     tmp /= Decimal(i)
#     factorial_inv.append(tmp)
#
#
# LOG10 = Decimal('2.302585092994045684017991454684364207601101488628772976033327900967572609677352480235997205089598298')
# LGE = Decimal('0.4342944819032518276511289189166050822943970058036665661144537831658646492088707747292249493384317484')
#
#
# def natural_exponential(x):
#     r = Decimal(0)
#     for power in range(51):
#         r += (x ** Decimal(power)) * factorial_inv[power]
#     return r
#
#
# def power_of_ten(x):
#     return natural_exponential(x) * LOG10
#
#
# def natural_logarithm(x, n=10000):
#     integrand = lambda t: 1 / t
#     h = (x - 1) / n
#     return (h / 3) * (integrand(1) + 4 * sum(integrand(1 + i * h) for i in range(1, n, 2)) + 2 * sum(
#         integrand(1 + i * h) for i in range(2, n - 1, 2)) + integrand(x))


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def rps2(self, user1, user2, again_check=False):
        embed = Embed(color=0xffd6fe)
        user1 = self.bot.get_user(user1)
        user2 = self.bot.get_user(user2)
        mmr1 = db.record("SELECT mook_chi_pa_mmr FROM games WHERE UserID = ?", user1.id)
        mmr1 = mmr1[0]
        mmr2 = db.record("SELECT mook_chi_pa_mmr FROM games WHERE UserID = ?", user2.id)
        mmr2 = mmr2[0]
        mmr_ckdl = mmr1 - mmr2
        if not again_check:
            await user1.send(f"{user2}와(과)의 매칭이 잡혔어요! 15초 안에 묵, 찌, 빠 중 하나를 말해 주세요")
        else:
            await user1.send("비겼어요! 다시 15초 안에 묵, 찌, 빠 중 하나를 말해주세요")
        try:
            msg1 = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author.id == user1.id and isinstance(message.channel, DMChannel)
            )
        except asyncio.TimeoutError:
            await user1.send("시간초과 패배!")
            await user2.send("상대의 시간초과 패배로 인한 승리!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user2.mention} ({str(user2)}의 승리!)")
            mmr_delta = 50 - mmr_ckdl // 37
            mmr1 = mmr1 - mmr_delta
            mmr2 = mmr2 + mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            db.commit()
            await user1.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user2.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.", embed=embedf)
            return
        if msg1.content == "찌" or len(msg1.content.replace("ㅉ", "")) == 0:
            thing1 = 1
            embed.add_field(name=f"{user1.display_name}", value=":v:")
        elif msg1.content == "묵" or len(msg1.content.replace("ㅁ", "")) == 0:
            thing1 = 2
            embed.add_field(name=f"{user1.display_name}", value=":punch:")
        elif msg1.content == "빠" or len(msg1.content.replace("ㅃ", "")) == 0:
            thing1 = 3
            embed.add_field(name=f"{user1.display_name}", value=":raised_back_of_hand: ")
        else:
            await user1.send("실격패!")
            await user2.send("상대의 실격패로 인한 승리!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user2.mention} ({str(user2)}의 승리!")
            mmr_delta = 50 - mmr_ckdl // 37
            mmr1 = mmr1 - mmr_delta
            mmr2 = mmr2 + mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            db.commit()
            await user1.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user2.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.", embed=embedf)
            return
        if not again_check:
            await user2.send(f"{user1}와(과)의 매칭이 잡혔어요! 15초 안에 묵, 찌, 빠 중 하나를 말해 주세요")
        else:
            await user2.send("비겼어요! 다시 15초 안에 묵, 찌, 빠 중 하나를 말해주세요")
        try:
            msg2 = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author.id == user2.id and isinstance(message.channel, DMChannel)
            )
        except asyncio.TimeoutError:
            await user2.send("시간초과 패배!")
            await user1.send("상대의 시간초과 패배로 인한 승리!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user1.mention} ({str(user1)}의 승리!")
            mmr_delta = 50 - mmr_ckdl // 37
            mmr1 = mmr1 + mmr_delta
            mmr2 = mmr2 - mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            db.commit()
            await user2.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user1.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.", embed=embedf)
            return
        if msg2.content == "찌" or len(msg2.content.replace("ㅉ", "")) == 0:
            thing2 = 1
            embed.add_field(name=f"{user2.display_name}", value=":v:")
        elif msg2.content == "묵" or len(msg2.content.replace("ㅁ", "")) == 0:
            thing2 = 2
            embed.add_field(name=f"{user2.display_name}", value=":punch:")
        elif msg2.content == "빠" or len(msg2.content.replace("ㅃ", "")) == 0:
            thing2 = 3
            embed.add_field(name=f"{user2.display_name}", value=":raised_back_of_hand: ")
        else:
            await user1.send("실격패!")
            await user2.send("상대의 실격패로 인한 승리!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user1.mention} ({str(user1)}의 승리!")
            mmr_delta = 50 - mmr_ckdl // 37
            mmr1 = mmr1 + mmr_delta
            mmr2 = mmr2 - mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            db.commit()
            await user2.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user1.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.", embed=embedf)
            return

        if thing1 == thing2:
            return await self.rps2(user1.id, user2.id, again_check=True)
        elif thing1 - thing2 == 1 or thing1 - thing2 == -2:
            embed.set_footer(text=f"{user1.display_name}의 공격 차례!")
            await user1.send(embed=embed)
            await user2.send(embed=embed)
            await self.user1_attack(self, user1, user2, embed)
        else:
            embed.set_footer(text=f"{user2.display_name}의 공격 차례")
            await self.user2_attack(self, user1, user2, embed)

    async def user1_attack(self, a, user1, user2, emb):
        embed = Embed(color=0xffd6fe)
        mmr1 = db.record("SELECT mook_chi_pa_mmr FROM games WHERE UserID = ?", user1.id)
        mmr1 = mmr1[0]
        mmr2 = db.record("SELECT mook_chi_pa_mmr FROM games WHERE UserID = ?", user2.id)
        mmr2 = mmr2[0]
        mmr_ckdl = mmr1 - mmr2
        await user1.send(embed=emb)
        try:
            msg1 = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author.id == user1.id and isinstance(message.channel, DMChannel)
            )
        except asyncio.TimeoutError:
            await user1.send("시간초과 패배!")
            await user2.send("상대의 시간초과 패배로 인한 승리!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user2.mention} ({str(user2)}의 승리!)")
            mmr_delta = 50 - mmr_ckdl // 37
            mmr1 = mmr1 - mmr_delta
            mmr2 = mmr2 + mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            db.commit()
            await user1.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user2.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.", embed=embedf)
            return
        if msg1.content == "찌" or len(msg1.content.replace("ㅉ", "")) == 0:
            thing1 = 1
            embed.add_field(name=f"{user1.display_name}", value=":v:")
        elif msg1.content == "묵" or len(msg1.content.replace("ㅁ", "")) == 0:
            thing1 = 2
            embed.add_field(name=f"{user1.display_name}", value=":punch:")
        elif msg1.content == "빠" or len(msg1.content.replace("ㅃ", "")) == 0:
            thing1 = 3
            embed.add_field(name=f"{user1.display_name}", value=":raised_back_of_hand: ")
        else:
            await user1.send("실격패!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user2.display_name}의 승리!")
            mmr_delta = 50 - mmr_ckdl // 37
            mmr1 = mmr1 - mmr_delta
            mmr2 = mmr2 + mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            await user1.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user2.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이애요.", embed=embedf)
            return
        await user2.send(embed=emb)
        try:
            msg2 = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author.id == user2.id and isinstance(message.channel, DMChannel)
            )
        except asyncio.TimeoutError:
            await user2.send("시간초과 패배!")
            await user1.send("상대의 시간초과 패배로 인한 승리!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user1.mention} ({str(user1)}의 승리!")
            mmr_delta = 50 - mmr_ckdl // 37
            mmr1 = mmr1 + mmr_delta
            mmr2 = mmr2 - mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            db.commit()
            await user2.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user1.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.", embed=embedf)
            return
        if msg2.content == "찌" or len(msg2.content.replace("ㅉ", "")) == 0:
            thing2 = 1
            embed.add_field(name=f"{user2.display_name}", value=":v:")
        elif msg2.content == "묵" or len(msg2.content.replace("ㅁ", "")) == 0:
            thing2 = 2
            embed.add_field(name=f"{user2.display_name}", value=":punch:")
        elif msg2.content == "빠" or len(msg2.content.replace("ㅃ", "")) == 0:
            thing2 = 3
            embed.add_field(name=f"{user2.display_name}", value=":raised_back_of_hand: ")
        else:
            await user2.send("실격패!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user1.display_name}의 승리!")
            mmr_delta = 50 + mmr_ckdl // 23
            mmr1 = mmr1 + mmr_delta
            mmr2 = mmr2 - mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            await user2.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user1.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.", embed=embedf)
            return
        if thing1 == thing2:
            mmr_delta = 50 - mmr_ckdl // 37
            mmr1 = mmr1 + mmr_delta
            mmr2 = mmr2 - mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            await user1.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr1} 점이에요.")
            await user2.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr2} 점이에요.")
            await user1.send(embed=embed)
            await user2.send(embed=embed)
            return
        elif thing1 - thing2 == 1 or thing1 - thing2 == -2:
            embed.set_footer(text=f"{user1.display_name}의 공격 차례!")
            await self.user1_attack(self, user1, user2, embed)
        else:
            embed.set_footer(text=f"{user2.display_name}의 공격 차례")
            await self.user2_attack(self, user1, user2, embed)

    async def user2_attack(self, a, user1, user2, emb):
        embed = Embed(color=0xffd6fe)
        mmr1 = db.record("SELECT mook_chi_pa_mmr FROM games WHERE UserID = ?", user1.id)
        mmr1 = mmr1[0]
        mmr2 = db.record("SELECT mook_chi_pa_mmr FROM games WHERE UserID = ?", user2.id)
        mmr2 = mmr2[0]
        mmr_ckdl = mmr1 - mmr2
        await user1.send(embed=emb)
        try:
            msg1 = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author.id == user1.id and isinstance(message.channel, DMChannel)
            )
        except asyncio.TimeoutError:
            await user1.send("시간초과 패배!")
            await user2.send("상대의 시간초과 패배로 인한 승리!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user2.mention} ({str(user2)}의 승리!)")
            mmr_delta = 50 - mmr_ckdl // 37
            mmr1 = mmr1 - mmr_delta
            mmr2 = mmr2 + mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            db.commit()
            await user1.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user2.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.", embed=embedf)
            return
        if msg1.content == "찌" or len(msg1.content.replace("ㅉ", "")) == 0:
            thing1 = 1
            embed.add_field(name=f"{user1.display_name}", value=":v:")
        elif msg1.content == "묵" or len(msg1.content.replace("ㅁ", "")) == 0:
            thing1 = 2
            embed.add_field(name=f"{user1.display_name}", value=":punch:")
        elif msg1.content == "빠" or len(msg1.content.replace("ㅃ", "")) == 0:
            thing1 = 3
            embed.add_field(name=f"{user1.display_name}", value=":raised_back_of_hand: ")
        else:
            await user1.send("실격패!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user2.display_name}의 승리!")
            mmr_delta = 50 - mmr_ckdl // 37
            mmr1 = mmr1 - mmr_delta
            mmr2 = mmr2 + mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            await user1.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user2.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.", embed=embedf)
            return
        await user2.send(embed=emb)
        try:
            msg2 = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author.id == user2.id and isinstance(message.channel, DMChannel)
            )
        except asyncio.TimeoutError:
            await user2.send("시간초과 패배!")
            await user1.send("상대의 시간초과 패배로 인한 승리!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user1.mention} ({str(user1)}의 승리!")
            mmr_delta = 50 - mmr_ckdl // 37
            mmr1 = mmr1 + mmr_delta
            mmr2 = mmr2 - mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            db.commit()
            await user2.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user1.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.", embed=embedf)
            return
        if msg2.content == "찌" or len(msg2.content.replace("ㅉ", "")) == 0:
            thing2 = 1
            embed.add_field(name=f"{user2.display_name}", value=":v:")
        elif msg2.content == "묵" or len(msg2.content.replace("ㅁ", "")) == 0:
            thing2 = 2
            embed.add_field(name=f"{user2.display_name}", value=":punch:")
        elif msg2.content == "빠" or len(msg2.content.replace("ㅃ", "")) == 0:
            thing2 = 3
            embed.add_field(name=f"{user2.display_name}", value=":raised_back_of_hand: ")
        else:
            await user2.send("실격패!")
            embedf = Embed(color=0xffd6fe)
            embedf.add_field(name="묵찌빠 진행 결과!", value=f"{user1.display_name}의 승리!")
            mmr_delta = 50 + mmr_ckdl // 23
            mmr1 = mmr1 + mmr_delta
            mmr2 = mmr2 - mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            await user2.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.", embed=embedf)
            await user1.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.", embed=embedf)
            return

        if thing1 == thing2:
            mmr_delta = 50 + mmr_ckdl // 23
            mmr1 = mmr1 - mmr_delta
            mmr2 = mmr2 + mmr_delta
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr1, user1.id)
            db.execute("UPDATE games SET mook_chi_pa_mmr = ?, room_number = NULL WHERE UserID = ?", mmr2, user2.id)
            await user1.send(f"졌어요... {mmr_delta}점을 잃어서 현재 점수는 {mmr1} 점이에요.")
            await user2.send(f"이겼어요! {mmr_delta}점을 얻어서 현재 점수는 {mmr2} 점이에요.")
            await user1.send(embed=embed)
            await user2.send(embed=embed)
            return
        elif thing1 - thing2 == 1 or thing1 - thing2 == -2:
            embed.set_footer(text=f"{user1.display_name}의 공격 차례!")
            await self.user1_attack(self, user1, user2, embed)
        else:
            embed.set_footer(text=f"{user2.display_name}의 공격 차례")
            await self.user2_attack(self, user1, user2, embed)

    async def user_attack(self, a, ctx):
        thing = 0
        embed = Embed(color=ctx.author.color)
        rsp = randint(1, 3)
        try:
            msg = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author == ctx.author and message.channel == ctx.channel
            )
            if msg.content == "가위" or msg.content == "찌" or len(msg.content.replace("ㅉ", "")) == 0:
                thing = 1
                embed.add_field(name=f"{ctx.author.display_name}", value=":v:")
            elif msg.content == "바위" or thing == "주먹" or msg.content == "묵" or len(msg.content.replace("ㅁ", "")) == 0:
                thing = 2
                embed.add_field(name=f"{ctx.author.display_name}", value=":punch:")
            elif msg.content == "보" or msg.content == "빠" or len(msg.content.replace("ㅃ", "")) == 0:
                thing = 3
                embed.add_field(name=f"{ctx.author.display_name}", value=":raised_back_of_hand: ")
            else:
                await send(ctx, "올바른 걸 내줘")
                return
            if rsp == 1:
                embed.add_field(name="커뉴봇", value=":v:")
            if rsp == 2:
                embed.add_field(name="커뉴봇", value=":punch:")
            if rsp == 3:
                embed.add_field(name="커뉴봇", value=":raised_back_of_hand:")
            if thing == rsp:
                embed.set_footer(text="승리!")
                await send(ctx, embed=embed)
                ag = grant_check("묵찌빠 승자", ctx.author.id)
                if ag == 1:
                    await grant(ctx, "묵찌빠 승자", "커뉴봇과의 묵찌빠 대결에서 승리하세요")
                return
            elif thing - rsp == 1 or thing - rsp == -2:
                embed.set_footer(text="공격권이 왔어! 뭘로 공격할 거야?")
                await send(ctx, embed=embed)
                await self.user_attack(self, ctx)
            else:
                embed.set_footer(text="내가 공격할 차례군! 방어할 준비를 해")
                await send(ctx, embed=embed)
                await self.conubot_attack(self, ctx)

        except asyncio.TimeoutError:
            await send(ctx, "게임을 중단했어.")

    async def conubot_attack(self, a, ctx):
        thing = 0
        embed = Embed(color=ctx.author.color)
        rsp = randint(1, 3)
        try:
            msg = await self.bot.wait_for(
                "message",
                timeout=15,
                check=lambda message: message.author == ctx.author and message.channel == ctx.channel
            )
            if msg.content == "가위" or msg.content == "찌" or len(msg.content.replace("ㅉ", "")) == 0:
                thing = 1
                embed.add_field(name=f"{ctx.author.display_name}", value=":v:")
            elif msg.content == "바위" or thing == "주먹" or msg.content == "묵" or len(msg.content.replace("ㅁ", "")) == 0:
                thing = 2
                embed.add_field(name=f"{ctx.author.display_name}", value=":punch:")
            elif msg.content == "보" or msg.content == "빠" or len(msg.content.replace("ㅃ", "")) == 0:
                thing = 3
                embed.add_field(name=f"{ctx.author.display_name}", value=":raised_back_of_hand: ")
            else:
                await send(ctx, "올바른 걸 내줘")
                return
            if rsp == 1:
                embed.add_field(name="커뉴봇", value=":v:")
            if rsp == 2:
                embed.add_field(name="커뉴봇", value=":punch:")
            if rsp == 3:
                embed.add_field(name="커뉴봇", value=":raised_back_of_hand:")
            if thing == rsp:
                embed.set_footer(text="패배...")
                await send(ctx, embed=embed)
                return
            elif thing - rsp == 1 or thing - rsp == -2:
                embed.set_footer(text="공격권이 왔어! 뭘로 공격할 거야?")
                await send(ctx, embed=embed)
                await self.user_attack(self, ctx)
            else:
                embed.set_footer(text="내가 공격할 차례군! 방어할 준비를 해")
                await send(ctx, embed=embed)
                await self.conubot_attack(self, ctx)

        except asyncio.TimeoutError:
            await send(ctx, "게임을 중단했어.")

    @command(name="묵찌빠", aliases=["묵"])
    async def mook_chi_ppa(self, ctx, thing: Optional[str] = "도움", page: Optional[int] = 1):
        a = db.record("SELECT UserID FROM games WHERE UserID = ?", ctx.author.id)
        if a is None: db.execute("INSERT INTO games (UserID) VALUES (?)", ctx.author.id)
        rsp = randint(1, 3)
        embedd = Embed(color=ctx.author.color)
        if thing == "가위" or thing == "찌":
            thing = 1
            embedd.add_field(name=f"{ctx.author.display_name}", value=":v:")
        elif thing == "바위" or thing == "주먹" or thing == "묵":
            thing = 2
            embedd.add_field(name=f"{ctx.author.display_name}", value=":punch:")
        elif thing == "보" or thing == "빠":
            thing = 3
            embedd.add_field(name=f"{ctx.author.display_name}", value=":raised_back_of_hand: ")
        elif thing == "매칭":
            mmr = db.record("SELECT mook_chi_pa_mmr FROM games WHERE UserID = ?", ctx.author.id)
            mmr = mmr[0]
            tier, tnum = check_tier(ctx.author.id)
            rooms_info = db.records("SELECT UserID, mook_chi_pa_mmr FROM games WHERE room_number = 1")
            cur_room = db.record("SELECT room_number FROM games WHERE UserID = ?", ctx.author.id)
            cur_room = cur_room[0]
            if cur_room is not None:
                await send(ctx, "이미 매칭을 잡는 중이에요! 매칭을 취소하고 싶다면 `커뉴야 묵찌빠 매칭취소`를 입력해 주세요.")
                return
            await send(ctx, f"{ctx.author.mention}\n{tier} {tnum} 구간에서 매칭을 잡는 중이에요.")
            for queue_people in rooms_info:
                if math.fabs(queue_people[1] - mmr) <= 1000:
                    db.execute("UPDATE games SET room_number = 0 WHERE userID = ?", ctx.author.id)
                    db.execute("UPDATE games SET room_number = 0 WHERE userID = ?", queue_people[0])
                    await self.rps2(ctx.author.id, queue_people[0])
                    return
            db.execute("UPDATE games SET room_number = 1 WHERE UserID = ?", ctx.author.id)
            db.commit()
            return
        elif thing == "매칭취소":
            cur_room = db.record("SELECT room_number FROM games WHERE UserID = ?", ctx.author.id)
            cur_room = cur_room[0]
            if cur_room is None:
                await send(ctx, "매칭을 잡고 있지 않아!")
                return
            else:
                db.execute("UPDATE games SET room_number = NULL Where UserID = ?", ctx.author.id)
                await send(ctx, "매칭 취소 완료")
                return
        elif thing == "티어":
            mmr = db.record("SELECT mook_chi_pa_mmr FROM games WHERE UserID = ?", ctx.author.id)[0]
            if mmr >= 4500:
                l = grant_check("황금의 묵찌빠", ctx.author.id)
                if l == 1:
                    await grant(ctx, "황금의 묵찌빠", "묵찌빠 점수 4500점을 달성하세요")
            mmrd = 250 - mmr % 250
            tier, num = check_tier(ctx.author.id)
            embeddd = Embed(color=0xffd6fe)
            embeddd.add_field(name=f"{ctx.author.display_name}의 묵찌빠 티어", value=f"{tier} {num} ({mmr}점)", inline=False)
            embeddd.add_field(name=f"다음 티어로 가기까지 얻어야 하는 점수", value=f"{mmrd}", inline=False)
            await send(ctx, embed=embeddd)
            return
        elif thing == "리더보드":
            records = db.records(
                "SELECT UserID, mook_chi_pa_mmr FROM games WHERE mook_chi_pa_mmr != 4000 ORDER BY mook_chi_pa_mmr DESC LIMIT ?, ?",
                10 * page - 10, 10)
            tjfaud = ""
            now_people = 10 * page - 9
            for record in records:
                tier, num = check_tier(record[0])
                tjfaud = tjfaud + f"{now_people}. <@{record[0]}> (티어: {tier} {num} | 점수: {record[1]}) \n"
                now_people += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 사람이 없는 것 같아요!"
            await send(ctx, embed=Embed(color=ctx.author.color, title="묵찌빠 랭킹!", description=tjfaud))
            return
        else:
            await send(ctx, "`커뉴야 묵찌빠 <묵/찌/빠/매칭/매칭취소/티어/리더보드>`")
            return
        if rsp == 1:
            embedd.add_field(name="커뉴봇", value=":v:")
        if rsp == 2:
            embedd.add_field(name="커뉴봇", value=":punch:")
        if rsp == 3:
            embedd.add_field(name="커뉴봇", value=":raised_back_of_hand:")
        if thing == rsp:
            await send(ctx, "비겼네! 다시 하자")
            return
        elif thing - rsp == 1 or thing - rsp == -2:
            embedd.set_footer(text="공격권이 왔어! 뭘로 공격할 거야? (묵, 찌, 빠 중 하나를 말해봐)")
            await send(ctx, embed=embedd)
            await self.user_attack(self, ctx)
        else:
            embedd.set_footer(text="내가 공격할 차례군! 방어할 준비를 해 (묵, 찌, 빠 중 하나를 말해봐)")
            await send(ctx, embed=embedd)
            await self.conubot_attack(self, ctx)

    @command(name="랜덤채팅", aliases=["랜챗"])
    async def random_chat(self, ctx, activity: Optional[str] = "도움", activity2: Optional[str] = "조회",
                          not_to_meet: Optional[Member] = ""):
        if activity == "도움":
            await send(ctx, embed=Embed(color=0xffd6fe, title="커뉴봇 랜덤채팅 명령어",
                                       description="개선된 매칭 알고리즘으로 만든 랜덤 채팅 시스템이에요.\n\t\n`커뉴야 랜덤채팅 시작` 으로 매칭을 잡고 두 명이 대기하게 되면 매칭이 잡혀요. 그러면 채팅을 할 수가 있게 돼요."))
        elif activity == "시작":
            now = db.record("SELECT room_number FROM games WHERE UserID = ?", ctx.author.id)
            try:
                now = now[0]
            except TypeError:
                db.execute("INSERT INTO games (UserID) VALUES (?)", ctx.author.id)
                now = None
            if now == 2:
                await send(ctx, "이미 매칭을 기다리고 있어요!")
                return
            elif now is not None:
                await send(ctx, "봇과의 DM으로 해야 하는 기능은 한 번에 하나만 실행될 수 있어요!")
                return
            queue_people = db.record("SELECT UserID FROM games WHERE room_number = 2")
            try:
                queue_people = queue_people[0]
            except TypeError:
                db.execute("UPDATE games SET room_number = 2 WHERE UserID = ?", ctx.author.id)
                await send(ctx, "랜덤채팅 매칭을 잡기 시작했어요! 과연 누가 걸릴까요?")
                return
            blocked = db.record("SELECT random_chat_not_meet FROM games WHERE UserID = ?", ctx.author.id)
            try:
                blocked = blocked[0].split(",")
                if queue_people in blocked:
                    db.execute("UPDATE games SET room_number = 2 WHERE UserID = ?", ctx.author.id)
                    await send(ctx, "랜덤채팅 매칭을 잡기 시작했어요! 과연 누가 걸릴까요?")
                    return
            except:
                pass
            blocked2 = db.record("SELECT random_chat_not_meet FROM games WHERE UserID = ?", queue_people)
            try:
                blocked2 = blocked2[0].split(",")
                if ctx.author.id in blocked2:
                    return
            except:
                pass
            i = randint(10000000, 40000000)
            db.execute("UPDATE games SET room_number = ? WHERE UserID = ?", i, ctx.author.id)
            db.execute("UPDATE games SET room_number = ? WHERE UserID = ?", i, queue_people)
            db.commit()
            await ctx.author.send(f"{str(self.bot.get_user(queue_people))}와(과)의 랜덤채팅이 시작됐어요!")
            await self.bot.get_user(queue_people).send(f"{ctx.author}와(과)의 랜덤채팅이 시작됐어요!")
        elif activity == "종료":
            now_room = db.record("SELECT room_number FROM games WHERE UserID = ?", ctx.author.id)
            now_room = now_room[0]
            if now_room == 2:
                db.execute("UPDATE games SET room_number = NULL WHERE UserID = ?", ctx.author.id)
                db.commit()
                await send(ctx, "랜덤채팅 매칭 대기열에서 빠져나왔어요.")
            elif now_room is not None:
                if now_room < 2:
                    await send(ctx, "`커뉴야 묵 매칭취소`")
                cur_tkdeo = db.record("SELECT UserID FROM games WHERE room_number = ? AND UserID != ?", now_room,
                                      ctx.author.id)
                await ctx.author.send("랜덤채팅이 종료되었어요.")
                await self.bot.get_user(cur_tkdeo[0]).send("랜덤채팅이 종료되었어요.")
                db.execute("UPDATE games SET room_number = NULL WHERE UserID = ?", ctx.author.id)
                db.execute("UPDATE games SET room_number = NULL WHERE UserID = ?", cur_tkdeo[0])
                db.commit()
            else:
                await send(ctx, "랜덤채팅 매칭을 잡고 있지도 않고 채팅하고 있지도 않아요!")
        elif activity == "만나지않기":
            if activity2 == "조회":
                member_blocked = db.record("SELECT random_chat_not_meet FROM games WHERE UserID = ?", ctx.author.id)
                try:
                    member_blocked = member_blocked[0].split(",")
                    users = []
                    for member_ in member_blocked:
                        users.append(self.bot.get_user(int(member_)))
                    member_blocked = ""
                    for user_ in users:
                        member_blocked += f"{str(user_)}\n"
                except AttributeError:
                    member_blocked = ""
                await send(ctx, f"현재 {ctx.author.name}님이 랜덤채팅에서 차단한 사람들은 아래와 같아요:\n{member_blocked}")
            elif activity2 == "추가":
                if not not_to_meet:
                    await send(ctx, "`커뉴야 랜덤채팅 만나지않기 추가 (멤버)`의 형식으로 입력해 주세요!")
                    return
                not_meet = db.record("SELECT random_chat_not_meet FROM games WHERE UserID = ?", ctx.author.id)
                not_meet = not_meet[0] + f",{not_to_meet.id}"
                if len(not_meet) > 60:
                    await send(ctx, "랜덤채팅 차단은 3명까지만 할 수 있어요!")
                    return
                await send(ctx, f"성공적으로 {str(not_to_meet)}을 랜덤채팅에서 안 만나도록 설정했어요!")
                db.execute("UPDATE games SET random_chat_not_meet = ? WHERE UserID = ?", not_meet, ctx.author.id)
                db.commit()
            elif activity2 == "삭제":
                if not not_to_meet:
                    await send(ctx, "`커뉴야 랜덤채팅 만나지않기 삭제 (멤버)`의 형식으로 입력해 주세요!")
                    return
                not_meet = db.record("SELECT random_chat_not_meet FROM games WHERE UserID = ?", ctx.author.id)
                not_meet = not_meet[0]
                if f",{not_to_meet.id}" in not_meet:
                    not_meet = not_meet.replace(f",{not_to_meet.id}", "")
                elif f"{not_to_meet.id}," in not_meet:
                    not_meet = not_meet.replace(f"{not_to_meet.id},", "")
                else:
                    await send(ctx, "그 사용자는 차단되지 않았어요!")
                    return
                await send(ctx, f"성공적으로 {str(not_to_meet)}을 랜덤채팅에서 다시 만나도록 설정했어요!")
                db.execute("UPDATE games SET random_chat_not_meet = ? WHERE UserID = ?", not_meet, ctx.author.id)
                db.commit()
        else:
            await send(ctx, "`커뉴야 랜덤채팅 <도움/시작/종료/만나지않기>`")

    @command(name="지건")
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = " "):
        await ctx.message.delete()
        await send(ctx, f"{ctx.author.display_name} 님이  {member} 님에게 지건을 꽂았습니다!\n이유: {reason}")

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await send(ctx, "멤버를 찾을 수 없어요!")

    @command(name="서버추천", aliases=["섭추"])
    @cooldown(1, 20, BucketType.member)
    async def recommend_server(self, ctx):
        if ctx.guild is None:
            server_id, server_to_recommend = db.record(
                "SELECT GuildID, advert FROM guilds WHERE advert IS NOT NULL ORDER BY RANDOM() LIMIT 1")
        else:
            server_id, server_to_recommend = db.record(
                "SELECT GuildID, advert FROM guilds WHERE advert IS NOT NULL AND GuildID != ? ORDER BY RANDOM() LIMIT 1",
                ctx.guild.id)
        await send(ctx, f"**{self.bot.get_guild(server_id)}**\n{server_to_recommend}")

    @command(name="운빨테스트", aliases=["운"])
    async def luck_test(self, ctx):
        i = randint(1, 1000000)
        if (i % 10) == 6:
            await ctx.channel.send("10% 확률에 당첨되셨네요!")
        elif (i % 100) == 69:
            await ctx.channel.send("1% 확률에 당첨되셨네요!!")
        elif (i % 1000) == 697:
            await ctx.channel.send("0.1% 확률에 당첨되셨네요!!!!!!!!!!")
            l = grant_check("엄청난 운빨", ctx.author.id)
            if l == 1:
                await grant(ctx, "엄청난 운빨", "운빨테스트 명령어에서 0.1% 확률에 당첨되세요")
        elif (i % 10000) == 6974:
            await ctx.channel.send("0.01% 확률에 당첨되셨네요!!!!!!!!!!!!!!!!!!!!!!")
            l = grant_check("최강의 운빨", ctx.author.id)
            if l == 1:
                await grant(ctx, "최강의 운빨", "운빨테스트 명령어에서 0.01% 확률에 당첨되세요")
        else:
            await ctx.channel.send("평범한 운빨입니다")

    @command(name="파이값", aliases=["ㅠ"])
    async def display_pi(self, ctx, digit: Optional[int]):
        if not digit:
            return
        pi = "3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148086513282306647093844609550582231725359408128481117450284102701938521105559644622948954930381964428810975665933446128475648233786783165271201909145648566923460348610454326648213393607260249141273724587006606315588174881520920962829254091715364367892590360011330530548820466521384146951941511609433057270365759591953092186117381932611793105118548074462379962749567351885752724891227938183011949129833673362440656643086021394946395224737190702179860943702770539217176293176752384674818467669405132000568127145263560827785771342757789609173637178721468440901224953430146549585371050792279689258923542019956112129021960864034418159813629774771309960518707211349999998372978049951059731732816096318595024459455346908302642522308253344685035261931188171010003137838752886587533208381420617177669147303598253490428755468731159562863882353787593751957781857780532171226806613001927876611195909216420198938095257201065485863278865936153381827968230301952035301852968995773622599413891249721775283479131515574857242454150695950829533116861727855889075098381754637464939319255060400927701671139009848824012858361603563707660104710181942955596198946767837449448255379774726847104047534646208046684259069491293313677028989152104752162056966024058038150193511253382430035587640247496473263914199272604269922796782354781636009341721641219924586315030286182974555706749838505494588586926995690927210797509302955321165344987202755960236480665499119881834797753566369807426542527862551818417574672890977772793800081647060016145249192173217214772350141441973568548161361157352552133475741849468438523323907394143334547762416862518983569485562099219222184272550254256887671790494601653466804988627232791786085784383827967976681454100953883786360950680064225125205117392984896084128488626945604241965285022210661186306744278622039194945047123713786960956364371917287467764657573962413890865832645995813390478027590"
        if digit > 1998:
            await send(ctx, "글자수가 너무 많아 표시할 수 없어요!")
            return
        elif digit < 0:
            await send(ctx, "글자수는 양수로 입력해야 해요!")
            return
        else:
            await send(ctx, pi[:digit + 2])
        if digit == 767:
            l = grant_check("21134**999999**", ctx.author.id)
            if l == 1:
                await grant(ctx, "21134**999999**", "파이값 명령어에서 출력되는 글자가 999999로 끝나도록 자릿수를 설정하세요")

    @command(name="소개")
    async def introduce(self, ctx):
        await ctx.channel.send(embed=Embed(color=0xffd6fe, title="커뉴봇 소개",
                                           description="**연세대학교 컴퓨터과학과 출신** 다양한 기능을 가진 종합 디스코드 봇!\n`있어야 하는 기능은 다 넣되 쓸데없는 기능은 최소화하자`라는 인생 철학이지 개발 원칙 하에 만들어진 디스코드 봇이에요.\n레벨 시스템이나 관리 명령어, 오목같은 게임 명령어부터 시작해서 매우 다양한 명령어가 존재해요. `커뉴야 도움`, `커뉴야 관리`로 명령어들에 대해 알아보세요!"))

    @command(name="강화", aliases=["갈화"])
    @cooldown(1, 12, BucketType.user)
    async def enchant(self, ctx, *, item_name: Optional[str] = "커뉴봇"):
        enchant_info = db.record("SELECT enchant_info FROM games WHERE UserID = ?", ctx.author.id)
        try:
            enchant_info = json.loads(enchant_info[0])
        except TypeError:
            db.execute("INSERT INTO games (UserID) VALUES (?)", ctx.author.id)
            enchant_info = {"최대강화가능개수": 3}
        embed = Embed(color=ctx.author.color)
        if item_name in ["목록", "삭제", "파괴"]:
            await send(ctx, "혹시 강화를 할려는 의도가 아니었다면 `커뉴야 도움 강화`로 세부 명령어를 알아봐 주세요!")
        if item_name not in enchant_info:
            if len(enchant_info) - 1 == enchant_info["최대강화가능개수"]:
                await send(ctx, "강화하고 있는 아이템 수가 최대에 도달했어요!")
                return
            else:
                enchant_info.update({item_name: 0})
        level = enchant_info[item_name]
        probability = 1 - 0.0014 * level
        if probability < 0.1:
            probability = 0.1
        temp = random()
        if temp < probability:
            lv_to_up = randint(1, 35)
            lv_to_up = 6 - int(math.sqrt(lv_to_up))
            afterlevel = level + lv_to_up
            embed.add_field(name=f"{item_name} 강화 성공!", value=f"레벨 {level} -> {afterlevel}")
            if afterlevel >= 100:
                l = grant_check("강화의 시작", ctx.author.id)
                if l == 1:
                    await grant(ctx, "강화의 시작", "강화 명령어에서 100레벨을 달성하세요")
            if afterlevel >= 200:
                l = grant_check("평범한 강화", ctx.author.id)
                if l == 1:
                    await grant(ctx, "평범한 강화", "강화 명령어에서 200레벨을 달성하세요")
            if afterlevel >= 300:
                l = grant_check("고급스러운 강화", ctx.author.id)
                if l == 1:
                    await grant(ctx, "고급스러운 강화", "강화 명령어에서 300레벨을 달성하세요")
            if afterlevel >= 400:
                l = grant_check("숙련된 강화", ctx.author.id)
                if l == 1:
                    await grant(ctx, "숙련된 강화", "강화 명령어에서 400레벨을 달성하세요")
            if afterlevel >= 500:
                l = grant_check("낮은 확률을 뚫는", ctx.author.id)
                if l == 1:
                    await grant(ctx, "낮은 확률을 뚫는", "강화 명령어에서 500레벨을 달성하세요")
            if afterlevel >= 600:
                l = grant_check("사실상 만렙", ctx.author.id)
                if l == 1:
                    await grant(ctx, "사실상 만렙", "강화 명령어에서 600레벨을 달성하세요")
            if afterlevel >= 650:
                l = grant_check("만렙을 초월한", ctx.author.id)
                if l == 1:
                    await grant(ctx, "만렙을 초월한", "강화 명령어에서 650레벨을 달성하세요")
        else:
            lv_to_down = randint(1, 8)
            lv_to_down = 2 - int(math.sqrt(lv_to_down))
            afterlevel = level - lv_to_down
            embed.add_field(name=f"{item_name} 강화 실패...", value=f"레벨 {level} -> {afterlevel}")
        embed.set_footer(text=f"강화 성공 확률 {round(100 * probability, 3)} %")
        enchant_info[item_name] = afterlevel
        enchant_info = json.dumps(enchant_info, ensure_ascii=False)
        db.execute("UPDATE games SET enchant_info = ? WHERE UserID = ?", enchant_info, ctx.author.id)
        db.commit()
        await send(ctx, embed=embed)
        return

        # if extra == "리더보드":
        #     records = db.records("SELECT UserID, eLv FROM games WHERE eLv != 0 ORDER BY eLv DESC LIMIT ?, ?", 10*page-10, 10)
        #     tjfaud = ""
        #     now_people = 10*page-9
        #     for record in records:
        #         tjfaud = tjfaud + f"{now_people}. <@{record[0]}> (강화 레벨: {record[1]}) \n"
        #         now_people += 1
        #     if tjfaud == "":
        #         tjfaud = "선택하신 페이지에는 사람이 없는 것 같아요!"
        #     await send(ctx, embed=Embed(color=ctx.author.color, title="강화 랭킹!", description=tjfaud))

    @command(name="파괴", aliases=["강화삭제"])
    async def destroy(self, ctx, *, item_name: Optional[str] = "커뉴봇"):
        enchant_info = db.record("SELECT enchant_info FROM games WHERE UserID = ?", ctx.author.id)
        enchant_info = json.loads(enchant_info[0])
        if item_name not in enchant_info or item_name == "최대강화가능개수":
            await send(ctx, "그런 아이템을 강화하고 있지 않아 파괴할 수 없어요!")
            return
        await send(ctx, "정말로 아이템을 파괴할 건가요? `네`라고 입력해서 확실시해 주세요!")
        try:
            msg = await self.bot.wait_for(
                "message",
                timeout=20,
                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
            )
        except asyncio.TimeoutError:
            await send(ctx, "아이템 파괴를 취소했어요.")
            return
        if not msg.content == "네":
            await send(ctx, "아이템 파괴를 취소했어요.")
            return
        await send(ctx, "아이템 파괴를 완료했어요.")
        del enchant_info[item_name]
        enchant_info = json.dumps(enchant_info, ensure_ascii=False)
        db.execute("UPDATE games SET enchant_info = ? WHERE UserID = ?", enchant_info, ctx.author.id)
        db.commit()

    @command(name="강화목록", aliases=["강목"])
    async def display_enchant_list(self, ctx):
        embed = Embed(color=ctx.author.color, title=f"{str(ctx.author)}의 강화 목록!")
        enchant_info = db.record("SELECT enchant_info FROM games WHERE UserID = ?", ctx.author.id)
        enchant_info = json.loads(enchant_info[0])
        embed.set_footer(
            text=f'한 번에 최대로 강화할 수 있는 아이템의 개수는 {enchant_info["최대강화가능개수"]}개입니다' + '공식서버 가입 후 `커뉴야 구매 강화슬롯추가권`명령어로 최대 10개까지 이 값을 늘리세요' * (
                    enchant_info["최대강화가능개수"] < 10))
        del enchant_info["최대강화가능개수"]
        for item in enchant_info:
            embed.add_field(name="​", value=f"아이템 이름: {item} ({enchant_info[item]}레벨)", inline=False)
        await send(ctx, embed=embed)

    @command(name="가위바위보", aliases=["가바보"])
    async def rock_paper_scissors(self, ctx, rps: Optional[str] = "엄준식"):
        rsp = randint(1, 3)
        embed = Embed(color=ctx.author.color)
        embed.add_field(name="커뉴봇 가위바위보", value="​", inline=False)
        if rps == "가위" or rps == "찌":
            rps = 1
            embed.add_field(name=f"{ctx.author.display_name}", value=":v:")
        elif rps == "바위" or rps == "주먹" or rps == "묵":
            rps = 2
            embed.add_field(name=f"{ctx.author.display_name}", value=":punch:")
        elif rps == "보" or rps == "빠":
            rps = 3
            embed.add_field(name=f"{ctx.author.display_name}", value=":raised_back_of_hand: ")
        elif rps == "섬바삭보":
            emoji = '\N{THUMBS UP SIGN}'
            await ctx.message.add_reaction(emoji)
            await ctx.channel.send("ㄹㅇㅋㅋ 섬ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ밬ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ샄ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ봌ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ")
            l = grant_check("가위바위보에서 무슨 짓을...", ctx.author.id)
            if l == 1:
                await grant(ctx, "가위바위보에서 무슨 짓을...", "가위바위보 명령어에서 이스터에그를 발견하세요")
            return
        elif rps == "배리나":
            await ctx.channel.send(":rage:")
            return
        elif rps == "지":
            await send(ctx, "뭐이새꺄?")
            return
        elif rps == "우커바":
            await send(ctx, "우리 커여운 한바♡♡")
            return
        elif rps == '알맞은 걸':
            l = grant_check("설명대로", ctx.author.id)
            if l == 1:
                await grant(ctx, "설명대로", "가위바위보 명령어에서 이스터에그를 발견하세요. 물론 이스터에그가 이게 끝이 아니긴 해요.")
        else:
            await send(ctx, "알맞은 걸 내 주세요")
            return
        if rsp == 1:
            embed.add_field(name="커뉴봇", value=":v:")
        if rsp == 2:
            embed.add_field(name="커뉴봇", value=":punch:")
        if rsp == 3:
            embed.add_field(name="커뉴봇", value=":raised_back_of_hand:")
        if rps == rsp:
            embed.set_footer(text="비겼네요...")
        elif rps - rsp == 1 or rps - rsp == -2:
            embed.set_footer(text="이기셨네요! 축하드려요")
        else:
            embed.set_footer(text="ㅋ")
        await send(ctx, embed=embed)

    @command(name="기원")
    async def pray(self, ctx, *, giwon: Optional[str]):
        if giwon == "목록":
            await send(ctx, "기원들의 목록을 보시고 싶다면 `커뉴야 기원목록`을 확인해 보세요!")
        today = ((time() + 32400) // 86400)
        if not giwon:
            await send(ctx, "뭘 기원할 건지도 말해 주세요!")
            return
        giwon_list = db.records("SELECT * FROM Giwons WHERE GuildID = ?", ctx.guild.id)
        for giwons in giwon_list:
            if giwon == giwons[0]:
                if today == giwons[4]:
                    await send(ctx, "오늘은 이미 해당 항목을 기원했어요!")
                    return
                await ctx.guild.get_member(giwons[2]).edit(nick=f"{giwons[0]}{giwons[3] + 1}일차")
                db.execute("UPDATE Giwons SET days = ?, last_giwon_date = ? WHERE Giwon_name = ? AND GuildID = ?",
                           int(giwons[3]) + 1, today, giwons[0], giwons[1])
                db.commit()
                await send(ctx, f"{giwons[0]}을 기원했어요! 오늘은 해당 기원의 {giwons[3] + 1}일차에요.")
                if giwons[3] + 1 == 365:
                    l = grant_check("제발 이루어졌으면", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "제발 이루어졌으면", "기원 명령어에서 365일차 기원을 기원하세요")
                return
        guitar_giwons = db.record("SELECT * FROM Giwons WHERE GuildID = 0 AND Giwon_name = ?", giwon)
        if guitar_giwons:
            if today == guitar_giwons[4]:
                await send(ctx, "오늘은 이미 누군가가 해당 항목을 기원했어요!")
                return
            days = int(guitar_giwons[3])
            days += 1
            await send(ctx, f"{guitar_giwons[0]} 을(를) 기원했어요! {days}일차 기원이에요.")
            db.execute("UPDATE Giwons SET days = ?, last_giwon_date = ? WHERE Giwon_name = ? AND GuildID = 0", days,
                       today, guitar_giwons[0])
            db.commit()
            return
        else:
            if giwon.find("커뉴") + giwon.find("컨유") + giwon.find("커늒") + giwon.find("귀늒") + giwon.find(
                    "나몬") + giwon.find("병신") + giwon.find("섹스") + giwon.find("씨발") + giwon.find("ㅂㅅ") != -9:
                await send(ctx, ":weary:")
                return
            if len(giwon) > 70:
                await send(ctx, "기원이 너무 길어요!")
                return
            await send(ctx, f"{giwon} 을(를) 기원했어요! 새로 등록되는 기원이에요!")
            db.execute(
                "INSERT INTO Giwons (Giwon_name, GuildID, TargetID, days, last_giwon_date) VALUES (?, 0, 0, 1, ?)",
                giwon, today)
            db.commit()

    @command(name="업다운")
    async def up_down(self, ctx, number_range: Optional[int] = 100):
        number_to_guess = randint(1, number_range)
        tried = 1
        min_number = 1
        max_number = number_range
        while True:
            await send(ctx, f"{min_number}부터 {max_number}의 숫자 중에서 추측해 보세요! {tried}번째 시도에요.")
            try:
                number_guessed = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                await send(ctx, "게임을 중단했어요.")
                return
            try:
                number_guessed = int(number_guessed.content)
            except ValueError:
                await send(ctx, "숫자로만 보내 주세요")
                return
            if number_guessed == number_to_guess:
                await send(ctx, f"{tried}번만에 숫자를 추측하는 데 성공했어요!")
                if number_range >= 500:
                    l = grant_check("굉장한 찍신", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "굉장한 찍신", "업다운 명령어에서 최소 1부터 500까지의 수 중에서 하나를 한 번만에 맞히기")
                return
            elif number_guessed > number_to_guess:
                await send(ctx, "지금 추측하신 숫자는 정답보다 커요!")
                max_number = number_guessed
            else:
                await send(ctx, "지금 추측하신 숫자는 정답보다 작아요!")
                min_number = number_guessed
            tried += 1

    # @command(name="투표", aliases=["퉆", "i770d"])
    # async def i770d(self, ctx, activity: Optional[str], until: Optional[int] = 3, *, asdf: Optional[str]):
    #     today = ((time() + 32400) // 86400)
    #     if "i770d" in ctx.message.content:
    #         l = grant_check("다시 하는 1주년 이벤트", ctx.author.id)
    #         if l == 1:
    #             await grant(ctx, "다시 하는 1주년 이벤트", "기억력이 압도적으로 좋으신가요? 아니면 검색을 압도적으로 잘하시나요?")
    #     if activity == "생성":
    #         if not asdf:
    #             await send(ctx, "생성할 투표의 이름을 정해 주세요!")
    #         try:
    #             i770d_name = await self.bot.wait_for(
    #                 "message",
    #                 timeout=40,
    #                 check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
    #             )
    #         except asyncio.TimeoutError:
    #             await send(ctx, "투표 생성을 중단했어요.")
    #             return
    #         await send(ctx, "투표 보기들을 제시해 주세요! 줄바꿈 문자는 보기에 포함될 수 없어요. `ㅇㅇㅇㅇㅇ`을 입력하거나 보기 5개를 입력할 때까지 계속 입력할 수 있어요.")
    #         qhrls = []
    #         for i in range(5):
    #             try:
    #                 qhrl = await self.bot.wait_for(
    #                     "message",
    #                     timeout=30,
    #                     check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel and '\n' not in message.content
    #                 )
    #             except asyncio.TimeoutError:
    #                 await send(ctx, "투표 생성을 중단했어요.")
    #                 return
    #             if qhrl.content == "ㅇㅇㅇㅇㅇ":
    #                 if i == 0:
    #                     await send(ctx, "투표 생성을 취소했어요.")
    #                     return
    #                 break
    #             qhrls.append(qhrl.content)
    #         if len(qhrls) == 1:
    #             await send(ctx, '보기는 2개 이상이어야 해요!')
    #             return
    #         await send(ctx, f"투표 제작을 완료헀어요! 오늘부터 {until}일 후 투표 명령어를 실행하시면 투표가 끝나요.")
    #         db.execute("INSERT INTO i770d (id, name, choices, until) VALUES (?, ?, ?, ?)", ctx.author.id, i770d_name, '\n'.join(qhrls), today + until)
    #         db.commit()
    #     elif activity == '목록':
    #         official_vote = db.record("SELECT * FROM i770d WHERE official = True ORDER BY RANDOM() LIMMIT 1")
    # todo 투표 ID 값 어떤 식으로 설정할지 생각

    @command(name="잡초키우기", aliases=["잡키", "잠키", 'ㅈㅋ'])
    @cooldown(1, 12, BucketType.user)
    async def grow_zapcho(self, ctx, activity: Optional[str] = "키우기", buy: Optional[str] = "1",
                          buy_amount: Optional[int] = 5):
        if randint(1, 40) == 1:
            num = randint(10000, 99999)
            await send(ctx, 
                f"매크로 방지를 위해 확인을 할게요. 10초 안에 어디든 좋으니 커뉴봇이 볼 수 있는 곳에{num}이라고 보내 주세요.\n구매에도 매크로쓰는사람 있는 :weary:")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=10,
                    check=lambda message: message.author == ctx.author and message.content == str(num)
                )
            except asyncio.TimeoutError:
                await send(ctx, ":weary:")
                await self.ban_10min(ctx.author.id)
                return
            if msg.content != str(num):
                await send(ctx, ":weary:")
                await self.ban_10min(ctx.author.id)
                return
        level = db.record("SELECT zl, user_setting FROM games WHERE UserID = ?", ctx.author.id)
        setting = level[1]
        if ctx.guild.id != 743101101401964647:
            try:
                print((self.bot.get_guild(743101101401964647)).get_member(ctx.author.id).display_name)
            except AttributeError:
                await send(ctx, "공식서버 가입자만 사용할 수 있는 기능이에요!")
                return
        try:
            level = level[0]
        except TypeError:
            db.execute("INSERT INTO games (UserID, zl, zf) VALUES (?, 0, 0)", ctx.author.id)
            level = 0
        if ('ㅈㅋ' in ctx.message.content) and (setting & 256 == 0):
            await send(ctx, '어허')
            return
        if level is None:
            try:
                db.execute("INSERT INTO games (UserID, zl, zf) VALUES (?, 0, 0)", ctx.author.id)
            except sqlite3.IntegrityError:
                db.execute("UPDATE games SET zl = 0, zf = 0 WHERE UserID = ?", ctx.author.id)
            embed = Embed(color=0x00ff7f)
            embed.add_field(name="잡초키우기 가입 완료!",
                            value="잡초를 땅에 심었어요!\n`커뉴야 잡초키우기`로 잡초에게 물을 줄 수 있고 `커뉴야 잡초키우기 비료`로 비료를 줄 수 있는 등 컨텐츠들이 있어요!\n레벨업을 하면 보상을 받을 수 있으니 보상도 노려 보세요!")
            embed.set_footer(text="`커뉴야 잡초키우기 도움` 으로 게임 방법을 확인해 보세요!")
            embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/783226362856734730/818716399701852180/224_20210125223208.png")
            await send(ctx, embed=embed)
            db.commit()
            return
        fer = db.record("SELECT zf FROM games WHERE UserID = ?", ctx.author.id)
        money = db.record("SELECT Money FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", ctx.author.id)
        exp = db.record("SELECT XP FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", ctx.author.id)
        xpboost = db.record("SELECT XPBoost FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", ctx.author.id)
        fer = fer[0]
        money = money[0]
        exp = exp[0]
        xpboost = xpboost[0]
        if activity == "도움":
            embed = Embed(color=0x00ff7f)
            embed.add_field(name="잡초키우기\n버전: 1.0.6",
                            value="<@634632747272503306>가 계획하고 <@724496900920705045>가 만든 게임.\n\t\n`커뉴야 잡초키우기`: 잡초에게 물을 준다. 일정확률로 잡초가 레벨업한다.\n`커뉴야 잡초키우기 내정보`: 현재 자신의 잡초키우기 정보를 보여준다.\n`커뉴야 잡초키우기 도움`: 이 도움말을 표시한다.\n`커뉴야 잡초키우기 리더보드`: 다른 사람들의 잡초 레벨과 비료 개수가 있는 리더보드를 표시한다.\n`커뉴야 잡초키우기 비료`: 잡초에게 비료를 준다. 높은 확률로 잡초가 레벨업한다.\n`커뉴야 잡초키우기 상점`: 잡초키우기에 필요한 아이템들을 살 수 있다.\n`커뉴야 잡초키우기 최근업뎃`: 최근 업데이트 정보를 보여준다.")
            await send(ctx, embed=embed)
        elif activity == "내정보":
            embed = Embed(color=0x00ff7f)
            ids = db.column("SELECT UserID FROM games ORDER BY zl DESC")
            rank = ids.index(ctx.author.id) + 1
            embed.add_field(name=f"{ctx.author.display_name}의 잡초 정보", value=f"** **", inline=False)
            embed.add_field(name="레벨", value=f"{level}", inline=True)
            embed.add_field(name="레벨 등수", value=f"{rank}등")
            embed.add_field(name="비료", value=f"{fer} 개")
            await send(ctx, embed=embed)
        elif activity == "리더보드":
            records = db.records("SELECT UserID, zl, zf FROM games WHERE zl IS NOT NULL ORDER BY zl DESC LIMIT ?, ?",
                                 10 * int(buy) - 10, 10)
            tjfaud = ""
            now_people = int(buy) * 10 - 9
            for record in records:
                tjfaud = tjfaud + f"{now_people}. <@{record[0]}> (잡초 레벨: {int(record[1])} | 비료 개수: {record[2]})  \n"
                now_people += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 사람이 없는 것 같아요!"
            await send(ctx, embed=Embed(color=0x00ff7f, title="잡초키우기 랭킹!", description=tjfaud))
        elif activity in ["비료", "ㅂㄹ"]:
            if activity == 'ㅂㄹ' and setting & 256 == 0:
                await send(ctx, '어허')
                return
            if fer <= 0:
                await send(ctx, "비료가 없다. `커뉴야 잡초키우기 상점`에서 비료를 구매해 보자.")
                return
            level = level + 1
            fer = fer - 1
            db.execute("UPDATE games SET zl = ?, zf = ? WHERE UserID = ?", level, fer, ctx.author.id)
            i = randint(1, 4)
            reward = "없음 :("
            if i != 1:
                i = randint(1, 126)
                if i < 114:
                    mg = min(250 + int(level ** 0.8 / 6), 900 + randint(0, 100))
                    if ctx.guild.id != 743101101401964647:
                        mg = int(mg / 2.5)
                    money = money + mg
                    db.execute("UPDATE exp SET Money = ? WHERE UserID = ? AND GuildID = 743101101401964647", money,
                               ctx.author.id)
                    reward = f"돈 {mg} (현재 남은 돈 {money})"
                elif i < 126:
                    eg = 100 + int(level ** 0.75 / 11)
                    if ctx.guild.id != 743101101401964647:
                        eg = int(eg / 2.5)
                    exp = exp + eg
                    db.execute("UPDATE exp SET XP = ? WHERE UserID = ? AND GuildID = 743101101401964647", exp,
                               ctx.author.id)
                    reward = f"경험치 {eg} (현재 경험치 {exp})"
                else:
                    xpboost = xpboost + 0.02
                    db.execute("UPDATE exp SET XPBoost = ? WHERE UserID = ? AND GuildID = 743101101401964647", xpboost,
                               ctx.author.id)
                    reward = f"경험치 부스트 2%p...? (현재 경부 {xpboost})"
            embed = Embed(color=0x00ff7f, title="잡초에게 비료를 주었다!")
            embed.add_field(name="잡초 레벨", value=f"{int(level) - 1} -> {int(level)}")
            if ctx.guild.id != 743101101401964647:
                embed.set_footer(text="공식서버에서 명령어를 실행해 더 많은 보상을 가져가세요 (2.5배)")
            if int(level) >= 300:
                l = grant_check("나무를 키우는 자", ctx.author.id)
                if l == 1:
                    await grant(ctx, "나무를 키우는 자", "잡초키우기 명령어에서 잡초 레벨 300을 달성하세요")
                    mv = self.bot.get_guild(743101101401964647)
                    await mv.get_member(ctx.author.id).add_roles(mv.get_role(819414894038089738))
            if int(level) >= 1000:
                l = grant_check("내일지구가멸망해도나무를키우겠다", ctx.author.id)
                if l == 1:
                    await grant(ctx, "내일지구가멸망해도나무를키우겠다", "잡초키우기 명령어에서 잡초 레벨 1000을 달성하세요")
                    mv = self.bot.get_guild(743101101401964647)
                    await mv.get_member(ctx.author.id).add_roles(mv.get_role(848710492356739073))
            if int(level) >= 10000:
                l = grant_check("드루이드", ctx.author.id)
                if l == 1:
                    await grant(ctx, "드루이드", "잡초키우기 명령어에서 잡초 레벨 10000을 달성하세요")
                    mv = self.bot.get_guild(743101101401964647)
                    await mv.get_member(ctx.author.id).add_roles(mv.get_role(901680973916307497))
            embed.add_field(name="비료 개수", value=f"{fer + 1} -> {fer}")
            embed.add_field(name="받은 보상", value=reward, inline=False)
            embed.set_thumbnail(
                url="https://media.discordapp.net/attachments/783226362856734730/818719628602638387/224_20210125224126.png")
            await send(ctx, embed=embed)
        elif activity == "상점":
            embed = Embed(color=0x00ff7f)
            embed.add_field(name="비료",
                            value="잡초가 잘 자라게 해주는 비료를 구매합니다.\n개당 300<:treasure:811456823248027648>, 한 번에 20개 이상 사는 경우 비료 구매 명령어를 여러 번 사용해야 하는 고통을 줄여주는 대신 그만큼의 수수료가 따릅니다. 아래는 수수료가 포함된 가격의 예시입니다.\n20개 가격: 6120, 100개 가격: 33000, 500개 가격: 225000")
            embed.set_footer(text="아이템 구매를 원한다면 `커뉴야 잡키 구매 (아이템이름)을 입력하자. (띄어쓰기가 있는 아이템이라면 붙여서)")
            await send(ctx, embed=embed)
        elif activity == "구매":
            if buy == "비료":
                price = buy_amount * 300
                if buy_amount >= 20:
                    price = price * (100 + buy_amount // 10) // 100
                if buy_amount >= 500:
                    price = buy_amount * 450
                if money >= price:
                    money -= price
                    fer += buy_amount
                    db.execute("UPDATE exp SET Money = ? WHERE userID = ? AND GuildID = 743101101401964647", money,
                               ctx.author.id)
                    db.execute("UPDATE games SET zf = ? WHERE UserID = ?", fer, ctx.author.id)
                    await send(ctx, f"비료 {buy_amount}개를 {price}<:treasure:811456823248027648>에 구매 완료! 남은 비료: {fer}개")
                    db.commit()
                else:
                    await send(ctx, "돈이 부족해요.")
            else:
                await send(ctx, f"존재하지 않는 아이템명: `{buy}`")
        elif activity == "최근업뎃":
            embed = Embed(color=0x00ff7f)
            embed.add_field(name="잡초키우기 1.0.8버전 업데이트",
                            value="상점에서 비료를 원하는 개수만큼 살 수 있도록 변경\n공식서버 밖에서 명령어를 실행할 경우 주는 보상을 하향 조정")
            await send(ctx, embed=embed)
        else:
            afterlevel = level + 0.01 * randint(15, 40)
            growth = int((afterlevel - int(afterlevel)) * 100) // 10
            growth_text = ""
            for i in range(growth):
                growth_text += "ㅣ"
            for i in range(10 - growth):
                growth_text += "ㆍ"
            db.execute("UPDATE games SET zl = ? WHERE UserID = ?", afterlevel, ctx.author.id)
            reward = "없음 :("
            thumb = "https://media.discordapp.net/attachments/783226362856734730/818719604071071754/224_20210125223755.png"
            if randint(1, 10) == 1:
                fer = fer + 1
                db.execute("UPDATE games SET zf = ? WHERE UserID = ?", fer, ctx.author.id)
                reward = f"\n비료를 획득했다! (현재 남은 비료 {fer})"
                thumb = "https://media.discordapp.net/attachments/783226362856734730/818719628602638387/224_20210125224126.png"
            if int(level) != int(afterlevel):
                i = randint(1, 3)
                if i != 1:
                    thumb = "https://media.discordapp.net/attachments/783226362856734730/818719628602638387/224_20210125224126.png"
                    i = randint(1, 126)
                    if i < 114:
                        mg = 280 + int(level ** 0.8 / 6)
                        if ctx.guild.id != 743101101401964647:
                            mg = int(mg / 2)
                        money = money + mg
                        db.execute("UPDATE exp SET Money = ? WHERE UserID = ? AND GuildID = 743101101401964647", money,
                                   ctx.author.id)
                        reward = f"돈 {mg} (현재 남은 돈 {money})"
                    elif i < 126:
                        eg = 125 + int(level ** 0.75 / 11)
                        if ctx.guild.id != 743101101401964647:
                            eg = int(eg / 2)
                        exp = exp + eg
                        db.execute("UPDATE exp SET XP = ? WHERE UserID = ? AND GuildID = 743101101401964647", exp,
                                   ctx.author.id)
                        reward = f"경험치 {eg} (현재 경험치 {exp})"
                    else:
                        xpboost = xpboost + 0.02
                        db.execute("UPDATE exp SET XPBoost = ? WHERE UserID = ? AND GuildID = 743101101401964647",
                                   xpboost,
                                   ctx.author.id)
                        reward = f"경험치 부스트 2%p...? (현재 경부 {xpboost})"
                if randint(1, 10) == 1:
                    fer = fer + 1
                    db.execute("UPDATE games SET zf = ? WHERE UserID = ?", fer, ctx.author.id)
                    reward = f"\n비료를 획득했다! (현재 남은 비료 {fer})"
            embed = Embed(color=0x00ff7f, title="잡초에게 물을 주었다.")
            embed.add_field(name="잡초 레벨", value=f"{int(level)} -> {int(afterlevel)}")
            if ctx.guild.id != 743101101401964647:
                embed.set_footer(text="공식서버에서 명령어를 실행해 더 많은 보상을 가져가세요 (2.5배)")
            if int(level) >= 300:
                l = grant_check("나무를 키우는 자", ctx.author.id)
                if l == 1:
                    await grant(ctx, "나무를 키우는 자", "잡초키우기 명령어에서 잡초 레벨 300을 달성하세요")
                    mv = self.bot.get_guild(743101101401964647)
                    await mv.get_member(ctx.author.id).add_roles(mv.get_role(819414894038089738))
            if int(level) >= 1000:
                l = grant_check("내일지구가멸망해도나무를키우겠다", ctx.author.id)
                if l == 1:
                    await grant(ctx, "내일지구가멸망해도나무를키우겠다", "잡초키우기 명령어에서 잡초 레벨 1000을 달성하세요")
                    mv = self.bot.get_guild(743101101401964647)
                    await mv.get_member(ctx.author.id).add_roles(mv.get_role(848710492356739073))
            if int(level) >= 10000:
                l = grant_check("드루이드", ctx.author.id)
                if l == 1:
                    await grant(ctx, "드루이드", "잡초키우기 명령어에서 잡초 레벨 10000을 달성하세요")
                    mv = self.bot.get_guild(743101101401964647)
                    await mv.get_member(ctx.author.id).add_roles(mv.get_role(901680973916307497))
            embed.add_field(name="잡초 성장 진행도", value=growth_text, inline=False)
            embed.add_field(name="받은 보상", value=reward, inline=False)
            embed.set_thumbnail(url=thumb)
            await send(ctx, embed=embed)
        db.commit()

    async def explore(self, ctx, location, lid, thumb):
        author = convert_ctx(ctx)
        explore_level = db.record("SELECT explore_level FROM games WHERE UserID = ?", author.id)
        explore_level = explore_level[0]
        money, exp, XPBoost = db.record(
            "SELECT Money, XP, XPBoost FROM exp WHERE UserID = ? AND GuildID = 743101101401964647",
            author.id)
        level_to_up = round(math.sqrt(explore_level * 0.5) * random())
        explore_level = explore_level + level_to_up
        db.execute("UPDATE games SET explore_level = ? WHERE UserID = ?", explore_level, author.id)
        embed = Embed(color=0x4849c3)
        if level_to_up == 0:
            embed.add_field(name=f"{author.display_name}\n{location} 탐험 결과", value=f"탐험 레벨: {explore_level}",
                            inline=False)
        else:
            embed.add_field(name=f"{author.display_name}\n{location} 탐험 결과", value=f"탐험 레벨: {explore_level} 로 증가!",
                            inline=False)
        i = randint(1, 351)
        if i < 320:
            money_to_add = round(lid * (uniform(3, 4.2)))
            if ctx.guild.id != 743101101401964647:
                money_to_add = int(money_to_add / 2.5)
                embed.set_footer(text="공식서버에서 명령어를 실행해 더 많은 보상을 가져가세요 (2.5배)")
            db.execute("UPDATE exp SET Money = ? WHERE UserID = ? AND GuildID = 743101101401964647",
                       money + money_to_add, author.id)
            embed.add_field(name="획득한 보상", value=f"돈 +{money_to_add}")
        elif i != 351:
            eg = round(lid * (lid ** 0.33) * 0.3)
            if ctx.guild.id != 743101101401964647:
                eg = int(eg / 2.5)
                embed.set_footer(text="공식서버에서 명령어를 실행해 더 많은 보상을 가져가세요 (2.5배)")
            db.execute("UPDATE exp SET XP = ? WHERE UserID = ? AND GuildID = 743101101401964647",
                       exp + eg, author.id)
            embed.add_field(name="획득한 보상", value=f"경험치 +{round(lid * (lid ** 0.33) * 0.3)}")
        else:
            db.execute("UPDATE exp SET XPBoost = ? WHERE UserID = ? AND GuildID = 743101101401964647", XPBoost + 0.02,
                       author.id)
            embed.add_field(name="획득한 보상", value="경험치 부스트 +2%p")
        if location == "도감" and randint(1, 90) == 1:
            l = grant_check("여긴 지역 아닌데?", author.id)
            if l == 1:
                await grant(ctx, "여긴 지역 아닌데?", "우주탐험을 돌리던 중 도감을 잠금해제 하세요 (실제로 잠금해제되는 건 채널은 아니고 도전과제입니다!)")
        elif 11 < lid < 69 and randint(1, 90) == 1:
            if lid == 12:
                await self.bot.get_channel(797358463725994014).set_permissions(author, read_messages=True)
            elif lid == 13:
                await self.bot.get_channel(816311528906031174).set_permissions(author, read_messages=True)
            elif lid == 14:
                await self.bot.get_channel(816313818677510155).set_permissions(author, read_messages=True)
            elif lid == 15:
                await self.bot.get_channel(816312247210082324).set_permissions(author, read_messages=True)
            elif lid == 16:
                await self.bot.get_channel(816304199405928508).set_permissions(author, read_messages=True)
            elif lid == 17:
                await self.bot.get_channel(797358965218213888).set_permissions(author, read_messages=True)
            elif lid == 18:
                await self.bot.get_channel(816314241391919144).set_permissions(author, read_messages=True)
            elif lid == 19:
                await self.bot.get_channel(816310659603103745).set_permissions(author, read_messages=True)
            elif lid == 20:
                await self.bot.get_channel(816311041487011840).set_permissions(author, read_messages=True)
            elif lid == 21:
                await self.bot.get_channel(797366179458711573).set_permissions(author, read_messages=True)
            elif lid == 22:
                await self.bot.get_channel(797366192230236180).set_permissions(author, read_messages=True)
            elif lid == 23:
                await self.bot.get_channel(816313536170426369).set_permissions(author, read_messages=True)
            elif lid == 24:
                await self.bot.get_channel(797364032809336842).set_permissions(author, read_messages=True)
            elif lid == 25:
                await self.bot.get_channel(816313127280836648).set_permissions(author, read_messages=True)
            elif lid == 26:
                await self.bot.get_channel(797367513268486154).set_permissions(author, read_messages=True)
            elif lid == 27:
                await self.bot.get_channel(816312660333297724).set_permissions(author, read_messages=True)
            elif lid == 28:
                await self.bot.get_channel(797367536324444170).set_permissions(author, read_messages=True)
            elif lid == 29:
                await self.bot.get_channel(797367813442109440).set_permissions(author, read_messages=True)
            elif lid == 30:
                await self.bot.get_channel(797417099650924594).set_permissions(author, read_messages=True)
            elif lid == 31:
                await self.bot.get_channel(797392100030545970).set_permissions(author, read_messages=True)
            elif lid == 32:
                await self.bot.get_channel(797417424663347200).set_permissions(author, read_messages=True)
            elif lid == 33:
                await self.bot.get_channel(797417867582504981).set_permissions(author, read_messages=True)
            elif lid == 34:
                await self.bot.get_channel(797417975157358632).set_permissions(author, read_messages=True)
            elif lid == 35:
                await self.bot.get_channel(829215126494248960).set_permissions(author, read_messages=True)
            elif lid == 36:
                await self.bot.get_channel(829215527020920862).set_permissions(author, read_messages=True)
            elif lid == 37:
                await self.bot.get_channel(829213747942785054).set_permissions(author, read_messages=True)
            elif lid == 38:
                await self.bot.get_channel(829218499674112011).set_permissions(author, read_messages=True)
            elif lid == 39:
                await self.bot.get_channel(829214662507233291).set_permissions(author, read_messages=True)
            elif lid == 40:
                await self.bot.get_channel(829215683157819392).set_permissions(author, read_messages=True)
            elif lid == 41:
                await self.bot.get_channel(829216095739183124).set_permissions(author, read_messages=True)
            elif lid == 42:
                await self.bot.get_channel(829213194165551104).set_permissions(author, read_messages=True)
            elif lid == 43:
                await self.bot.get_channel(829219600725049374).set_permissions(author, read_messages=True)
            elif lid == 44:
                await self.bot.get_channel(817693910309797898).set_permissions(author, read_messages=True)
            elif lid == 45:
                await self.bot.get_channel(817694204196814888).set_permissions(author, read_messages=True)
            elif lid == 46:
                await self.bot.get_channel(829220245469134904).set_permissions(author, read_messages=True)
            elif lid == 47:
                await self.bot.get_channel(829221259949637652).set_permissions(author, read_messages=True)
            elif lid == 60:
                await self.bot.get_channel(829899588595875900).set_permissions(author, read_messages=True)
            embed.add_field(name="특별 보상", value=f"{location} 채널로 접근할 수 있게 되었어요!")
            l = grant_check("우주 구석구석 탐험해주겠다", author.id)
            if l == 1:
                await grant(ctx, "우주 구석구석 탐험해주겠다", "우주탐험 명령어에서 채널에 접근할 권한을 얻으세요")
        elif lid == 70 and randint(1, 2500) == 1:
            await self.bot.get_channel(1203617615717605407).set_permissions(author, read_messages=True)
            embed.add_field(name="특별 보상", value=f"{location} 채널로 접근할 수 있게 되었어요!")
            l = grant_check("우주 구석구석 탐험해주겠다", author.id)
            if l == 1:
                await grant(ctx, "우주 구석구석 탐험해주겠다", "우주탐험 명령어에서 채널에 접근할 권한을 얻으세요")
        if thumb:
            embed.set_thumbnail(url=thumb)
        await send(ctx, embed=embed)
        if explore_level >= 10000:
            l = grant_check("우주 저 너머로", author.id)
            if l == 1:
                await grant(ctx, "우주 저 너머로", "우주탐험 명령어에서 탐험 레벨 10000을 달성하세요")
                mv = self.bot.get_guild(743101101401964647)
                await mv.get_member(author.id).add_roles(mv.get_role(819414894255276063))
        if explore_level >= 100000:
            l = grant_check("우주 저 끝까지", author.id)
            if l == 1:
                await grant(ctx, "우주 저 끝까지", "우주탐험 명령어에서 탐험 레벨 100000을 달성하세요")
                mv = self.bot.get_guild(743101101401964647)
                await mv.get_member(author.id).add_roles(mv.get_role(848707209969532989))
        db.commit()
        return

    @command(name="우주탐험", aliases=["우탐", 'ㅇㅌ'])
    @cooldown(1, 12, BucketType.user)
    async def utam_normal(self, ctx, activity: Optional[str] = "최대", location: Optional[str] = "최대"):
        await self.exploring_space(ctx, activity, location)

    """@slash(name="우주탐험", description="우주탐험 게임을 실행할 수 있는 명령어. (공식서버 회원만 사용 가능)")
    @cooldown(1, 12, BucketType.user)
    async def utam_slash(self, interaction, 무엇: Optional[str] = "최대", 어디: Optional[str] = "최대"):
        await self.exploring_space(interaction, 무엇, 어디)"""

    async def exploring_space(self, ctx, activity, location):
        author = convert_ctx(ctx)
        if ctx.guild.id != 743101101401964647:
            try:
                print((self.bot.get_guild(743101101401964647)).get_member(author.id).display_name)
            except AttributeError:
                await send(ctx, "공식 커뮤니티 가입자만 사용할 수 있는 기능이에요!")
                return
        thumb = None
        info = db.record("SELECT explore_level, user_setting FROM games WHERE UserID = ?", author.id)
        try:
            explore_level = info[0]
        except TypeError:
            db.execute("INSERT INTO games (UserID, explore_level) VALUES (?, 0)", author.id)
            explore_level = 0
        if isinstance(ctx, Context) and ('ㅇㅌ' in ctx.message.content) and (info[1] & 256 == 0):
            await send(ctx, '어허')
            return
        if explore_level == 0: activity = "튜토리얼"
        if activity == "튜토리얼":
            embed = Embed(color=0x4849c3)
            embed.add_field(name="커뉴봇 우주탐험 튜토리얼",
                            value="`커뉴야 우주탐험`을 입력해서 우주 탐험을 진행할 수 있어요.\n\t\n우주를 탐험하면 공식서버처럼 처음에는 가까운 곳만 탐험할 수 있지만 탐험 레벨이 오르면 더 먼 곳까지 탐험할 수 있게 돼요.\n\t\n우주를 탐험하다 보면 다른 게임들처럼 돈이나 경험치, 낮은 확률로 경험치 부스트를 얻을 수 있어요.\n\t\n그러나 매우 먼 곳을 탐험하게 된다면 아주 낮은 확률로 아직 아무에게도 알려지지 않은 무언가까지 획득할 수도 있어요!\n\t\n탐험을 하다 보면 자동으로 탐험 레벨이 오르니 우주를 개척해 나가 보세요.")
            await send(ctx, embed=embed)
            explore_level = explore_level + 1
            db.execute("UPDATE games SET explore_level = ? WHERE UserID = ?", explore_level, author.id)
            return
        if activity == "도움":
            embed = Embed(color=0x4849c3)
            embed.add_field(name="우주탐험\n버전: 1.0.5",
                            value="<@724496900920705045>의 불타는 의지로 만들어진 게임\n\t\n`커뉴야 우주탐험`: 드넓은 우주를 탐험한다.\n`커뉴야 우주탐험 도감`: 자기에게 잠금 해제된 지역들의 도감을 보여준다.\n`커뉴야 우주탐험 리더보드`: 여러 사람들의 우주탐험 레벨들을 보여준다.\n`커뉴야 우주탐험 도움`: 이 도움말을 표시한다.\n`커뉴야 우주탐험 업데이트`: 최근 업데이트 정보를 확인한다.")
            await send(ctx, embed=embed)
            return
        elif activity == "도감":
            embed = Embed(color=0x4849c3)
            embed.set_footer(text=f"현재 레벨: {explore_level}")
            lid = 0
            location = "1. 달"
            lid += 1
            if 9 < explore_level:
                location += "\n2. 화성: 10레벨 이상"
                lid += 1
            if 49 < explore_level:
                location += "\n3. 수성: 50레벨 이상"
                lid += 1
            if 99 < explore_level:
                location += "\n4. 금성: 100레벨 이상"
                lid += 1
            if 149 < explore_level:
                location += "\n5. 태양: 150레벨 이상"
                lid += 1
            if 199 < explore_level:
                location += "\n6. 목성: 200레벨 이상"
                lid += 1
            if 299 < explore_level:
                location += "\n7. 토성: 300레벨 이상"
                lid += 1
            if 399 < explore_level:
                location += "\n8. 천왕성: 400레벨 이상"
                lid += 1
            if 499 < explore_level:
                location += "\n9. 해왕성: 500레벨 이상"
                lid += 1
            if 599 < explore_level:
                location += "\n10. 카이퍼벨트: 600레벨 이상"
                lid += 1
            if 749 < explore_level:
                location += "\n11. 오르트구름: 750레벨 이상"
                lid += 1
            if 999 < explore_level:
                location += "\n12. 바너드: 1000레벨 이상"
                lid += 1
            if 1499 < explore_level:
                location += "\n13. 로스154: 1500레벨 이상"
                lid += 1
            if 1999 < explore_level:
                location += "\n14. 에리다누스자리엡실론: 2000레벨 이상"
                lid += 1
            if 2499 < explore_level:
                location += "\n15. 로스128: 2500레벨 이상"
                lid += 1
            if 2999 < explore_level:
                location += "\n16. 고래자리타우: 3000레벨 이상"
                lid += 1
            if 3499 < explore_level:
                location += "\n17. 글리제876: 3500레벨 이상"
                lid += 1
            if 3999 < explore_level:
                location += "\n18. 에리다누스자리82: 4000레벨 이상"
                lid += 1
            if 4999 < explore_level:
                location += "\n19. 글리제581: 5000레벨 이상"
                lid += 1
            if 5999 < explore_level:
                location += "\n20. 글리제667: 6000레벨 이상"
                lid += 1
            if 6999 < explore_level:
                location += "\n21. 데네볼라: 7000레벨 이상"
                lid += 1
            if 7999 < explore_level:
                location += "\n22. 레굴루스: 8000레벨 이상"
                lid += 1
            if 8999 < explore_level:
                location += "\n23. 알코르: 9000레벨 이상"
                lid += 1
            if 9999 < explore_level:
                location += "\n24. k2-18b: 10000레벨 이상"
                lid += 1
            if 11999 < explore_level:
                location += "\n25. 아케르나르: 12000레벨 이상"
                lid += 1
            if 13999 < explore_level:
                location += "\n26. 스피카: 14000레벨 이상"
                lid += 1
            if 15999 < explore_level:
                location += "\n27. 미라: 16000레벨 이상"
                lid += 1
            if 17999 < explore_level:
                location += "\n28. 플레이아데스성단: 18000레벨 이상"
                lid += 1
            if 19999 < explore_level:
                location += "\n29. 민타카: 20000레벨 이상"
                lid += 1
            if 22499 < explore_level:
                location += "\n30. 캣츠아이성운: 22500레벨 이상"
                lid += 1
            if 24999 < explore_level:
                location += "\n31. 큰개자리vy: 25000레벨 이상"
                lid += 1
            if 27499 < explore_level:
                location += "\n32. 장미성운: 27500레벨 이상"
                lid += 1
            if 29999 < explore_level:
                location += "\n33. 방패자리uy: 30000레벨 이상"
                lid += 1
            if 34999 < explore_level:
                location += "\n34. 삼렬성운: 35000레벨 이상"
                lid += 1
            if 39999 < explore_level:
                location += "\n35. 보데은하: 40000레벨 이상"
                lid += 1
            if 44999 < explore_level:
                location += "\n36. 고양이눈은하: 45000레벨 이상"
                lid += 1
            if 49999 < explore_level:
                location += "\n37. 검은눈은하: 50000레벨 이상"
                lid += 1
            if 59999 < explore_level:
                location += "\n38. 사자자리은하군: 60000레벨 이상"
                lid += 1
            if 69999 < explore_level:
                location += "\n39. 고래자리A은하: 70000레벨 이상"
                lid += 1
            if 79999 < explore_level:
                location += "\n40. 처녀자리A은하: 80000레벨 이상"
                lid += 1
            if 89999 < explore_level:
                location += "\n41. 머리털바람개비은하: 90000레벨 이상"
                lid += 1
            if 99999 < explore_level:
                location += "\n42. M91: 100000레벨 이상"
                lid += 1
            if 109999 < explore_level:
                location += "\n43. 공기펌프자리은하단: 110000레벨 이상"
                lid += 1
            if 119999 < explore_level:
                location += "\n44. IC1101: 120000레벨 이상"
                lid += 1
            if 129999 < explore_level:
                location += "\n45. 3C273: 130000레벨 이상"
                lid += 1
            if 139999 < explore_level:
                location += "\n46. 바다뱀자리센타우르스자리초은하단: 140000레벨 이상"
                lid += 1
            if 149999 < explore_level:
                location += "\n47. 물고기자리고래자리복합초은하단: 150000레벨 이상"
                lid += 1
            if 199999 < explore_level:
                location += "\n48. Metaverse: 200000레벨 이상"
                lid += 1
                embed.set_footer(text="축하드려요! 모든 지역을 여셨네요")
            if 19999999 < explore_level:
                lid += 10
            embed.add_field(name=f"{author.display_name}의 우주탐험 도감", value=location)
            await send(ctx, embed=embed)
            await self.explore(ctx, "도감", lid, None)
        elif activity == "최근업뎃":
            embed = Embed(color=0x4849c3)
            embed.add_field(name="우주탐험 1.0.6 업데이트", value="직접 찾아보세요!")
        elif activity == "리더보드":
            if location == "최대": location = 1
            records = db.records(
                "SELECT UserID, explore_level FROM games WHERE explore_level != 0 ORDER BY explore_level DESC LIMIT ?, ?",
                10 * int(location) - 10, 10)
            tjfaud = ""
            now_people = 10 * int(location) - 9
            for record in records:
                tjfaud = tjfaud + f"{now_people}. <@{record[0]}> (탐험 레벨: {record[1]}) \n"
                now_people += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 사람이 없는 것 같아요!"
            await send(ctx, embed=Embed(color=0x4849c3, title="우주탐험 랭킹!", description=tjfaud))
        else:
            if randint(1, 40) == 1:
                num = randint(10000, 99999)
                await send(ctx, f"매크로 방지를 위해 확인을 할게요. 10초 안에 어디든 좋으니 커뉴봇이 볼 수 있는 곳에{num}이라고 보내 주세요.")
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        timeout=10,
                        check=lambda message: message.author == author and message.content == str(num)
                    )
                except asyncio.TimeoutError:
                    await send(ctx, ":weary:")
                    await self.ban_10min(author.id)
                    return
                if msg.content != str(num):
                    await send(ctx, ":weary:")
                    await self.ban_10min(author.id)
                    return
            location = activity
            if explore_level < 10 and location == "최대" or location == "달":
                location = "달"
                lid = 1
                thumb = "https://cdn.discordapp.com/attachments/749224990209212419/899645452088139796/560cae6aee73c92e93fa98f60f389542c647386fd319ea36220e74c153e3e80df2e95c6a835227307077107603e0938bb02f.png"
            if (9 < explore_level < 50 and location == "최대") or (explore_level > 9 and location == "화성"):
                location = "화성"
                lid = 2
                thumb = "https://cdn.discordapp.com/attachments/749224990209212419/899645685492768789/9k.png"
            if (49 < explore_level < 100 and location == "최대") or (explore_level > 49 and location == "수성"):
                location = "수성"
                lid = 3
                thumb = "https://cdn.discordapp.com/attachments/749224990209212419/899645584955277332/9k.png"
            if (99 < explore_level < 150 and location == "최대") or (explore_level > 99 and location == "금성"):
                location = "금성"
                lid = 4
                thumb = "https://cdn.discordapp.com/attachments/749224990209212419/899645886630596719/9k.png"
            if (149 < explore_level < 200 and location == "최대") or (explore_level > 150 and location == "태양"):
                location = "태양"
                lid = 5
                thumb = "https://cdn.discordapp.com/attachments/749224990209212419/899645960249020466/9k.png"
            if (199 < explore_level < 300 and location == "최대") or (explore_level > 199 and location == "목성"):
                location = "목성"
                lid = 6
                thumb = "https://cdn.discordapp.com/attachments/749224990209212419/899646095213334548/Z.png"
            if (299 < explore_level < 400 and location == "최대") or (explore_level > 299 and location == "토성"):
                location = "토성"
                lid = 7
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899646193183903794/9k.png'
            if (399 < explore_level < 500 and location == "최대") or (explore_level > 399 and location == "천왕성"):
                location = "천왕성"
                lid = 8
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899646286301638737/Z.png'
            if (499 < explore_level < 600 and location == "최대") or (explore_level > 499 and location == "해왕성"):
                location = "해왕성"
                lid = 9
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899646359290912830/9k.png'
            if (599 < explore_level < 750 and location == "최대") or (explore_level > 599 and location == "카이퍼벨트"):
                location = "카이퍼 벨트"
                lid = 10
            if (749 < explore_level < 1000 and location == "최대") or (explore_level > 749 and location == "오르트구름"):
                location = "오르트 구름"
                lid = 11
            if (999 < explore_level < 1500 and location == "최대") or (explore_level > 999 and location == "바너드"):
                location = "바너드"
                lid = 12
                thumb = "https://cdn.discordapp.com/attachments/773409630125817887/899646568746082304/2Q.png"
            if (1499 < explore_level < 2000 and location == "최대") or (explore_level > 1499 and location == "로스154"):
                location = "로스154"
                lid = 13
                thumb = 'https://cdn.discordapp.com/attachments/773409630125817887/899646684143968316/Z.png'
            if (1999 < explore_level < 2500 and location == "최대") or (
                    explore_level > 1999 and location == "에리다누스자리엡실론"):
                location = "에리다누스자리엡실론"
                lid = 14
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899647477500764170/9k.png'
            if (2499 < explore_level < 3000 and location == "최대") or (explore_level > 2499 and location == "로스128"):
                location = "로스128"
                lid = 15
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899647662545063976/Z.png'
            if (2999 < explore_level < 3500 and location == "최대") or (explore_level > 2999 and location == "고래자리타우"):
                location = "고래자리타우"
                lid = 16
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899648893476806676/ED8380EC9AB0EBB384.png'
            if (3499 < explore_level < 4000 and location == "최대") or (explore_level > 3499 and location == "글리제876"):
                location = "글리제876"
                lid = 17
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899649033541419048/Z.png'
            if (3999 < explore_level < 5000 and location == "최대") or (explore_level > 3999 and location == "에리다누스자리82"):
                location = "에리다누스자리82"
                lid = 18
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899649162671427614/Z.png'
            if (4999 < explore_level < 6000 and location == "최대") or (explore_level > 4999 and location == "글리제581"):
                location = "글리제581"
                lid = 19
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899649448995590154/9k.png'
            if (5999 < explore_level < 7000 and location == "최대") or (explore_level > 5999 and location == "글리제667"):
                location = "글리제667"
                lid = 20
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899649574912802836/9k.png'
            if (6999 < explore_level < 8000 and location == "최대") or (explore_level > 6999 and location == "데네볼라"):
                location = "데네볼라"
                lid = 21
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899649940299599922/9k.png'
            if (7999 < explore_level < 9000 and location == "최대") or (explore_level > 7999 and location == "레굴루스"):
                location = "레굴루스"
                lid = 22
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899650072386605076/64acb76ffaf4ef74cfba2d6749dfb2910ed05496bf0b285eb5cda8cef749751c29276b7e1f3b30e95e690080039798c96e7a.png'
            if (8999 < explore_level < 10000 and location == "최대") or (explore_level > 8999 and location == "알코르"):
                location = "알코르"
                lid = 23
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899650167551164426/9k.png'
            if (9999 < explore_level < 12000 and location == "최대") or (explore_level > 9999 and location == "k2-18b"):
                location = "k2-18b"
                lid = 24
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899650258882138182/2Q.png'
            if (11999 < explore_level < 14000 and location == "최대") or (explore_level > 11999 and location == "아케르나르"):
                location = "아케르나르"
                lid = 25
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899650472355438592/9k.png'
            if (13999 < explore_level < 16000 and location == "최대") or (explore_level > 13999 and location == "스피카"):
                location = "스피카"
                lid = 26
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899650616845008896/2Q.png'
            if (15999 < explore_level < 18000 and location == "최대") or (explore_level > 15999 and location == "미라"):
                location = "미라"
                lid = 27
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899650705126744104/2Q.png'
            if (17999 < explore_level < 20000 and location == "최대") or (
                    explore_level > 17999 and location == "플레이아데스성단"):
                location = "플레이아데스성단"
                lid = 28
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899650819970990090/Z.png'
            if (19999 < explore_level < 22500 and location == "최대") or (explore_level > 19999 and location == "민타카"):
                location = "민타카"
                lid = 29
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899650889806131200/Z.png'
            if (22499 < explore_level < 25000 and location == "최대") or (explore_level > 22499 and location == "캣츠아이성운"):
                location = "캣츠아이성운"
                lid = 30
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899650958307500052/2Q.png'
            if (24999 < explore_level < 27500 and location == "최대") or (explore_level > 24999 and location == "큰개자리vy"):
                location = "큰개자리vy"
                lid = 31
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899651172078587944/Z.png'
            if (27499 < explore_level < 30000 and location == "최대") or (explore_level > 27499 and location == "장미성운"):
                location = "장미성운"
                lid = 32
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899651313850257428/2Q.png'
            if (29999 < explore_level < 35000 and location == "최대") or (explore_level > 29999 and location == "방패자리uy"):
                location = "방패자리uy"
                lid = 33
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899651406804418570/Z.png'
            if (34999 < explore_level < 40000 and location == "최대") or (explore_level > 34999 and location == "삼렬성운"):
                location = "삼렬성운"
                lid = 34
                thumb = 'https://cdn.discordapp.com/icons/743101101401964647/3b165fc7ac8f1a15f15696f3ece4a14b.webp?size=1024'
            if (39999 < explore_level < 45000 and location == "최대") or (explore_level > 39999 and location == "보데은하"):
                location = "보데은하"
                lid = 35
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899651522386866206/Z.png'
            if (44999 < explore_level < 50000 and location == "최대") or (explore_level > 44999 and location == "고양이눈은하"):
                location = "고양이눈은하"
                lid = 36
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899651608177176616/9k.png'
            if (49999 < explore_level < 60000 and location == "최대") or (explore_level > 49999 and location == "검은눈은하"):
                location = "검은눈은하"
                lid = 37
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899651678356271164/9k.png'
            if (59999 < explore_level < 70000 and location == "최대") or (
                    explore_level > 59999 and location == "사자자리은하군"):
                location = "사자자리은하군"
                lid = 38
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899651986427899974/2Q.png'
            if (69999 < explore_level < 80000 and location == "최대") or (
                    explore_level > 69999 and location == "고래자리A은하"):
                location = "고래자리A은하"
                lid = 39
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899652059194859520/9k.png'
            if (79999 < explore_level < 90000 and location == "최대") or (
                    explore_level > 79999 and location == "처녀자리A은하"):
                location = "처녀자리A은하"
                lid = 40
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899652503069671424/9k.png'
            if (89999 < explore_level < 100000 and location == "최대") or (
                    explore_level > 89999 and location == "머리털바람개비은하"):
                location = "머리털바람개비은하"
                lid = 41
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899652608568991744/2Q.png'
            if (99999 < explore_level < 110000 and location == "최대") or (explore_level > 99999 and location == "M91"):
                location = "M91"
                lid = 42
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899652728098283560/9k.png'
            if (109999 < explore_level < 120000 and location == "최대") or (
                    explore_level > 109999 and location == "공기펌프자리은하단"):
                location = "공기펌프자리은하단"
                lid = 43
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899653016867708978/Z.png'
            if (119999 < explore_level < 130000 and location == "최대") or (
                    explore_level > 119999 and location == "IC1101"):
                location = "IC1101"
                lid = 44
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899653117623275550/Z.png'
            if (129999 < explore_level < 140000 and location == "최대") or (
                    explore_level > 129999 and location == "3C273"):
                location = "3C273"
                lid = 45
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899653242391240744/300px-Best_image_of_bright_quasar_3C_273.png'
            if (139999 < explore_level < 150000 and location == "최대") or (
                    explore_level > 139999 and location == "바다뱀자리센타우르스자리초은하단"):
                location = "바다뱀자리센타우르스자리초은하단"
                lid = 46
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899653396687122482/400px-Hyamap.png'
            if (149999 < explore_level < 200000 and location == "최대") or (
                    explore_level > 149999 and location == "물고기자리고래자리복합초은하단"):
                location = "물고기자리고래자리복합초은하단"
                lid = 47
                thumb = 'https://cdn.discordapp.com/attachments/749224990209212419/899653561569390633/9k.png'
            if (199999 < explore_level < 20000000 and location == "최대") or (
                    explore_level > 199999 and location == "Metaverse"):
                location = "Metaverse"
                lid = 60
            if (19999999 < explore_level and location == "최대") or (
                    explore_level > 199999 and location == "Beyond Metaverse"):
                location = "Beyond Metaverse"
                lid = 70
            try:
                await self.explore(ctx, location, lid, thumb if thumb else None)
            except UnboundLocalError:
                await send(ctx, "뭘 할려고 하는 거에요?")

    @command(name='색깔')
    async def display_color(self, ctx, c: Optional[str]):
        if not c:
            await send(ctx, "`커뉴야 색깔 (색상코드)`로 입력해주세요!\n가능한 형식 (원하는 색이 ffd6fe라고 가정하면): #ffd6fe, 0xffd6fe, ffd6fe")
            return
        if c[0] == '#':
            c_ = c[1:]
        elif c.startswith('0x'):
            c_ = c[2:]
        else:
            c_ = c
        if len(c_) != 6:
            await send(ctx, '올바르지 않은 입력이에요!')
            return
        try:
            color = tuple(int(c_[i:i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            await send(ctx, '올바르지 않은 입력이에요!')
            return

        def create_colored_image(col, width=128, height=128):
            # Create a new image with RGB mode
            im = Image.new("RGB", (width, height), col)

            # Save the image (you can also display it using img.show())
            im.save(u := r"C:\Users\namon\PycharmProjects\discordbot\lib\images\color.png")
            return u

        u = create_colored_image(color)
        await send(ctx, file=File(u))

    @command(name="입력해")
    async def typin(self, ctx):
        with ctx.channel.typing():
            await asyncio.sleep(0.1)

    async def ban_10min(self, user):
        self.bot.banlist.extend([user])
        await self.bot.get_channel(744923718245154926).send(
            embed=Embed(color=0xffd6fe, title="매크로방지로 10분 정지됨", description=f"정지된 유저: {str(self.bot.get_user(user))}"))
        await sleep(600)
        self.bot.banlist.remove(user)
        await self.bot.get_channel(744923718245154926).send(
            embed=Embed(color=0xffd6fe, title="정지가 풀림", description=f"풀린 유저: {str(self.bot.get_user(user))}"))

    @command(name="기원목록")
    @cooldown(1, 10, BucketType.user)
    async def display_giwon_list(self, ctx, where: Optional[str] = "전체", criteria: Optional[str] = "랜덤"):
        embed = Embed(color=ctx.author.color)
        tjfaud = ""
        if where in ['신규', '오늘기원됨', '오랫동안기원됨']:
            criteria = where
            where = '전체'
        if where == "서버":
            guild_giwons = db.records("SELECT Giwon_name, TargetID, days FROM Giwons WHERE GuildID = ?", ctx.guild.id)
            if not guild_giwons:
                embed.add_field(name=f"{ctx.guild.name}의 기원 목록", value="없음!")
                await send(ctx, embed=embed)
                return
            for giwon in guild_giwons:
                tjfaud += f"{self.bot.get_user(giwon[1])}에게 기원되고 있는 {giwon[0]} ({giwon[2]}일차)\n"
            embed.add_field(name=f"{ctx.guild.name}의 기원 목록", value=tjfaud)
            await send(ctx, embed=embed)
        elif where == "전체":
            setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
            if setting & 16 == 0:
                criteria = '랜덤'
            if criteria == "랜덤":
                whole_giwons = db.records(
                    "SELECT Giwon_name, days FROM Giwons WHERE GuildID = 0 ORDER BY RANDOM() LIMIT 20")
            elif criteria == '신규':
                whole_giwons = db.records(
                    "SELECT Giwon_name, days FROM Giwons WHERE GuildID = 0 ORDER BY last_giwon_date DESC LIMIT 20")
            elif criteria == "오늘기원됨":
                whole_giwons = db.records(
                    "SELECT Giwon_name, days FROM Giwons WHERE GuildID = 0 AND last_giwon_date = ?", today)
            elif criteria == "오랫동안기원됨":
                whole_giwons = db.records(
                    "SELECT Giwon_name, days FROM Giwons WHERE GuildID = 0 ORDER BY days DESC LIMIT 20")
            else:
                await send(ctx, "존재하지 않는 정렬 기준이에요!")
                return
            for giwon in whole_giwons:
                tjfaud += f"{giwon[0]} {giwon[1]}일차\n"
            embed.add_field(name="전체 기원 목록", value=tjfaud)
            await send(ctx, embed=embed)
        else:
            await send(ctx, "`커뉴야 기원목록 <전체/서버/신규/오늘기원됨/오랫동안기원됨>`")

    @command(name="퀴즈")
    @cooldown(1, 5, BucketType.user)
    async def quiz_game(self, ctx, activity: Optional[str] = "도움", *, wanted_subject: Optional[str] = ""):
        if activity == "도움":
            await send(ctx, embed=Embed(color=0xfeff81, title="커뉴봇 퀴즈 기능 도움!",
                                       description="<@704342782826774648>의 아이디어를 바탕으로 <@724496900920705045>가 개발한 커뉴봇 퀴즈게임이에요!\n`커뉴야 퀴즈 도움`: 이 도움말을 표시해요.\n`커뉴야 퀴즈 출제`: 내고 싶은 퀴즈를 낼 수 있어요. 다만 이상한 퀴즈는 안 되기 때문에 등록까지 시간이 좀 걸릴 수 있어요.\n`커뉴야 퀴즈 풀기`: 다른 사람이 낸 퀴즈를 도전할 수 있어요.\n`커뉴야 퀴즈 주제`: 특정한 주제에 문제 수가 몇 개인지 확인해요.\n`커뉴야 퀴즈 뮤트`: `커뉴야 퀴즈 풀기`에서 주제를 입력하지 않았을 때 피할 주제를 설정할 수 있어요.\n`커뉴야 퀴즈 목록`: 풀 수 있는 주요주제들의 목록을 표시해요\n`커뉴야 퀴즈 신고`: `커뉴야 퀴즈 신고 (코드)`로 문제를 신고할 수 있어요.\n`커뉴야 퀴즈 내문제`: 현재까지 등록된 문제 중 자신이 낸 문제들을 확인하고 잘못된 문제를 수정하는 등의 행동을 할 수 있어요."))
        elif activity == "출제":
            if isinstance(ctx.channel, DMChannel):
                await send(ctx, "개인 메세지에서는 출제 기능을 이용할 수 없어요!")
                return
            if wanted_subject:
                subject = wanted_subject
            else:
                await send(ctx, "무엇과 관련된 퀴즈인가요?")
                try:
                    subject = await self.bot.wait_for(
                        "message",
                        timeout=30,
                        check=lambda
                            message: message.author.id == ctx.author.id and message.channel.id == ctx.channel.id
                    )
                except asyncio.TimeoutError:
                    await send(ctx, "퀴즈를 출제하지 않기로 했어요.")
                    return
                subject = subject.content
            await send(ctx, "퀴즈를 내 주세요! 정답이 하나만 나오게 내 주세요.")
            try:
                quiz = await self.bot.wait_for(
                    "message",
                    timeout=90,
                    check=lambda message: message.author.id == ctx.author.id and message.channel.id == ctx.channel.id
                )
            except asyncio.TimeoutError:
                await send(ctx, "퀴즈를 출제하지 않기로 했어요.")
                return
            quiz = quiz.content
            await send(ctx, "퀴즈의 정답을 말해 주세요!")
            try:
                answer = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda message: message.author.id == ctx.author.id and message.channel.id == ctx.channel.id
                )
            except asyncio.TimeoutError:
                await send(ctx, "퀴즈를 출제하지 않기로 했어요.")
                return
            await answer.delete()
            answer = answer.content
            await send(ctx, "퀴즈 출제 등록을 완료했어요!")
            quiz_code = ""
            for i in range(10): quiz_code += choice(
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "a", "b", "c", "A", "B", "q", "w", "e", "r", "t",
                 "y", "u", "i", "o", "p", "s", "d", "f", "g", "h", "j", "k", "l", "z", "x", "v", "n", "m", "Q", "W",
                 "E", "R", "T", "Y", "U", "I", "O", "P", "S", "D", "F", "G", "H", "J", "K", "L", "Z", "X", "C", "V",
                 "N", "M"])
            await self.bot.get_channel(819810253658521611).send(
                f"퀴즈 등록 요청: 코드 {quiz_code}\n출제자: {str(ctx.author)} (아이디 {ctx.author.id})\n주제: {subject}\n내용: {quiz}\n정답: {answer}")
            db.execute("INSERT INTO quiz_temp (content, subject, answer, maker, code) VALUES (?, ?, ?, ?, ?)", quiz,
                       subject, answer, ctx.author.id, quiz_code)
            db.commit()
        elif activity == "풀기":
            if ',' in wanted_subject:
                check = db.record("SELECT user_setting FROM games WHERE UseriD = ?", ctx.author.id)[0] & 8192
                if not check:
                    await send(ctx, '`커뉴야 뀨 구매 퀴즈 주제 다중 선택`')
                    return
            embed = Embed(color=0xfeff81, title="커뉴봇 퀴즈")
            quiz_mmr = db.record("SELECT quiz_mmr FROM games WHERE UserID = ?", ctx.author.id)
            try:
                quiz_mmr = quiz_mmr[0]
            except TypeError:
                db.execute("INSERT INTO games (UserID) VALUES (?)", ctx.author.id)
                quiz_mmr = 0
            if not wanted_subject:
                mute_subject = db.record("SELECT quiz_mute FROM games WHERE UserID = ?", ctx.author.id)
                quiz_to_solve = db.record("SELECT * FROM quiz ORDER BY RANDOM() LIMIT 1")
                if quiz_to_solve[1] == mute_subject[0]:
                    return await self.quiz_game(ctx=ctx, activity=activity)
                quiz_count = db.record("SELECT count(*) FROM quiz")
                quiz_count = quiz_count[0]
            else:
                if ',' in wanted_subject:
                    wanted_subject = [*map(lambda s: s.strip(), wanted_subject.split(','))]
                    or_text = ' OR '.join([f'quiz_subject = "{ws}"' for ws in wanted_subject])
                    quiz_count = db.record(f"SELECT count(*) FROM quiz WHERE {or_text}")[0]
                    if quiz_count < 10 or set(wanted_subject) & {'그대로적기', '그대로쓰세요'}:
                        await send(ctx, "그 주제 세트는 아직 문제가 너무 적어요! 주제를 바꾸거나 후보 주제를 추가해 주세요")
                        return
                    quiz_to_solve = db.record(f"SELECT * FROM quiz WHERE {or_text} ORDER BY RANDOM() LIMIT 1")
                else:
                    quiz_count = db.record("SELECT count(*) FROM quiz WHERE quiz_subject = ?", wanted_subject)[0]
                    if quiz_count < 10 or wanted_subject in ['그대로적기', '그대로쓰세요']:
                        await send(ctx, "그 주제는 아직 문제가 너무 적어요! 다른 주제로 골라 주세요")
                        return
                    quiz_to_solve = db.record("SELECT * FROM quiz WHERE quiz_subject = ? ORDER BY RANDOM() LIMIT 1",
                                              wanted_subject)
                if not quiz_to_solve:
                    await send(ctx, "이 메세지가 나왔다면 바로 문의해주세요. 비상!!!!!!!!!!!!!")
                    return
            result = 0
            for i in range(2000):
                result += simulate_quiz(10, quiz_count)
            result /= 2000
            try:
                correct_rate = quiz_to_solve[4] / (quiz_to_solve[4] + quiz_to_solve[5])
            except ZeroDivisionError:
                correct_rate = 0.5
            mmrdelta = round(400 * (0.0625 ** correct_rate))
            embed.add_field(name=f"{quiz_to_solve[1]} 와(과) 관련된 퀴즈!", value=quiz_to_solve[0], inline=False)
            embed.add_field(name=f"퀴즈 세부 정보",
                            value=f"{str(self.bot.get_user(quiz_to_solve[2]))}의 퀴즈\n 제한시간 5분\n정답률 {round(correct_rate * 100, 3)}% ({quiz_to_solve[4] + quiz_to_solve[5]}번 중 {quiz_to_solve[4]}번 정답이 입력됨)\n맞으면 얻는 점수: {mmrdelta}, 틀리면 잃는 점수: {round(2500 / mmrdelta) + 5}",
                            inline=False)
            embed.set_footer(
                text=f"퀴즈 풀기 명령어를 10번 돌릴 경우 중복이 뜰 가능성이 약 {round(100 * result, 2)}% 정도에요.\n중복이 안 뜰 만큼만 풀어주세요.")
            await send(ctx, embed=embed)
            try:
                search_string = await self.bot.wait_for(
                    "message",
                    timeout=300,
                    check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
                )
                answer = search_string.content
            except asyncio.TimeoutError:
                answer = ""
                await send(ctx, "제한시간 초과!")
                l = grant_check("잠수의 제왕", ctx.author.id)
                if l == 1:
                    await grant(ctx, "잠수의 제왕", "퀴즈 명령어에서 시간초과로 문제를 틀리세요")
            embed = Embed(color=0xfeff81)
            if answer.lower() == quiz_to_solve[3].lower():
                quiz_mmr += mmrdelta
                embed.add_field(name="정답!", value=f"퀴즈 점수: {quiz_mmr - mmrdelta} -> {quiz_mmr}")
                await send(ctx, embed=embed)
                if quiz_mmr >= 40000:
                    l = grant_check("능지떡상", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "능지떡상", "퀴즈 명령어에서 퀴즈 점수 40000점을 달성하세요")
                        try:
                            mv = self.bot.get_guild(743101101401964647)
                            await mv.get_member(ctx.author.id).add_roles(mv.get_role(824203786532814948))
                        except:
                            pass
                if quiz_mmr >= 100000:
                    l = grant_check("능지개떡상", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "능지개떡상", "퀴즈 명령어에서 퀴즈 점수 100000점을 달성하세요")
                if 0 < correct_rate <= 0.04:
                    l = grant_check("능지 1등급", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "능지 1등급", "퀴즈 명령어에서 정답률이 0%는 아니지만 4% 이하인 문제를 맞히세요")
                    try:
                        mv = self.bot.get_guild(743101101401964647)
                        await mv.get_member(ctx.author.id).add_roles(mv.get_role(825208406004334632))
                    except:
                        pass
                db.execute("UPDATE games SET quiz_mmr = ? WHERE UserID = ?", quiz_mmr, ctx.author.id)
                db.execute("UPDATE quiz SET correct_answers =  correct_answers + 1 WHERE quizid = ?", quiz_to_solve[6])
                db.commit()
            else:
                quiz_mmr -= round((2500 / mmrdelta) + 5)
                embed.add_field(name="오답...", value=f"퀴즈 점수: {quiz_mmr + round((2500 / mmrdelta) + 5)} -> {quiz_mmr}")
                embed.set_footer(text=f"`커뉴야 퀴즈 신고 {quiz_to_solve[6]}`으로 이 문제를 신고하세요")
                await send(ctx, embed=embed)
                if 0.96 <= correct_rate < 1:
                    l = grant_check("능지 9등급", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "능지 9등급", "퀴즈 명령어에서 정답률이 100%는 아니지만 96% 이상인 문제를 틀리세요")
                db.execute("UPDATE games SET quiz_mmr = ? WHERE UserID = ?", quiz_mmr, ctx.author.id)
                db.execute("UPDATE quiz SET wrong_answers =  wrong_answers + 1 WHERE quizid = ?", quiz_to_solve[6])
                db.commit()
        elif activity == "신고":
            if not wanted_subject:
                await send(ctx, "`커뉴야 퀴즈 신고 (코드)`로 신고해 주세요")
                return
            q = db.record("SELECT * FROM quiz WHERE quizid = ?", wanted_subject)
            try:
                await send(ctx, f"{q[1]} 주제의 퀴즈로, 내용은 {q[0]}(이)에요.\n이 퀴즈를 신고하시겠습니까? 추가로 할 말이 있다면 말하거나 `취소`라고 입력해 취소하세요")
            except TypeError:
                await send(ctx, "존재하지 않는 퀴즈 코드에요!")
                return
            try:
                search_string = await self.bot.wait_for(
                    "message",
                    timeout=60,
                    check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
                )
                m = search_string.content
            except asyncio.TimeoutError:
                await send(ctx, "신고하지 않기로 했어요.")
                return
            if m == "취소":
                await send(ctx, "신고하지 않기로 했어요.")
                return
            else:
                await self.bot.get_channel(819810391647322122).send(
                    f"{str(ctx.author)}님이 퀴즈를 신고함\n퀴즈 정보 및 mmrdelta \n{q} {q[2]} {q} 할말 {m}")
                await send(ctx, "신고가 성공적으로 접수됐어요!")
        elif activity == "내점수":
            quiz_mmr = db.record("SELECT quiz_mmr FROM games WHERE UserID = ?", ctx.author.id)
            ids = db.records("SELECT quiz_mmr FROM games WHERE quiz_mmr IS NOT NULL ORDER BY quiz_mmr DESC")
            my_rank = ids.index(quiz_mmr) + 1
            embed = Embed(color=0xfeff81, title=f"{ctx.author.display_name}의 퀴즈 정보")
            embed.add_field(name="퀴즈 점수", value=str(int(quiz_mmr[0])), inline=False)
            embed.add_field(name="퀴즈 등수", value=my_rank, inline=False)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            await send(ctx, embed=embed)
        elif activity == "주제":
            if not wanted_subject:
                await send(ctx, "`커뉴야 퀴즈 주제 (주제명)`으로 입력해 주세요!")
                return
            questions = db.records("SELECT quizid FROM quiz WHERE quiz_subject = ?", wanted_subject)
            n = len(questions)
            await send(ctx, f"{wanted_subject} 주제에 등록된 문제 수는 {n}개에요!")
        elif activity == "뮤트":
            if not wanted_subject:
                await send(ctx, "`커뉴야 퀴즈 뮤트 (주제)` 로 입력해 주세요!")
                return
            await send(ctx, f"{wanted_subject}주제를 뮤트시킬려고 해요. `확인`이라고 입력해서 주제뮤트를 진행하세요.")
            try:
                search_string = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                await send(ctx, "뮤트하지 않기로 했어요.")
                return
            if search_string.content == "확인":
                await send(ctx, "해당 주제를 뮤트 주제로 설정했어요!")
                db.execute("UPDATE games SET quiz_mute = ? WHERE UserID = ?", wanted_subject, ctx.author.id)
                db.commit()
            else:
                await send(ctx, "뮤트하지 않기로 했어요.")
                return
            if wanted_subject == "수학":
                l = grant_check("수포자", ctx.author.id)
                if l == 1:
                    await grant(ctx, "수포자", "퀴즈 명령어에서 수학 주제를 뮤트시키세요")
        elif activity == "목록":
            embed = Embed(color=0xfeff81, title="풀 수 있는 주요 주제 목록",
                          description="80+: 수학\n70+: 해리포터\n60+: 지오메트리 대시\n50+:\n40+:영어, 원신\n30+: 마인크래프트, 브롤스타즈, 유물과 유적, 아이작의 번제, 냥코대전쟁\n20+: 끄투코리아, 우주, 돌 키우기, 역사\n10+: 쿠키런, 사자성어v23, 음악, 공식서버, 디스코드, 서준, 케인, 상식, 랜덤다이스, Phigros, 커뉴봇, 레식, 다이나믹스")
            embed.set_footer(
                text="30+라는 뜻은 해당 주제에 최소 30개의 문제가 존재한다는 뜻입니다\n여기 있는 주제들은 `커뉴야 퀴즈 풀기 (주제)`로 특정 주제만 골라서 풀 수 있습니다")
            await send(ctx, embed=embed)
        elif activity == '내문제':
            my_problem_count = db.record("SELECT count(1) FROM quiz WHERE quiz_maker = ?", ctx.author.id)[0]
            if my_problem_count >= 20:
                l = grant_check("퀴즈 출제자", ctx.author.id)
                if l == 1:
                    await grant(ctx, "퀴즈 출제자", "퀴즈 명령어에서 20문제 이상을 출제하세요")
            if my_problem_count >= 100:
                l = grant_check("프로 퀴즈 출제자", ctx.author.id)
                if l == 1:
                    await grant(ctx, "프로 퀴즈 출제자", "퀴즈 명령어에서 100문제 이상을 출제하세요")
            await send(ctx, 
                f'현재 {ctx.author.display_name}님은 {my_problem_count}개의 아마도 정상적인 문제를 출제했어요!\n\n특정한 퀴즈 문제를 삭제하거나 데이터를 수정하고 싶으시면 다음 중 하나를 입력하세요:\n수정하고 싶은 문제의 퀴즈 ID (퀴즈 ID는 문제를 틀렸을 때 나오는 알파벳과 숫자가 섞인 문자열입니다)\n수정하고 싶은 문제의 내용(중 일부)')
            try:
                search_string = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                return
            search_string = search_string.content
            target_quizzes = db.records(
                "SELECT quizid, quiz_subject, quiz_content, quiz_answer FROM quiz WHERE quiz_maker = ? AND (quizid = ? OR quiz_content LIKE ?)",
                ctx.author.id, search_string, f"%{search_string}%")
            if len(target_quizzes) == 1:
                target_quiz = target_quizzes[0]
            elif len(target_quizzes) == 0:
                await send(ctx, "검색된 퀴즈가 없어요! 당연하지만, 자기 자신이 낸 문제만 수정하거나 삭제할 수 있어요.")
                return
            else:
                embed = Embed(color=0xfeff81, title='여러 개의 퀴즈 문제가 검색됨')
                i = 0
                for quiz in target_quizzes:
                    embed.add_field(name=str(i + 1), value=f'주제: {quiz[1]}\n내용: {quiz[2]}\n 정답: {quiz[3]}',
                                    inline=False)
                    i += 1
                await send(ctx, 
                    f'어느 퀴즈를 수정 또는 삭제하시겠습니까? 굵은 글씨로 써 있는 번호를 말해 주세요', embed=embed)
                try:
                    which_quiz = await self.bot.wait_for(
                        "message",
                        timeout=30,
                        check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
                    )
                except asyncio.TimeoutError:
                    await send(ctx, '퀴즈 수정 또는 삭제 작업을 하지 않기로 했어요.')
                    return
                try:
                    msg = int(which_quiz.content)
                except ValueError:
                    await ctx.channel.send("올바르지 않은 입력이에요!")
                    return
                if len(target_quizzes) < msg:
                    await ctx.channel.send("번호가 너무 커요!")
                    return
                target_quiz = target_quizzes[msg - 1]
            await send(ctx, 
                f'수정 또는 삭제할 문제는, {target_quiz[1]}주제의 문제로, 내용은 {target_quiz[2]}, 정답은 {target_quiz[3]}(이)에요.\n정확히 다음과 같은 형식으로 입력해 주셔야 해요.\n첫 번째 줄에는 `수정` 또는 `삭제`를 입력합니다. `삭제`를 입력할 경우 여기까지만 입력하시면 됩니다.\n`수정`을 입력할 경우, 두 번째 줄에 `주제`, `내용`, `정답`중 하나를 입력합니다.\n`수정`을 입력할 경우, 세 번째 줄에, 해당 퀴즈를 어떻게 수정하고 싶은지를 입력합니다.\n\n사용예시: 어떤 OX퀴즈의 답이 잘못되어 답을 O로 바꾸고 싶을 경우, ```수정\n정답\nO```를 입력하시면 됩니다.')
            try:
                modify = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda message: message.author.id == ctx.author.id and message.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                return
            modify = modify.content.split('\n')
            if len(modify) == 0:
                await send(ctx, "잘못된 방식으로 입력했어요!")
                return
            if modify[0] == '삭제':
                db.execute("DELETE FROM quiz WHERE quizid = ?", target_quiz[0])
                await send(ctx, '해당 문제를 성공적으로 삭제했어요!')
                db.commit()
            elif modify[0] == '수정':
                if len(modify) != 3:
                    await send(ctx, "잘못된 방식으로 입력했어요!")
                    return
                if modify[1] == '주제':
                    db.execute("UPDATE quiz SET quiz_subject = ? WHERE quizid = ?", modify[2], target_quiz[0])
                elif modify[1] == '내용':
                    db.execute("UPDATE quiz SET quiz_content = ? WHERE quizid = ?", modify[2], target_quiz[0])
                elif modify[1] == '정답':
                    db.execute("UPDATE quiz SET quiz_answer = ? WHERE quizid = ?", modify[2], target_quiz[0])
                else:
                    await send(ctx, "잘못된 방식으로 입력했어요!")
                    return
                await send(ctx, f'성공적으로 문제의 {modify[1]}을(를) {modify[2]}(으)로 바꿨어요!')
                db.commit()
            else:
                await send(ctx, "잘못된 방식으로 입력했어요!")
                return
        else:
            await send(ctx, "`커뉴야 퀴즈 <도움/출제/풀기/내점수/주제/뮤트/목록/내문제>`")

    @command(name="수락")
    async def quiz_accept(self, ctx, code: Optional[str]):
        if ctx.author.id != 724496900920705045 or ctx.channel.id == 807172985647267841: return
        content, subject, answer, maker = db.record(
            "SELECT content, subject, answer, maker FROM quiz_temp WHERE code = ?", code)
        db.execute(
            "INSERT INTO quiz (quiz_content, quiz_subject, quiz_answer, quiz_maker, quizid) VALUES (?, ?, ?, ?, ?)",
            content, subject, answer, maker, code)
        db.execute("DELETE FROM quiz_temp WHERE code = ?", code)
        db.commit()
        await send(ctx, "수락했어요!")

    @command(name="거절")
    async def quiz_decline(self, ctx, code: Optional[str]):
        if ctx.author.id != 724496900920705045 or ctx.channel.id == 807172985647267841: return
        code = db.record("SELECT code FROM quiz_temp WHERE code = ?", code)
        code = code[0]
        db.execute("DELETE FROM quiz_temp WHERE code = ?", code)
        db.commit()
        await send(ctx, "거절했어요")

    @command(name="전부수락")
    async def accept_all(self, ctx):
        if ctx.author.id != 724496900920705045 or ctx.channel.id == 807172985647267841: return
        db.execute(
            "INSERT INTO quiz (quiz_content, quiz_subject, quiz_maker, quiz_answer, quizid) SELECT content, subject, maker, answer, code from quiz_temp")
        db.execute("DELETE FROM quiz_temp")
        await send(ctx, "전부 수락했어요!")

    @command(name="골라")
    async def choose_random(self, ctx, *things: Optional[str]):
        if not things:
            chosen = "​"
        else:
            chosen = things[randint(0, len(things) - 1)]
        await send(ctx, chosen.replace("🥴", "😩"))

    @command(name="섞어")
    async def shuffle_things(self, ctx, *things: Optional[str]):
        if not things:
            await send(ctx, "`커뉴야 섞어 (섞을 것들)` 이라고 입력해 주세요! 섞을 것들은 띄어쓰기 단위로 구분해요.")
            return
        things = list(things)
        if len(things) == 1:
            await send(ctx, '엄')
            return
        shuffle(things)
        await send(ctx, ", ".join(things))

    @command(name="말해")
    async def tell(self, ctx, *, content: Optional[str] = "​"):
        if "@" in content:
            await send(ctx, "핑할라그러네나쁜ㅡㅡ")
            return
        await send(ctx, str(ctx.author) + ":" + content.replace("🥴", "😩"))

    @command(name="랜덤숫자", aliases=["주사위"])
    async def pick_random_number(self, ctx, n1: int, n2: Optional[int]):
        if not n2:
            if n1 < 1:
                await send(ctx, "`커뉴야 랜덤숫자 (양수)` 로 입력해 주세요!")
                return
            picked = randint(1, n1)
            await send(ctx, picked)
            return
        if n1 > n2:
            await send(ctx, "`커뉴야 랜덤숫자 (더 작은 수) (더 큰 수)` 로 입력해 주세요!")
            return
        picked = randint(n1, n2)
        await send(ctx, picked)
        if picked == 42:
            l = grant_check("삶과 우주 그리고 모든 것에 대한 궁극적 질문의 해답", ctx.author.id)
            if l == 1:
                await grant(ctx, "삶과 우주 그리고 모든 것에 대한 궁극적 질문의 해답", "`커뉴야 랜덤숫자`명령어를 실행해 커뉴봇이 42라고 대답하게 하세요")

    def translate_SBJB(self, text):
        text = text.replace("ㄱㄷㅋㄴ", "ㄱㄱㅋㄴ")
        text = text.replace("피곤", choice(
            ["피겅", "피건", "피곰", "피곦", "피걷", "피균", "피곧", "피공", "피고느..", "피론", "피", "곤", "비곤", "ㅍ", "ㅠㅣ곤", "피고", "피고노",
             "vlrhs", "파강", 'vㅣ곤']))
        text = text.replace("ㅇㅇ", choice(["ㄴㄴ", "ㅌㅌ"]))
        text = text.replace("산", "싼")
        text = text.replace("ㄹㅇㅋㅋ", choice(["ㅇㅇㅌㅌ", "ㄹㄹㅋㅋ"]))
        text = text.replace("오타", choice(["오라타", "와", "어타", "오타ㅏ"]))
        text = text.replace("근데", choice(["근게", "근ㄴ데"]))
        text = text.replace("강화", choice(["강홬", "갈퓨ㅏ"]))
        text = text.replace("코인", choice(["코린", "커인"]))
        text = text.replace("으악", choice(["으낙", "우악"]))
        text = text.replace("인데", choice(["인다", "인에"]))
        text = text.replace("?", choice(["(", "?/", "ㅐ?"]))
        text = text.replace("차단", choice(["차담", "차다", "파간"]))
        text = text.replace("차단", choice(["으팀", "두탐", "우타", "우탑"]))
        text = text.replace("차", choice(["처", "파"]))
        text = text.replace("제외", choice(["3웨", "제욎"]))
        text = text.replace("제외", choice(["항", "하"]))
        text = text.replace("0", choice(["00", "ㅔ"]))
        text = text.replace("검", choice(["건", "굼", "감", "겸", "건", "감", "겁"]))
        text = text.replace("서버시간", choice(["서버시강", "스버시간", "서버시산"]))
        text = text.replace("올려", choice(["옹려", "올로", "골려", "올러"]))
        text = text.replace("시간", choice(["시감", "스버시간", "서버시산"]))
        text = text.replace("나가", choice(["느가", "나다", "다가", "마가3", "느그", "니기", "아가", "skrk"]))
        text = text.replace("ㄱ", choice(["ㄹ", "ㄷ", "ㅎ", "3", "ㅅ"]))
        text = text.replace("저런", choice(["저건", "자러", "저럼", "더런", "저선"]))
        text = text.replace("재바열보", "재바여로")
        text = text.replace("층", "팡")
        text = text.replace("해도", "해고")
        text = text.replace("다고", "닥ㅎ")
        text = text.replace("\n", "ㄴ/")
        text = text.replace("봐요", "봥")
        text = text.replace("꺼", "RJ")
        text = text.replace("설", "성")
        text = text.replace("잘", "장")
        text = text.replace("야", "어ㅑ")
        text = text.replace("였나", "리여ㅛ나")
        text = text.replace("편", "펵")
        text = text.replace("지을까", "질따")
        text = text.replace("나", "나ㅏ")
        text = text.replace("걸", "럴")
        text = text.replace("섬바삭보", "섬바삳보")
        text = text.replace("보", "ㅂㅎ")
        text = text.replace("발", "밧")
        text = text.replace("먹어", "막아")
        text = text.replace("육성", "육섵")
        text = text.replace("한", "하")
        text = text.replace("렵네", "려벤")
        text = text.replace("🤪", choice(["🇿🇦", "🇦🇿"]))
        text = text.replace("근", "금")
        text = text.replace("어", "어ㅓ")
        text = text.replace("마", "만")
        text = text.replace("갖", "같")
        text = text.replace("응애", "으으ㅐ")
        text = text.replace("슬", "쓸")
        text = text.replace("겠는", "겠난")
        text = text.replace("겠", "깄")
        text = text.replace("으로", "읋")
        text = text.replace("열심", "영심")
        text = text.replace("타만", "태민")
        text = text.replace("ㄷㄷ", "ㄷ4")
        text = text.replace("제발", "제방")
        text = text.replace("유", "쥬")
        text = text.replace("체크", "케츠")
        text = text.replace("팝", "찹")
        text = text.replace("하기", "허기")
        text = text.replace("티어", "치어")
        text = text.replace("날", "냘")
        text = text.replace("으악", "으낙")
        text = text.replace("봇", "못")
        text = text.replace("y", "t")
        text = text.replace("z", "w")
        text = text.replace("ㅋ", "ㅌ")
        text = text.replace("사람", "사라")
        text = text.replace("찮", "차노")
        text = text.replace("잡고", "잡조")
        text = text.replace("과제", "과지")
        text = text.replace("기원", "기워")
        text = text.replace("육", "욕")
        text = text.replace("사운드", "사운그")
        text = text.replace("거", "버")
        text = text.replace("버린다", "머린다")
        text = text.replace("바", "뱌")
        text = text.replace("창", "탕")
        text = text.replace("수도", "수조")
        text = text.replace("그럼", "스럼")
        text = text.replace("어케", "아케")
        text = text.replace("시세", "시게")
        text = text.replace("하네", "하메")
        text = text.replace("스탭도", "스탭고")
        text = text.replace("지랄", "지랑")
        text = text.replace("죽어", "북어")
        text = text.replace("찾네", "찾에")
        text = text.replace("뭐", "모")
        text = text.replace("하네", "해네")
        text = text.replace("올인", "올이")
        text = text.replace("몰라", "몰리")
        text = text.replace("임", "딤")
        text = text.replace("같은", "닼은")
        text = text.replace("맞", "맺")
        text = text.replace("가요", "가뇨")
        text = text.replace("기분", "기준")
        text = text.replace("탯", "탭")
        text = text.replace("잡소리", "잡소라")
        text = text.replace("금", "감")
        text = text.replace("모으잖", "모르잖")
        text = text.replace("그래서", "그래거")
        text = text.replace("춤", "툼")
        text = text.replace("니깐", "깐")
        text = text.replace("모르겠", "모으겠")
        text = text.replace("아닌", "나닌")
        text = text.replace("차단", "차간")
        text = text.replace("야지", "여지")
        text = text.replace("나!", "남")
        text = text.replace("좀", "종")
        text = text.replace("서버", "거버")
        text = text.replace("섹스", "섹사")
        text = text.replace("!", "ㅃ")
        text = text.replace("다좀", "다ㅊ좀")
        text = text.replace("싸", "사")
        text = text.replace("언제", "안제")
        text = text.replace("펙", "픽")
        text = text.replace("무서움", "무사움")
        text = text.replace("오우", "오유")
        text = text.replace("어져", "어쟈")
        text = text.replace("놈아", "놈라")
        text = text.replace("멈", "몀")
        text = text.replace("어제", "아제")
        text = text.replace("머리", "마리")
        text = text.replace("으니", "으네")
        text = text.replace("차피", "차치")
        text = text.replace("정지", "장지")
        text = text.replace("음", "름")
        text = text.replace("성민", "성밍")
        text = text.replace("써가", "쓰가")
        text = text.replace("하려", "라려")
        text = text.replace("스", "ㅡ")
        text = text.replace("에서", "에사")
        text = text.replace("여자", "야자")
        text = text.replace("어딨", "아디ㅛ")
        text = text.replace("동아리", "종아리")
        text = text.replace("실패", "실채")
        text = text.replace("노", "농")
        text = text.replace("비료", "비려")
        text = text.replace("😩", choice(
            ["😩'", '🇪🇷', '🎆', '🎴', ':ㅈㄷ', ';we', ';;we', ':w', ':e', '↙️', '👳‍♂️', '💒', '🖌️']))
        text = text.replace("잡키", "잡")
        text = text.replace("렴", "려")
        text = text.replace("ㅁ", "ㅁ/")
        text = text.replace("고", "교")
        text = text.replace("골라", "골러")
        text = text.replace("버그", "버스")
        text = text.replace("화", "퐈")
        if "씨밧" not in text:
            text = text.replace("아니", "않")
        return text

    @command(name="서바준보", aliases=["서바준ㅂㅎ", "서뱌준ㅂㅎ"])
    @cooldown(1, 3)
    async def SBJB(self, ctx, *, text: Optional[str]):
        if not text:
            files = [f for f in os.listdir('C:/Users/namon/PycharmProjects/discordbot/lib/sbjb') if
                     os.path.isfile(os.path.join('C:/Users/namon/PycharmProjects/discordbot/lib/sbjb', f))]
            file_name = choice(files)
            await send(ctx, f"{file_name}".replace('.png', '.sbjb'),
                           file=File(os.path.join('C:/Users/namon/PycharmProjects/discordbot/lib/sbjb', file_name)))
        else:
            await send(ctx, self.translate_SBJB(text))

    @command(name="구매")
    async def buy_item(self, ctx, *, item: str):
        if ctx.guild.id != 743101101401964647:
            await send(ctx, "커뉴봇 공식 커뮤니티 서버에서만 이용할 수 있는 기능이에요!")
            return
        tems = 0
        dtype = -1
        delta = -1
        if item in ["원", "원하는 사람 강제닉변권"]:
            cost = 10000
            buy = "원하는 사람 강제닉변권"
        elif item in ["프", "프리미엄 티켓"]:
            cost = 123456
            buy = "프리미엄 티켓"
        elif item in ["닉", "닉네임 변경권"]:
            cost = 25000
            buy = "닉네임 변경권"
        elif item in ["강", "강제 닉변 방지권"]:
            cost = 15000
            buy = "강제 닉변 방지권"
        elif item in ["커", "커스텀 커맨드 생성권"]:
            cost = 3000
            buy = "커스텀 커맨드 생성권"
        elif item in ["고", "고속 레벨업 티켓"]:
            cost = 45000
            buy = "고속 레벨업 티켓"
        elif item in ["공", "공지 홍보권"]:
            cost = 8000
            buy = "공지 홍보권"
        elif item in ["슬", "강화 슬롯 추가권"]:
            cost = 9999
            buy = "강화 슬롯 추가권"
            enchant_info = db.record("SELECT enchant_info FROM games WHERE UseriD = ?", ctx.author.id)
            enchant_info = json.loads(enchant_info[0])
            if enchant_info["최대강화가능개수"] == 10:
                await send(ctx, "해당 아이템을 더 이상 살 수 없어요!")
                return
            money = db.record("SELECT money FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", ctx.author.id)
            money = money[0]
            if money < cost:
                await send(ctx, "그 아이템을 사기 위한 돈이 부족해요!")
                return
            db.execute("UPDATE exp SET money = money - ? WHERE UserID = ? AND GuildID = 743101101401964647", cost,
                       ctx.author.id)
            enchant_info["최대강화가능개수"] += 1
            db.execute("UPDATE games SET enchant_info = ? WHERE UserID = ?",
                       json.dumps(enchant_info, ensure_ascii=False), ctx.author.id)
            db.commit()
            await send(ctx, f"{buy} 구매 완료!")
            return
        elif item == "커뉴야 애교":
            cost = 500000
            buy = "커뉴야 애교"
            money = db.record("SELECT money FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", ctx.author.id)
            money = money[0]
            if money < cost:
                await send(ctx, "...?")
                return
            db.execute("UPDATE games SET user_setting = user_setting + 1 WHERE UserID = ?", ctx.author.id)
            db.commit()
            await send(ctx, "뿌잉뿌잉>_<")
            l = grant_check("뿌잉뿌잉>_<", ctx.author.id)
            if l == 1:
                await grant(ctx, "뿌잉뿌잉>_<", ">_<")
        else:
            tems = db.record("SELECT created_by, cost, amount, description FROM items WHERE name = ?", item)
            if not tems:
                await send(ctx, "아이템 이름을 다시 한 번 확인해 주세요!")
                return
            cost = tems[1]
            buy = item
            delta = 0
            dtype = 0
            try:
                cost = int(cost)
            except ValueError:
                if "+" in cost:
                    delta = int(cost[cost.index("+") + 1:])
                    cost = int(cost[:cost.index("+")])
                    dtype = 1
                else:
                    delta = int(cost[cost.index("*") + 1:])
                    cost = int(cost[:cost.index("*")])
                    dtype = 2
        money = db.record("SELECT money FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", ctx.author.id)[0]
        if money < cost:
            await send(ctx, "그 아이템을 사기 위한 돈이 부족해요!")
            return
        db.execute("UPDATE exp SET money = money - ? WHERE UserID = ? AND GuildID = 743101101401964647", cost,
                   ctx.author.id)
        await self.bot.get_channel(874829010071347240).send(f"{buy} 를! 구매한 {str(ctx.author)}")
        try:
            await self.bot.get_user(tems[0]).send(f"{str(ctx.author)}님이 {buy}를 구매하셨습니다.")
        except:
            pass
        try:
            await send(ctx, f"{buy} 구매 완료!\n\n아래는 이 아이템의 설명이에요.\n\n{tems[3]}")
        except TypeError:
            await send(ctx, f"{buy} 구매 완료!")
            if buy == '프리미엄 티켓':
                mv = self.bot.get_guild(743101101401964647)
                await mv.get_member(ctx.author.id).add_roles(mv.get_role(760773508195811359))
            return
        try:
            db.execute("UPDATE exp SET Money = Money + ? WHERE UserID = ? AND GuildID = 743101101401964647", tems[1],
                       tems[0])
        except:
            pass
        if tems[2] == 1:
            db.execute("DELETE FROM items WHERE name = ? AND created_by = ?", buy, tems[0])
        else:
            if dtype == 1:
                db.execute("UPDATE items SET cost = cost + ? WHERE name = ? AND created_by = ?", delta, buy, tems[0])
            elif dtype == 2:
                db.execute("UPDATE items SET cost = cost * ? WHERE name = ? AND created_by = ?", delta, buy, tems[0])
            if tems[2] == -1:
                return
            else:
                db.execute("UPDATE items SET amount = amount - 1 WHERE name = ? AND created_by = ?", buy, tems[0])

    @command(name="설명")
    async def desc(self, ctx, *, item: str):
        try:
            await send(ctx, db.record("SELECT description FROM items WHERE name = ?", item)[0])
        except TypeError:
            await send(ctx, "존재하지 않는 아이템이에요!")

    @command(name="출석체크", aliases=["출첵", "ㅊㅊ", "ㅊ"])
    @cooldown(1, 20, BucketType.user)
    async def attend(self, ctx):
        t = time()
        if (t + 32400) % 86400 > 86399:
            l = grant_check("서두르면 일을 그르친다", ctx.author.id)
            if l == 1:
                await grant(ctx, "서두르면 일을 그르친다", "날 바뀌는 걸 1초 남기고 출석체크를 진행하세요")
        if today < ((t + 32400) // 86400):
            self.day_reset()
        attend_time_ = (datetime.now())
        visual_today = attend_time_.strftime("%Y년 %m월 %d일 (%a)")
        attend_time = attend_time_.strftime("%H:%M:%S")
        if attend_time[0:2] != "00" and attend_time[3:] == "00:00":
            l = grant_check("시차 적응 좀 해요", ctx.author.id)
            if l == 1:
                await grant(ctx, "시차 적응 좀 해요", "0시가 아닌 정시에 출석체크를 진행하세요")
        today_attended = db.records("SELECT UserID FROM attends WHERE attend_date = ? ORDER BY rank ASC",
                                    today)
        for ids in today_attended:
            if ids[0] == ctx.author.id:
                await send(ctx, "내일 다시 출석체크를 해 주세요")
                return
        db.execute("INSERT INTO attends (USERID, attend_date, time_constant, rank) VALUES (?, ?, ?, ?)", ctx.author.id,
                   today, attend_time, len(today_attended) + 1)
        db.commit()
        my_attends = db.records("SELECT attend_date FROM attends WHERE UserID = ? ORDER BY attend_date DESC",
                                ctx.author.id)
        streak = 0
        day_temp = int(today)
        for day in my_attends:
            if day[0] == day_temp:
                streak += 1
                day_temp -= 1
            else:
                break
        db.commit()

        l = grant_check("출첵", ctx.author.id)
        if l == 1:
            await grant(ctx, "출첵", "출석체크 명령어로 출석체크를 진행하세요")
        if streak >= 10:
            l = grant_check("단골 출첵러", ctx.author.id)
            if l == 1:
                await grant(ctx, "단골 출첵러", "출석체크를 10일 연속으로 진행하세요")
        if streak >= 50:
            l = grant_check("프로 출첵러", ctx.author.id)
            if l == 1:
                await grant(ctx, "프로 출첵러", "출석체크를 50일 연속으로 진행하세요")
        embed = Embed(color=ctx.author.color)
        name, value = self.add_money(ctx, streak, visual_today)
        embed.add_field(name=name, value=value, inline=False)
        event_check = db.record("SELECT BIGEVENT, BIGEVENT_DAY, EVENT, EVENT_DAY FROM MISC_DATA WHERE USERID = ?",
                                ctx.author.id)
        if event_check:
            if event_check[0]:
                days_left = today - event_check[1]
                if not days_left:
                    name_string = f'{event_check[0]} D-DAY'
                else:
                    name_string = f'{event_check[0]} D{days_left}'
            else:
                name_string = '​'
            if event_check[2]:
                days_left = today - event_check[3]
                if not days_left:
                    value_string = f'{event_check[2]} D-DAY'
                else:
                    value_string = f'{event_check[2]} D{days_left}'
            else:
                value_string = '​'
            embed.add_field(name=name_string, value=value_string, inline=False)
        await self.bot.get_channel(817335216133111838).send(f"{attend_time}\n{str(ctx.author)}님의 출석체크")
        if len(today_attended) == 0:
            embed.set_footer(text=f"1등이시네요! 축하드려요\n출석체크 진행: {attend_time}")
            l = grant_check("번개같은 출석", ctx.author.id)
            if l == 1:
                await grant(ctx, "번개같은 출석", "출석체크 1등을 하세요")
            await self.bot.get_channel(803935769650790400).send(f"오늘의 출석 1등은 {str(ctx.author)}님입니다. 축하드립니다!")
            await self.bot.get_channel(787284733552885760).send(
                f"오늘의 출석 1등은 {ctx.author.mention} ({str(ctx.author)})님입니다. 축하드립니다!")
            db.execute("INSERT INTO serverstat (day) VALUES (?)", today)
            db.execute("UPDATE clash_of_clans SET member_time = member_time + 1")
            db.commit()
        else:
            if len(today_attended) == 1:
                l = grant_check("2등도 잘한거야", ctx.author.id)
                if l == 1:
                    await grant(ctx, "2등도 잘한거야", "출석체크 2등을 하세요")
            embed.set_footer(text=f"오늘의 출첵 1등: {self.bot.get_user(today_attended[0][0])}\n출석체크 진행: {attend_time}")
            if len(today_attended) == 4:
                await self.send_serverstat()
        if randint(1, 10) == 1:
            embed.set_footer(text='반복할일 기능을 사용하고 있는 경우 다른 명령어를 사용하기 전까지 조금만 기다려 주세요.')
        await send(ctx, f"{ctx.author.mention}", embed=embed)
        repeating_tasks = db.records(
            "SELECT SPECIFIC_CONTENT, UNTIL, REPETITION, PROGRESSION, AMOUNT_OF_TASK FROM TASKS WHERE IDS LIKE ? AND REPETITION != 0",
            f'%{ctx.author.id}%')
        if not repeating_tasks:
            return
        embed = Embed(color=0x00b2ff, title='오늘 초기화된 반복 할일 정보')
        check = 1
        task_check = 0
        for task in repeating_tasks:
            a = re.compile('^(\d{4}-\d{2}-\d{2}).*$')
            b = a.search(task[1])
            until = datetime.strptime(b.group(1), '%Y-%m-%d')
            if until > datetime.now(): continue
            task_check = 1
            repetition_sgn = 2 * (task[2] > 0) - 1
            repetition_val = abs(task[2])
            if repetition_sgn == 1:
                v = repetition_val
            else:
                yoils = deque(sorted(list(map(int, list(str(repetition_val))))))
                cur_yoil = datetime.now().weekday()
                while yoils[0] != cur_yoil:
                    yoils.rotate(-1)
                v = yoils[1] - yoils[0]
                if v < 0:
                    v += 7
            until += timedelta(days=v)
            db.execute(
                "UPDATE TASKS SET UNTIL = ?, PROGRESSION = 0 WHERE SPECIFIC_CONTENT = ? AND UNTIL = ? AND IDS LIKE ? AND REPETITION = ?",
                until, task[0], task[1], f'%{ctx.author.id}%', task[2])
            t = task[3] == task[4]
            check = check and t
            s = ' 모든 반복할일들을 끝냈어요!' * t
            embed.add_field(name=task[0], value=f'{task[3]} / {task[4]} 만큼 진행된 상태에요!{s}')
        if check:
            embed.set_footer(text='수고했어요! 모든 반복할일들을 끝냈어요.')
        if task_check:
            await send(ctx, embed=embed)
            db.commit()

    def day_reset(self):
        global today
        global first_place
        today += 1
        first_place = ""
        return

    def add_money(self, ctx, streak, visual_today):
        global today
        today_attended = db.records("SELECT UserID FROM attends WHERE attend_date = ? ORDER BY rank ASC",
                                    today)
        gtype = db.record("SELECT guild_type FROM guilds WHERE GuildID = ?", ctx.guild.id)
        if gtype[0] & 1 == 1:
            money = db.record("SELECT Money FROM exp WHERE UserID = ? AND GuildID = ?", ctx.author.id, ctx.guild.id)
            money = money[0]
            if len(today_attended) < 4:
                money_to_add = 1500 - 300 * len(today_attended)
            else:
                money_to_add = 500
            money_to_add += randint(-69, 69)
            money += money_to_add + streak
            db.execute("UPDATE exp SET Money = ? WHERE UseriD = ? AND GuildID = ?", money, ctx.author.id, ctx.guild.id)
            value = f"{money_to_add}<:treasure:811456823248027648>을 받았어요.\n 현재 가지고 있는 돈은 {money}<:treasure:811456823248027648>(이)에요."
        else:
            value = choice(
                ["`커뉴야 서버강화`를 사용해 보세요! 50레벨이 넘으면 자기 서버 홍보도 가능합니다.", "관리자 분이라면 `커뉴야 공지채널 설정`명령어로 봇의 공지를 받아 보세요!",
                 "`커뉴야 문의` 명령어를 사용하거나 `커뉴야 공식서버`로 공식서버에 들어가셔서 무언가를 문의하실 수 있습니다!", "`커뉴야 업데이트`명령어로 최근 업데이트 내용을 알아보세요",
                 "출석체크와 관련된 명령어는 이것 말고도 몇 개 더 있어요. `커뉴야 도움`을 통해 알아보세요.",
                 "에러가 나거나 무언가 잘 안 된다면 `커뉴야 권한진단`을 해 보시고 권한 문제가 아니라면 `커뉴야 문의`로 개발자에게 문의하는 것을 두려워하지 마세요",
                 "당신의 봇 사용 현황을 알아보고 싶으시다면 `커뉴야 스펙`을 이용해보세요", '`커뉴야 커뉴핑크`명령어가 새로 출시됐대요. 한 번 해 보세요!'])
        name = f"{visual_today}: {len(today_attended)} 등, {streak} 연속으로 출석체크 완료!"
        db.commit()
        return name, value

    async def send_serverstat(self):
        today_stat = db.record("SELECT fire, member_delta, fire_bot, total_exp FROM serverstat WHERE day = ?",
                               today - 1)
        m = self.bot.get_guild(743101101401964647)
        l = ["<@&834406523823587348>"]
        l.append(datetime.now().strftime("%y/%m/%d"))
        l.append(
            f"총 서버 멤버: **{len(m.members)}** (사람{(p := len(list(filter(lambda t: not t.bot, m.members))))}명 + 봇 {len(m.members) - p})")
        l.append(f"오늘의 서버 멤버 변화: **{today_stat[1]}**")
        l.append(f"오늘의 서버 화력: **{today_stat[0]}**")
        l.append(f"그 중 봇이 보낸 메세지 개수 **{today_stat[2]}**")
        l.append(f"오늘 사람들이 벌어들인 총 경험치: **{today_stat[3]}**")
        await self.bot.get_channel(770642262282993715).send("\n".join(l))
        fire = today_stat[0]
        firecoin, yesterday = db.record("SELECT value, value_temp FROM coins WHERE coin_name = '화력코인'")
        delta = fire / yesterday
        delta_ = delta ** 0.55
        firecoin_ = int(firecoin * delta_) - 3
        db.execute("UPDATE coins SET value = ?, value_temp = ?, value_delta = ? WHERE coin_name = '화력코인'", firecoin_,
                   fire, firecoin_ - yesterday)
        db.commit()
        await self.bot.get_channel(770642262282993715).send(embed=Embed(color=0xffcc4d, title="화력코인 값이 갱신됨",
                                                                        description=f"어제의 서버 화력: {fire:,}\n\n그에 따른 오늘의 화력코인 가치: {firecoin_}\n\n어제 대비 등락률: {delta_ * 100 - 100} %"))

    @command(name="출첵목록")
    @cooldown(1, 5, BucketType.user)
    async def attend_mokrok(self, ctx, ex: Optional[str]):
        today_attended = db.records(
            "SELECT UserID, time_constant FROM attends WHERE attend_date = ? ORDER BY rank ASC LIMIT 25", today)
        tjfaud = ""
        i = 0
        for attend_person in enumerate(today_attended):
            if ex == "서버":
                try:
                    tjfaud += f"\n\n{i + 1}.{ctx.guild.get_member(attend_person[1][0]).display_name} | {attend_person[1][1]}"
                    i += 1
                except AttributeError:
                    pass
            else:
                tjfaud += f"\n\n{attend_person[0] + 1}.{self.bot.get_user(attend_person[1][0])} | {attend_person[1][1]}"
        await send(ctx, embed=Embed(color=0xffd6fe, title=f"{len(today_attended) if not i else i} 등까지의 출석체크 목록!",
                                   description=tjfaud))

    @command(name="출첵내역")
    async def my_attend(self, ctx):
        attends = db.records(
            "SELECT attend_date, time_constant, rank FROM attends WHERE UserID = ? ORDER BY attend_date DESC",
            ctx.author.id)
        max_attend = db.record("SELECT max_attend FROM games WHERE UserID = ?", ctx.author.id)[0]
        streak = 0
        day_temp = int(today)
        for day in attends:
            if day[0] == day_temp:
                streak += 1
                day_temp -= 1
            else:
                break
        tjfaud = ""
        second_place = 0
        for attend in attends:
            ago = int(today - attend[0])
            day = f"\n**{ago}일 전**" if today != attend[0] else "**오늘**"
            tjfaud += f"{day}\n{attend[1]}에 {attend[2]} 등으로 출석체크 진행"
            if attend[2] == 2:
                second_place += 1
            if ago >= max_attend - 1:
                break
        embed = Embed(color=0xffd6fe, title=f"최근 {max_attend}일간의 출석체크 내역!", description=tjfaud)
        embed.set_footer(text=f"{streak}일 연속으로 출석체크 중!\n출석체크 데이터는 출석체크한 지 15일이 지나면 자동으로 페기될까요?")
        await send(ctx, embed=embed)
        if second_place >= 3:
            l = grant_check("개같은 출석", ctx.author.id)
            if l == 1:
                await grant(ctx, "개같은 출석", "출첵내역에 표시되는 출석체크 기간 동안 2등으로 출석체크를 3번 진행하세요")

    @command(name="연속출석")
    async def attend_streak(self, ctx):
        my_attends = db.records("SELECT attend_date FROM attends WHERE UserID = ? ORDER BY attend_date DESC",
                                ctx.author.id)
        streak = 0
        day_temp = int(today)
        for day in my_attends:
            if day[0] == day_temp:
                streak += 1
                day_temp -= 1
            else:
                break
        await send(ctx, f"{ctx.author.name}님은 현재 {streak} 연속으로 출석체크를 진행하시는 중이에요!")

    @command(name="쫀득쫀득한")
    async def congrats_pizza_achievement(self, ctx, *, pizzacheck: Optional[str]):
        if pizzacheck == "피자 치쥬가 뫄이뫄이 들어있는 피이자이아아...! 햄토핑도 좋쿠우 빵에들어가있누눈 치즈도 좋쿠우 매코무한양파아아..!! 피먀양 맛 없써어! 새쿄뮤한 토마토쇼슈 버섯 뫄이쩌엉! 피자 사듀떼여":
            l = grant_check("안 사줄 수가 없어!", ctx.author.id)
            if l == 1:
                await grant(ctx, "안 사줄 수가 없어!", "<:kkyu_with_3_hearts:872405007243288677>")

    # @command(name='잡소리')
    # async def zapsori(self, ctx, day: int, author: Optional[str] = '커뉴'):
    #     l = grant_check('공식서버 고렙', ctx.author.id)
    #     if l == 1:
    #         await send(ctx, "?")
    #         return
    #     date_viewable = -100
    #     for ach in ['공식서버 고인물', '공식서버 초고렙', '공식서버 정복자', '뿌잉뿌잉>_<', '아니 씨밧', 'ㅇㅇㅌㅌ']:
    #         l = grant_check(ach, ctx.author.id)
    #         if l == 0:
    #             date_viewable += 12
    #     if ctx.author.id == 448024256576618497:
    #         date_viewable = 0
    #     final_day = 340
    #     if final_day + date_viewable < day:
    #         await send(ctx, '열람 불가능한 회차에요! 특정한 도전과제들을 더 달성하세요...')
    #         return
    #     if day == 156:
    #         await send(ctx, 
    #             '바보같은 잡소리 작가 때문에 156일차 잡소리는 두 개에요.\n먼저 쓴 156일차, 나중에 쓴 156일차 중 무엇을 열람하실 건가요?\n먼저 쓴 156일차를 열람하시려면 1, 나중에 쓴 156일차를 열람하시려면 2를 입력하세요')
    #         try:
    #             msg = await self.bot.wait_for(
    #                 "message",
    #                 timeout=20,
    #                 check=lambda message: message.author == ctx.author and ctx.channel == message.channel
    #             )
    #         except asyncio.TimeoutError:
    #             await send(ctx, '잡소리를 열람하지 않기로 했어요.')
    #             return
    #         try:
    #             msg = int(msg.content)
    #         except ValueError:
    #             await send(ctx, '올바르지 않은 입력이에요!')
    #             return
    #         if msg == 2:
    #             day += 1
    #     elif day > 156:
    #         day += 1
    #     zap = db.record("SELECT content FROM zapsori WHERE id = ?", day)
    #     try:
    #         zap = zap[0]
    #     except TypeError:
    #         await send(ctx, '아직 등록되지 않았거나 애초에 써지지 않은 날짜에요! `커뉴야 날짜차이 20210301`로 오늘이 몇 일차인지 알아보세요')
    #         return
    #     await ctx.author.send(f"커뉴의 1일1잡소리 **{day}** 일차!\n{zap}")

    @command(name='날짜차이')
    async def calculate_day(self, ctx, d1: Optional[int], d2: Optional[int]):
        if not d1:
            await send(ctx, '`커뉴야 날짜차이 (날짜1)` 또는 `커뉴야 날짜차이 (날짜1) (날짜2)`, 날짜는 20240219와 같은 형식으로')
            return
        if not d2:
            d1 = datetime.strptime(str(d1), "%Y%m%d")
            d2 = datetime.now()
        else:
            d1 = datetime.strptime(str(d1), "%Y%m%d")
            d2 = datetime.strptime(str(d2), "%Y%m%d")
        delta = d2 - d1  # 과거면 델타 양수 미래면 델타 음수
        delta = str(delta)
        try:
            e = delta.index(' ')
        except ValueError:
            await send(ctx, '그게 왜 궁금해요?')
            return
        td = int(delta[:e])
        d1 = d1.strftime('%Y년 %m월 %d일')
        d2 = d2.strftime('%Y년 %m월 %d일')
        if td > 0:
            await send(ctx, f'{d1}은 {d2}로부터 {td}일 전이에요!')
        elif td < 0:
            await send(ctx, f'{d1}은 {d2}로부터 {-td}일 후에요!')
        else:
            await send(ctx, "?")

    def calculate_net_worth(self, coin_info):
        net_worth = 0
        for coin in coin_info:
            if coin[0] == "현금":
                try:
                    net_worth += int(10 ** coin[1])
                except TypeError:
                    net_worth = -1
                    break
            else:
                try:
                    net_worth += db.record("SELECT value FROM coins WHERE coin_name = ?", coin[0])[0] * int(
                        10 ** coin[1])
                except TypeError:
                    net_worth = -1
                    break
        return net_worth

    @command(name="코인")
    async def conucoin(self, ctx, activity: Optional[str], a2: Optional[str], am: Optional[int]):
        # logam_to_actual = lambda x: power_of_ten(Decimal(x))
        raw_money = db.record("SELECT logam FROM coin_info WHERE UserID = ? AND coin_name = '현금'", ctx.author.id)
        try:
            raw_money = raw_money[0]
            raw_money = round(10 ** raw_money)
        except TypeError:
            db.execute("INSERT INTO coin_info (UserID, coin_name, logam) VALUES (?, '현금', 6)", ctx.author.id)
            raw_money = 1000000
        coins = db.records("SELECT coin_name, logam FROM coin_info WHERE UserID = ? AND coin_name != '현금'",
                           ctx.author.id)
        if not activity:
            embed = Embed(color=0xffcc4d, title=f"{str(ctx.author)} 님이 보유중인 코인")
            embed.add_field(name="보유 중인 현금", value=f"{round(raw_money):,} 코인")
            for coin in coins:
                embed.add_field(name=f"보유 중인 {coin[0]}", value=f"{round(10 ** coin[1]):,} 코인")
            if raw_money >= 100000000:
                l = grant_check("코인 투자자", ctx.author.id)
                if l == 1:
                    await grant(ctx, "코인 투자자", "코인에서 현금 100000000코인을 가지세요")
            if raw_money >= 1000000000:
                l = grant_check("코인 부자", ctx.author.id)
                if l == 1:
                    await grant(ctx, "코인 부자", "코인에서 현금 1000000000코인을 가지세요")
            if raw_money >= 1000000000000:
                l = grant_check("코인 대부호", ctx.author.id)
                if l == 1:
                    await grant(ctx, "코인 대부호", "코인에서 현금 1조코인을 가지세요")
            await send(ctx, embed=embed)
        elif activity in ["투자", "구매", "판매"]:
            if a2 == "공섭":
                if not am:
                    await send(ctx, "교환할 양도 입력해 주세요")
                    return
                meta_coin = db.record("SELECT money FROM exp WHERE UserID = ? AND GuildID = 743101101401964647",
                                      ctx.author.id)
                if not meta_coin:
                    await send(ctx, "공식서버 가입자 전용 기능이에요! `커뉴야 공식서버`로 공식서버에 입장하세요")
                    return
                meta_coin = meta_coin[0]
                embed = Embed(color=0xffcc4d, title=f"공식서버 코인과의 환전")
                embed.add_field(name="코인 환전하기",
                                value=f"공식서버의 돈과 환전하려고 해요.\n\n가진 공식서버 돈: {meta_coin:,}\n\n가진 커뉴코인: {raw_money:,}\n\n`확인`을 입력해 커뉴코인으로의 투자를 진행하세요")
                await send(ctx, embed=embed)
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        timeout=30,
                        check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                    )
                except asyncio.TimeoutError:
                    await send(ctx, "투자를 종료했어요.")
                    return
                if msg.content == "확인":
                    if am > meta_coin:
                        await send(ctx, "투자를 위한 돈이 부족해요!")
                        return
                    db.execute("UPDATE exp SET Money = Money - ? WHERE UserID = ? AND GuildID = 743101101401964647", am,
                               ctx.author.id)
                    raw_money = db.record("SELECT logam FROM coin_info WHERE UserID = ? AND coin_name = '현금'",
                                          ctx.author.id)
                    raw_money = raw_money[0]
                    raw_money = round(10 ** raw_money)
                    raw_money += am * 100
                    db.execute("UPDATE coin_info SET logam = ? WHERE UserID = ? AND coin_name = '현금'",
                               math.log10(raw_money), ctx.author.id)
                    await send(ctx, f"환전을 완료해서 {am * 100:,} 커뉴코인을 획득했어요!")
                    db.commit()
                else:
                    return
            else:
                val = db.record("SELECT value FROM coins WHERE coin_name = ?", a2)
                try:
                    val = val[0]
                except TypeError:
                    embed = Embed(color=0xffcc4d, title=f"{ctx.author} 님에게 가능한 코인 환전")
                    meta_coin = db.record("SELECT money FROM exp WHERE UserID = ? AND GuildID = 743101101401964647",
                                          ctx.author.id)
                    if meta_coin:
                        embed.add_field(name="공식서버의 돈과 환전",
                                        value="공식서버 돈 1당 100 커뉴코인으로 환전 가능\n`커뉴야 코인 투자 공섭 (투자할 양)`으로 환전하세요",
                                        inline=False)
                    embed.add_field(name="존재하는 코인과 환전",
                                    value="여러 종류의 코인 중 원하는 코인에 투자하세요.\n`커뉴야 코인 시세`로 시세를 확인하고 `커뉴야 코인 투자 (코인 이름)` 으로 투자하세요",
                                    inline=False)
                    await send(ctx, embed=embed)
                    return
                embed = Embed(color=0xffcc4d, title=f"{a2} 구매/판매")
                embed.add_field(name=f"{a2} 거래하기",
                                value=f"{a2} 하나당 가격: {val:,}\n\n`구매`로 {a2}을(를) 구매하고 `판매`로 {a2}을(를) 판매하세요")
                if activity == "투자":
                    await send(ctx, embed=embed)
                    try:
                        msg = await self.bot.wait_for(
                            "message",
                            timeout=30,
                            check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                        )
                    except asyncio.TimeoutError:
                        await send(ctx, "투자를 종료했어요.")
                        return
                    activity = msg.content
                if activity == "구매":
                    if not am:
                        await send(ctx, f"코인을 몇 개나 구매하실 건가요?")
                        try:
                            msg = await self.bot.wait_for(
                                "message",
                                timeout=20,
                                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                            )
                        except asyncio.TimeoutError:
                            await send(ctx, "투자를 종료했어요.")
                            return
                        try:
                            am = int(msg.content)
                        except ValueError:
                            await send(ctx, "올바르지 않은 입력이에요! 정수로 입력해 주세요")
                            return
                    if raw_money < am * val:
                        await send(ctx, "그만큼의 코인을 사기 위한 돈이 부족해요!")
                        return
                    if val == 0:
                        l = grant_check("이걸 왜사요", ctx.author.id)
                        if l == 1:
                            await grant(ctx, "이걸 왜사요", "가격이 0원인 코인을 구매하세요")
                    try:
                        coin = math.log10(raw_money - am * val)
                    except ValueError:
                        coin = 0
                    for info in coins:
                        if info[0] == a2:
                            am_ = math.log10(am + 10 ** info[1])
                            db.execute("UPDATE coin_info SET logam = ? WHERE UserID = ? AND coin_name = ?",
                                       am_,
                                       ctx.author.id, a2)
                            break
                    else:
                        db.execute("INSERT INTO coin_info (UserID, coin_name, logam) VALUES (?, ?, ?)", ctx.author.id,
                                   a2, math.log10(am))
                    db.execute("UPDATE coin_info SET logam = ? WHERE UserID = ? AND coin_name = '현금'", coin,
                               ctx.author.id)
                    db.commit()
                    await send(ctx, "거래 완료! `커뉴야 코인`으로 현재 상황을 알아보세요")
                elif activity == "판매":
                    if not am:
                        await send(ctx, f"코인을 몇 개나 판매하실 건가요?")
                        try:
                            msg = await self.bot.wait_for(
                                "message",
                                timeout=20,
                                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                            )
                        except asyncio.TimeoutError:
                            await send(ctx, "투자를 종료했어요.")
                            return
                        try:
                            am = int(msg.content)
                        except TypeError:
                            await send(ctx, "올바르지 않은 입력이에요! 정수로 입력해 주세요")
                            return
                    for info in coins:
                        if info[0] == a2:
                            now_coin = round(10 ** info[1])
                            break
                    else:
                        await send(ctx, "그만큼의 코인을 가지고 있지 않아요!")
                        return
                    if am > now_coin:
                        await send(ctx, "그만큼의 코인을 가지고 있지 않아요!")
                        return
                    coin = math.log10(raw_money + am * val)
                    db.execute("UPDATE coin_info SET logam = ? WHERE UserID = ? AND coin_name = '현금'", coin,
                               ctx.author.id)
                    if now_coin == am:
                        db.execute("DELETE FROM coin_info WHERE UserID = ? AND coin_name = ?", ctx.author.id, a2)
                    else:
                        db.execute("UPDATE coin_info SET logam = ? WHERE USERID = ? AND coin_name = ?",
                                   math.log10(now_coin - am),
                                   ctx.author.id, a2)
                    db.commit()
                    await send(ctx, "거래 완료! `커뉴야 코인`으로 현재 상황을 알아보세요")
        elif activity == "시세":
            embed = Embed(color=0xffcc4d, title="코인 시세")
            sisae = db.records("SELECT * FROM coins")
            for coin in sisae:
                if coin[0] == "화력코인":
                    embed.add_field(name=coin[0], value=f"현재 가격: {coin[1]:,} (변화량 {coin[3]:,}), 변동성: 알 수 없음",
                                    inline=False)
                else:
                    embed.add_field(name=coin[0], value=f"현재 가격: {coin[1]:,} (변화량 {coin[3]:,}), 변동성: {coin[2]}",
                                    inline=False)
            await send(ctx, embed=embed)
        elif activity == "룰렛":
            if a2 and a2 == '도움':
                await send(ctx, embed=Embed(color=0xffcc4d, title='커뉴봇 코인 룰렛 도움', description='코인으로 할 수 있는 도박 '
                                                                                             '기능이에요!\n\n공이 1부터 36까지의 수 중 랜덤한 수에 도달하게 되는데, 어디에 도달할지를 베팅하면 돼요. 베팅할 방법은 여러 가지가 있지만, 그 베팅이 맞을 확률이 낮을수록 '
                                                                                             '보상금도 그에 맞게 커져요!\n\n`커뉴야 코인 룰렛 도움`: 이 도움말을 표시합니다.\n`커뉴야 코인 룰렛 (걸돈)`: 룰렛 도박에 얼마를 걸지 정합니다.'))
                return
            c = randint(1, 36)
            try:
                a2 = int(a2)
                am = a2
            except:
                a2 = None
            if not a2:
                await send(ctx, "룰렛에 얼마를 걸으실 건가요?")
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        timeout=20,
                        check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                    )
                except asyncio.TimeoutError:
                    await send(ctx, "도박을 종료했어요.")
                    return
                try:
                    am = int(msg.content)
                except ValueError:
                    await send(ctx, "정수로만 입력해 주세요")
                    return
            net_worth = 0
            coin_info = db.records("SELECT coin_name, logam FROM coin_info WHERE UserID = ?", ctx.author.id)
            ac = 1
            for coin in coin_info:
                if coin[0] == "현금":
                    try:
                        net_worth += int(10 ** coin[1])
                        cash = int(10 ** coin[1])
                    except TypeError:
                        net_worth = 0
                        break
                else:
                    try:
                        net_worth += db.record("SELECT value FROM coins WHERE coin_name = ?", coin[0])[0] * int(
                            10 ** coin[1])
                        if int(10 ** coin[1]) != 0:
                            ac = 0
                    except TypeError:
                        net_worth = 0
                        break

            if am <= 0:
                await send(ctx, "걸 돈은 양수로만 입력해 주세요!")
                return
            if cash < am:
                await send(ctx, "그만큼을 걸 돈이 부족해요! 돈을 더 벌거나 가지고 있는 코인을 팔아 현금을 확보한 후 진행하세요")
                return
            await send(ctx, 
                f"{am:,} 커뉴코인을 걸어 룰렛을 진행해요. 어느 수에 베팅하실 건가요? (1부터 36 중에서)\n`홀수` (`홀`, `ㅎ`), `짝수` (`짝`, `ㅉ`)로 입력하거나 수 "
                f"하나만 입력하거나 수의 범위를 입력하실 수 있습니다. (예시: `홀수`, `6`, `6-9`)\n다만 성공확률이 1/2 이하이도록 베팅해야만 베팅 성공 시 배당금을 받을 수 있어요")
            try:
                bet = await self.bot.wait_for(
                    "message",
                    timeout=40,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
            except asyncio.TimeoutError:
                await send(ctx, "도박을 종료했어요.")
                return
            bet = bet.content
            try:
                bet = int(bet)
                if bet > 36:
                    await send(ctx, "올바르지 않은 입력이에요!")
                    return
                if c == bet:
                    wl = 36
                else:
                    wl = 0
            except ValueError:
                if bet in ['홀수', '홀', 'ㅎ']:
                    wl = 2 * (c % 2)
                elif bet in ['짝수', '짝', 'ㅉ']:
                    wl = 2 - 2 * (c % 2)
                else:
                    bc = re.compile("\d{1,2}[-]\d{1,2}")
                    if bc.match(bet):
                        hy = bet.index("-")
                        min_num = int(bet[:hy])
                        max_num = int(bet[hy + 1:])
                        if min_num > max_num or max_num > 36:
                            await send(ctx, "올바르지 않은 입력이에요!")
                            return
                        if c in (cl := range(min_num, max_num + 1)):
                            wl = int(36 / len(cl))
                        else:
                            wl = 0
                    else:
                        await send(ctx, "올바르지 않은 입력이에요!")
                        return
            if ac == 1 and am > (3 / 4) * net_worth and net_worth >= 100000000:
                l = grant_check("몰빵 가즈아", ctx.author.id)
                if l == 1:
                    await grant(ctx, "몰빵 가즈아", "코인 자산이 1억이 넘었고 전재산을 현금으로 인출한 상태에서 룰렛으로 전재산의 75% 이상을 거세요")
            if wl == 0:
                wt = f"수를 맞히지 못했어요... {am:,} 커뉴코인을 잃어 현재 남은 코인은 {cash - am:,} 코인이에요."
            else:
                wt = f"수를 맞히셨어요!!! {am * (wl - 1):,} 커뉴코인을 얻어 현재 남은 코인은 {cash + am * (wl - 1):,} 코인이에요."
            embed = Embed(color=0xffcc4d, title="룰렛 도박 결과!", description=f"당신은 {bet}에 걸었고, 공은 {c} 자리에 도달했어요!\n{wt}")
            await send(ctx, embed=embed)
            try:
                cash = math.log10(cash + am * (wl - 1))
            except ValueError:
                cash = -9999999999
            db.execute("UPDATE coin_info SET logam = ? WHERE UserID = ? AND coin_name = '현금'", cash, ctx.author.id)
            db.commit()
            if wl == 36:
                ag = grant_check("도박의 신", ctx.author.id)
                if ag == 1:
                    await grant(ctx, "도박의 신", "룰렛에서 숫자 하나에만 걸었을 때 도박에 승리하세요")
                return
        elif activity == "지원금":
            next_help = db.record("SELECT coin_help_time FROM games WHERE USERID = ?", ctx.author.id)[0]
            if datetime.now() < datetime.fromisoformat(next_help):
                await send(ctx, '지원금은 30분에 한 번만 받을 수 있어요!')
                return
            coin_info = db.records("SELECT coin_name, logam FROM coin_info WHERE UserID = ?", ctx.author.id)
            net_worth = self.calculate_net_worth(coin_info)
            if net_worth == -1:
                await send(ctx, '이걸 보시면 꼭 개발자에게 문의해주세요 좀 급한 상황입니다')
                return
            if net_worth < 1e6:
                help_money = int(max(1e6 - net_worth, 1e5))
            elif net_worth < 1e7:
                help_money = 100000
            else:
                help_money = randint(5000, 50000)
            cash = db.record("SELECT logam FROM coin_info WHERE UserID = ? AND coin_name = '현금'", ctx.author.id)[0]
            cash = math.log10(10 ** cash + help_money)
            db.execute("UPDATE coin_info SET logam = ? WHERE USerID = ? AND coin_name = '현금'", cash, ctx.author.id)
            db.execute("UPDATE games SET coin_help_time = ? WHERE UserID = ?",
                       (datetime.now() + timedelta(minutes=30)).isoformat(), ctx.author.id)
            db.commit()
            await send(ctx, f"지원금을 약 {help_money:,}만큼 받았어요!")
        elif activity == '자산':
            coin_info = db.records("SELECT coin_name, logam FROM coin_info WHERE UserID = ?", ctx.author.id)
            net_worth = self.calculate_net_worth(coin_info)
            if net_worth == -1:
                await send(ctx, '이걸 보시면 꼭 개발자에게 문의해주세요 좀 급한 상황입니다')
                return
            await send(ctx, f'현재 {ctx.author.name}님의 코인 총 자산은 {net_worth:,}(이)에요!')
        elif activity == '블랙잭':
            if not a2:
                await send(ctx, "`커뉴야 코인 블랙잭 (걸 돈)`")
                return
            elif a2 == '도움':
                await send(ctx, embed=Embed(color=0xffcc4d, title='커뉴봇 코인 블랙잭 도움', description='코인으로 할 수 있는 도박 기능이에요! '
                                                                                              '다만 룰렛과 다르게 완전한 운빨 게임이 아닌 만큼 0코인을 걸 수도 있어요.\n\n기본적인 목표는, 자신의 카드에 써 있는 값 총합이 21을 넘지 않으면서 21에 최대한 '
                                                                                              '가까워지도록 카드를 뽑는 거에요. (J,Q,K는 항상 10으로 간주되고 에이스는 11으로 간주되거나 1로 간주돼요.)\n처음에 플레이어와 딜러는 각각 카드를 2장씩 뽑고 플레이어의 '
                                                                                              '카드는 둘 모두, 딜러의 카드는 하나만 볼 수 있어요. 만약 이때 플레이어의 카드 값 총합이 21이라면 가장 좋은 패인 블랙잭을 얻은 것이고, 즉시 승리하며 건 돈의 1.5배를 '
                                                                                              '받게 돼요!\n플레이어는 자신과 딜러의 카드를 보고 카드를 더 뽑을지 그만 뽑을지를 결정할 수 있어요. 카드는 원하는 만큼 더 뽑을 수 있지만 값 총합이 21이 넘어버리면 '
                                                                                              '버스트되었다고 부르고 즉시 패배해요.\n플레이어가 카드를 그만 뽑기로 결정했다면 이제 딜러의 차례에요. 딜러는 플레이어의 패와 관계없이 무조건 자신의 손에 든 패의 값 총합이 17 '
                                                                                              '이상이 될 때까지 카드를 뽑아요. 물론 이 과정에서 딜러의 패의 값 총합이 21을 넘는다면 딜러가 버스트되고 플레이어는 즉시 승리해요.\n둘 모두의 차례가 끝나면, '
                                                                                              '즉시 승리/패배하는 조건이 만족되지 않았다고 가정할 때 플레이어와 딜러 손에 든 패의 값 총합을 비교해서 더 큰 쪽이 이겨요.\n\n`히트`하면 추가로 카드 하나를 '
                                                                                              '뽑아요.\n`스탠드`하면 카드를 그만 뽑고 딜러의 차례로 넘겨요.\n`더블 다운`하면 판돈을 2배로 늘리고, 카드를 한 장 더 뽑은 뒤 딜러의 차례로 넘겨요.\n\n`커뉴야 코인 '
                                                                                              '블랙잭 (걸 돈)`으로 게임을 시작하세요!'))
                return
            elif not a2.isdigit():
                await send(ctx, "`커뉴야 코인 블랙잭 (걸 돈)`")
                return
            pan_don = int(a2)
            cash = round(
                10 ** db.record("SELECT logam FROM coin_info WHERE coin_name = '현금' AND UserID = ?", ctx.author.id)[0])
            if pan_don < 0:
                await send(ctx, "걸 돈은 양수로만 입력해 주세요!")
                return
            if cash < pan_don:
                await send(ctx, '그만큼을 걸 돈이 부족해요! 돈을 더 벌거나 가지고 있는 코인을 팔아 현금을 확보한 후 진행하세요')
                return
            bj_cards = ['♠ A', '♠ 2', '♠ 3', '♠ 4', '♠ 5', '♠ 6', '♠ 7', '♠ 8', '♠ 9', '♠ 10', '♠ J', '♠ Q', '♠ K',
                        '♦ A', '♦ 2',
                        '♦ 3', '♦ 4', '♦ 5', '♦ 6', '♦ 7', '♦ 8', '♦ 9', '♦ 10', '♦ J', '♦ Q', '♦ K', '♥ A', '♥ 2',
                        '♥ 3', '♥ 4',
                        '♥ 5', '♥ 6', '♥ 7', '♥ 8', '♥ 9', '♥ 10', '♥ J', '♥ Q', '♥ K', '♣ A', '♣ 2', '♣ 3', '♣ 4',
                        '♣ 5', '♣ 6',
                        '♣ 7', '♣ 8', '♣ 9', '♣ 10', '♣ J', '♣ Q', '♣ K', '♠ A', '♠ 2', '♠ 3', '♠ 4', '♠ 5', '♠ 6',
                        '♠ 7', '♠ 8',
                        '♠ 9', '♠ 10', '♠ J', '♠ Q', '♠ K', '♦ A', '♦ 2', '♦ 3', '♦ 4', '♦ 5', '♦ 6', '♦ 7', '♦ 8',
                        '♦ 9', '♦ 10',
                        '♦ J', '♦ Q', '♦ K', '♥ A', '♥ 2', '♥ 3', '♥ 4', '♥ 5', '♥ 6', '♥ 7', '♥ 8', '♥ 9', '♥ 10',
                        '♥ J', '♥ Q',
                        '♥ K', '♣ A', '♣ 2', '♣ 3', '♣ 4', '♣ 5', '♣ 6', '♣ 7', '♣ 8', '♣ 9', '♣ 10', '♣ J', '♣ Q',
                        '♣ K', '♠ A',
                        '♠ 2', '♠ 3', '♠ 4', '♠ 5', '♠ 6', '♠ 7', '♠ 8', '♠ 9', '♠ 10', '♠ J', '♠ Q', '♠ K', '♦ A',
                        '♦ 2', '♦ 3',
                        '♦ 4', '♦ 5', '♦ 6', '♦ 7', '♦ 8', '♦ 9', '♦ 10', '♦ J', '♦ Q', '♦ K', '♥ A', '♥ 2', '♥ 3',
                        '♥ 4', '♥ 5',
                        '♥ 6', '♥ 7', '♥ 8', '♥ 9', '♥ 10', '♥ J', '♥ Q', '♥ K', '♣ A', '♣ 2', '♣ 3', '♣ 4', '♣ 5',
                        '♣ 6', '♣ 7',
                        '♣ 8', '♣ 9', '♣ 10', '♣ J', '♣ Q', '♣ K', '♠ A', '♠ 2', '♠ 3', '♠ 4', '♠ 5', '♠ 6', '♠ 7',
                        '♠ 8', '♠ 9',
                        '♠ 10', '♠ J', '♠ Q', '♠ K', '♦ A', '♦ 2', '♦ 3', '♦ 4', '♦ 5', '♦ 6', '♦ 7', '♦ 8', '♦ 9',
                        '♦ 10', '♦ J',
                        '♦ Q', '♦ K', '♥ A', '♥ 2', '♥ 3', '♥ 4', '♥ 5', '♥ 6', '♥ 7', '♥ 8', '♥ 9', '♥ 10', '♥ J',
                        '♥ Q', '♥ K',
                        '♣ A', '♣ 2', '♣ 3', '♣ 4', '♣ 5', '♣ 6', '♣ 7', '♣ 8', '♣ 9', '♣ 10', '♣ J', '♣ Q', '♣ K']
            shuffle(bj_cards)
            my_cards = []
            my_card_values = []
            dealer_cards = []
            dealer_card_values = []
            for _ in range(2):
                card = bj_cards.pop()
                my_cards.append(card)
                my_card_values.append(card.split()[1])
            for _ in range(2):
                card = bj_cards.pop()
                dealer_cards.append(card)
                dealer_card_values.append(card.split()[1])
            bj_check = 1
            wl = -1
            turn_end_check = 0
            double_down = -1
            while True:
                embed = Embed(color=0xffcc4d, title=f'커뉴봇 블랙잭: {ctx.author.display_name}')
                my_status, my_value = calc_card_value(my_card_values)
                dealer_status, dealer_value = calc_card_value([dealer_card_values[0]])
                if turn_end_check:
                    break
                embed.add_field(name='현재 카드', value='\n'.join(my_cards) + f'\n총 카드 값: {my_status}{my_value}')
                embed.add_field(name='딜러 카드', value=dealer_cards[0] + f'\n???\n총 카드 값: {dealer_status}{dealer_value}')
                if bj_check == 1 and my_value == 21:
                    actual_dealer_status, actual_dealer_value = calc_card_value(dealer_card_values)
                    if actual_dealer_value == 21:
                        wl = 1
                    else:
                        wl = 2.5
                    turn_end_check = 1
                    l = grant_check("블랙잭!", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "블랙잭!", "`커뉴야 코인 블랙잭`에서 블랙잭 21 카드패를 가지세요")
                elif my_value > 21:
                    wl = 0
                    turn_end_check = 1
                else:
                    if double_down == -1:
                        if cash >= pan_don * 2:
                            possible_responses = ['히트', 'ㅎ', 'ㅎ😩ㅎ', 'hit', 'h', '스탠드', 'ㅅ', 'stand', 's', '더블다운', 'ㄷ',
                                                  'double down', 'dd']
                        else:
                            possible_responses = ['히트', 'ㅎ', 'ㅎ😩ㅎ', 'hit', 'h', '스탠드', 'ㅅ', 'stand', 's']
                    else:
                        possible_responses = ['스탠드', 'ㅅ', 'stand', 's']
                    embed.add_field(name='가능한 행동들', value='히트, ㅎ, hit, h' * (
                                'h' in possible_responses) + '\n스탠드, ㅅ, stand, s' + '\n더블다운, ㄷ, double down, dd' * (
                                                                      'dd' in possible_responses) + '\n30초가 지나도 답변이 없다면 스테이로 간주합니다.',
                                    inline=False)
                    await send(ctx, embed=embed)
                    msg = ''
                    try:
                        msg = await self.bot.wait_for(
                            "message",
                            timeout=30,
                            check=lambda
                                message: message.author.id == ctx.author.id and message.content.lower() in possible_responses
                        )
                        msg = msg.content.lower()
                    except asyncio.TimeoutError:
                        turn_end_check = 1
                    if not turn_end_check:
                        if msg in ['히트', 'ㅎ', 'ㅎ😩ㅎ', 'hit', 'h']:
                            card = bj_cards.pop()
                            my_cards.append(card)
                            my_card_values.append(card.split()[1])
                            if msg == 'ㅎ😩ㅎ':
                                l = grant_check("ㅎ😩ㅎ", ctx.author.id)
                                if l == 1:
                                    await grant(ctx, "ㅎ😩ㅎ", "히트라고 알아듣겠습니다!")
                        elif msg in ['스탠드', 'ㅅ', 'stand', 's']:
                            turn_end_check = 1
                        elif msg in ['더블다운', 'ㄷ', 'double down', 'dd']:
                            double_down = 1
                            pan_don *= 2
                            card = bj_cards.pop()
                            my_cards.append(card)
                            my_card_values.append(card.split()[1])
                        else:
                            await send(ctx, '예기치 않게 종료됐어요. 비상!!!!!!!!')
                            return
                bj_check = 0
            if wl == -1:
                while True:
                    dealer_status, dealer_value = calc_card_value(dealer_card_values)
                    if dealer_value >= 17:
                        break
                    else:
                        card = bj_cards.pop()
                        dealer_cards.append(card)
                        dealer_card_values.append(card.split()[1])
                if dealer_value > 21 or my_value > dealer_value:
                    wl = 2
                elif my_value == dealer_value:
                    wl = 1
                else:
                    wl = 0
            dealer_status, dealer_value = calc_card_value(dealer_card_values)
            embed.add_field(name='현재 카드', value='\n'.join(my_cards) + f'\n총 카드 값: {my_status}{my_value}')
            embed.add_field(name='딜러 카드', value='\n'.join(dealer_cards) + f'\n총 카드 값: {dealer_status}{dealer_value}')
            if wl > 1:
                result = '승리'
            elif wl == 1:
                result = '푸시(무승부)'
            else:
                result = '패배'
            cash_delta = int(pan_don * (wl - 1))
            embed.add_field(name='결과', value=f'{result}, 수익금 {cash_delta:,} -> 남은 돈 {cash + cash_delta:,}',
                            inline=False)
            await send(ctx, embed=embed)
            try:
                cash = math.log10(cash + cash_delta)
            except ValueError:
                cash = -99999999
            db.execute("UPDATE coin_info SET logam = ? WHERE UserID = ? AND coin_name = '현금'", cash, ctx.author.id)
            db.commit()
        elif activity == '그래프':
            fire_data = db.records("SELECT fire FROM serverstat ORDER BY Day DESC limit 11")
            today_firecoin = db.record("SELECT value FROM coins WHERE coin_name = '화력코인'")[0]
            data = [today_firecoin]
            for i in range(9):
                data.append(round((data[-1] + 8) * ((fire_data[i + 2][0] / fire_data[i + 1][0]) ** 0.55)))
            data = data[::-1]
            x = np.array(range(1, 11))
            y = np.array(data)
            model = make_interp_spline(x, y)
            xs = np.linspace(1, 10, 500)
            ys = model(xs)
            plt.rc('font', family='Malgun Gothic')
            plt.rcParams['axes.unicode_minus'] = False

            plt.plot(xs, ys)

            plt.title('최근 10일간 화력코인 가격 변화')
            plt.xlabel("시간 (값은 의미없음)")
            plt.ylabel("가격")
            plt.savefig(u := r"C:\Users\namon\PycharmProjects\discordbot\lib\images\19201080_temp.png")
            plt.clf()
            await ctx.channel.send(file=File(u))
        else:
            await send(ctx, "`커뉴야 코인 [(빈 칸)/투자/시세/룰렛/블랙잭/지원금/자산/그래프]`")

    @command(name="스펙")
    @cooldown(1, 18, BucketType.user)
    async def spec(self, ctx, c: Optional[str]):
        l = grant_check("스펙 확인", ctx.author.id)
        if l == 1:
            await grant(ctx, "스펙 확인",
                        "`커뉴야 스펙`명령어로 자신의 스펙을 확인하세요 (`커뉴야 도전과제 목록 3`으로 얻을 수 있는 도전과제는 모두 이 명령어 또는 `커뉴야 지분`명령어를 기반으로 해요. 가끔은 이 명령어를 확인하시는 걸 추천드려요!)")
        embed = Embed(color=0x9affff, title=f"{ctx.author}님의 스펙")
        cmd_infos = db.records("SELECT command, uses FROM cmd_uses WHERE USERID = ? ORDER BY uses DESC", ctx.author.id)
        total_uses = 0
        if not c:
            sbjb_uses = 0
            for cmd_info in cmd_infos:
                total_uses += cmd_info[1]
                if cmd_info[0] == "사귀자" and cmd_info[1] >= 100:
                    l = grant_check("돈으로 살 수 없는 것 그렇기에 더 소중한 것", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "돈으로 살 수 없는 것 그렇기에 더 소중한 것", "`커뉴야 사귀자`명령어를 100번 이상 사용하세요")
                if cmd_info[0] == "😩" and cmd_info[1] >= 100:
                    l = grant_check("피겅", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "피겅", "`커뉴야 :weary:` 명령어를 100번 이상 사용하세요")
                if cmd_info[0] in ["서바준보", "오타원본"]:
                    sbjb_uses += cmd_info[1]
            if sbjb_uses >= 500:
                l = grant_check("뭔 오태민 하면 나오냐", ctx.author.id)
                if l == 1:
                    await grant(ctx, "뭔 오태민 하면 나오냐", "`커뉴야 서바준보` 명령어와 `커뉴야 오타원본` 명령어 사용 횟수의 합이 750을 넘기세요")
            if len(cmd_infos) >= 5 and cmd_infos[4][1] >= 500:
                l = grant_check("광기", ctx.author.id)
                if l == 1:
                    await grant(ctx, "광기", "서로 다른 5개의 커맨드를 500번 이상 사용하세요")
            if len(cmd_infos) >= 10 and cmd_infos[9][1] >= 500:
                l = grant_check("진짜 광기", ctx.author.id)
                if l == 1:
                    await grant(ctx, "진짜 광기", "서로 다른 10개의 커맨드를 500번 이상 사용하세요")
            game_info = db.record("SELECT * FROM games WHERE UserID = ?", ctx.author.id)
            coin_info = db.records("SELECT coin_name, logam FROM coin_info WHERE UserID = ?", ctx.author.id)
            ach_count = db.record("SELECT count(*) FROM achievement_progress WHERE UserID = ?", ctx.author.id)[0]
            conupink_exp = db.record("SELECT total_exp FROM conupink_user_info WHERE UserID = ?", ctx.author.id)
            if not conupink_exp:
                conupink_exp = '`커뉴야 커뉴핑크`명령어가 **진짜로** 출시됐습니다. 한 번 사용해 보세요!'
            else:
                conupink_exp = str(conupink_exp[0])
            net_worth = self.calculate_net_worth(coin_info)
            if net_worth == -1:
                net_worth = '이거 보시면 개발자에게 최대한 빨리 문의해주세요'
            net_worth = str(net_worth)
            embed.add_field(name="총 커맨드 사용 횟수", value=str(total_uses))
            embed.add_field(name="가장 많이 사용한 커맨드", value=f"{cmd_infos[0][0]} : {cmd_infos[0][1]}회")
            embed.add_field(name="발견한 커맨드들", value=f"{len(cmd_infos)} / {len(self.bot.commands)}")
            embed.add_field(name="`커뉴야 심심해`에서 발견한 TMI들", value=f'{game_info[27].count("1")}종류')
            embed.add_field(name="묵찌빠 점수", value=str(game_info[2]))
            embed.add_field(name="퀴즈 점수", value=str(game_info[6]))
            embed.add_field(name="퀴즈 뮤트 주제", value=str(game_info[9]))
            embed.add_field(name="오목 점수", value=str(game_info[8]))
            embed.add_field(name="코인 총 자산", value=str(net_worth))
            embed.add_field(name="달성한 도전 과제", value=f"{str(ach_count)} / 123")
            embed.add_field(name='뀨 보유량', value=str(game_info[18]))
            embed.add_field(name='커뉴핑크 경험치', value=conupink_exp)
            try:
                print(self.bot.get_guild(743101101401964647).get_member(ctx.author.id).display_name)
                embed.add_field(name="잡초키우기 레벨", value=str(game_info[4]))
                embed.add_field(name="잡초키우기 비료 개수", value=str(game_info[5]))
                embed.add_field(name="우주탐험 레벨", value=str(game_info[3]))
                embed.add_field(name="공식서버 레벨", value=
                db.record("SELECT Level FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", ctx.author.id)[0])
                embed.add_field(name="공식서버 경험치 부스트", value=
                db.record("SELECT XPBoost FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", ctx.author.id)[
                    0])
                embed.add_field(name="공식서버 돈", value=
                db.record("SELECT Money FROM exp WHERE UserID = ? AND GuildID = 743101101401964647", ctx.author.id)[0])
            except AttributeError:
                embed.add_field(name="공식서버 관련 스탯", value="공식서버에 입장하지 않았습니다. `커뉴야 공식서버`로 공식서버에 입장 후 6종류의 스펙 지수를 더 확인하세요")
            await send(ctx, embed=embed)
            if total_uses > 1000:
                l = grant_check("단골 사용자 1", ctx.author.id)
                if l == 1:
                    await grant(ctx, "단골 사용자 1", "커맨드를 1000회 이상 사용하세요")
                if total_uses > 10000:
                    l = grant_check("단골 사용자 2", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "단골 사용자 2", "커맨드를 10000회 이상 사용하세요")
            if len(cmd_infos) >= 50:
                l = grant_check("명령어 마스터", ctx.author.id)
                if l == 1:
                    await grant(ctx, "명령어 마스터", "서로 다른 커맨드를 50개 이상 사용하세요")
                if len(cmd_infos) >= 100:
                    l = grant_check("명령어의 전설", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "명령어의 전설", "서로 다른 커맨드를 100개 이상 사용하세요")
                    if len(cmd_infos) == len(self.bot.commands):
                        l = grant_check("명령어의 신", ctx.author.id)
                        if l == 1:
                            await grant(ctx, "명령어의 신", "모든 커맨드를 발견하세요")
            if total_uses < 100 or total_uses >= 10000:
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        timeout=5,
                        check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                    )
                except asyncio.TimeoutError:
                    return
                if msg.content == "으으ㅐ":
                    l = grant_check("으으ㅐ", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "으으ㅐ",
                                    "`커뉴야 스펙` 명령어에서 커맨드 사용 횟수가 100회 미만 또는 10000회 이상일 때 스펙 명령어를 사용한 직후 으으ㅐ라고 입력하세요")
        else:
            i = 0
            for cmd_info in cmd_infos:
                total_uses += cmd_info[1]
                i += 1
                if i <= 24:
                    embed.add_field(name=f"`커뉴야 {cmd_info[0]}` 명령어 사용 횟수", value=cmd_info[1])
            embed.add_field(name="총 커맨드 사용 횟수", value=str(total_uses))
            await send(ctx, embed=embed)

    @command(name="끼임해제")
    async def reset_room(self, ctx):
        room_number = db.record("SELECT room_number FROM games WHERE USerID = ?", ctx.author.id)[0]
        try:
            if room_number >= 10000000:
                await send(ctx, "`커뉴야 랜덤채팅 종료`")
                return
        except TypeError:
            await send(ctx, "아무 방에도 들어가 있지 않아요!")
            return
        with ctx.channel.typing:
            room_info = db.record("SELECT people_in FROM rooms WHERE room_number = ?", room_number)[0]
            if ctx.author.id in (people := room_info.split(",")):
                people.remove(ctx.author.id)
                db.execute("UPDATE rooms SET people_in = ? WHERE room_number = ?", people.join(","), room_number)
            db.execute("UPDATE games SET room_number = NULL WHERE userID = ?", ctx.author.id)
            db.commit()
            await send(ctx, "끼임해제가 완료됐어요!")

    @command(name="어디")
    async def check_room(self, ctx):
        room_number = db.record("SELECT room_number FROM games WHERE USerID = ?", ctx.author.id)
        try:
            await send(ctx, room_number[0])
        except:
            await send(ctx, "아무 방에도 들어가 있지 않아요!")

    @command(name="디엠테스트")
    async def dm_test(self, ctx):
        await send(ctx, "디엠이 왔는지 확인해 보세요!")
        try:
            await ctx.author.send("뀨우? >w<")
        except Forbidden:
            await send(ctx, ":weary:")

    @command(name="지분")
    @cooldown(4, 1, BucketType.user)
    async def jb(self, ctx, *, test: str):
        try:
            command_name = self.bot.get_command(test).name
        except AttributeError:
            await send(ctx, "존재하지 않는 커맨드에요!")
            return

        total_uses = int(db.record("SELECT sum(uses) FROM cmd_uses WHERE command = ?", command_name)[0])
        try:
            my_uses = int(
                db.record("SELECT uses FROM cmd_uses WHERE USERID = ? AND command = ?", ctx.author.id, command_name)[0])
        except TypeError:
            my_uses = 0
        embed = Embed(color=0x9affff, title=f"{test} 명령어에 대한 지분 정보")
        embed.add_field(name="현재 당신의 사용 횟수", value=str(my_uses), inline=False)
        embed.add_field(name="이 커맨드의 총 사용 횟수", value=str(total_uses), inline=False)
        embed.add_field(name="당신이 차지하고 있는 지분", value=f"{round(my_uses / total_uses * 100, 3)}%", inline=False)
        embed.set_footer(text="퍼센트가 한 자리 수여도 생각보다 높을 수 있대요...")
        if my_uses != 0:
            show_rank_check = db.record("SELECT user_setting FROM games WHERE USERID = ?", ctx.author.id)[0]
            if show_rank_check & 1024:
                cmd_use_info = db.records("SELECT uses FROM cmd_uses WHERE command = ? ORDER BY uses DESC",
                                          command_name)
                min_rank = 0
                max_rank = 0
                for i in range(len(cmd_use_info)):
                    if cmd_use_info[i][0] == my_uses and min_rank == 0:
                        min_rank = i + 1
                    elif cmd_use_info[i][0] != my_uses and min_rank != 0:
                        max_rank = i
                        break
                if max_rank == 0:
                    max_rank = len(cmd_use_info) - 1
                same_use_count = max_rank - min_rank + 1
                if len(cmd_use_info) == 1:
                    same_use_count = 1
                if same_use_count == 1:
                    embed.add_field(name='당신의 지분 순위', value=f'{min_rank}위', inline=False)
                else:
                    embed.add_field(name='당신의 지분 순위', value=f'공동 {min_rank} (사용횟수 같은 사람 {same_use_count}명)',
                                    inline=False)
                if randint(1, 15) == 1:
                    embed.set_footer(text='개인정보처리방침상 다른 사람의 지분 순위는 알 수 없어요!')
        await send(ctx, embed=embed)
        if my_uses / total_uses * 100 >= 75 and my_uses >= 200:
            l = grant_check("압도적 지분가", ctx.author.id)
            if l == 1:
                await grant(ctx, "압도적 지분가", "한 명령어에서 지분 75% 이상을 보유하며 그 동시에 사용횟수 200번을 넘기세요")

    @command(name="심심해")
    @cooldown(1, 90, BucketType.default)
    async def tmi(self, ctx, extra: Optional[str]):
        tracker = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0] & 16384
        tmi_list = ["1. 이 자리는 예전에 어떤 말이 있었을까요? 더 이상 참말이 아닌 말이 이곳에 적혀 있었던 거 같네요...",
                    "2. 공식서버의 맨 위 채널은 관리자 전용 채널인데 이름이 \"엄\"이래요", "3. 공식서버의 맨 처음 이름은 `다같이 "
                                                                 "게임합시다`였지만 딱히 게임 서버 느낌이 나지 않아 첫 멤버를 불러오기 전에 이름을 바꿨대요.",
                    "4. 공식서버의 메인채팅방의 첫챗은 영어래요.", "5. 멤버가 2명일 시절 공식서버는 이름이 "
                                                 "`이름 추천좀` 이었고 그 당시 서버장의 닉네임은 `프사 추천좀`이었대요.",
                    "6. 옛날에는 스탭 역할에 초록 이름색이 있었대요. 그러나 이름색을 마음대로 바꾸는 시스템이 있기에 첫 스탭이 "
                    "임명되기 전 스탭 이름색이 사라졌대요.",
                    "7. 서버 초기부터 있었던 칭호 역할과 지금 있는 칭호 역할 중 겹치는 역할은 스탭 역할과 초대자 역할들밖에 없대요.",
                    "8. 지금 밴당한 사람이 "
                    "매우 많지만 그 중 들낙으로 밴당한 사람은 의외로 200명이 채 안 된대요. 나머지는 무슨 사유일까요?",
                    "9. 처벌 내역에서 많이 출몰하는 봇들은 시간순으로 Arcane에서 Dyno로, "
                    "Dyno에서 커뉴봇으로 점차 바뀌어 왔지만 실제로 가장 많은 사람을 서버에서 차단시킨 봇은 지금 서버에 있지도 않은 MEE6이래요.",
                    "10. 서버 초기에는 테러의 위험이 높았대요. 그래서 "
                    "테러를 미연에 방지하기 위해 약 530명 정도의 매우 많은 사용자가 차단되었대요.",
                    "11. 고급 스탭 이상 전용 사설 채널인 권력의땅은 2020년 8월 31일부터 있었는데, "
                    "실제로 서버장을 제외한 사람이 그 채널에 정식으로 가입한 것은 채널이 생긴 지 세 달도 더 지난 후였대요.",
                    "12. 권력의땅에 서버장과 부계정을 제외하고 처음으로 입장한 사람은 그 당시 고급 "
                    "스탭은커녕 스탭조차 아니었대요.", "13. 서버가 생긴 직후 규칙은 7개가 있었고 서버 보안을 다뤘던 임시 조항인 999번 규칙이 있었대요.",
                    "14. 현재 서버사진은 M20 즉 "
                    "삼렬성운이래요.", "15. 매일매일 서버스탯 초기에는 금성채널에서 하루 동안 보내진 메세지의 개수도 서버스탯 계산에 포함시켰대요.",
                    "16. 칭호도감 채널은 옛날에 전혀 다른 서버 가이드 "
                    "목적의 채널로 쓰였대요. 그러나 서버가 바뀌며 이전 가이드와는 맞지 않게 되었고 지금의 칭호도감으로 채널 사용처가 바뀌게 됐대요.",
                    "17. 규칙 채널이 맨 처음 있었을 때는 채널명이 규칙과 "
                    "정보 였고 서버 규칙 이외에 전반적인 개요도 같이 설명했대요.",
                    "18. 1주년 이벤트 때 잠깐 있었다가 없어진 채널인 준비중(역사관)은 공식서버의 봇 제외 멤버수가 200명을 돌파하면 "
                    "모두에게 공개될 예정이래요.", "19. 이 자연수는 개발자가 두 번째로 좋ㅇ...",
                    "20. 섭장님에게 잘못 하다간 끝장이 나머린다 맨이야 그러니 조심하라맨이야",
                    "21. 2021년 초에는 "
                    "서버 화력도 적었고 멤버 유입도 없었대요. 그래서 슬픈 서버장은 그동안 서버스탯을 기록하지 않았대요.",
                    "22. 현재 서버-건의질문 이라는 이름의 채널은 건의와-질문 -> 건의사항 -> "
                    "서버-건의질문 으로 이름이 바뀌어왔고 현재의 이름을 얻기 전까지는 서버 건의뿐만아니라 커뉴봇 건의도 다 그곳에서 받았대요.",
                    "23. 사실 지구로부터 떨어진 거리는 수성보다 금성이 더 멀대요. "
                    "채널 순서가 그렇게 정해진 이유겠죠?",
                    "24. 커스텀봇 채널로 쓰고 있는 세레스와 에리스는 사실 붙어 있으면 안 된대요. 세레스는 화성과 목성 사이 소행성대에 위치해 있지만 에리스는 "
                    "해왕성보다 더 멀리 카이퍼벨트에 있대요!",
                    "25. 커뉴의 잡소리가 시작되기 전까지는 그 채널이 고렙공지 채널이었대요. 실제로 고렙공지 채널을 또 분리시키기 전에는 잡소리 중간중간에 고렙공지가 "
                    "있다죠.",
                    "26. 예전에는 게임채널들의 정렬 순서가 화력이 아닌 해당 게임의 서버 내 인기도였는데, 채널마다 고정메세지에 이 게임을 하는 사람은 체크 반응을 달아 달라는 메세지가 있어 그 "
                    "반응 개수 순으로 순서를 배열했대요. 지금도 오래된 채널에 가면 그 흔적이 남아 있다네요!",
                    "27. 예전에는 유튜브 구독자가 10명만 돼도 주던 칭호가 있었대요. 서버 역사상 가장 얻기 쉬운 "
                    "칭호였다죠.", "28. 공식서버에서 가장 유명한 애교들 중 하나인 피자애교를 커뉴봇한테 부려보세요.",
                    "29. 커뉴봇의 서로 다른 명령어들 중 60%는 대화형 명령어래요. 명령어를 모두 찾는 "
                    "게 거의 불가능할 정도로 어려운 것도 그것 때문이에요.",
                    "30. 커뉴봇의 상태메세지를 10분마다 자동으로 업데이트하기 전까지는 `커뉴야 상메업뎃`이라는 지금은 없어진 명령어로 수동으로 상메를 업데이트했대요.",
                    "31. 한 번은 퀴즈 문제 정보가 있는 데이터베이스에서 데이터 절반 이상이 갑자기 없어졌대요. 이 사건도 백업을 해 놓았기에 무사한 거였으니까 저장과 백업은 제발 생활화하세요.",
                    "32. 이 명령어와 같은 업데이트에서 나온 레벨공식 명령어는 사실 봇 개발 초기부터 계획된 기능이었대요.",
                    "33. 커뉴봇 오픈베타의 프사 출처는 개발자 여자친구의 손가락이래요.",
                    "34. 사실 !커뉴봇과 커뉴봇 오픈베타 말고 커뉴봇이 하나 더 있대요. 강화와 서버강화 명령어가 처음 나오기 전 해당 기능을 테스트할 때 썼었대요.",
                    "35. 예전에 `커뉴야 강화`기능은 서버강화처럼 한 번에 한 레벨씩만 올라갔고 아이템 이름도 못 정했으며 심지어 강화하는 데 아이템 레벨/5 만큼의 돈이 들었대요.",
                    "36. `커뉴야 애교`명령어를 쓰면 돈 50만을 내면 볼 수 있다고 오는 답변은 처음에는 대화 명령어 공모 이벤트 때 나온 아이디어로 장난이었지만 이후 실제로 돈 50만을 내면 도전과제와 함께 영구적으로 봇이 애교를 부려주는 기능으로 진화했대요.",
                    "37. 사설 채널에 접근할 수 있는 최소레벨은 6에서 4로, 4에서 2로 계속 줄어들었대요.",
                    "38. 한 번은 유저들이 봇 커맨드를 도배라고 말할 수 있을 정도로 써대는 바람에 봇이 잠시 IP밴을 먹은 적도 있대요.",
                    "39. 2020년 추석 당시 서버가 처음으로 우주 테마가 되었고 그때의 이름은 우주 전체를 하나의 디코섭 안에 담았다 해서 농축된 우주 즉 Condensed Universe였대요.",
                    "40. 여태껏 서버 이름은 6번이나 바뀌었지만 서버 사진은 딱 한 번밖에 바뀐 적이 없대요.",
                    "41. 예전에는 경험치를 선물하는 기능이 있었는데 한 유저가 또다른 유저에게 과도한 양의 경험치를 선물했고 레벨이 과하게 올라버리는 바람에 해당 기능을 삭제하고 선물로 오고간 경험치 모두두를 롤백하는 조치를 취했대요.",
                    "42. 역할받기 채널에서 초고렙공지 알림은 62렙 이상만 접근 가능이라고 나와 있지만 접근 가능한 최소레벨이 바뀐 지 엄청 오래됐대요.",
                    "43. 우주탐험이나 잡초키우기를 하던 중 매크로를 사용한 것이 들통난 사례는 두 번 있었는데, 매크로로 인해 레벨은 굉장히 빨리 올랐지만 누구도 넘을 수 없는 1등의 벽이 있어 그 벽을 넘지는 못했대요.",
                    "43. 서버 내에서는 멤버가 100명, 200명을 돌파하기 직전에 100번째, 200번째 멤버를 데려오면 보상을 주겠다며 이벤트를 열었는데, 두 번 다 부계정으로 어뷰징을 해서 데려온 것이 들통났고 스탭 해고나 장기 격리, 패시브로 민심 하락 등 결국 큰 벌을 받았대요.",
                    "44. 격리를 당하게 되면 공지를 포함해 거의 아무 채널도 볼 수 없게 되고 전용 감옥채널만 보이게 되는데, 그 채널은 관리자와 처벌 대상자가 아니면 누구도 볼 수 없고 여태껏 본 사람도 4명밖에 없대요.",
                    "45. 커뉴의 잡소리 모음 채널의 채널주제는 9개월 넘도록 바뀐 적이 없대요. 지금 채널의 사용처와 전혀 다른 게 그것 때문일까요?",
                    "46. 이스터 에그 도전과제들은 이름 안에 달성법이 어느 정도 들어 있는 것들이 있지만, 이스터 에그 도전과제가 아니어도 가끔은 이름 안에 쉬운 달성법을 숨겨 놓는 경우가 있대요.",
                    "47. 공식서버에서 보내신 메세지 중 45퍼센트 이상이 수성에서 보내졌고, 다른 커맨드방에서 보내진 메세지까지 합하면 총 메세지 개수의 60%에 육박한대요. 서버스탯이 과연 정말로 의미있을까요?",
                    "48. 지금 커뉴봇 명령어를 과하게 쓰는 사람들은 다 나빠요. 원래 그 기능은 디탕이 되라고 만든 기능이 아니에요...",
                    "49. 만약 20번 TMI를 제외한 TMI에서 오타를 발견한다면 문의해 주세요",
                    "50. 봇 커맨드 사용횟수를 따져 보면 가장 많이 쓰이는 10종류의 커맨드가 전체 커맨드 사용횟수의 약 90%를 차지한대요.",
                    "51. 잡초키우기나 퀴즈 처럼 다른 사람의 아이디어로 만들어진 기능들은 기능 추천자가 해당 기능을 대표하는 색을 정할 수 있대요. 기능 추천 한 번 해 보시는 것은 어때요?",
                    "52. `커뉴야 `와 `ㅋ` 말고도 봇 접두사가 하나 더 있다던데...",
                    "53. 실시간 리더보드 메세지가 처음 보내진 시점은 3월 25일 3시 25분이래요. 노린건가",
                    "54. 커뉴봇이 가진 첫 태그는 지금의 0898이 아닌 4893이었지만 어쩌다 보니 태그가 바뀌어버렸대요. 나중에도 태그가 또 바뀌게 될까요?",
                    "55. 봇이 생긴 그날 봇에게 `커뉴야`라고 말하면 `뀨?`라고 대답했대요.",
                    "56. 여러분들이 보내오는 퀴즈들 중 4분의 1은 문제 푸는 데 영향을 주는 오타가 있거나 취소할려 했지만 그냥 내버린 경우래요. 퀴즈는 제발 생각하고 내 주세요...",
                    "57. 이 명령어의 쿨타임은 100초이고 모두가 쿨타임을 공유한대요. 컨텐츠가 너무 빨리 소비될까봐 일부러 쿨타임을 길게 설정했으니 양해해 주세요!",
                    "58. 서버의 가장 유명한 오타들 중 하나인 `씨밧`을 커뉴봇에게 외쳐보세요.",
                    "59. 견우성(알타이르)와 직녀성(베가), 미자르와 알코르는 얽힌 신화가 있어 보통 두 별이 같이 언급된대요. 그러면 다음이 채널이 생길 때...",
                    "60. 개발자의 연애는 9월 17일인 고백데이이자 16렙 이상부터 볼 수 있는 커뉴의 잡소리 200일차인 날부터 시작되었대요. 그런데 156일차를 두 번 써서 하루가 밀리게 되어 정확히는 잡소리 201일차인 날부터 사귀기 시작했대요.",
                    "61. 서버 초기 5번 규칙은 초등학생 유저의 활동을 막았었대요.",
                    "62. 원하는 사람을 원하는 채널에서 3일 동안 뮤트시키는 기능을 했던 아이템인 채널 뮤트권은 이 TMI가 나온 업데이트에서 사라졌대요.",
                    "63. 봇의 디자인이 거의 없는 이유는 여러 개가 있지만 큰 이유 중에 하나로 개발자의 미적 감각이 있대요.",
                    "64. 삶과 우주 그리고 모든 것에 대한 궁극적 질문의 해답은 42래요. 아무거나 골라서 나온 수가 그거라면...?",
                    "65. 커뉴봇이 있기 전의 규칙 7번 조항에서는 나간 사람의 레벨을 차감했대요. 그러나 봇이 생기면서 나간 사람의 데이터는 나가자마자 없어지도록 바뀌었다네요.",
                    "66. 들낙하면 차단하는 규칙은 무섭고 빡세 보이지만 봇이 들어가 있는 서버들 중 들낙퇴치를 활성화시킨 서버가 생각보다 많대요.",
                    "67. 봇 인증은 지금 당장이라도 받을 수 있지만 일부러 안 받는 거래요.",
                    "68. 잡소리 모음 카테고리를 나눌 때 원래는 주계열성의 스펙트럼형으로 나눌까 했었지만 작가분들의 수가 너무 적어서 그러지 않았대요.",
                    "69. 개발자에 있어서 이 수는 매우 중요하대요.",
                    "70. 2주년 이벤트 때까지 공식서버가 살아 있다는 가정이 필요하겠지만, 2주년 이벤트 때 사용될 채널은 이미 정해 놨대요.",
                    "71. 한 번은 봇의 숨겨진 접두사를 찾는 이벤트가 열렸대요. 그러나 지금까지도 아무도 그것을 찾지 못하고 있대요.",
                    "72. 도전과제를 얻기 위해서는 가끔은 발칙해질 필요가 있대요.",
                    "73. 그 무엇도 잼민유저의 유입을 막을 수는 없대요...참 슬퍼요",
                    "74. `!커뉴봇 님이 입력하고 있어요...`라고 채널에 뜨게 하는 명령어는 딱 두 개가 있대요. 뭘까요?",
                    "75. 공식서버의 전신이 되는 서버에서는 뮤트를 먹은 사람만 채팅 칠 수 있었던 채널이 있었대요.",
                    "76. 예전에는 `커뉴야` 라는 접두사 대신 봇을 핑해도 그 메세지에 명령어가 들어가 있다면 명령어를 사용하는 것으로 인식했대요. 그러나 봇 핑으로 명령어를 쓰는 일이 거의 없어 해당 기능은 사라졌대요.",
                    "77. 만약 봇의 웹사이트가 만들어진다면 가장 먼저 도전과제 목록부터 웹사이트에 이식할 예정이래요.",
                    "78. ㅇ바ㅇ보 드립은 서버가 생길 무렵 있었던 채팅방에서부터 유래된 드립이래요. 지금 그 채팅방은 망한 걸로 알고 있지만 고마운 곳이라고 할 수 있죠.",
                    "79. 공식서버에서 4레벨을 찍으셨다면 가끔은 게임채널들을 둘러보세요. 가끔 오셔서 게임 얘기를 나누셔도 되고 자기가 하는 게임이 없다면 채널을 하나 만드셔도 되니까요.",
                    "80. 이 TMI들도 도전과제처럼 업데이트를 할 때 정기적으로 약간씩 추가된대요. 그래서 TMI를 추가했지만 업데이트 내역에는 표시되지 않는 것일 수 있으니 업데이트 후 높은 번호의 TMI가 없나 한번 확인해 보는 것도 나쁘지 않을 듯 싶네요.",
                    "81. 한글은 너무 위대한 나머지 잡초키우기에서 잡초 성장 진행도에까지 쓰인대요.",
                    "82. 공식서버 오타 밈 명령어들을 계속 사용하다 보면 언젠가는 보답이 있지 않을까요?",
                    "83. 봇 기능들 중 몇몇 개는 개발자가 자기가 발견한 새로운 무언가가 잘 작동하나 보기 위해 만들어지기도 했대요.",
                    "84. 오랜 기간은 아니었지만 한때는 숫자방에서 52나 69로 끝나는 수에 각각 :cucumber:, :cancer:반응을 다는 문화가 있었대요.",
                    "85. 지금은 당연한 사실이지만 나중에는 재미있는 TMI가 될 만한 것들도 분명히 있을 거에요. 서버 일들을 눈여겨 봐 보세요!",
                    "86. 1일1잡소리가 시작되기 전에도 그곳의 채널명은 똑같이 커뉴의-잡소리-모음 이었대요.",
                    "87. 1주년 이벤트 이후로 전체 메세지 대비 수성에서 보내진 메세지의 지분이 점점 줄어들고 있대요.",
                    "88. `커뉴야 스펙`이라는 명령어 이름은 원래는 이름 아이디어를 받던 도중 나온 장난식 아이디어였지만 생각보다 좋은 이름이었어서 그냥 채택했대요.",
                    "89. 공식서버에서 가장 유명한 애교인 피자 애교는 처음에 그것을 전한 사람이 오타를 내서 잘못 전해졌대요. 피이자아아아...! 가 원래 맞는 표기래요!",
                    "90. 서버가 우주 컨셉으로 처음 바뀌었을 때는 20레벨이면 모든 레벨 채널들을 다 열 수 있었대요.",
                    "91. 이곳의 전신이 되는 서버에서는 세페이드 변광성처럼 특정한 천체 하나만을 가리키는 것이 아닌 채널명도 쓰였대요.",
                    "92. 수정되기까지 가장 오랜 시간이 걸린 오타는 `커뉴야 잡초키우기 상점`에서 `띄어쓰기가`를 `띄어쓱가`라고 낸 오타래요.",
                    "93. 서버에 처음 들어온 후로부터 62레벨을 달성할 때까지 가장 빨리 도달한 사람은 약 17일 만에 62레벨까지 도달했대요.",
                    "94. 봇 초창기에는 대부분의 명령어에 대한 대답으로 해체(반말)을 택했지만 나중에는 해요체로 통일시키며 개발했다고 해요. 그러나 지금도 해체로 말하는 명령어가 몇몇 개 남아 있다네요.",
                    "95. 전 서버, 전 유저가 쿨타임을 공유하는 명령어는 이 명령어가 유일하대요.",
                    "96. 예전에 잡소리 채널들에서 한 명이 반응을 달았다 뗐다 하면 봇이 그럴 때마다 메세지를 보냈고 결과적으로 반응 테러가 가능했었대요.",
                    "97. woozy 이모지와 관련되어 서버에서 벌어지는 격렬한 싸움의 근원은 공식서버가 생기기 전에 다른 서버에서 시작되었지만 그 서버에 있던 사람 중 한 명이 이곳으로 와버리는 일이 생겨 이곳까지 논쟁에 물들었대요.",
                    "98. 43번 TMI는 두 개래요. 개발자는 숫자를 못세나보죠?",
                    "99. 숫자 세기 이벤트가 열린 적이 있는데, 이벤트 개최 공지가 발송된 다음날 하루 동안 3000개가 넘는 숫자가 세졌대요.",
                    "100. 이 TMI는 업데이트로 추가된 것은 더 나중이지만 2021년 11월 29일에 작성됐대요."
                    "101. 71번 TMI에 나온 숨겨진 접두사는 찾은 사람이 딱 한 명 있어요. 발견자가 들낙으로 밴을 먹어서 공식서버 안의 사람들은 아무도 모를 뿐이죠.",
                    "102. 뀨 상점에 알파 센타우리만 팔았을 때 커뉴봇이 번 돈은 11500원이래요. 지금은 어떨까요?",
                    "103. 삭제되지는 않았지만 버그 등의 사유로 인해 서비스가 잠정 중단된 명령어들 중 중단된 기간이 가장 긴 명령어는 `커뉴야 코인`이래요.",
                    "104. 공식서버의 특정한 칭호를 얻으면 들어갈 수 있는 커뉴봇 베타 실험실이라는 방이 있는데 그 방은 다른 어떤 방들과도 사뭇 다른 분위기를 가지고 있대요. 그 방에 뭐가 있길래 같은 사람들이 있는 방인데도 분위기가 다를까요?",
                    "105. 출석체크 1등은 쉬우면서도 어려워요. 자정에 딱 맞춰서 여러 번 시도하다 보면 한 번쯤은 성공하지 않을까요?",
                    "106. `커뉴야 출첵목록`을 들여다보면 가끔 누군가가 00:00:20 전후로 출석체크를 한 것이 보이는데 그런 경우 중 대부분은 정각에 출석체크를 하려다 너무 일찍 눌러서 날이 바뀌기 전에 누른 것으로 판정되어 실패한 경우래요.",
                    "107. 해외여행을 갔는데 만약 그때 출석체크 1등을 도전하려면 어떻게 해야 할까요?",
                    "108. 커뉴봇 커뮤니티를 대표하는 밈들 중 하나인 오타 밈이 6페이지 도전과제 이름들에서 보이네요. 이것들 중 몇 개를 깬다면?",
                    "109. 커뉴봇에서 가장 많이 쓰인 명령어인 우주탐험과 잡초키우기 각각의 사용횟수 중 35%는 유령 지분이래요. 실제로 그만큼 명령어가 사용된 것은 맞지만 지분 35%를 먹고 있던 사람이 나가서 그렇게 됐다는데 그래도 서버에 타격이 크지 않다네요.",
                    "110. 어떤 도전과제는 달성법을 아무도 모르거나 너무 근래에 나와서 달성자가 없기도 하지만, 달성법은 알아도 극도로 어려워 달성자가 한 명뿐인 도전 과제도 있대요.",
                    "111. 가끔 특정한 게임채널이 주목받을 때가 있는데, 그러면 상당히 많은 사람들이 그 게임을 시작하거나 복귀한대요. 순위가 바뀌어도 계속 1등을 유지하는 게임채널이 있다면 그곳에 합류해 보는 건 어때요?",
                    "112. `커뉴야 출첵목록 서버`는 그 서버에서 출석한 사람들의 목록이 아니라 출석한 사람들 중 그 서버에 있는 사람들의 목록이에요. 헷갈리지 마세요!",
                    "113. 가끔 아이디어를 내는 이벤트가 있다면 참여해 보세요. 조금만 괜찮은 아이디어여도 당첨이 거의 확실해진다는데요?",
                    "114. 임베드에 커뉴봇 프사 색이 아닌 색이 나오는 명령어 중 입퇴장 로그와 51번 TMI에처럼 아이디어를 낸 사람이 색을 정한 명령어를 빼면 다 명령어를 만들 때 갑자기 개발자가 꽂힌 색으로 임베드 색을 정했대요.",
                    "115. 커뉴봇 건의질문 채널에 신기능을 건의했는데 그 기능이 유료 기능으로 추가되면 건의한 사람은 그 기능을 무료로 쓸 수 있게 해준대요. 그 신기능이 비싸게 나오기라도 하면 이득이 생각보다 크겠는데요?",
                    "116. 가끔 업데이트가 오래 걸리면 TMI가 한 번에 20개보다 많이 추가될 때도 있대요.",
                    "117. 일부 사람들의 뇌절을 방지하기 위해 만든 명령어를 뇌절의 근원이 되는 명령어의 사용이 불가능한 곳에서 쓴다면 무언가 일어나지 않을까요?",
                    "118. 이스터에그 도전과제 중 오타를 내야 받을 수 있는 도전과제가 있는데 전에 거의 밝혀질 뻔했다가 정체를 숨기는 데 성공한 도전과제가 있대요.",
                    "119. 서버스탯의 오늘의 서버 화력 통계는 별 의미 없대요. 사람들이 총 벌어들인 경험치가 그것보다 훨씬 더 서버 활동량을 잘 보여주는 통계에요.",
                    "120. 전류 주위에 자기장이 생긴다는 위대한 발견도 우연히 발견됐대요. 71번 TMI에 나온 다른 접두사나 아직 달성법이 발견되지 않은 이스터에그 도전과제도 우연의 일치로 발견될 수 있지 않을까요?",
                    "121. 베타 봇이 켜지면 헷갈려하시는 분들이 많던데 베타의 데이터는 본서버의 데이터와는 전혀 달라요.",
                    "122. 우주의 특정 부분에서만 사용 가능하다는 화폐 `아니 씨밧`을 모아 오타를 연구...?",
                    "123. 가끔 서버 사람들이 국기 이모지를 쓰는 경우가 있는데, :flag_za: 와 :flag_az: 는 :zany_face: 를, :flag_er: 은 :weary: 를, :flag_th: 는 :thinking: 을 의미한대요.",
                    "124. 알파 센타우리를 비롯한 몇몇 채널들의 채널부스트 값은 볼 수 없대요.",
                    "125. 도전과제 달성 조건을 찾아보는 잼민이가 있다는데 어떻게 생각하시나요? 지금 당장 이 채널에 얘기해보세요.",
                    "126. 커뉴봇이 아주 띠껍게 말한다면 권한진단 명령어를 제발 좀 사용하세요...",
                    "127. 봇이 짧은 뻘소리를 하는 명령어는 방금 당신이 쓴 심심해도 있지만 공식서버 밖에서 출석체크를 했을 때도 몇 개 되지는 않지만 이런 비슷한 말을 한대요. 이거 말고도 그런 명령어가 하나 더 있다던데 뭘까요?",
                    "128. 여러 TMI들에서 언급되었던 다른 접두사는 결국 2022년 초에 발견되었는데, 그대로쓰세요 주제의 퀴즈를 풀다 보면 답이 나온다네요.",
                    "129. 77번 TMI에서 언급된 채팅방은 2022년 1월을 끝으로 결국 없어지고 말았대요...",
                    "130. 도전과제 기능이 처음 나왔을 때는 목록이 4페이지까지밖에 없었대요. 도전과제 수가 많아짐에 따라 목록의 페이지 수도 지금과 같이 늘어난 거죠.",
                    "131. 이걸 봐도 심심하시다면 `커뉴야 도움`을 입력하고 안 써봤던 명령어들을 탐방해 보세요. 당신이 좋아할 명령어가 들어 있을지 누가 알아요?",
                    "132. 공식서버에서 사용빈도가 낮아 킥당한 봇 중에는 언빌리바봇이 있는데 그 봇의 상징이 피쟈아...<:kkyu_with_3_hearts:872405007243288677>래요. 다시 불러오고 싶네요...",
                    "133. 레벨 채널들의 컨셉도 채널의 인기가 낮다면 바뀌고 게임채널도 화력이 낮으면 없어지고 잡소리 채널도 작가가 잡소리를 쓰지 않으면 아카이브로 가거나 없어지지만 사설 채널만은 무슨 일이 있어도 사라지지 않는대요. 왜 그럴까요?",
                    "134. 커뉴야 색깔 명령어는 원래 입력된 색의 단색 이미지를 만들어 보내도록 계획되었지만 개발자의 능력 부족으로 실패했대요.",
                    "135. 커뉴야 할거 명령어는 개발자 자신이 쓰려고 한 시간 반만에 만든 거였는데 처음에는 편의성이 아주 떨어졌고 개발자 자신도 못 쓰겠었던 나머지 이 TMI가 나온 업데이트에서 해당 명령어의 편의성을 대폭 개선했대요.",
                    "136. 보통 업데이트는 개발자가 자기 직전에 하는데 그래서 업데이트를 하기 한 다음날이 될 때마다 개발자는 커뉴봇이 에러 메세지를 보내지 않았을까 조마조마한대요.",
                    "137. 업데이트를 가장 크게 저해하는 사람이 누구일까요?",
                    "138. 최근에 나오는 기능들 중에서는 명령어 안에 인수를 몇 개 넣었는지에 따라 알맞게 반응하는 등 더 편해진 기능들이 많대요. 확실히 실력이 늘기는 느나봐요.",
                    "139. 뻘문의를 하신다면 개발자의 정성스러운 답변과 함께 봇 정지를 먹을 수 있어요.",
                    "140. 서버 초기에는 초대권한 역할의 이름이 ㅇㅅㅇ, 별명변경권 역할의 이름이 ㅇㅂㅇ이었대요. ㅇㅁㅇ이라는 역할 이름은 지금도 있는데 무슨 역할일까요?",
                    "141. 이 TMI가 추가된 업데이트부터 커뉴봇에 슬래시 커맨드 기능이 같이 추가되었대요.",
                    "142. 한 번은 이 심심해 명령어로 나오는 답변들을 묶어서 파는 사람이 생겼는데, 그것으로 인해 모든 TMI를 다 발견한 사람에게 도전과제를 줄까 말까 생각 중이라네요.",
                    "143. 143번 버스는 대치동을 다니다 보면 자주 보게 되는 버스 노선들 중 하나인데, 이 개발자라는 놈은 143 버스가 연속으로 세 대가 지나가는 걸 본 적이 있대요. 이걸 본 서준은 아니 저거 버스 버스 라고 말했겠죠? :ROFLL",
                    "144. 개발자 자신도 심심하면 이 명령어에 나오는 답변들 중 일부분을 돌려보기도 한대요.",
                    "145. 공식서버의 맨 위 채널은 관리자 전용 채널인데 이름이 \"엄\"이래요. 라고 2번 TMI가 말해주고 있고, 실제로도 오랫동안 채널이름이 \"엄\"이었지만, 언젠가부터 누군가가 엄을 런으로 오타내면서 채널 이름도 \"런\"으로 바뀌었대요.",
                    "146. 122번 TMI에서 나온 게 무슨 말인지 알아요? 아니 씨밧이라는 오타를 낸 당사자도 결국 해당 게임의 유저가 돼버렸대요.",
                    "147. 개발자는 잼들을 정말 싫어해요. 주변에서 잼을 발견한다면 즉시 신고하시고, 신고하면 5뀨를 드리겠습니다! 라고 말한 적이 있었는데, 그런 말을 한 지가 꽤 됐음에도 지금까지 그런 신고를 받아준다네요.",
                    "148. 이스터에그 도전과제야말로 커뉴봇의 진정한 폐단 아닐까요? 원래 해당 도전과제들의 기획 목적은 커뉴봇을 많이 사용하면서 뜻밖의 발견을 하자는 것이었는데, 도전과제 달성법을 잼민이들이 서로 쳐 공유하는 듯해요.",
                    "149. 148번 TMI에서 이어지는 내용인데, 그때문에 개발자가 흑화해서 굉장히 어렵고 달성해도 왜 달성했는지 모르는 이스터에그 도전과제를 준비중이라는데, 그러는 개발자와 잼들 중에 누가 더 선넘일까요?",
                    "150. 슬래시 커맨드를 추가하면서 커뉴봇 소스 코드 전체가 뜯어고쳐졌는데, 그때 다른 사람을 킥하거나 밴하거나 뮤트하는 등의 관리 명령어들이 삭제됐어요. 그때문에 차단 권한이 없을 때 차단 명령어를 실행하면 얻을 수 있었던 도전과제 `차담 마려벤요?` 또한 더 이상 얻을 수 없게 되었죠.",
                    "151. 업데이트를 가장 크게 저해하는 집단이 무엇일까요? 이전에도 비슷한 질문을 했던 것 같은데 지금은 답이 달라졌네요.",
                    "152. 어느 날 갑자기 공식서버를 이전한다면 여러분들은 어떻게 반응할까요?",
                    "153. 공식서버의 금성 채널은 서버의 나이테같은 채널이에요. 그곳의 고정메세지를 보면 10000 단위의 수마다 고정이 되어 있는데, 그 날짜를 보면 대강의 서버 화력 변화를 알 수 있죠...",
                    "154. 가끔 가다 숨겨진 접두사에 관련된 TMI를 찾아볼 수 있는데, 그것은 이벤트용으로 만든 게 아니었고 사실 아주 오래 전 커뉴봇에 영어기능을 추가하자는 것에서 나온 거였대요. 그러나 이제 그게 쓸모없어졌고 업데이트로 그 접두사였던 `c!`은 사라졌대요.",
                    "155. 커뉴는 귀여울까요?",
                    "156. 뜯어고쳐진 커뉴봇의 소스코드에서는, 첫 40줄동안 import 뭐시기나 from 뭐시기 import 뭐시기로 도배돼 있대요. 파이썬을 할 줄 아시면 무슨 말인지 이해하겠죠..",
                    "157. 두 개 이상의 TMI가 비슷한 내용을 말하고 있다는 느낌을 받으실 수도 있는데, 역사는 반복된다는 말을 떠올려 보세요. 분명히 두 TMI들은 많은 시간 간격을 두고 작성됐겠지만, 내용이 왜 비슷하겠어요?",
                    "158. 소스 코드에 이 160개의 답변들을 개발자가 손으로 직접 다 쓰는데, 그래서 화면이 초록으로 빛난대요?",
                    "159. 159가 59+100이길래 하는 말인데, 59번 TMI에서 미자르와 알코르에 대해 얘기한 게 혹시 기억나시나요? 한 명 정도는 그 떡밥을 잡아서 2주년 이벤트 때 이벤트가 열릴 채널 이름이 미자르일 것이라고 한 명쯤은 알아줄 거라고 생각했는데 그런 사람은 없더라고요.",
                    "160. 레벨이 아주 높고 우주탐험으로 많은 지역에 가보신 분들은 왜 북극성이 없을까 이런 의문 들어보신 적 없나요?",
                    "161. 한 번은 커뉴봇이 약 2년간 업데이트가 없었던 적이 있었대요. 그런데 7년 동안 업데이트를 안 한 게임도 있으니 이 정도면 양호한 편 아닐까요?",
                    "162. 언젠가 커뉴봇에는 꼭 게임 기능이 하나 더 추가될 거에요. 이걸 읽는 당신은 이미 여기에 언급된 게임 기능을 열심히 하고 있으려나요?",
                    "163. 이 봇이 만들어진지 3년이 넘어간 이 시점, 개발자는 봇에 어떤 기능이 었었는지도 가끔 헷갈려한대요.",
                    "164. 수능이 끝난 뒤로 개발자가 프로그래밍 외주 문의를 받고 있대요. 가격도 그렇게 안 비싼 선에서 해준다는데...",
                    "165. 가끔은 소스 코드를 건드리지 않았는데도 디스코드 자체에서 무언가 바뀌는 바람에 작동되던 게 안 되는 일이 일어나기도 한다네요.",
                    "166. 개발자는 처음에 토끼공듀 Lv.2000같은 유저가 커뉴봇에 단 한 명이라도 존재할 거라곤 생각을 못 했대요. 그걸 가정으로 일부 게임 명령어도 설계되어 있는데...",
                    "167. 도대체 왜 개발자는 TMI에 미래에 일어날 일을 이미 일어난 일인 양 적어두는 걸까요? 적은 지 꽤 오래된 TMI 중에서 아직 반영이 안 된 TMI마저 보이네요.",
                    "168. 나 예비번호 언제 뜨냐? 보통 오늘 조기발표하지 않음? 진짜 한 33번 정도 받고 당당하게 붙고 싶은데 결과가 안 나와...",
                    "169. 고3이거나 고3이 될 수험생이거나 미래 수험생 여러분들 진심으로 축하드립니다.",
                    "170. 사실 여기서 개발자가 무슨 불만을 토로해도 아무 소용이 없대요. 예전에 써 놓았던 유저들에 대한 불만 사항들이 1년이 지나도 2년이 지나도 똑같대요.",
                    "171. 예전엔 잡초키우기에서 한 번에 비료를 5개씩만 살 수 있었는데 나중에 몇 개든 살 수 있도록 바뀐 거래요. 그래서 잡초키우기 상점에서는 한 번에 비료를 많이 사면 오히려 가격이 오르는 거에요.",
                    "172. 한 번 작성된 TMI는 더 이상 사실이 아니게 되더라도 과거의 흔적 느낌으로 살려두지만, 정말 못 봐주겠는 TMI가 실제로 수정된 사례가 딱 세 건 있대요. 혹시 찾으실 수 있나요? 참고로, 그 중 하나는 바로 이 TMI에요. 원래는 세 건이 아니라 한 건이라고 써 있었죠.",
                    "173. 게임 명령어가 아닌 평범한 대화 명령어도 정말 많이 쓰시는 유저분이 계신 거 같아요. 하긴 거기에 몇 개의 도전 과제가 숨겨져 있으니까...",
                    "174. 공식서버의 건의와 질문 채널에서 분명 업데이트되지 않은 커뉴봇 기능인데 해결완료 태그가 붙은 포스트가 있다면, 이미 개발자가 그 내용을 코드로 구현하는 데 성공했고 업데이트에 맞춰 출시할 거라는 뜻이에요.",
                    "175. 공식서버와 관련된 일부 커뉴봇 도전 과제는 공식서버의 칭호와 자동으로 연동돼서 도전과제를 달성하면 자동으로 칭호까지 부여된대요.",
                    "176. 172번 TMI에서 언급한 정말 못 봐주겠는 TMI도 있지만 정말 못 봐주겠는 도전 과제도 있어서, 이 TMI가 새로 추가되었던 업데이트와 동시에 삭제됐대요. 어차피 달성률 0%였으니...",
                    "177. 사람들이 명령어를 사용할 때, 이스터에그 도전과제 달성 조건과 정말 비슷했지만 달성하지 못하는 경우도 종종 있대요.",
                    "178. 공식서버의 게임채널이 지금의 스레드 제도로 바뀌기 전까지는 게임채널 화력을 바탕으로 채널 순서를 정했는데, 그때 자기가 하는 게임의 채널을 살리려고 발악하는 사람들이 많았대요.",
                    "179. 슬래시 커맨드 관련 이슈가 생긴 이후 상당수의 대규모 디스코드 봇들이 사멸했는데, 커뉴봇이 그 자리를 대체할 수 있을까요?",
                    "180. 예전에 개발자가 멍청했을 때부터 봇을 만들었어서 여기서도 든과 던을 헷갈리는 미친짓을 하진 않았나 코드 전체를 살펴봤는데 한 건도 없네요!",
                    "181. 109번 TMI는 더 이상 참이 아니게 됐대요. 이제는 그곳에서 언급한 사람이 아닌데 이 TMI가 작성될 때 기준으로 총 커맨드 사용 횟수가 27만번이 넘는 분이 두 명령어 지분의 40% 가까이 가지고 있대요!",
                    "182. 이걸 봐도 심심하시다면 `커뉴야 커뉴핑크`를 해보시는 게 어떨까요? 이걸 보는 시점에 그 명령어가 출시됐을지는 모르겠지만요.",
                    "183. `커뉴야 색깔` 명령어는 원래 입력된 색의 단색 이미지를 만들어 보내도록 계획되었지만 개발자의 능력 부족으로 실패해서 해당 색깔의 임베드를 보내는 이상한 명령어였지만 얼마 전부터 다시 입력된 색의 단색 이미지를 만들어 보내는 명령어가 됐대요.",
                    "184. 이걸 봐도 심심하시다면 이 명령어를 계속 써 보세요. 계속, 계속, 계속 써 보세요.",
                    "185. 이것보다 낮은 번호의 TMI들 중에서는 의외로 커뉴봇의 특정한 기능 하나를 다루는 게 많이 없대요.",
                    "186. 일부 TMI들은 서로 연결돼서 몇 개의 TMI가 비슷한 주제의 내용을 다른 시점에서 들려주는 경우도 있대요.",
                    "187. 이전 업데이트 중에 `커뉴야 퀴즈 내문제` 명령어를 신설한 업데이트가 있었는데 그때 개발자가 업데이트 로그에 저 내용을 넣는 걸 까먹었대요!",
                    "188. 도전 과제들 중 가장 개발자의 속을 많이 썩인 도전과제는 `잡소리 독자`로, 존재하던 버그가 몇 번의 업데이트를 거치고 나서야 비로소 고쳐졌대요.",
                    "189. 왜 하필 이 명령어에서 이스터 에그 도전과제의 힌트를 주냐고 따지실 수 있지만, 열심히 이 명령어의 내용을 확인해 보시는 분들의 정성에 대한 보상이에요.",
                    "190. 여기에서 나오는 답변을 모두 찾을 생각을 하고 계신다면, 굉장한 인내력을 가지고 아주 오랫동안 명령어를 실행해야 할 거에요.",
                    "191. 172번 TMI와 비슷한 이야기인데, 최대한 오랫동안 이런 TMI들의 진실성을 유지할 수 있도록 정말 쓰고 싶은 내용이 아니라면 TMI에 특정한 수치를 직접적으로 포함시키지 않는대요.",
                    "192. 공식서버의 모든 채널을 한 번씩 다 가보는 것은 미친듯이 어려운 일이래요. 아마 그럴 수 있는 방법 중에 가장 쉬운 방법이 관리자 권한 얻기일걸요?",
                    "193. 뀨로 사는 기능들 중에서는 보기에는 커맨드의 출력에서 단순히 쓸만한 거 하나 추가하는 정도인 기능이 있지만 만드는 입장에서는 구현하기가 생각보다 굉장히 까다로운 것들도 있대요.",
                    "194. 사람들이 `커뉴야 문의`를 쓰는 걸 생각보다 귀찮아하는 것 같더라고요.",
                    "195. 2024년 1월까지만 해도, 한 명령어가 도움말에 두 번 쓰인 경우가 있었대요. 개발자가 얼마나 멍청하면...",
                    "196. 프로그래밍? 그렇게 어렵지 않아요. 요즘 시대에 직접 한번 배워 보시는 게 어때요?",
                    "197. 공식서버의 채널들 중 일부는 어떤 이유로든지 채널 컨셉이 바뀌는 경우가 있대요. 만약 특정한 채널에서 스크롤을 올려봤는데 지금이랑 완전히 다른 용도로 쓰이고 있었다면, 이전에는 어떻게 쓰였는지를 맞혀보세요!",
                    "198. `커뉴야 코인`이 부활한 이후에는 진짜 코인 보유량을 저장하는 대신 코인 보유량이 너무 많을 때를 대비해서 특수한 방법으로 저장한대요. 이 방법을 쓴다면 1 뒤에 0이 10000000개가 있는 만큼의 코인을 가져도 문제없이 저장할 수 있다는데, 어떤 방법일까요?",
                    "199. `커뉴야 커뉴핑크`에서는 `커뉴야 잡초키우기`와 `커뉴야 우주탐험`과는 조금 다른 방식으로 매크로를 방지한대요.",
                    "200. 이 TMI는 업데이트로 추가된 것은 더 나중이지만 2024년 1월 28일에 작성됐대요.",
                    "201. 예전 공식서버에서는 상당히 많은 칭호 역할에 대해 역할 전용 방이 따로 있었대요. 그러나 오래 지나지 않아 수요가 적다는 이유로 삭제됐죠.",
                    "202. 커뉴핑크 베타 시절에는 (1, 2)칸같은 칸부터 불투명도 업그레이드 가격이 많이 비쌌대요. 그래서 불투명도 업그레이드에 대한 인식이 지금과는 달랐대요.",
                    "203. 개발자는 커뉴봇만큼은 확률형 아이템으로부터 자유롭게 만들고 싶어해요. 무슨 말인지 알죠?",
                    "204. 커뉴핑크 초기 개발 기간 동안 개발자는 컨텐츠 아이디어를 얻기 위해서 이거 키우기 저거 키우기 같은 모바일 똥겜들을 여러 번 깔았다 지웠대요...",
                    "205. 명령어가 같다면 세부 옵션에 관계없이 쿨타임이 공유되는 것은 계속 지적받아 왔지만 고치기 매우 힘든 문제에요. 이걸 보고 있을 시점이라면 고쳐져 있을까요?",
                    "206. 지금 다니는 학교가 남녀공학이라고요? 제발 졸업하기 전까지 후회 없는 학교생활을 하세요...",
                    "207. 심심해는 제발 재미로만 봐 주세요. 이 내용을 다루는 TMI만 한 5개 있는 거 같은데 랜덤함수가 알아서 잘 해 주겠죠?",
                    "208. 이름이 오타인 도전과제를 달성하고 싶다면, 커뉴봇의 어떤 기능의 어느 문구에서 그 오타의 원래 글자가 나오는지 보세요.",
                    "209. 알데바락 우주센터와 활발히 거래하면 알데바락의 조각이나 폴룩스의 조각, 심지어는...",
                    "210. 공식서버 전체에서 가장 인기가 많은 이모지는 :weary: 이모지에요. 아무 때나 이 이모지를 쓰는 건 흔한 일이에요!",
                    "211. 커뉴봇이 커뉴봇이 아니었던 적이 있었다는 걸 알고 있었나요? 2021년 만우절 때는 커뉴봇이 아니라 우커바봇이었대요.",
                    "212. 저를 보고 싶으면 제 대학 후배가 되어보시는 건 어떨까요? 물론 정상적인 사람들만 오시면 좋겠네요!",
                    "213. 연세대학교 컴퓨터과학과 24학번은 100명이 조금 넘는 정원에 여자 인원수 8명을 자랑하고 있는 과입니다!",
                    "214. 2022년 만우절에 공식서버의 큰 컨텐츠들 중 하나인 `잡소리`를 중단한다는 거짓 공지를 했었대요.",
                    "215. 연세가 붙은 버전들은 아마도 대학 1학년 동안 만든 버전일 거에요. 이동안에는 경력직 개발자마냥 맥북을 쓰며...",
                    "216. 가끔은, 공식서버가 어떻게 지금까지 터지지 않고 유지될 수 있는지 서버장인 개발자도 궁금해질 때가 있어요.",
                    "217. 대학교에 오시면 동아리를 꼭 하나 들어가시는 걸 추천드릴게요. 개발자는 낭만 있는 천체관측 동아리에 들어갔어요!",
                    "218. 심심해처럼 오랫동안 기록하는 컨텐츠는 일종의 나이테에요. 대학 추가합격 기원이나 대학 생활이나 그런 얘기가 대표적이죠.",
                    "219. 이 TMI가 작성되는 버전에서는 `커뉴야 계산` 명령어가 정말 별볼일 없지만 이 명령어를 언젠가 성능 높은 계산기로 만드는 게 목표에요.",
                    "220. 2023년 만우절에는 하루에 진짜같은 가짜 잡소리 여러 개가 올라왔대요. 만우절 이벤트는 해마다 속는 사람이 계속 나와요...",
                    "221. 대학교에 오시면 이런 거 그만 하고 제발 놀러 나가세요...",
                    "222. 어떨 때는 커뉴봇이 동시에 2개의 기계에서 돌아가기도 한대요. 222. 어떨 때는 커뉴봇이 동시에 2개의 기계에서 돌아가기도 한대요.",
                    "223. 아마도 연세6이나 연세7 업데이트는 정말로 슬래시 커맨드를 새로 지원하게 될 가능성이 있어요.",
                    "224. 오랫동안 골치아픈 이슈 중 하나는 무언가를 실시간으로 만드는 거에요. 생각보다 구현이 쉽지 않나 봐요.",
                    "225. 오타가 있어도 제보하지 말아 주세요. 만약 이것보다 낮은 번호의 TMI가 반대 내용을 말하고 있다면 무시하세요.",
                    "226. 프로그래밍 과외 (특히 파이썬) 받으실 분 구합니다. 시간이 지날수록 제 몸값은 오르므로 지금이 가장 싸요.",
                    "227. 방학에도 하루에 8시간씩 공부하는 대학 새내기가 있다는데요?",
                    "228. TMI가 n번까지 있을 때 모든 TMI를 한 번씩 보기 위해서 명령어를 쳐야 하는 횟수의 기댓값은 n(1+1/2+...+1/n)이에요. 지금은 230개의 TMI가 있고 저 값은 1384 정도에요.",
                    "229. 228번 TMI에 나오는 공식은 기댓값의 선형성으로 어렵지 않게 증명할 수 있어요.",
                    "230. 여기서 나오는 TMI들이 말하는 시점은 비선형적이에요. 이 기능이 4차원이라고 할 수 있겠네요.",
                    "231. 연세6 업데이트가 저번에 있었고, 진짜로 슬래시 커맨드를 지원하게 됐어요!",
                    "232. 이걸 봐도 심심하시다면 어려운 이스터 에그 도전과제 아이디어를 투고해보세요!",
                    "233. 서버비 수금이 안 되면 내년에 서비스 종료해버릴 거에요",
                    "234. TMI에는 가끔씩 멍청이들은 이해하기 힘들거나 드립인지도 모를 고수준 드립이 나올 때가 있어요.",
                    "235. 개발자랑 친해지면 가끔 얘가 밥사준대요.",
                    "236. 꽤 자주, 공식서버가 어떻게 지금까지 터지지 않고 유지될 수 있는지 서버장인 개발자도 궁금해질 때가 있어요.",
                    "237. 공식서버가 시작된지 약 1년이 지난 시점 `역사관`이라는 걸 준비하던 때가 있었어요. 하지만 결국 열지 못했죠.",
                    "238. 내가 이걸 왜 하고 있을까? 누구 좋으라고? 나 좋으라고? 프로젝트 나가고 싶다고 하면 나보고 오라고 할 사람이 한둘이 아닐 텐데?",
                    "239. 어차피 업데이트를 뭘 해도 신경 안 쓸 거죠? 그래 주세요.",
                    "240. 318665857834031151167461은 합성수에요."]
        embed = Embed(color=0xffd6fe, title="TMI를 말해드릴게요... 번호는 만든 순서임...",)
        seen = db.record("SELECT tmi FROM games WHERE UserID = ?", ctx.author.id)[0]
        if extra == '리스트':
            if not tracker:
                await send(ctx, '`커뉴야 뀨 구매 TMI 트래커`')
                return
            get_index_of_one = lambda lst: [i + 1 for i, val in enumerate(lst) if val == '1']
            really_seen = list(map(str, get_index_of_one(seen)))
            await send(ctx, f'지금까지 {",".join(really_seen)}번 TMI를 봤어요!')
            return
        elif extra and extra.isdigit():
            if not tracker:
                await send(ctx, '`커뉴야 뀨 구매 TMI 트래커`')
                return
            extra = int(extra) - 1
            if extra >= len(tmi_list):
                await send(ctx, '존재하지 않는 번호에요!')
                return
            if seen[extra] == '0':
                await send(ctx, '아직 발견한 적 없는 TMI에요! yonsei1 업데이트 이후 랜덤으로 발견한 TMI만 다시 볼 수 있어요.')
                return
            embed.add_field(name="사실은...", value=tmi_list[extra])
        else:
            if randint(1, 3000) != 1:
                idx = randint(0, len(tmi_list) - 1)
                tjfaud = tmi_list[idx]
                if seen[idx] == '0':
                    if tracker:
                        embed.set_footer(text='처음 발견한 TMI에요!')
                    seen = seen[:idx] + '1' + seen[idx + 1:]
                    db.execute("UPDATE games SET tmi = ? WHERE UserID = ?", seen, ctx.author.id)
                    db.commit()
            else:
                tjfaud = "0\. 그만!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                l = grant_check("얼마나 심심하셨길래...", ctx.author.id)
                if l == 1:
                    await grant(ctx, "얼마나 심심하셨길래...", "`커뉴야 심심해` 명령어 실행 시 1/3000의 확률로 얻을 수 있는 도전과제")
            embed.add_field(name="사실은...", value=tjfaud)
        await send(ctx, embed=embed)

    @command(name="오타원본", aliases=["오라타원본", "와원본", "어타원본", '오타ㅏ원본'])
    async def SBJB_original(self, ctx, *, a: str):
        if "ㅆㅅㄴ" in a:
            b = "https://cdn.discordapp.com/attachments/819847476319354950/898433458534240256/unknown.png\n2021.05.21\nhttps://cdn.discordapp.com/attachments/819847476319354950/898433657407156264/unknown.png\n2021.05.21\nhttps://cdn.discordapp.com/attachments/819847476319354950/898433840253632532/unknown.png\n2021.09.11\nhttps://cdn.discordapp.com/attachments/819847476319354950/898434048605704232/unknown.png\n2021.09.14"
        if "으팀" in a:
            b = "https://cdn.discordapp.com/attachments/819847476319354950/898432843301142568/unknown.png\n2021.05.28\nhttps://cdn.discordapp.com/attachments/819847476319354950/898433287763161118/unknown.png\n2021.10.08"
        elif a == "피겅":
            b = "https://cdn.discordapp.com/attachments/773409630125817887/898024270863687680/unknown.png\n2021.07.03\nhttps://cdn.discordapp.com/attachments/815416004480860160/898010435419246612/VLRJD.png\n2021.07.07"
        elif a == "피곦":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898013788190670908/unknown.png\n2021.07.17"
        elif a == "핑이나 막아라!":
            b = "https://cdn.discordapp.com/attachments/815416004480860160/898010418432315422/defendping.png\n2021.07.25"
        elif a == "원병준보":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898014547720413223/unknown.png\n2021.07.20"
        elif "우틈" in a:
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898014889182904320/unknown.png\n2021.07.23"
        elif a == "재바얄보":
            b = "https://media.discordapp.net/attachments/794563329560674344/869029884196954162/unknown.png\n2021.07.26"
        elif "옹려" in a:
            b = "https://cdn.discordapp.com/attachments/819847476319354950/898430729292234752/unknown.png\n2021.07.26\nhttps://cdn.discordapp.com/attachments/819847476319354950/898431135829352448/unknown.png\n2021.07.27\nhttps://cdn.discordapp.com/attachments/819847476319354950/898431229962100777/unknown.png\n2021.08.12"
        elif a == "피돈":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898015828866396170/unknown.png\n2021.07.31"
        elif a == "일요릴":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898016109649887302/unknown.png\n2021.08.02"
        elif "올료" in a:
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898016337731936326/unknown.png\n2021.08.02"
        elif a == "피건":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898016581249036308/unknown.png\n2021.08.05"
        elif "유링겟ㅍㅇ" in a:
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898016831997104209/unknown.png\n2021.08.05"
        elif "씨밧" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/874945194385088552/unknown.png\n2021.08.11"
        elif a == "ㅇㅇㅌㅌ":
            b = "https://cdn.discordapp.com/attachments/815416004480860160/898010401785147462/ddxx.png\n2021.08.13"
        elif a == "ㄹㄹㅋㅋ":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898018699770998814/unknown.png\n2021.08.16"
        elif a == "피곰":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898018966860103740/unknown.png\n2021.08.18"
        elif a == "피균":
            b = "https://cdn.discordapp.com/attachments/773409630125817887/898446354957860874/unknown.png\n2021.08.19"
        elif a == "찹콘":
            b = "https://cdn.discordapp.com/attachments/815416004480860160/898010450527125544/chopcorn.png\n2021.08.20"
        elif a == "피곧":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898019196410155088/unknown.png\n2021.08.21"
        elif a == "오태민":
            b = "https://cdn.discordapp.com/attachments/815416004480860160/898010487474761728/taemin.png\n2021.08.21"
        elif "개소리어" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/878983914646044732/unknown.png\n2021.08.22"
        elif "영심히" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/878988276302762014/unknown.png\n2021.08.22"
        elif "첨읋" in a or a == "서술형3":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/878988922414329856/unknown.png\n2021.08.22"
        elif "깄" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/878989178841481276/unknown.png\n2021.08.22"
        elif "이름같고" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/878990025021337630/unknown.png\n2021.08.22"
        elif "제방" in a:
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898020457834500136/unknown.png\n2021.08.22"
        elif "모으겠네" in a:
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898020683077009428/unknown.png\n2021.08.22"
        elif "보깐" in a:
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898020904393658368/unknown.png\n2021.08.23"
        elif "맞툼법" in a:
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898021118953291826/unknown.png\n2021.08.24"
        elif a == "그래거":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898021337212268574/unknown.png\n2021.08.24"
        elif a == "모으잖금":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898021728477933588/unknown.png\n2021.08.25"
        elif a == "근게":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898021974146682950/unknown.png\n2021.08.25"
        elif a == "지원감":
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898022238379474954/unknown.png\n2021.08.26"
        elif "기준" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/881073535748038676/4a7e4a44c4ba276c.PNG\n2021.08.28"
        elif "스탭" in a:
            b = "https://cdn.discordapp.com/attachments/770644244658389022/898022666915708928/unknown.png\n2021.08.30"
        elif a in ['ㅋ갈퓨ㅏ', '갈퓨ㅏ']:
            b = 'https://cdn.discordapp.com/attachments/760766690551398411/881759793574981652/unknown.png?ex=65d2db4d&is=65c0664d&hm=8bc931140732260dbfb3227285b37dc0ebd096707ac4e2720fe72da953d9311a&\n2021.08.30'
        elif "디탕" in a:
            b = "https://cdn.discordapp.com/attachments/819847476319354950/898429569206460436/Screenshot_20210831-1008552.png\n2021.08.31"
        elif a == "3웨":
            b = "https://cdn.discordapp.com/attachments/815416004480860160/898010467044294726/3we.png\n2021.09.01"
        elif a == "피공":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/883350420163035206/Screenshot_20210903-225754_Discord.jpg\n2021.09.04"
        elif a in ["피고느", "피고느.."]:
            b = "https://cdn.discordapp.com/attachments/743339107731767366/898027272005644289/unknown.png\n2021.09.05"
        elif a == "잡소라":
            b = "https://cdn.discordapp.com/attachments/819847476319354950/898027596955136120/unknown.png\n2021.09.06"
        elif a in ["우탑", "우암"]:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/8847486 39761756200/Screenshot_20210907-193350_Discord.jpg\n2021.09.07"
        elif a == "할렐우야":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/884757755406204928/Screenshot_20210907-200844_Discord.jpg\n2021.09.07"
        elif a == "싸면":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/884766565311074344/Screenshot_20210907-204512_Discord.jpg\n2021.09.07"
        elif a == "한건다":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/884768801781088317/Screenshot_20210907-205508_Discord.jpg\n2021.09.07"
        elif a == "차간":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885178043461664778/Screenshot_20210909-000119_Discord.jpg\n2021.09.09"
        elif a == "부리고":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885535599421976626/Screenshot_20210909-234118_Discord.jpg\n2021.09.09"
        elif "여지" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885541916962340985/Screenshot_20210910-000707_Discord.jpg\n2021.09.10"
        elif "남" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885543495467683911/Screenshot_20210910-001315_Discord.jpg\n2021.09.10"
        elif "겠난" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885841773304348762/Screenshot_20210910-195832_Discord.jpg\n2021.09.10"
        elif "커인" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885842881485627392/Screenshot_20210910-200244_Discord.jpg\n2021.09.10"
        elif "거버" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885846612801388564/Screenshot_20210910-200911_Discord.jpg\n2021.09.10"
        elif a == "오옹ㅃ":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885848377907109898/unknown.png\n2021.09.10"
        elif a == "검 4":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885848837644746762/unknown.png\n2021.09.10"
        elif a == "섹사":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885849029592879124/unknown.png\n2021.09.10"
        elif a == "느가":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885849942990671892/unknown.png\n2021.09.10"
        elif "곰 ㅇ ㅋ" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885852266660249610/unknown.png\n2021.09.10"
        elif a == "노가다ㅊ좀":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885853388166811708/unknown.png\n2021.09.10"
        elif a == "검 ㄹ":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885853721882419260/unknown.png\n2021.09.10"
        elif "골려" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885873241611182221/unknown.png\n2021.09.10"
        elif a == "섬바삳보":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885873269725605909/unknown.png\n2021.09.10"
        elif a == "안제":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885874472597487677/unknown.png\n2021.09.10"
        elif "스픽" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885876106580885554/unknown.png\n2021.09.10"
        elif a == "(":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885876662443597864/unknown.png\n2021.09.10"
        elif a == "감":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/885877467632521286/unknown.png\n2021.09.10"
        elif "쓰가" in a:
            b = "https://cdn.discordapp.com/attachments/819847476319354950/898438561613877248/unknown.png\n2021.09.13"
        elif a == "확인라려다가":
            b = "https://cdn.discordapp.com/attachments/819847476319354950/898438343308763176/unknown.png\n2021.09.13"
        elif "야자" in a:
            b = "https://cdn.discordapp.com/attachments/819847476319354950/898437764008280064/unknown.png\nhttps://cdn.discordapp.com/attachments/819847476319354950/898438075162714182/unknown.png\n2021.09.13\n위: 화질 안좋지만 당시 찍은 사진, 아래: 화질 좋지만 나중에 찍은 사진 입니다"
        elif a == "아디ㅛ지":
            b = "https://cdn.discordapp.com/attachments/819847476319354950/898432437045043220/unknown.png\n2021.09.13"
        elif a == "건 ㄱ":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887110270890147870/unknown.png\n2021.09.14"
        elif "종아리" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887110394064285696/unknown.png\n2021.09.14"
        elif "으네" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887186316712898610/Screenshot_20210913-214222_Discord.jpg\n2021.09.14"
        elif a == "저럼":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887189728334598174/unknown.png\n2021.09.14"
        elif "실채" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887197544352985088/unknown.png\n2021.09.14"
        elif a == "우악":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887216664020660344/unknown.png\n2021.09.14"
        elif a == "마가3":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887217714739941406/unknown.png\n2021.09.14"
        elif a == "저선":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887218490166095892/unknown.png\n2021.09.14"
        elif "골러" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887276242032820234/Screenshot_20210914-185853_Discord.jpg\n2021.09.14"
        elif a == "파강":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887280088436056064/Screenshot_20210914-191249_Discord.jpg\n2021.09.14"
        elif a == "겁 ㅍ":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887285434126856232/Screenshot_20210914-193506_Discord.jpg\n2021.09.14"
        elif a == "더런":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887288211729186826/Screenshot_20210914-194557_Discord.jpg\n2021.09.14"
        elif "에사" in a:
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887288312476356628/Screenshot_20210914-194653_Discord.jpg\n2021.09.14"
        elif a == "감 ㄱ":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887288761237532672/Screenshot_20210914-194828_Discord.jpg\n2021.09.14"
        elif a == "아가":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/887291304298549278/Screenshot_20210914-195831_Discord.jpg\n2021.09.14"
        elif a == "편의즘":
            b = "https://cdn.discordapp.com/attachments/743339605838921748/903464651667431515/Screenshot_20211029-110550_Discord.jpg\n2021.09.14"
        elif a == "피고노":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/891330901429063721/Screenshot_20210925-233041_Discord.jpg\n2021.09.25"
        elif a == "으으ㅐ":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/891214806500118558/unknown.png\n2021.09.25"
        elif a == "재바여로":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/891548294143164426/unknown.png\n2021.09.26"
        elif a == "차담 마려벤요?":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/891549066465521694/unknown.png\n2021.09.26"
        elif a == "ㅎ😩ㅎ":
            b = "https://cdn.discordapp.com/attachments/794563329560674344/894506144939274240/Screenshot_20211004-174802_Discord.jpg\n2021.10.04"
        elif a == '🇿🇦':
            b = 'https://cdn.discordapp.com/attachments/773409630125817887/938369317689507840/zany_face_-_flag_za.png\n2021.10.08'
        elif a == '미핀':
            b = 'https://media.discordapp.net/attachments/773409630125817887/938369844758347776/Screenshot_20211014-203638_Discord.png\n2021.10.14'
        elif a in ['디토', '디토새끼야']:
            b = 'https://media.discordapp.net/attachments/773409630125817887/938370155740803113/unknown.png\n2021.10.15'
        elif a == '💒':
            b = 'https://cdn.discordapp.com/attachments/773409630125817887/938370465280442408/unknown.png\n2021.10.22'
        elif '씨말' in a:
            b = 'https://media.discordapp.net/attachments/773409630125817887/938370650672885821/Screenshot_20211025-182458_Discord.png\n2021.10.25'
        elif a == '🇪🇷':
            b = 'https://media.discordapp.net/attachments/773409630125817887/938371080459018280/unknown.png\n2021.11.03'
        elif a == '중국확가':
            b = 'https://media.discordapp.net/attachments/773409630125817887/938371295408705556/Screenshot_20211108-130023_Discord.png\n2021.11.08'
        elif a == '🇦🇿':
            b = 'https://media.discordapp.net/attachments/773409630125817887/938371481518346271/Screenshot_20211110-101648_Discord.png\n2021.11.10'
        elif a == '🎆':
            b = 'https://media.discordapp.net/attachments/773409630125817887/938371708367298570/unknown.png?width=824&height=670\n2021.11.10'
        elif '옹옹' in a:
            b = 'https://media.discordapp.net/attachments/773409630125817887/938371859743928340/Screenshot_20211111-180716_Discord.png\n2021.11.11'
        elif '와' in a:
            b = 'https://media.discordapp.net/attachments/794563329560674344/909071800007290890/Screenshot_20211113-222638_Discord.jpg\n2021.11.13'
        elif '버스' in a:
            b = 'https://cdn.discordapp.com/attachments/749224990209212419/1205133954244681738/-_.png?ex=65d74374&is=65c4ce74&hm=079d3c9d61f2677778a4bf8bfe7ed599e943da332f30c8bd0ba43f421e4386bd&\n2021.11.15'
        elif a == '자자ㅣ':
            b = 'https://cdn.discordapp.com/attachments/773409630125817887/938372292168253440/unknown.png\n2021.11.19'
        elif a == '체라':
            b = 'https://media.discordapp.net/attachments/794563329560674344/911111650290057247/unknown.png\n2021.11.19'
        elif a == '필곤':
            b = 'https://cdn.discordapp.com/attachments/794563329560674344/912660132809310228/Screenshot_20211123-200527_Discord.jpg\n2021.11.23'
        elif a == '씨별':
            b = 'https://media.discordapp.net/attachments/773409630125817887/938373000095477760/Screenshot_20211206-024026_Discord.png\n2021.12.06'
        elif a == '원자분보':
            b = 'https://media.discordapp.net/attachments/794563329560674344/918828792988979220/Screenshot_20211210-203724_Discord.jpg\n2021.12.10'
        elif a == '고인무':
            b = 'https://cdn.discordapp.com/attachments/794563329560674344/919047613326704680/Screenshot_20211211-110700_Discord.jpg\n2021.12.11'
        elif a == '🎴':
            b = 'https://media.discordapp.net/attachments/773409630125817887/938373368292466759/unknown.png\n2021.12.13'
        elif a == '어타':
            b = 'https://media.discordapp.net/attachments/773409630125817887/938717851970310184/-__.png\n2021.12.14'
        elif 'rofll' in a or 'ROFLL' in a:
            b = 'https://media.discordapp.net/attachments/794563329560674344/920636362678501386/unknown.png\n2021.12.15'
        elif a == "VR":
            b = 'https://media.discordapp.net/attachments/794563329560674344/921013472425287721/unknown.png\n2021.12.16'
        elif a == '핑이나 멍거라!':
            b = 'https://media.discordapp.net/attachments/794563329560674344/921340432565288960/unknown-14.png\n2021.12.17'
        elif a == '↙️' or a == '↙':
            b = 'https://media.discordapp.net/attachments/794563329560674344/925233433872039986/Screenshot_20211228-124709_Discord.jpg\n2021.12.28'
        elif a == '🖌️':
            b = 'https://media.discordapp.net/attachments/794563329560674344/925251939275534377/Screenshot_20211228-140048_Discord.jpg\n2021.12.28'
        elif a == '풀음표':
            b = 'https://media.discordapp.net/attachments/794563329560674344/926437208494325810/unknown.png\n2021.12.31'
        elif a == '저ㅓㅁ에':
            b = 'https://media.discordapp.net/attachments/794563329560674344/927538619642708029/Screenshot_20220103-212715_Discord.jpg\n2022.01.03'
        elif a == '🇹🇭':
            b = 'https://media.discordapp.net/attachments/794563329560674344/930372514524307486/Screenshot_20220111-170739_Discord.jpg\n2022.01.11'
        elif a == '키팢':
            b = 'https://media.discordapp.net/attachments/794563329560674344/930760560562290728/Screenshot_20220112-184921_Discord.jpg\n2022.01.12'
        elif a in ['ㄹ', '저건 ㄹ']:
            b = 'https://media.discordapp.net/attachments/773409630125817887/938375196820242452/unknown.png\n2022.01.17'
        elif a == '오타ㅏ':
            b = 'https://media.discordapp.net/attachments/890783714232107079/936896106271498240/Screenshot_20220129-171035_Discord.jpg\n2022.01.29'
        elif a == '알데바락':
            b = 'https://cdn.discordapp.com/attachments/794563329560674344/1008294851340668998/Screenshot_20220814-174340_Discord.jpg?ex=65b613c1&is=65a39ec1&hm=a95a00ca4cdf622ba31c588385e8ee8a20615e219c7bf85f2140e5065a9f12f5&\n2022.08.14'
        elif a == '맞긴래':
            b = 'https://cdn.discordapp.com/attachments/794563329560674344/1010546774584328284/Screenshot_20220820-225144_Discord.jpg?ex=65d0ba06&is=65be4506&hm=7cce2c33713a6fe69229ba94a48fe09e8ae1c5a9c2069cd9e559fca95f656bff&\n2022.08.20'
        try:
            await send(ctx, b)
        except UnboundLocalError:
            await send(ctx, "없거나 아직 등록되지 않은 오타에요! `피론`은 오타원본이 유실되었지만 다른 오타는 찾아보면 어딘가는 있을 거에요. 빠진 오타라면 넣어 달라고 건의해주세요!")

    @command(name="뀨")
    async def premium(self, ctx, activity: Optional[str], *, item: Optional[str]):
        kkyu = db.record("SELECT kkyu FROM games WHERE UserID = ?", ctx.author.id)[0]
        if not activity:
            if randint(1, 5) != 1:
                await send(ctx, "뀨?!")
            else:
                activity = "도움"
        if activity == "도움":
            embed = Embed(color=0x00b2ff, title="커뉴봇의 한계를 돌파해볼까요?",
                          description="뀨는 커뉴봇에서 유일한 유료 재화입니다.\n현재는 마땅한 수단이 없어 개발자에게 직접 거래하는 방식으로 진행되고 있지만 만약 가능하다면 "
                                      "절차를 간단화하도록 노력하겠습니다.\n그렇다고 해도, 공식서버의 이벤트에 참여하거나 공식서버의 #건의와-질문 에서 유의미한 건의를 해 주시거나 하는 등 결제하지 "
                                      "않아도 뀨를 획득할 수 있는 수단 또한 존재합니다.\n아무래도 커뉴봇의 개발 방향상 공식서버의 레벨 밸런스같은 밸런스를 붕괴시키는 기능은 넣지 않을 예정이므로 큰 "
                                      "걱정을 하실 필요까지는 없어요!\n`커뉴야 뀨 도움`: 이 도움말을 표시합니다.\n`커뉴야 뀨 가격`: 뀨를 구매할 수 있는 결제 수단과 가격, "
                                      "기타 정보 등을 알려줍니다.\n`커뉴야 뀨 보유` 또는 `커뉴야 뀨 보유량`: 현재 보유 중인 뀨의 양을 알려줍니다.\n`커뉴야 뀨 상점`: 뀨로 구매할 수 있는 "
                                      "것들의 목록을 보여줍니다.\n`커뉴야 뀨 설명 (아이템명)`: (아이템명)에 대한 설명을 해 줍니다.\n`커뉴야 뀨 구매 (아이템명)`: (아이템명) 을 구매합니다.\n`커뉴야 뀨 인벤토리` (혹은 `커뉴야 뀨 인벤`): 현재까지 뀨로 "
                                      "구매한 것들의 목록을 보여줍니다. 상점의 1페이지에서 파는 기능만 보여줍니다.\n`커뉴야 뀨 주의사항`: 뀨와 관련된 행동을 하시기 전에 먼저 읽어야 할 사항들을 "
                                      "보여줍니다. 이 사항을 읽지 않음으로 인해 생기는 피해를 개발자는 보상하지 않습니다.")
            await send(ctx, embed=embed)
        elif activity == "가격":
            await send(ctx, embed=Embed(color=0x00b2ff, title="뀨 구매하기",
                                       description="결제 수단은 **문화상품권**, **Google Play 기프트 카드**, **Discord Nitro (또는 "
                                                   "클래식)**, **계좌이체** 로 가능합니다. 단 니트로로 결제는 항상 되는 것은 아닙니다. 현재는 니트로 또는 니트로 클래식으로의 결제가 "
                                                   "**가능합니다.**\n단, 계좌이체의 경우 10000원 이상을 결제하고 싶은 경우에만 받고 있습니다.\n\n아래는 가격표입니다. 한화로 "
                                                   "100원이 1뀨에 상응하며 한 번에 많은 뀨를 구입할 경우 약간의 보너스 뀨를 받을 수 있습니다.기본 가격표는 다음과 "
                                                   "같습니다.\n5000원 -> 50뀨\n10000원 -> 110뀨\n20000원 -> 240뀨\n만약 1000원같은 돈을 쓰시고 싶다면 "
                                                   "다음과 같은 방법으로 뀨가 지급됩니다:\n결제는 1000원 이상만 가능하며, 500원 단위로 카운트되고, 어뷰징 방지를 위해 500원 "
                                                   "미만은 버려집니다.\n기본적으로 한화 100원당 1뀨로 환산되고, 10000원과 20000원을 사면 받는 보너스는 똑같이 그 이상만큼의 "
                                                   "금액을 주시면 지급됩니다. (예: 11000원을 내셨다면 121뀨를 지급)\n어디까지나 돈이 오가는 내용은 민감한 내용이기 때문에 만약 "
                                                   "아이템 가격 조절 등이 일어난다면 억울한 일이 없도록 조절된 모든 내용을 다 반영해드립니다.\n환불은 어떤 방법으로든 구매한 지 7일 "
                                                   "이내에만 가능하며, 구매한 뀨를 쓰지 않은 상태여야 가능합니다.\n만약 모종의 버그로 인해 원래 그러지 않았어야 할 상황에서 뀨를 얻거나 "
                                                   "잃게 되면 그는 모두 롤백해 드립니다.\n기타 자신이 사고 쓴 뀨 이외에 돌발 상황이 발생한다면 모두 정상적인 상황이 되도록 "
                                                   "롤백합니다.\n\n구매가 정상적으로 완료되었다면 커뉴봇이 개인 메세지로 구매가 완료되었다고 말합니다. 꼭 개인 메세지 수신을 켜 주세요!"))
        elif activity == "주의사항":
            await send(ctx, 
                embed=Embed(color=0x00b2ff, title='뀨 구매, 사용 전 주의사항', description='1. 아이템을 구매하기 전, 자신이 구매하려고 하는 '
                                                                                 '아이템이 정확히 무슨 효과를 가지는지를 정확히 알고 구매하시길 바랍니다. 아이템을 구매할 때도 주의해야 할 사항이 있을 수 있습니다.\n2. 결제한 뀨를 환불하는 것은 `커뉴야 뀨 '
                                                                                 '가격`에 적혀 있는 기준에 따라 가능하지만, 뀨로 아이템을 구매한 이후 그 아이템을 환불하는 것은 불가능합니다.\n3. 상점의 2페이지에 있는 모든 아이템들은 아이템을 구매하신 '
                                                                                 '**서버**에 귀속됩니다.'))
        elif activity == "상점":
            if not item:
                embed = Embed(color=0x00b2ff, title="뀨 상점",
                              description="1. 새로운 기능 해금\n2. 기존 기능 강화\n3. 서버 단위의 기능\n커뉴핑크 안에서 뀨로 사는 아이템들의 경우 커뉴핑크 상점을 통해 찾아주세요\n`커뉴야 뀨 상점 <1/2/3/4>`으로 목록을 확인하세요")
                embed.set_footer(
                    text='구매한 경우에만 쓸 수 있는 명령어 또는 세부 옵션이 존재한다면 1페이지, 그렇지 않다면 (구매한 경우에만 자동으로 추가되는 옵션 등) 2페이지로 분류됩니다.')
                await send(ctx, embed=embed)
                return
            try:
                item = int(item)
            except:
                await send(ctx, "올바르지 않은 입력이에요!")
                return
            if item == 1:
                await send(ctx, embed=Embed(color=0x00b2ff, title="뀨 상점",
                                           description='알파 센타우리: 15뀨\n오목 자동 매칭: 9뀨\n다채로운 기원목록: 5뀨\n자세한 스톱워치: 3뀨\n도전과제 페이지순 정렬: 2뀨\n새로운 줄임말: 2뀨\n금성챗 특정숫자 알림: 2뀨\n퀴즈 주제 다중 선택: 5뀨\nTMI 트래커: 6뀨'))
            elif item == 2:
                await send(ctx, embed=Embed(color=0x00b2ff, title="뀨 상점",
                                           description='출첵내역 연장: 1뀨\n도전과제 달성률 표시: 5뀨\n강화슬롯 추가: 2뀨\n더 좋은 도전과제 목록: 6뀨\n지분 순위: 8뀨'))
            elif item == 3:
                await send(ctx, embed=Embed(color=0x00b2ff, title="뀨 상점",
                                           description='이곳까지 찾아와주셔서 감사합니다. 이야기가 나와서 말인데, 서버 관련된 기능은 무엇을 넣어야 괜찮을까요? 사실 꼭 서버 관련된 기능이 아니더라도, 뀨와 관련되어 있든 아니든 봇과 관련된 아이디어는 어떤 것이라도 감사히 받고 있습니다.\n새로운 뀨 아이템 아이디어가 채택된다면, 제안해주신 아이템은 실제로 책정된 가격과 상관없이 무료로 지급됩니다.\n다른 아이디어들도 정상적인 아이디어를 제공해 주신다면 감사히 받고 있고 도전과제로 보상해 드리고 있습니다!'))
            elif item == 4:
                await send(ctx, embed=Embed(color=0x00b2ff, title="뀨 상점", description='공식서버 들낙 해제: 1950뀨'))
        elif activity in ["보유", "보유량"]:
            await send(ctx, f"현재 {str(ctx.author)} 님은 {kkyu}뀨를 가지고 있어요!")
        elif activity == "구매":
            if item == "알파 센타우리":
                p = await self.purchase_kkyu(ctx, kkyu, item, 15,
                                             "도전과제 \"알파 센타우리\" 및 #알파-센타우리 채널 입장권\n\n돈 주고 게임을 사는 건 흔한 일이죠.\n주의: 커뉴봇의 데이터베이스에 이 아이템을 구매했다고 저장하는 대신, 게임을 플레이할 수 있는 채널 입장권만 부여합니다. 즉, 이 아이템을 구매한 후 서버에서 나갔다가 다시 들어온다면 아이템이 그냥 날아가는 셈이 됩니다.")
                if p:
                    l = grant_check("알파 센타우리", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "알파 센타우리", "알파 센타우리를 구매하세요")
                    else:
                        await send(ctx, "이미 구매한 상품이에요!")
                        return
                    await self.bot.get_channel(916323859731464202).set_permissions(ctx.author, read_messages=True)
            elif item == "출첵내역 연장":
                duration = db.record("SELECT max_attend FROM games WHERE UseriD = ?", ctx.author.id)[0]
                if duration == 25:
                    await send(ctx, "더 이상 구매할 수 없는 아이템이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 1,
                                             "출첵내역 명령어에서 볼 수 있는 출첵 내역들을 2일만큼 연장합니다. 5회까지만 구매 가능합니다.")
                if p:
                    duration += 2
                    db.execute("UPDATE games SET max_attend = ? WHERE useriD = ?", duration, ctx.author.id)
                    db.commit()
            elif item == "공식서버 들낙 해제":
                meta = self.bot.get_guild(743101101401964647)
                banlist = await meta.bans()
                bl = {}
                for b in banlist:
                    bl[b.user.id] = b.reason
                if ctx.author.id in bl and bl[ctx.author.id] == "들낙":
                    p = await self.purchase_kkyu(ctx, kkyu, item, 1950,
                                                 "들낙으로 인해 공식서버 밴을 당했다면 그걸 풀어 드립니다.")
                    if p:
                        await meta.unban(ctx.author.id)
                        await send(ctx, 
                            "가끔 이 아이템을 사고도 언밴이 안 될 때가 있습니다.\n그런 경우는 방금 밴이 풀려서 아직 그것이 반영되지 않았을 가능성이 높습니다.\n그런 경우가 아니라면 당신의 부계정 등도 이 서버에서 같이 밴당해서 IP 밴 때문에 밴이 풀린 계정에서도 밴을 당한 것처럼 되는 경우입니다.\n이런 일이 일어날 경우\n1. 디스코드를 껐다 켜세요\n2. 컴퓨터 자체를 껐다 켜세요\n3. VPN이나 프록시 서버 등에 접속해 잠시 네트워크를 우회한 뒤 시도하세요\n만약 그러고도 서버에 들어와지지 않는다면 개발자에게 문의해주세요.")
                else:
                    await send(ctx, 
                        "공식서버에서 차단당하지 않았거나 들낙이 아닌 사유로 차단된 사용자에요! 정말로 들낙으로 밴당하신게 맞으면 `커뉴야 문의`로 문의해주시면 확인해 드릴게요.")
            elif item == "오목 자동 매칭":
                setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if setting & 8:
                    await send(ctx, "이미 구매한 상품이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 9,
                                             "굳이 특정한 방에 들어가지 않아도 규칙만 고르면 자동으로 오목 매칭을 시켜드립니다. (구매 후 `커뉴야 오목 자동매칭 (규칙명)`으로 자동 매칭 가능)")
                if p:
                    setting += 8
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", setting, ctx.author.id)
                    db.commit()
            elif item == "도전과제 달성률 표시":
                setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if setting & 64:
                    await send(ctx, "이미 구매한 상품이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 5,
                                             "`커뉴야 도전과제 설명 (도전과제이름)`을 사용하면 원래 도전과제 설명이 나오던 것과 더불어 도전과제의 달성률도 같이 나옵니다.")
                if p:
                    setting += 64
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", setting, ctx.author.id)
                    db.commit()
            elif item == "강화슬롯 추가":
                enchant_info = db.record("SELECT enchant_info FROM games WHERE UseriD = ?", ctx.author.id)
                enchant_info = json.loads(enchant_info[0])
                if enchant_info["최대강화가능개수"] != 10:
                    await send(ctx, 
                        "공식서버의 상점에서 파는 `강화 슬롯 추가권`을 아직 최대로 구매하지 않으셨어요. 그걸로 추가 가능한 강화 슬롯의 한계가 뀨로 살 수 있는 강화 슬롯의 한계보다 "
                        "적으니 먼저 공식서버의 상점에서 강화 슬롯 추가권을 끝까지 사신 뒤 이 아이템을 구매하시는 것을 추천드려요. 뭐...물론 말리진 않아요")
                if enchant_info["최대강화가능개수"] != 15:
                    await send(ctx, "이미 이 아이템을 최대로 구매했어요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 2,
                                             "공식서버의 강화 슬롯 추가권과 동일한 역할을 하지만 강화 슬롯이 10개일 때 구매하는 것을 추천드립니다. 강화슬롯이 15개가 될 때까지 구매 가능합니다.")
                if p:
                    enchant_info["최대강화가능개수"] += 1
                    db.execute("UPDATE games SET enchant_info = ? WHERE UserID = ?",
                               json.dumps(enchant_info, ensure_ascii=False), ctx.author.id)
                    db.commit()
            elif item == "다채로운 기원목록":
                setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if setting & 16:
                    await send(ctx, "이미 구매한 상품이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 5,
                                             "`커뉴야 기원목록`명령어에 더 다양한 옵션을 해금합니다. `커뉴야 기원목록`뒤에 랜덤, 신규, 오늘기원됨, 오랫동안기원됨 을 붙이면 해당 순서로 기원들이 출력됩니다.")
                if p:
                    setting += 16
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", setting, ctx.author.id)
                    db.commit()
            elif item == "자세한 스톱워치":
                setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if setting & 4:
                    await send(ctx, "이미 구매한 상품이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 3,
                                             "`커뉴야 스톱워치 내역`에서 개별적인 스톱워치 내역에 대해 각 구간별로 얼마나 시간이 지났는지를 따로 게산해 줍니다. 이후의 업데이트에서 제목이 같고 기록한 횟수가 같은 다른 스톱워치 기록들과 비교분석하는 기능도 추가시킬 예정입니다.")
                if p:
                    setting += 4
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", setting, ctx.author.id)
                    db.commit()
            elif item == "도전과제 페이지순 정렬":
                setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if setting & 32:
                    await send(ctx, "이미 구매한 상품이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 2,
                                             "`커뉴야 도전과제`로 나오는 획득한 도전과제들을 페이지로 정렬합니다. 구매 후 `커뉴야 도전과제 페이지순`으로 가능합니다.")
                if p:
                    setting += 32
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", setting, ctx.author.id)
                    db.commit()
            elif item == '새로운 줄임말':
                setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if setting & 256:
                    await send(ctx, "이미 구매한 상품이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 2,
                                             "`커뉴야 우주탐험`, `커뉴야 잡초키우기`에 대해 각각 `ㅇㅌ`, `ㅈㅋ`라는 새로운 줄임말을 해금합니다.")
                if p:
                    setting += 256
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", setting, ctx.author.id)
                    db.commit()
            elif item == '더 좋은 도전과제 목록':
                setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if setting & 512:
                    await send(ctx, "이미 구매한 상품이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 6,
                                             "`커뉴야 도전과제 목록`에 나온 도전과제 중 어떤 도전과제를 달성했는지를 추가로 보여줍니다.")
                if p:
                    setting += 512
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", setting, ctx.author.id)
                    db.commit()
            elif item == '지분 순위':
                setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if setting & 1024:
                    await send(ctx, "이미 구매한 상품이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 8,
                                             "`커뉴야 지분`으로 당신의 지분을 알아볼 때 전체 유저 중 몇 번째로 많이 특정 커맨드를 사용했는지도 추가로 보여줍니다.")
                if p:
                    setting += 1024
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", setting, ctx.author.id)
                    db.commit()
            elif item == '금성챗 특정숫자 알림':
                setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if setting & 2048:
                    await send(ctx, "이미 구매한 상품이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 2,
                                             "(공식서버에 가입되어 있어야 효과가 있습니다) <#743339107731767366>에서 특정 수가 세어졌을 경우 커뉴봇이 개인 메세지로 알려줍니다. 특정 수는 `커뉴야 금성알림`으로 조회 및 변경할 수 있습니다.")
                if p:
                    setting += 2048
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", setting, ctx.author.id)
                    db.commit()
            elif item == '퀴즈 주제 다중 선택':
                setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if setting & 8192:
                    await send(ctx, "이미 구매한 상품이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 5,
                                             "`커뉴야 퀴즈 풀기`에서 특정한 주제를 정하고 싶을 때 주제들을 컴마로 구분하면 여러 주제 중 랜덤 문제를 풀 수 있습니다. 예시: `커뉴야 퀴즈 풀기 영어, 수학`")
                if p:
                    setting += 8192
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", setting, ctx.author.id)
                    db.commit()
            elif item == 'TMI 트래커':
                setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if setting & 16384:
                    await send(ctx, "이미 구매한 상품이에요!")
                    return
                p = await self.purchase_kkyu(ctx, kkyu, item, 6,
                                             "`커뉴야 심심해`에서 `커뉴야 심심해 리스트`를 사용하면 지금까지 발견한 TMI 목록을, `커뉴야 심심해 (번호)`를 사용하면 발견한 TMI에 한해 해당 번호의 TMI를 보여줍니다. 주의: yonsei1 업데이트 또는 그 이후에 발견한 TMI만 기록됩니다.")
                if p:
                    setting += 16384
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", setting, ctx.author.id)
                    db.commit()
        elif activity == '설명':
            d = db.record("SELECT description FROM kkyu WHERE name = ?", item)[0]
            await send(ctx, embed=Embed(color=0x00b2ff, title="아이템 설명", description=d))
        elif activity in ['인벤', '인벤토리']:
            raw_inven = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
            max_attend = db.record("SELECT max_attend FROM games WHERE UserID = ?", ctx.author.id)[0]
            tjfaud = '**혹시 구매한 무언가가 누락되어 있을 경우 `커뉴야 문의`로 문의주세요. 구매하지 않은 것처럼 되어 있더라도 구매한 데이터는 항상 남아 있기 때문에 복구가 가능합니다.**\n예외적으로, 알파 센타우리는 구매해도 아래 목록에 뜨지 않습니다. 알파 센타우리 채널을 접근할 권한이 있는지 확인해보세요.'
            if max_attend > 15:
                tjfaud += f'\n출첵내역 연장: {(max_attend - 15) // 2} / 5 회 구매'
            if raw_inven & 4:
                tjfaud += "\n자세한 스톱워치"
            if raw_inven & 8:
                tjfaud += "\n오목 자동 매칭"
            if raw_inven & 16:
                tjfaud += "\n다채로운 기원목록"
            if raw_inven & 32:
                tjfaud += "\n도전과제 페이지순 정렬"
            if raw_inven & 64:
                tjfaud += "\n도전과제 달성률 표시"
            if raw_inven & 256:
                tjfaud += "\n새로운 줄임말"
            if raw_inven & 512:
                tjfaud += "\n더 좋은 도전과제 목록"
            if raw_inven & 1024:
                tjfaud += "\n지분 순위"
            if raw_inven & 2048:
                tjfaud += "\n금성챗 특정숫자 알림"
            if raw_inven & 8192:
                tjfaud += "\n퀴즈 주제 다중 선택"
            if raw_inven & 16384:
                tjfaud += "\nTMI 트래커"
            await send(ctx, tjfaud or "구매한 아이템이 없어요!")

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

    @command(name='금성알림')
    async def venus_notification(self, ctx, activity: Optional[str] = '도움', number: Optional[int] = -1):
        if activity == '도움':
            embed = Embed(color=0xc1Bcb6, title='금성챗 특정 수 알림', description='만약 구매하지 않으셨다면, `커뉴야 뀨 구매 금성챗 특정숫자 알림`으로 '
                                                                           '먼저 명령어를 구매하신 뒤 이용하셔야 합니다.\n`커뉴야 금성알림 도움`: '
                                                                           '이 도움말을 표시합니다.\n`커뉴야 금성알림 조회` 또는 `커뉴야 금성알림 '
                                                                           '현재`: 현재 어떤 수가 세어질 때 '
                                                                           '알림을 보내도록 되어 있는지를 확인합니다.\n`커뉴야 금성알림 지정 ('
                                                                           '지정할 수)`: (지정할 수) 가 세어지면 커뉴봇이 알림을 보내도록 '
                                                                           '설정합니다.\n`커뉴야 금성알림 취소`: 만약 나중에 알림을 보내기로 되어 '
                                                                           '있었다면 그것을 취소합니다.')
            await send(ctx, embed=embed)
        else:
            if not db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0] & 2048:
                await send(ctx, '구매하지 않은 상품이에요!')
                return
            if activity == '조회':
                current_notification = db.record("SELECT venus FROM games WHERE UserID = ?", ctx.author.id)[0]
                current_venus_num = db.record("SELECT num FROM channels WHERE ChannelID = 743339107731767366")[0]
                if not current_notification or current_notification < current_venus_num:
                    await send(ctx, '아무것도 지정하지 않았거나 이미 알림을 보낸 후에요!')
                    return
                else:
                    await send(ctx, 
                        f"지금은 {current_notification}이 세어지면 알림을 받기로 돼 있어요! 참고로 현재는 {current_venus_num - 1}까지 세어진 상태에요.")
                    return
            elif activity == '지정':
                if number == -1:
                    await send(ctx, '`커뉴야 금성알림 지정 (지정할 수)`')
                    return
                current_venus_num = db.record("SELECT num FROM channels WHERE ChannelID = 743339107731767366")[0]
                if number < current_venus_num:
                    await send(ctx, '이미 금성채널에서는 그 수를 셌어요!')
                    return
                await send(ctx, f"설정을 완료했어요! {number}이 세어진다면 알림을 보낼게요. 봇이 DM을 보낼 수 있는 상태인지 `커뉴야 디엠테스트`등으로 확인해보세요.")
                db.execute("UPDATE games SET venus = ? WHERE UserID = ?", number, ctx.author.id)
                db.commit()
            elif activity == '취소':
                current_notification = db.record("SELECT venus FROM games WHERE UserID = ?", ctx.author.id)[0]
                if current_notification:
                    await send(ctx, "취소를 완료했어요!")
                    db.execute("UPDATE games SET venus = NULL WHERE UserID = ?", ctx.author.id)
                    db.commit()
            else:
                await send(ctx, '`커뉴야 금성알림 <도움/조회/지정/취소>`')

    def to_visual_line(self, line_name):
        if line_name[-1].isdigit():
            return line_name + '호선'
        elif line_name == '공항철도':
            return line_name
        return line_name + '선'

    @command(name='지하철')
    async def subway(self, ctx, activity: Optional[str] = '도움', station: Optional[str] = ''):
        l = grant_check("미래를 보는 자", ctx.author.id)
        if l == 1:
            await grant(ctx, "미래를 보는 자", "커뉴봇의 나중 버전에서 새로 나온 명령어를 실행하세요. 시제가 이상하다고요?")
        if activity == '도움':
            await send(ctx, embed=Embed(color=0xffd6fe, title='커뉴의 지하철외우기 프로젝트(베타)',
                                       description='지하철 노선도의 암기를 도와줍니다. 현재는 수도권 지하철 중에서도 일부만 지원하며 코드가 안정적이라는 확신이 된 이후 '
                                                   '더 많은 노선을 추가할 계획입니다. 암기를 도우는 데 초점이 맞춰져 있으므로, '
                                                   '많은 정보를 얻기를 기대하지는 말아주세요.\n`커뉴야 지하철 도움`: 이 도움말을 표시합니다.\n`커뉴야 지하철 노선`: 전체 지하철 '
                                                   '노선도를 출력합니다. 최종 업데이트: 2023년 6월 30일, 서해선 연장된 버전 있으면 제보 부탁드립니다.\n`커뉴야 지하철 역정보 ('
                                                   '역이름)`: 특정 역에 대해, 그 역에 어느 지하철이 지나는지 등의 간단한 정보를 출력합니다.\n`커뉴야 지하철 표시규칙`: 이 기능에서 '
                                                   '표시하는 것과 표시하지 않는 것의 규칙을 출력합니다.'))
            return
        elif activity == '노선':
            await send(ctx, 
                'https://media.discordapp.net/attachments/772705777407229992/1126005616196993154/6fae783e2a50557b.png?width=1042&height=670')
        elif activity == '표시규칙':
            await send(ctx, '## 이 명령어의 모든 기능은 다음과 같은 규칙을 따라서 표시합니다.\n1. 부역명이 있어도 이를 무시합니다. 대청(서울주택도시공사) 역은 대청역으로 표시하며, '
                           '왕십리역은 왕십리(성동구청)으로 되어 있는 노선도 있고 왕십리역으로 되어 있는 노선도 있지만 왕십리역으로 표시합니다.\n2. 예외적인 경우로 2호선 신촌역은 경의중앙선 신촌역과 헷갈리지 '
                           '않기 위해 신촌(지하)로 표기합니다.\n3. 동대문역사문화공원역: DDP역 처럼 줄인 이름으로 많이 불리는 지하철역이더라도, `동대문역사문화공원역` 처럼 정식 명칭으로 표시합니다.\n4. '
                           '이수(총신대입구)역인지 총신대입구(이수) 역인지 아무튼 그 역은 이수역으로 표시합니다. 총신대입구로 검색할 시 검색되지 않습니다.\n5. 모든 명칭은 현재를 기준으로 합니다. 예를 들어, '
                           '신천역에서 이름이 바뀐 잠실새내역은 잠실새내역으로만 표기합니다. 이 경우 신천으로 검색해도 검색되도록 구현 중입니다. (아직은 안됨)')
        elif activity == '역정보':
            if not station:
                await send(ctx, '`커뉴야 지하철 역정보 (역이름)`')
                return
            # colors =
            colors = [0xffd6fe]
            station_obj = eval(station)
            desc = ''
            if station_obj.transfer:
                transfer = '환승역'
            else:
                transfer = ''
            desc += '지나가는 지하철(들)은 다음과 같아요:\n'
            lines = station_obj.lines
            for line in lines:
                desc += f'{self.to_visual_line(line)} (역번호: {lines[line]})\n'
            await send(ctx, embed=Embed(title=station + '역' + transfer, color=choice(colors), description=desc))

    @command(name='소수판정', aliases=['소수판별'])
    async def primality_test_command(self, ctx, n: int):
        if n <= 1 or n > 10**1980:
            await send(ctx, ":weary:")
            return
        primality = isprime(n)
        if not primality:
            await send(ctx, f"{n}: 무조건 합성수입니다.")
        else:
            if n < 318665857834031151167461:
                await send(ctx, f"{n}: 무조건 소수입니다.")
            else:
                await send(ctx, f"{n}: 아마도 소수입니다.")

    @command(name='소인수분해')
    @cooldown(1, 5, BucketType.user)
    async def prime_factorization_command(self, ctx, n: int):
        if n == 1 or (n < 318665857834031151167461 and isprime(n)):
            await send(ctx, f'{n} = **{n}**')
            return
        if n == 318665857834031151167461:
            await send(ctx, '318665857834031151167461 = **399165290221 × 798330580441**')
            return
        if n <= 0:
            await send(ctx, ":weary:")
            return
        start_time = time()
        clock = start_time
        factors = defaultdict(int)
        m = n
        while n - 1:
            k = pollard_rho(n, clock)
            if k is None:
                break
            factors[k] += 1
            n //= k
            clock = time()
            if clock - start_time > 1:
                break
        if n != 1:
            await send(ctx, '너무 오래 걸려요...')
            return
        else:
            power_list = list('⁰¹²³⁴⁵⁶⁷⁸⁹')
            result = []
            distinct_factors = sorted(factors)
            for factor in distinct_factors:
                power = factors[factor]
                if power == 1:
                    result.append(str(factor))
                else:
                    result.append(str(factor) + ''.join([power_list[i] for i in list(map(int, list(str(power))))]))
            result = ' × '.join(result)
            if distinct_factors[-1] > 318665857834031151167461:
                result += ' ?'
            await send(ctx, f'{m} = **{result}**')

    @command(name='계산')
    @cooldown(1, 5, BucketType.user)
    async def conu_calculator(self, ctx, *, expression: Optional[str] = ''):
        if not expression:
            await send(ctx, "`커뉴야 계산 (계산식)`\n이 명령어를 처음 사용하신다면 `커뉴야 계산 도움`을 먼저 확인해보시는 것을 권장드립니다")
            return
        user_setting = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
        if expression == '도움':
            await send(ctx, embed=Embed(color=0xffd6fe,
                                       title='커뉴봇 계산 명령어 도움: ver.stable_2 (yonsei5)',
                                       description='식을 입력받아 계산하는 프로그램입니다.\n'
                                                   '기본적인 연산자는 +, -, *, /, **, %가 있으며 각각 덧셈, 뺄셈, 곱셈, 나눗셈, 제곱, 모듈로 연산을 의미합니다.\n'
                                                   '사용할 수 있는 함수는 현재는 sqrt, exp, ln, sin, cos, tan, harmonic이 있으며 각각 루트, 자연지수, 자연로그, 사인, 코사인, 탄젠트, 조화급수를 의미합니다.\n'
                                                   '사용할 수 있는 상수는 pi, gamma가 있으며 각각 원주율, 오일러-마스케로니 상수를 의미합니다.\n'
                                                   'e의 경우 파싱 과정에서 어려움을 겪고 있어서 지금은 추가되지 않은 상태고 나중에 추가될 예정입니다. e가 필요하시면 exp(1)을 사용해주세요.\n'
                                                   '앞으로 더 많은 함수들과 상수들이 추가될 예정입니다.\n'
                                                   '명령어에 관한 설정들을 바꾸고 싶다면 `커뉴야 계산 설정`\n'
                                                   'eval 함수는 사용하지 않아요. 이게 무슨 뜻인지 모르신다면 무시하셔도 좋습니다.'))
        elif expression.startswith('설정'):
            if expression == '설정':
                await send(ctx, embed=Embed(color=0xffd6fe,
                                           title='계산 명령어 설정',
                                           description=f'나눗셈 등으로 답이 유리수일 때 **{["분수", "소수"][user_setting & 131072 != 0]}**로 표시\n'
                                                       f'변경을 원하면 `커뉴야 계산 설정 <분수표기/소수표기>\n'
                                                       f'게산 결과의 정밀도 ****'))
            elif expression == '설정 분수표기':
                if user_setting & 131072:
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", user_setting - 131072, ctx.author.id)
                    await ctx.send('완료')
                else:
                    await ctx.send('엄')
            elif expression == '설정 소수표기':
                if not user_setting & 131072:
                    db.execute("UPDATE games SET user_setting = ? WHERE UserID = ?", user_setting + 131072, ctx.author.id)
                    await ctx.send('완료')
                else:
                    await ctx.send('엄')
        else:
            rpn = infix_to_postfix(expression)
            res = eval_postfix(rpn)
            if isinstance(res, Fraction):
                if user_setting & 131072:
                    await send(ctx, f"{ctx.author.mention}\n{float(res):,.5f}")
                else:
                    await send(ctx, f"{ctx.author.mention}\n{res}")
            else:
                await send(ctx, f"{ctx.author.mention}\n{res:,.5f}")

    @command(name='글자수')
    async def char_length_command(self, ctx, *, s):
        bsn = '\n'
        if '서준' in s or '서바준보' in s or '3웨' in s:
            await send(ctx, 
                f'{ctx.author.mention} 공백 및 줄바꿈 포함 {len(s)}자, 공백 및 줄바꿈 3웨 {len(s) - s.count(" ") - s.count(bsn)}자')
            l = grant_check("3웨", ctx.author.id)
            if l == 1:
                await grant(ctx, "3웨", "드립 칠 의도가 없으셨다면 죄송합니다")
        else:
            await send(ctx, 
                f'{ctx.author.mention} 공백 및 줄바꿈 포함 {len(s)}자, 공백 및 줄바꿈 제외 {len(s) - s.count(" ") - s.count(bsn)}자')

    @command(name='다음거울수')
    async def next_palindrome_command(self, ctx, n: str):
        if not n.isdigit():
            await send(ctx, '자연수로만 입력해 주세요.')
            return
        if len(n) > 1800:
            await send(ctx, '입력으로는 1800자리까지의 자연수만 가능해요!')
            return
        p = next_palindrome(n)
        if n == n[::-1]:
            txt = f'주어진 수는 거울수이고, '
        else:
            txt = f'주어진 수는 거울수가 아니고, '
        await send(ctx, txt + f'주어진 수보다 큰 거울수 중 가장 작은 것은 {p} 에요!')

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print('("fun")')

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id == 764291796998029332:
            await message.delete()
            await message.channel.send(f"{message.author}: {self.translate_SBJB(message.content)}")
            return
        if message.content == "큐 767":
            l = grant_check("이일일삼ㅅ...갸아앍 너무빨라", message.author.id)
            if l == 1:
                await grant(message, "이일일삼ㅅ...갸아앍 너무빨라", "좀더 느리게 다시 해봐요...")
        if isinstance(message.channel, DMChannel):
            now_room = db.record("SELECT room_number FROM games WHERE UserID = ?", message.author.id)
            if not now_room:
                return
            try:
                now_room = now_room[0]
            except TypeError:
                return
            if not now_room or now_room < 10000000:
                return
            random_chats = db.record("SELECT UserID FROM games WHERE room_number = ? AND UserID != ?", now_room,
                                     message.author.id)
            if random_chats is None:
                return
            if "discord.gg/" in message.content:
                await message.channel.send("서버 홍보하실려면 다른 데에서 해 주세요!")
                return
            random_chats = random_chats[0]
            await self.bot.get_user(random_chats).send(f"{str(message.author)}: {message.content}")


async def setup(bot):
    await bot.add_cog(Fun(bot))
