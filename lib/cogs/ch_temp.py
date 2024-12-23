import asyncio
import re
from calendar import monthrange
from typing import Optional
from time import *
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from anytree import AnyNode
from anytree import RenderTree
from anytree.exporter import JsonExporter
from anytree.importer import JsonImporter
from collections import deque
from discord import File, HTTPException, app_commands, Member, Embed, ui, Interaction, ButtonStyle
from discord.app_commands import Choice
from discord.ext.commands import Cog
from scipy.interpolate import make_interp_spline
from ..db import db
from datetime import datetime, timedelta

# -*- coding: utf-8 -*-
today = (time() + 32400) // 86400
study_messages = dict()
study_times = dict()
study_infos = dict()
message_waiting = dict()
message_output = dict()


class Cmds(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='공부정보', description='공부와 관련된 갖가지 정보를 보여줘요')
    async def hello(self, interaction):
        await main_function(interaction)

    """"@app_commands.command(name='출첵', description='봇을 사용하기 전에 매일 출석부터 하자')
    async def attend_command(self, interaction):
        await attend(interaction)"""

    @app_commands.command(name="할일추가", description='할 일을 추가해요. (슬래시 명령어 전용)')
    @app_commands.choices(
        종류=[Choice(name='비워두기', value=''), Choice(name='개념공부', value='개념공부'), Choice(name='문제풀이', value='문제풀이'),
            Choice(name='모의고사', value='모의고사'), Choice(name='복습하기', value='복습하기')])
    async def todo(self, interaction, 큰분류: Optional[str], 중간분류: Optional[str], 작은분류: Optional[str], 교재: Optional[str],
                   내용: str,
                   종류: Optional[str], 기간: str, 같이: Optional[Member],
                   얼마마다: Optional[str], 분량: Optional[str] = '0'):
        attend_check = db.record("SELECT USERID FROM ATTENDS WHERE ATTEND_DATE = ? AND USERID = ?",
                                 (time() + 32400) // 86400, interaction.user.id)
        if not attend_check:
            await interaction.channel.send("먼저 출석체크를 해 주세요")
            return
        if "%" in 내용 or "_" in 내용:
            await interaction.response.send_message("%나 _는 이름으로 쓸 수가 없어요...")
            return

        if not 기간:
            기간 = ''
        기간 = 기간.replace(" ", "")
        duration = re.compile("\d+일|\d+시간|\d+분")
        fa = duration.findall(기간)
        if fa:
            dt = 0
            for f in fa:
                if f.endswith("일"):
                    dt += 86400 * int(f[:-1])
                elif f.endswith("시간"):
                    dt += 3600 * int(f[:-2])
                elif f.endswith("분"):
                    dt += 60 * int(f[:-1])
            until = datetime.now() + timedelta(seconds=dt)
        else:
            await interaction.response.send_message("다른 입력 형식도 만드는 중이에요!")
            return
            # todo 이번주 월요일, 다음달 3일 등
        '''else:
            now = datetime.now()
            year = now.year
            duration = re.compile(".*월.*주.*일\d*시")
            fa = duration.findall(기간)
            if fa:
                for f in fa:
                    if f == "이번달":
                        month = now.month
                    elif f == "다음달":
                        if now.month == 12:
                            year += 1
                            month = 1
                    elif f == '''

        큰분류, 중간분류, 작은분류, 교재 = await handle_shortcut(interaction, 내용, 큰분류, 중간분류, 작은분류, 교재)

        interval_info = 0
        if 얼마마다:
            if re.compile('\d+일').search(얼마마다):
                sgn = 1
                val = 얼마마다[:-1]
                val = int(val)
            elif 얼마마다 == '매일':
                sgn = 1
                val = 1
            else:
                sgn = -1
                dates = list(얼마마다)
                yoils = set()
                for date in dates:
                    yoils.add(list('월화수목금토일').index(date))
                yoils = map(str, sorted(yoils, reverse=True))
                val = int(''.join(yoils))
            interval_info = sgn * val

        uid = [interaction.user.id]
        if 같이:
            uid.append(같이.id)
        uid = ','.join(list(map(str, uid)))

        quantity = re.findall(r'\d+', 분량)[0]
        unit = re.findall(r'\D+', 분량)
        if unit:
            unit = unit[0]
            if 분량.find(quantity) > 분량.find(unit):
                await interaction.response.send_message(
                    '분량은 10페이지,5장,40문제, 20 처럼 입력해 주세요... 분량을 정하기 싫으면 0만 입력하면 돼요.')
                return
        else:
            unit = None
        if not quantity:
            quantity = -1
        db.execute(
            'INSERT INTO TASKS (IDS, BIG_SUBJECT, SUBJECT, SMALL_SUBJECT, BOOK_NAME, SPECIFIC_CONTENT, STUDY_TYPE, '
            'UNTIL, AMOUNT_OF_TASK, UNIT_OF_TASK, REPETITION) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            uid, 큰분류, 중간분류, 작은분류, 교재, 내용, 종류, until, quantity, unit, interval_info)
        db.commit()
        view = MakeTaskButtons(timeout=60, user=interaction.user)

        embed = Embed(color=0x00b2ff, title='새로운 할 일이 생겼어요.')
        embed.add_field(name='분류', value=f'{큰분류}-{중간분류}-{작은분류}')
        embed.add_field(name='할 일', value=내용)
        if not 같이:
            embed.add_field(name='할 사람', value=str(interaction.user))
        else:
            embed.add_field(name='할 사람들', value=str(interaction.user) + 같이.name)
        if 교재:
            embed.add_field(name='교재', value=교재)
        if 종류:
            embed.add_field(name='타입', value=종류)
        if not 얼마마다:
            embed.add_field(name='기간', value=until)
        else:
            embed.add_field(name='반복', value=얼마마다)
        embed.add_field(name='분량', value=분량)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name='할일진행')
    async def task_progress(self, interaction, 내용: str, 진행할분량: int, 공부한시간_기록용: str):
        ch = interaction.channel
        search = db.records("SELECT * FROM TASKS WHERE IDS LIKE ? AND SPECIFIC_CONTENT LIKE ?",
                            f'%{interaction.user.id}%', f'%{내용}%')
        if not (now := await fetch_work(interaction, search)):
            return
        embed = Embed(color=0x00b2ff, title='할 일 진행 완료')
        new = list(now).copy()
        # now 유저아이디 큰 중간 작은 교재 내용 종류 기간 분량 반복 분량단위 진행도
        new[11] += 진행할분량
        if new[11] >= now[8]:
            new[11] = now[8]
            embed.add_field(name="진행한 분량", value=str(now[8] - now[11]))
            embed.add_field(name="진행도", value=f"{now[8]} / {now[8]} (100%)")
        else:
            embed.add_field(name="진행한 분량", value=str(진행할분량))
            embed.add_field(name="진행도", value=f"{new[11]} / {now[8]} ({round((new[11] / now[8]) * 100, 2)}%)")
        embed.add_field(name='기한', value=now[7] or '무기한')
        await ch.send(embed=embed)
        db.execute("UPDATE TASKS SET PROGRESSION = ? WHERE IDS LIKE ? AND SPECIFIC_CONTENT LIKE ?", new[11],
                   f'%{interaction.user.id}%', f'%{내용}%')
        db.commit()
        await ch.send('방금 한 것을 공부 기록으로 남기려면 **a/b**형태로 입력해주세요.')
        try:
            msg = await self.bot.wait_for(
                "message",
                timeout=120,
                check=lambda message: message.author == interaction.user and interaction.channel == message.channel
            )
        except asyncio.TimeoutError:
            return
        await ch.send("성공적으로 기록했어요!")
        await self.grades(interaction, now[1], now[2], now[3], now[4], now[5], now[6], msg.content, 공부한시간_기록용)

    @app_commands.command(name='할일현재')
    async def display_tasks(self, interaction):
        embed = Embed(color=0x00b2ff, title=f'{str(interaction.user)}님의 현재 할 일 (급한 순 정렬)')
        timed_tasks = db.records(
            "SELECT * FROM TASKS WHERE IDS LIKE ? AND UNTIL IS NOT NULL AND UNTIL > ? ORDER BY UNTIL LIMIT 10",
            f'%{interaction.user.id}%', datetime.now())
        for tt in timed_tasks:
            t = ''
            repetition = tt[9]
            repetition_sgn = 2 * (repetition > 0) - 1
            repetition_val = abs(repetition)
            if repetition_sgn == 1:
                t = f' ({repetition_val}일마다 반복)'
            else:
                u = []
                yoils = list(str(repetition_val))
                for i in range(7):
                    if i in yoils:
                        u.append(list('월화수목금토일')[i])
                t = f' ({", ".join(u)}요일마다 반복)'
            embed.add_field(
                name=f'{tt[1]}-{tt[2]}-{tt[3]}카테고리의 할 일 *{tt[5]}*',
                value=f'진행한 분량: {tt[11]} / {tt[8]} {tt[10]} ({round(tt[11] / tt[8] * 100, 2)}%)\n\n기한: {tt[7]}{t}'
            )
        untimed_tasks = db.records(
            "SELECT * FROM TASKS WHERE IDS LIKE ? AND UNTIL IS NULL LIMIT 10", f'%{interaction.user.id}%')
        for tt in untimed_tasks:
            embed.add_field(
                name=f'{tt[1]}-{tt[2]}-{tt[3]}카테고리의 할 일 *{tt[5]}*',
                value=f'진행한 분량: {tt[11]} / {tt[8]} {tt[10]} ({round(tt[11] / tt[8] * 100, 2)}%)\n\n기한 없음'
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='오늘내일할일')
    async def today_tomorrow(self, interaction):
        with Image.open(r"C:\Users\namon\PycharmProjects\discordbot\lib\images\10802340.png") as im:
            draw = ImageDraw.Draw(im, 'RGBA')
        background, line = \
            db.record('SELECT COLOR_BACKGROUND, COLOR_LINE FROM MISC_DATA WHERE USERID = ?',
                      interaction.user.id)
        if not background:
            background = 0xffffff
        if not line:
            line = 0x000000
        t = bin(background)[2:].rjust(24, '0')
        draw.rectangle(((0, 0), (1080, 2340)),
                       (int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)),
                       outline=(int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)))
        if max(int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)) > 127:
            defaultTextColor = (0, 0, 0, 255)
        else:
            defaultTextColor = (255, 255, 255, 255)
        background = (background // 0x10000, (background % 0x10000) // 0x100, background % 0x100, 255)
        line = (line // 0x10000, (line % 0x10000) // 0x100, line % 0x100, 255)
        draw.line(((0, 240), (1080, 240)), fill=line, width=20)
        a = datetime.now()
        today = int((time() + 32400) // 86400)
        dt1 = a.strftime('%Y-%m-%d')
        dt2 = (a + timedelta(days=1)).strftime('%Y-%m-%d')
        dt3 = (a + timedelta(days=2)).strftime('%Y-%m-%d')
        today_todo = db.records(
            "SELECT specific_content, amount_of_task, progression, color FROM TASKS WHERE IDS LIKE ? and ? <= UNTIL AND UNTIL <= ?",
            f'%{interaction.user.id}%', dt1, dt2)
        tomorrow_todo = db.records(
            "SELECT specific_content, amount_of_task, progression, color FROM TASKS WHERE IDS LIKE ? and ? <= UNTIL AND UNTIL <= ?",
            f'%{interaction.user.id}%', dt2, dt3)
        everyday_goal = db.records(
            "SELECT specific_content, amount_of_task, progression, color FROM TASKS WHERE IDS LIKE ? and ? <= UNTIL AND UNTIL <= ? AND REPETITION = 1",
            f'%{interaction.user.id}%', dt1, dt2)
        today_info = str(a.date()) + ' ' + list('월화수목금토일')[a.weekday()] + '요일'
        font = ImageFont.truetype(
            r'C:\Users\namon\PycharmProjects\discordbot\lib\fonts\SDMisaeng.ttf',
            160)
        draw.text((60, 40), today_info, fill=defaultTextColor, font=font)
        draw.text((0, 270), '- 오늘까지 할 일', fill=defaultTextColor, font=font)
        font2 = ImageFont.truetype(
            r'C:\Users\namon\PycharmProjects\discordbot\lib\fonts\SDMisaeng.ttf',
            100)
        i = 0
        if today_todo:
            for t in today_todo:
                if t[3]:
                    c = bin(t[3])[2:].rjust(24, '0')
                    fill = (int(c[0:8], 2), int(c[8:16], 2), int(c[16:], 2))
                else:
                    fill = defaultTextColor
                draw.text((0, 450 + i * 100),
                          f'{t[0]}: {t[2]} / {t[1]}, {round(t[2] / t[1] * 100, 1)}%',
                          fill=fill, font=font2)
                i += 1
        draw.text((0, 970), '- 내일까지 할 일', fill=defaultTextColor, font=font)
        i = 0
        if tomorrow_todo:
            for t in tomorrow_todo:
                if t[3]:
                    c = bin(t[3])[2:].rjust(24, '0')
                    fill = (int(c[0:8], 2), int(c[8:16], 2), int(c[16:], 2))
                else:
                    fill = defaultTextColor
                draw.text((0, 1150 + i * 100),
                          f'{t[0]}: {t[2]} / {t[1]}, {round(t[2] / t[1] * 100, 1)}%',
                          fill=fill, font=font2)
                i += 1
        draw.text((0, 1670), '- 오늘의 매일 목표', fill=defaultTextColor, font=font)
        i = 0
        if everyday_goal:
            for t in everyday_goal:
                if t[3]:
                    c = bin(t[3])[2:].rjust(24, '0')
                    fill = (int(c[0:8], 2), int(c[8:16], 2), int(c[16:], 2))
                else:
                    fill = defaultTextColor
                draw.text((0, 1850 + i * 100),
                          f'{t[0]}: {t[2]} / {t[1]}, {round(t[2] / t[1] * 100, 1)}%',
                          fill=fill, font=font2)
                i += 1
        im.save(u := r"C:\Users\namon\PycharmProjects\discordbot\lib\images\19201080_temp.png")
        await interaction.response.send_message(file=File(u))

    @app_commands.command(name='달력')
    async def monthly(self, interaction):
        with Image.open(r"C:\Users\namon\PycharmProjects\discordbot\lib\images\19201080.png") as im:
            draw = ImageDraw.Draw(im, 'RGBA')
            background, line = \
                db.record('SELECT COLOR_BACKGROUND, COLOR_LINE FROM MISC_DATA WHERE USERID = ?',
                          interaction.user.id)
            if not background:
                background = 0xffffff
            if not line:
                line = 0x000000
            t = bin(background)[2:].rjust(24, '0')
            draw.rectangle(((0, 0), (1920, 1080)),
                           (int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)),
                           outline=(int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)))
            if max(int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)) > 127:
                defaultTextColor = (0, 0, 0, 255)
            else:
                defaultTextColor = (255, 255, 255, 255)
            background = (background // 0x10000, (background % 0x10000) // 0x100, background % 0x100, 255)
            line = (line // 0x10000, (line % 0x10000) // 0x100, line % 0x100, 255)
            for i in range(1, 8):
                draw.line(((i * 274 - 10, 0), (i * 274 - 10, 1080)), fill=line, width=25)

            for i in range(1, 7):
                draw.line(((0, i * 180 - 10), (1920, i * 180 - 10)), fill=line, width=25)
            font = ImageFont.truetype(r'C:\Users\namon\PycharmProjects\discordbot\lib\fonts\SDMisaeng.ttf',
                                      150)
            a = datetime.now()
            b = monthrange(a.year, a.month)
            c = b[0]
            d = b[1]
            if c == 6:
                c = 0
            else:
                c += 1
            y = 200
            todo_list = db.records(
                "SELECT SPECIFIC_CONTENT, AMOUNT_OF_TASK, PROGRESSION, COLOR, REPETITION, UNTIL FROM TASKS WHERE IDS LIKE ?",
                f'%{interaction.user.id}%')
            z1 = re.compile('^(\d{4}-\d{2}-\d{2}).*$')
            z2 = z1.search(str(a))
            today = datetime.strptime(z2.group(1), '%Y-%m-%d')
            day_to_check = today - timedelta(days=a.day - 1)
            day1 = day_to_check
            day_until = day_to_check + timedelta(days=d - 1)
            colors = [0xffffff] * 7
            month_list = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                          [], [], [], [], [], [], [], [], [], []]
            for task in todo_list:
                task = list(task)
                z2 = z1.search(task[5])
                task[5] = datetime.strptime(z2.group(1), '%Y-%m-%d')
                if task[4] < 0:
                    task4 = map(int, list(str(-task[4])))
                    if task[3]:
                        for yoil in task4:
                            colors[yoil] = task[3]
                if day1 <= task[5] <= day_until:
                    if month_list[(task[5] - day1).days] == '':
                        month_list[(task[5] - day1).days] = task
                    else:
                        month_list[(task[5] - day1).days].append(task)
            for i in (l := ['일', '월', '화', '수', '목', '금', '토']):
                j = l.index(i)
                draw.text((j * 274 + 90, -0), i, font=font, fill=defaultTextColor)
            font = ImageFont.truetype(r'C:\Users\namon\PycharmProjects\discordbot\lib\fonts\SDMisaeng.ttf',
                                      60)
            for i in range(d):
                x = c * 274 + 20
                if a.day == i + 1:
                    draw.rectangle(((x - 20, y - 20), (x + 234, y + 140)), (255, 214, 254))
                if colors[c] != 0xffffff:
                    d = bin(colors[c])[2:].rjust(24, '0')
                    fill = (int(d[0:8], 2), int(d[8:16], 2), int(d[16:], 2))
                    draw.rectangle(((x - 20, y - 20), (x + 234, y + 140)), fill=fill)
                draw.text((x, y), str(i + 1), fill=defaultTextColor, font=font)
                if len(month_list[i]):
                    t = []
                    u = 0
                    v = 0
                    for task in month_list[i]:
                        t.append(task[0])
                        u += task[2]
                        v += task[1]
                    t = ', '.join(t)
                    small_font = ImageFont.truetype(
                        r'C:\Users\namon\PycharmProjects\discordbot\lib\fonts\SDMisaeng.ttf',
                        40)
                    draw.text((x + 50, y + 10), t, fill=defaultTextColor, font=small_font)
                    draw.text((x, y + 60), f'할 일 진행도\n{u} / {v} ({int(u / v * 100)}%)', fill=defaultTextColor,
                              font=small_font)
                c += 1
                if c == 7:
                    c = 0
                    y += 180
            im.save(u := r"C:\Users\namon\PycharmProjects\discordbot\lib\images\19201080_temp.png")
            await interaction.response.send_message(file=File(u))

    @app_commands.command(name="할일단축")
    @app_commands.choices(작업=[Choice(name='만들기', value='만들기'), Choice(name='없애기', value='없애기')],
                          넣을영역=[Choice(name='큰분류', value='큰분류'), Choice(name='중간분류', value='중간분류'),
                                Choice(name='작은분류', value='작은분류'), Choice(name='교재', value='교재')])
    async def make_shortcut(self, interaction, 작업: str, 키워드: str, 넣을영역: str):
        key, value = 키워드, 넣을영역
        shortcut = \
            db.record("SELECT USERID FROM SHORTCUTS WHERE USERID = ? AND KEYWORD = ? AND SUBJECT = ?",
                      interaction.user.id, key,
                      value)
        if 작업 == '만들기':
            if shortcut:
                await interaction.response.send_message('이미 있는 단축이에요...')
                return
            db.execute("INSERT INTO SHORTCUTS (USERID, KEYWORD, SUBJECT) VALUES (?, ?, ?)", interaction.user.id, key,
                       value)
            db.commit()
        elif 작업 == '없애기':
            if not shortcut:
                await interaction.response.send_message('존재하지 않는 단축이에요...')
                return
            db.execute("DELETE FROM SHORTCUTS WHERE USERID = ? AND KEYWORD = ? AND SUBJECT = ?", interaction.user.id,
                       key, value)
            db.commit()
        await interaction.response.send_message('완료')

    @app_commands.command(name='분류트리')
    @app_commands.choices(작업=[Choice(name='만들기', value='만들기'), Choice(name='없애기', value='없애기')])
    async def make_tree(self, interaction, 작업: str, 이것이: str, 이것을포함한다: str):
        if 작업 == '만들기':
            parent, dmdmo = 이것이, 이것을포함한다
            subsubject = db.record("SELECT CLASSIFY_TREE FROM MISC_DATA WHERE USERID = ?", interaction.user.id)
            if subsubject:
                subsubject = subsubject[0]
                importer = JsonImporter()
                root = importer.import_(subsubject)
                for desc in root.descendants:
                    if desc.info == parent:
                        r = desc
                        s = AnyNode(info=dmdmo, parent=desc)
                        break
                else:
                    r = AnyNode(info=parent, parent=root)
                    s = AnyNode(info=dmdmo, parent=r)
            else:
                root = AnyNode(info='현재 설정해둔 분류 트리 (같은 수준의 분류는 같은 depth에다가 설정해두는 걸 추천해요!)')
                r = AnyNode(info=parent, parent=root)
                s = AnyNode(info=dmdmo, parent=r)
            await export_tree(interaction, root)
        else:
            parent, dmdmo = 이것이, 이것을포함한다
            subsubject = db.record("SELECT CLASSIFY_TREE FROM MISC_DATA WHERE USERID = ?", interaction.user.id)
            if not subsubject:
                await interaction.response.send_message('분류해놓은 게 없어요.')
                return
            else:
                check = 0
                subsubject = subsubject[0]
                importer = JsonImporter()
                root = importer.import_(subsubject)
                for desc in root.descendants:
                    if check:
                        break
                    if parent == '맨위':
                        for desc2 in root.descendants:
                            if desc2.info == dmdmo:
                                desc2.parent = None
                                check = 1
                                break
                    if desc.info == parent:
                        for desc2 in desc.descendants:
                            if desc2.info == dmdmo:
                                desc2.parent = None
                                check = 1
                                break
                else:
                    await interaction.response.send_message('그런 분류는 없어요...')
                    return
            await export_tree(interaction, root)
        try:
            del root
        except NameError:
            pass
        try:
            del r
        except NameError:
            pass
        try:
            del s
        except NameError:
            pass
        await interaction.response.send_message('완료')

    @app_commands.command(name='공부시작')
    @app_commands.choices(
        종류=[Choice(name='비워두기', value=''), Choice(name='강의듣기', value='강의듣기'), Choice(name='개념공부', value='개념공부'),
            Choice(name='문제풀이', value='문제풀이'),
            Choice(name='모의고사', value='모의고사'), Choice(name='복습하기', value='복습하기')])
    async def start_studying(self, interaction, 큰분류: Optional[str], 중간분류: Optional[str], 작은분류: Optional[str],
                             교재: Optional[str], 내용: str,
                             종류: Optional[str], 할말: Optional[str]):
        global study_times, study_infos, study_messages
        embed = Embed(color=0x00b2ff, title='공부중!')
        big, middle, small, 교재 = await handle_shortcut(interaction, 내용, 큰분류, 중간분류, 작은분류, 교재)
        embed.add_field(name='공부 정보', value=f'{big}-{middle}-{small}분야에서 {교재}로 {내용}의 {종류}를 하고 있어요!')
        embed.add_field(name='경과 시간!', value='0 초')
        embed.set_footer(text=할말 or '꼭 열심히 공부해서 좋은 성과가 있기를!')
        view = ButtonsWhileStudying(user=interaction.user)
        rest_view = ButtonsWhilePausing(user=interaction.user)
        await interaction.response.send_message('처리 완료!')
        msg = await interaction.channel.send(embed=embed, view=view)
        start_time = time()
        study_times[interaction.user.id] = [start_time]
        study_messages[interaction.user.id] = msg
        study_infos[interaction.user.id] = [big, middle, small, 교재, 내용, 종류]
        while 1:
            await asyncio.sleep(15)
            timestamps = study_times[interaction.user.id].copy()
            resting = False
            timestamps.append(time())
            if len(timestamps) % 2:
                timestamps.append(time())
                resting = True
            total_time = int(timestamps[-1] - timestamps[0])
            break_time = int(sum(timestamps[2::2]) - sum(timestamps[1::2]) + timestamps[-1])
            embed = Embed(color=0x00b2ff, title='공부중!')
            embed.add_field(name='공부 정보', value=f'{big}-{middle}-{small}분야에서 {교재}로 {내용}의 {종류}를 하고 있어요!')
            embed.add_field(name='경과 시간!',
                            value=f'{to_visual_elapsed(total_time)}만큼이 지났고 그 중 {to_visual_elapsed(break_time)}만큼을 쉬어서 {to_visual_elapsed(total_time - break_time)}만큼을 공부한 셈이에요!')
            embed.set_footer(
                text=(할말 or '꼭 열심히 공부해서 좋은 성과가 있기를!') + '  버튼을 눌렀는데 상호작용 실패라고 떠도 버튼에 써있는 글자가 바뀌었다면 제대로 작동한 거에요!')
            if not resting:
                await msg.edit(embed=embed, view=view)
            else:
                await msg.edit(embed=embed, view=rest_view)
            if interaction.user.id not in study_messages:
                break

    @app_commands.command(name='공부기록', description='성적: a/b, 공부한시간: 1시간 5분 1500초 or 0:80:30')
    @app_commands.choices(
        종류=[Choice(name='비워두기', value=''), Choice(name='개념공부', value='개념공부'), Choice(name='문제풀이', value='문제풀이'),
            Choice(name='모의고사', value='모의고사'), Choice(name='복습하기', value='복습하기')])
    async def record_study(self, interaction, 큰분류: Optional[str], 중간분류: Optional[str], 작은분류: Optional[str],
                           교재: Optional[str], 내용: str, 종류: str, 성적: Optional[str], 공부한시간: Optional[str]):
        await self.grades(interaction, 큰분류, 중간분류, 작은분류, 교재, 내용, 종류, 성적, 공부한시간)

    async def grades(self, interaction, 큰분류: Optional[str], 중간분류: Optional[str], 작은분류: Optional[str], 교재: Optional[str],
                     내용: str, 종류: str, 성적: Optional[str], 공부한시간: Optional[str]):
        global today
        if 성적:
            grade = 성적.replace(' ', '')
        else:
            grade = ''
        today = (time() + 32400) // 86400
        if not grade:
            grade = '0/0'
        if not re.search('\d+/\d+', grade):
            await interaction.response.send_message('올바르지 않은 성적 정보에요...')
            return
        score, total = map(int, grade.split('/'))
        if score > total:
            await interaction.response.send_message('점수 입력이 올바르지 않아요...')
            return
        try:
            study_time = 공부한시간.split(':')
        except AttributeError:
            공부한시간 = '00:00:00'
        study_time = 공부한시간.split(':')
        if len(study_time) != 1:
            try:
                st = list(map(int, study_time))
            except ValueError:
                await interaction.response.send_message('공부시간 정보가 올바르지 않아요...')
                return
        else:
            study_time = 공부한시간.split(' ')
            st = [0, 0, 0]
            for t in study_time:
                if '시간' in t:
                    print(t)
                    try:
                        t = int(t[:-2])
                    except ValueError:
                        await interaction.response.send_message('공부시간 정보가 올바르지 않아요...')
                        return
                    st[0] = t
                elif '분' in t:
                    print(t)
                    try:
                        t = int(t[:-1])
                    except ValueError:
                        await interaction.response.send_message('공부시간 정보가 올바르지 않아요...')
                        return
                    st[1] = t
                elif '초' in t:
                    print(t)
                    try:
                        t = int(t[:-1])
                    except ValueError:
                        await interaction.response.send_message('공부시간 정보가 올바르지 않아요...')
                        return
                    st[2] = t
        study_time = st[0] * 3600 + st[1] * 60 + st[2]
        big, middle, small, 교재 = await handle_shortcut(interaction, 내용, 큰분류, 중간분류, 작은분류, 교재)
        db.execute(
            "INSERT INTO STUDY_DATA (USERID, BIG_SUBJECT, SUBJECT, SMALL_SUBJECT, BOOK_NAME, SPECIFIC_CONTENT, STUDY_TYPE, DURATION, GRADE_GOT, GRADE_FULL, STUDY_DATE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            interaction.user.id, big, middle, small, 교재, 내용, 종류, study_time, score, total, today)
        db.commit()
        await interaction.response.send_message('완료')

    @app_commands.command(name='공부설정')
    @app_commands.choices(
        바꿀거=[Choice(name='배경색', value='배경색'), Choice(name='선색', value='선색'), Choice(name='큰분류제목', value='큰분류제목'),
             Choice(name='중간분류제목', value='중간분류제목'), Choice(name='작은분류제목', value='작은분류제목')])
    async def study_settings(self, interaction, 바꿀거: str, 뭘로: str):
        if '색' in 바꿀거:
            color = 뭘로.split('x')
            check = 1
            if len(color) != 2:
                check = 0
            else:
                color = color[1].split('#')
                if len(color) != 1:
                    check = 0
                else:
                    try:
                        color = int(color[0], 16)
                    except ValueError:
                        check = 0
            if not check:
                await interaction.response.send_message('00b2ff, 0x00b2ff, #00b2ff의 형식만 사용할 수 있어요...')
                return
            if 바꿀거 == '배경색':
                z = db.execute("UPDATE MISC_DATA SET COLOR_BACKGROUND = ? WHERE USERID = ?", color, interaction.user.id)
                if not z:
                    db.execute("INSERT INTO MISC_DATA (USERID, COLOR_BACKGROUND) VALUES(?, ?)", interaction.user.id,
                               color)
            else:
                z = db.execute("UPDATE MISC_DATA SET COLOR_LINE = ? WHERE USERID = ?", color, interaction.user.id)
                if not z:
                    db.execute("INSERT INTO MISC_DATA (USERID, COLOR_LINE) VALUES(?, ?)", interaction.user.id, color)
        elif '분류제목' in 바꿀거:
            if '작' in 바꿀거:
                z = db.execute("UPDATE MISC_DATA SET SMALL_SUBJECT_NAME = ? WHERE USERID = ?", 뭘로, interaction.user.id)
                if not z:
                    db.execute("INSERT INTO MISC_DATA (USERID, SMALL_SUBJECT_NAME) VALUES(?, ?)", interaction.user.id,
                               뭘로)
            elif '중' in 바꿀거:
                z = db.execute("UPDATE MISC_DATA SET SUBJECT_NAME = ? WHERE USERID = ?", 뭘로, interaction.user.id)
                if not z:
                    db.execute("INSERT INTO MISC_DATA (USERID, SUBJECT_NAME) VALUES(?, ?)", interaction.user.id,
                               뭘로)
            elif '큰' in 바꿀거:
                z = db.execute("UPDATE MISC_DATA SET BIG_SUBJECT_NAME = ? WHERE USERID = ?", 뭘로, interaction.user.id)
                if not z:
                    db.execute("INSERT INTO MISC_DATA (USERID, BIG_SUBJECT_NAME) VALUES(?, ?)", interaction.user.id,
                               뭘로)
            db.commit()
        await interaction.response.send_message('완료')

    @app_commands.command(name='공부일지')
    @app_commands.choices(
        분류기준=[Choice(name='큰분류', value='큰분류'), Choice(name='중간분류', value='중간분류'), Choice(name='작은분류', value='작은분류')])
    async def life_journal(self, interaction, 며칠전: Optional[int] = 0, 분류기준: Optional[str] = '큰분류'):
        d = (time() + 32400) // 86400
        d -= 며칠전
        sum_study_time = db.record('SELECT sum(DURATION) FROM STUDY_DATA WHERE STUDY_DATE = ?', d)[0]
        if 분류기준 == '큰분류':
            grades = db.records(
                "SELECT BIG_SUBJECT, SPECIFIC_CONTENT, GRADE_GOT, GRADE_FULL FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE = ? AND (GRADE_FULL IS NOT NULL AND GRADE_FULL != 0)",
                interaction.user.id, d)
        elif 분류기준 == '중간분류':
            grades = db.records(
                "SELECT SUBJECT, SPECIFIC_CONTENT, GRADE_GOT, GRADE_FULL FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE = ? AND (GRADE_FULL IS NOT NULL AND GRADE_FULL != 0)",
                interaction.user.id, d)
        else:
            grades = db.records(
                "SELECT SMALL_SUBJECT, SPECIFIC_CONTENT, GRADE_GOT, GRADE_FULL FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE = ? AND (GRADE_FULL IS NOT NULL AND GRADE_FULL != 0)",
                interaction.user.id, d)
        a = datetime.now() - timedelta(days=며칠전)
        text = str(a.date()) + ' ' + list('월화수목금토일')[a.weekday()] + f'요일: 총 {to_visual_elapsed(sum_study_time)}\n'
        subjects = set()
        for i in range(len(grades)):
            subjects.add(grades[i][0])
        for subject in subjects:
            text += '\n' + subject + '\n'
            for i in range(len(grades)):
                grade = grades[i]
                if grade[0] != subject: continue
                text += f'{grade[1]} (채점 {grade[2]}/{grade[3]} {round(grade[2] / grade[3] * 100, 2)}%)\n'
        if 분류기준 == '큰분류':
            non_grades = db.records(
                "SELECT BIG_SUBJECT, SPECIFIC_CONTENT FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE = ? AND (GRADE_FULL IS NULL OR GRADE_FULL = 0)",
                interaction.user.id, d)
        elif 분류기준 == '중간분류':
            non_grades = db.records(
                "SELECT SUBJECT, SPECIFIC_CONTENT FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE = ? AND (GRADE_FULL IS NULL OR GRADE_FULL = 0)",
                interaction.user.id, d)
        else:
            non_grades = db.records(
                "SELECT SMALL_SUBJECT, SPECIFIC_CONTENT FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE = ? AND (GRADE_FULL IS NULL OR GRADE_FULL = 0)",
                interaction.user.id, d)
        subjects = set()
        for i in range(len(non_grades)):
            subjects.add(non_grades[i][0])
        for subject in subjects:
            text += '\n' + subject + '\n'
            for i in range(len(non_grades)):
                non_grade = non_grades[i]
                if non_grade[0] != subject: continue
                text += f'{non_grade[1]}\n'
        await interaction.response.send_message('뀨!')
        while True:
            try:
                await interaction.channel.send(text[:2000])
            except HTTPException:
                break
            text = text[2000:]

    @app_commands.command(name='이벤트', description='언제 에는 YYYY/MM/DD 형식의 미래의 날짜만 입력할 수 있어요!')
    @app_commands.choices(얼마나큰=[Choice(name='큰', value='큰'), Choice(name='보통', value='보통')])
    async def make_event(self, interaction, 얼마나큰: str, 어떤: str, 언제: str):
        try:
            event_day = datetime.strptime(언제, '%Y/%m/%d')
        except ValueError:
            await interaction.response.send_message('명령어 설명에 나온 대로 형식을 맞춰서 보내 주세요...')
            return
        t = datetime.now()
        d = (event_day - datetime(year=t.year, month=t.month, day=t.day)).days + (time() + 32400) // 86400
        if 얼마나큰 == '큰':
            a = db.execute("UPDATE MISC_DATA SET BIGEVENT = ?, BIGEVENT_DAY = ? WHERE USERID = ?", 어떤, d,
                           interaction.user.id)
            if not a:
                db.execute("INSERT INTO MISC_DATA (USERID, BIGEVENT, BIGEVENT_DAY) VALUES (?, ?, ?)",
                           interaction.user.id, 어떤, d)
        else:
            a = db.execute("UPDATE MISC_DATA SET EVENT = ?, EVENT_DAY = ? WHERE USERID = ?", 어떤, d, interaction.user.id)
            if not a:
                db.execute("INSERT INTO MISC_DATA (USERID, EVENT, EVENT_DAY) VALUES (?, ?, ?)", interaction.user.id, 어떤,
                           d)
        db.commit()
        await interaction.response.send_message('다가오는 이벤트를 바꿨어요!')

    @app_commands.command(name='성적그래프', description='기간: x일 전까지, 분류필터: x 분류의 성적만, 교재필터: x 교재의 성적만')
    @app_commands.choices(데이터추출=[Choice(name='날짜별', value='날짜별'), Choice(name='데이터별', value='데이터별')])
    async def grade_graph(self, interaction, 데이터추출: str, 기간: Optional[int] = 7, 분류필터: Optional[str] = '',
                          교재필터: Optional[str] = ''):
        duration, rhkahr = 기간, 분류필터
        book = 교재필터
        today = (time() + 32400) // 86400 - 13
        if not rhkahr and not book:
            top_text = f'모든 과목, 모든 교재의 {데이터추출} 성적 정보'
            if 데이터추출 == '날짜별':
                base_data = db.records(
                    "SELECT sum(GRADE_GOT), sum(GRADE_FULL) FROM STUDY_DATA WHERE USERID = ? AND GRADE_GOT > 0 AND STUDY_DATE > ? GROUP BY STUDY_DATE ORDER BY STUDY_DATE",
                    interaction.user.id, today - duration)
            else:
                base_data = db.records(
                    "SELECT GRADE_GOT, GRADE_FULL FROM STUDY_DATA WHERE USERID = ? AND GRADE_GOT > 0 AND STUDY_DATE > ? ORDER BY STUDY_DATE",
                    interaction.user.id, today - duration)
        elif rhkahr and not book:
            top_text = f'{rhkahr}, 모든 교재의 {데이터추출} 성적 정보'
            if 데이터추출 == '날짜별':
                base_data = db.records(
                    "SELECT sum(GRADE_GOT), sum(GRADE_FULL) FROM STUDY_DATA WHERE USERID = ? AND GRADE_GOT IS NOT NULL AND STUDY_DATE > ? AND ? IN (BIG_SUBJECT, SUBJECT, SMALL_SUBJECT) GROUP BY STUDY_DATE ORDER BY STUDY_DATE",
                    interaction.user.id, today - duration, rhkahr)
            else:
                base_data = db.records(
                    "SELECT GRADE_GOT, GRADE_FULL FROM STUDY_DATA WHERE USERID = ? AND GRADE_GOT IS NOT NULL AND STUDY_DATE > ? AND ? IN (BIG_SUBJECT, SUBJECT, SMALL_SUBJECT) ORDER BY STUDY_DATE",
                    interaction.user.id, today - duration, rhkahr)
        elif not rhkahr and book:
            top_text = f'모든 과목, {book}의 {데이터추출} 성적 정보'
            if 데이터추출 == '날짜별':
                base_data = db.records(
                    "SELECT sum(GRADE_GOT), sum(GRADE_FULL) FROM STUDY_DATA WHERE USERID = ? AND GRADE_GOT IS NOT NULL AND STUDY_DATE > ? AND BOOK_NAME = ? GROUP BY STUDY_DATE ORDER BY STUDY_DATE",
                    interaction.user.id, today - duration, book)
            else:
                base_data = db.records(
                    "SELECT GRADE_GOT, GRADE_FULL FROM STUDY_DATA WHERE USERID = ? AND GRADE_GOT IS NOT NULL AND STUDY_DATE > ? AND BOOK_NAME = ? ORDER BY STUDY_DATE",
                    interaction.user.id, today - duration, book)
        else:
            top_text = f'{rhkahr}, {book}의 {데이터추출} 성적 정보'
            if 데이터추출 == '날짜별':
                base_data = db.records(
                    "SELECT sum(GRADE_GOT), sum(GRADE_FULL) FROM STUDY_DATA WHERE USERID = ? AND GRADE_GOT IS NOT NULL AND STUDY_DATE > ? AND ? IN (BIG_SUBJECT, SUBJECT, SMALL_SUBJECT) AND BOOK_NAME = ? GROUP BY STUDY_DATE ORDER BY STUDY_DATE",
                    interaction.user.id, today - duration, rhkahr, book)
            else:
                base_data = db.records(
                    "SELECT GRADE_GOT, GRADE_FULL FROM STUDY_DATA WHERE USERID = ? AND GRADE_GOT IS NOT NULL AND STUDY_DATE > ? AND ? IN (BIG_SUBJECT, SUBJECT, SMALL_SUBJECT) AND BOOK_NAME = ? ORDER BY STUDY_DATE",
                    interaction.user.id, today - duration, rhkahr, book)
        grade_list = []
        for data in base_data:
            grade_list.append(data[0] * 100 // data[1])
        x = np.array(range(1, len(grade_list) + 1))
        y = np.array(grade_list)

        model = make_interp_spline(x, y)

        xs = np.linspace(1, len(grade_list), 500)
        ys = model(xs)
        plt.rc('font', family='Malgun Gothic')
        plt.rcParams['axes.unicode_minus'] = False

        plt.plot(xs, ys)

        plt.title(top_text)
        plt.xlabel("시간 (값은 의미없음)")
        plt.ylabel("성적 (%)")
        plt.savefig(u := r"C:\Users\namon\PycharmProjects\discordbot\lib\images\19201080_temp.png")
        plt.clf()
        await interaction.response.send_message(file=File(u))

    @app_commands.command(name='공부시간그래프')
    @app_commands.choices(
        필터=[Choice(name='큰분류', value='큰분류'), Choice(name='중간분류', value='중간분류'), Choice(name='작은분류', value='작은분류'),
            Choice(name='교재', value='교재'), Choice(name='종류', value='종류')])
    async def study_time_graph(self, interaction, 필터: str, 기간: Optional[int] = 7):
        filter_name = 필터
        today = int((time() + 32400) // 86400)
        if filter_name == '큰분류':
            base_data = db.records(
                "SELECT BIG_SUBJECT, sum(DURATION), STUDY_DATE FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE > ? GROUP BY BIG_SUBJECT, STUDY_DATE",
                interaction.user.id, today - 기간)
            fn = db.record("SELECT BIG_SUBJECT_NAME FROM MISC_DATA WHERE USERID = ?", interaction.user.id)
            if fn and fn[0]:
                filter_name = fn[0]
        elif filter_name == '중간분류':
            base_data = db.records(
                "SELECT SUBJECT, sum(DURATION), STUDY_DATE FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE > ? GROUP BY SUBJECT, STUDY_DATE",
                interaction.user.id, today - 기간)
            fn = db.record("SELECT SUBJECT_NAME FROM MISC_DATA WHERE USERID = ?", interaction.user.id)
            if fn and fn[0]:
                filter_name = fn[0]
        elif filter_name == '작은분류':
            base_data = db.records(
                "SELECT SMALL_SUBJECT, sum(DURATION), STUDY_DATE FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE > ? GROUP BY SMALL_SUBJECT, STUDY_DATE",
                interaction.user.id, today - 기간)
            fn = db.record("SELECT SMALL_SUBJECT_NAME FROM MISC_DATA WHERE USERID = ?", interaction.user.id)
            if fn and fn[0]:
                filter_name = fn[0]
        elif filter_name == '교재':
            base_data = db.records(
                "SELECT BOOK_NAME, sum(DURATION), STUDY_DATE FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE > ? GROUP BY BOOK_NAME, STUDY_DATE",
                interaction.user.id, today - 기간)
        elif filter_name == '종류':
            base_data = db.records(
                "SELECT STUDY_TYPE, sum(DURATION), STUDY_DATE FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE > ? GROUP BY STUDY_TYPE, STUDY_DATE",
                interaction.user.id, today - 기간)
        mindate = 100000000000
        for data in base_data:
            mindate = min(mindate, data[2])
        max_delta = today - mindate
        t = datetime.now()
        labels = []
        for i in range(max_delta + 1):
            labels.append((t - timedelta(days=max_delta - i)).strftime('%m/%d'))
        actual_data = dict()
        empty_list = [0.0] * (max_delta + 1)
        for data in base_data:
            if data[0] not in actual_data:
                actual_data[data[0]] = np.array(empty_list.copy())
            actual_data[data[0]][max_delta - today + data[2]] += data[1] / 3600
        bottom = np.array(empty_list.copy())
        subject_order = []

        plt.rc('font', family='Malgun Gothic')
        plt.rcParams['axes.unicode_minus'] = False

        for key in actual_data:
            plt.bar(labels, actual_data[key], bottom=bottom)
            bottom += actual_data[key]
            subject_order.append(key)

        plt.ylabel('공부 시간 (시간)')
        plt.title(f'{filter_name}에 따라서 분류한 최근 {기간}일간의 공부 시간')
        plt.legend(subject_order)
        plt.savefig(u := r"C:\Users\namon\PycharmProjects\discordbot\lib\images\19201080_temp.png")
        plt.clf()
        await interaction.response.send_message(file=File(u))

    @Cog.listener()
    async def on_message(self, message):
        global message_waiting, message_output
        if message.author.id in message_waiting and message_waiting[message.author.id] == message.channel.id:
            del message_waiting[message.author.id]
            message_output[message.author.id] = message.content
        if message.channel.id == 863043058819268638 and not message.author.bot:
            try:
                await message.channel.send(exec(message.content))
            except Exception as e:
                await message.channel.send(e)


async def setup(bot):
    await bot.add_cog(Cmds(bot))
    print('new study cog ready')


async def main_function(interaction):
    daily_check = db.record("SELECT ATTEND_DATE FROM ATTENDS WHERE USERID = ?", interaction.user.id)
    if not daily_check:
        await interaction.response.send_message("출석체크를 먼저 진행해주세요.")
        return
    a = datetime.now()
    dt1 = a.strftime('%Y-%m-%d')
    dt2 = (a + timedelta(days=1)).strftime('%Y-%m-%d')
    today_tasks = db.records(
        "SELECT specific_content FROM TASKS WHERE IDS LIKE ? and ? <= UNTIL AND UNTIL <= ? ORDER BY UNTIL ASC",
        f'%{interaction.user.id}%', dt1, dt2)
    embed = Embed(color=0x00b2ff, title=str(interaction.user))
    today_tasks = [today_tasks[i][0] for i in range(len(today_tasks))]
    embed.add_field(name='오늘까지 할 일들은?', value=', '.join(today_tasks) or '없네요!')
    today_study_time = db.records(
        "SELECT SUBJECT, sum(DURATION) FROM STUDY_DATA WHERE USERID = ? AND STUDY_DATE = ? GROUP BY SUBJECT",
        interaction.user.id, (time() + 32400) // 86400)
    time_text = ''
    for tst in today_study_time:
        time_text += tst[0] + ' : ' + to_visual_elapsed(tst[1]) + '\n'
    if not time_text:
        time_text = '** **'
    embed.add_field(name='오늘 한 것들은?', value=time_text, inline=False)
    await interaction.response.send_message(embed=embed)


async def attend(interaction):
    global today
    t = time()
    if today < ((t + 32400) // 86400):
        today += 1
    attend_time = (datetime.now())
    visual_today = attend_time.strftime("오늘은 %Y년 %m월 %d일 (%a)")
    today_attended = db.records("SELECT USERID FROM ATTENDS WHERE ATTEND_DATE = ?", today)
    for ids in today_attended:
        if ids[0] == interaction.user.id:
            await interaction.response.send_message("오늘은 이미 출석해쪄!")
            return
    db.execute("INSERT INTO ATTENDS (USERID, ATTEND_DATE) VALUES (?, ?)", interaction.user.id, today)
    db.commit()
    event_check = db.record("SELECT BIGEVENT, BIGEVENT_DAY, EVENT, EVENT_DAY FROM MISC_DATA WHERE USERID = ?",
                            interaction.user.id)
    embed = Embed(color=0x00b2ff)
    embed.add_field(name="출석체크를 완료해쪄!", value=visual_today, inline=False)
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
        embed.add_field(name=name_string, value=value_string)
    view = ButtonHi(timeout=60, user=interaction.user)
    await interaction.response.send_message(
        '출석체크 완료!' + '\n반복해서 해야 되는 할 일 데이터를 건드리고 있으니까 여기다가 다시 메세지를 보내기 전까지 할일 관련 명령어는 쓰지 말아죠!', embed=embed,
        view=view)
    repeating_tasks = db.records(
        "SELECT SPECIFIC_CONTENT, UNTIL, REPETITION, PROGRESSION, AMOUNT_OF_TASK FROM TASKS WHERE IDS LIKE ? AND REPETITION != 0",
        f'%{interaction.user.id}%')
    embed = Embed(color=0x00b2ff, title='오늘 초기화된 반복 할일들의 정보야!')
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
            until, task[0], task[1], f'%{interaction.user.id}%', task[2])
        t = task[3] == task[4]
        check = check and t
        s = (' 할 일을 다 마무리했네...! 잘해쪄') * t
        embed.add_field(name=task[0], value=f'{task[3]} / {task[4]} 만큼 진행된 상태야!{s}')
    if check:
        embed.set_footer(text='반복 할 일들을 모두 마쳐쪄! 수고해쪄')
    if task_check:
        await interaction.channel.send(embed=embed)
        db.commit()


async def handle_shortcut(interaction, 내용, 큰분류, 중간분류, 작은분류, 교재):
    shortcuts = db.records("SELECT KEYWORD, SUBJECT FROM SHORTCUTS WHERE USERID = ?", interaction.user.id)
    possible_shortcuts = [[] for i in range(4)]
    cnt = [0, 0, 0, 0]
    ask_text = ['', '', '', '']
    for shortcut in shortcuts:
        if shortcut[0] in 내용:
            idx = ['큰분류', '중간분류', '작은분류', '교재'].index(shortcut[1])
            possible_shortcuts[idx].append(shortcut)
            ask_text[idx] += f'**{cnt[idx] + 1}**. {shortcut[0]} -> {shortcut[1]}\n'
            cnt[idx] += 1
    f_shortcut = [None, None, None, None]
    for i in range(4):
        if cnt[i] == 1:
            f_shortcut[i] = possible_shortcuts[i][0][0]
        elif cnt[i]:
            if (i == 0 and 큰분류) or (i == 1 and 중간분류) or (i == 2 and 작은분류) or (i == 3 and 교재):
                continue
            embed = Embed(color=0x00b2ff, title='ㅇㅁㅇ?', description=ask_text[i])
            await interaction.channel.send(
                f"여기 있는 {['큰분류', '중간분류', '작은분류', '교재'][i]}들 중 어느 걸 선택할지 굵은 글씨로 써있는 번호만 말해 주세요.", embed=embed)
            message_waiting[interaction.user.id] = interaction.channel.id
            while interaction.user.id in message_waiting:
                await asyncio.sleep(1)
            await asyncio.sleep(0.5)
            msg = message_output[interaction.user.id]
            try:
                msg = int(msg)
            except ValueError:
                await interaction.channel.send("숫자로만 입력해 주세요.")
                return
            if msg:
                try:
                    f_shortcut[i] = possible_shortcuts[i][msg - 1][0]
                except IndexError:
                    await interaction.channel.send("번호를 제대로 입력해 주세요.")
                    return
    if f_shortcut:
        if not 큰분류:
            큰분류 = f_shortcut[0]
        if not 중간분류:
            중간분류 = f_shortcut[1]
        if not 작은분류:
            작은분류 = f_shortcut[2]
        if not 교재:
            교재 = f_shortcut[3]

    classify_tree = db.record("SELECT CLASSIFY_TREE FROM MISC_DATA WHERE USERID = ?", interaction.user.id)
    if classify_tree:
        classify_tree = classify_tree[0]
        importer = JsonImporter()
        root = importer.import_(classify_tree)
        cur_dict = {작은분류: "작은분류", 중간분류: "중간분류", 큰분류: "큰분류"}
        for node in root.descendants:
            if node.info in cur_dict:
                if cur_dict[node.info] == '큰분류':
                    continue
                elif cur_dict[node.info] == '중간분류':
                    if not 큰분류:
                        큰분류 = node.parent.info
                elif cur_dict[node.info] == '작은분류':
                    if not 중간분류:
                        중간분류 = node.parent.info
                        if not 큰분류:
                            큰분류 = node.parent.parent.info

    if 큰분류 == '현재 설정해둔 분류 트리 (같은 수준의 분류는 같은 depth에다가 설정해두는 걸 추천해요)':
        큰분류 = None
    elif 중간분류 == '현재 설정해둔 분류 트리 (같은 수준의 분류는 같은 depth에다가 설정해두는 걸 추천해요)':
        중간분류 = None
    elif 작은분류 == '현재 설정해둔 분류 트리 (같은 수준의 분류는 같은 depth에다가 설정해두는 걸 추천해요)':
        작은분류 = None

    if 큰분류 and not 중간분류:
        중간분류 = 큰분류
    if 중간분류 and not 작은분류:
        작은분류 = 중간분류

    return 큰분류, 중간분류, 작은분류, 교재


async def export_tree(interaction, root):
    exporter = JsonExporter(indent=2, sort_keys=True, ensure_ascii=False)
    j = exporter.export(root)
    st = ''
    for pre, fill, node in RenderTree(root):
        st += "%s%s" % (pre, node.info) + '\n'
    await interaction.channel.send(st)
    a = db.execute("UPDATE MISC_DATA SET CLASSIFY_TREE = ? WHERE UserID = ?", j, interaction.user.id)
    if not a:
        db.execute("INSERT INTO MISC_DATA (USERID, CLASSIFY_TREE) VALUES (?, ?)", interaction.user.id, j)
    db.commit()


def to_visual_elapsed(elapsed):
    visual_elapsed = ''
    visual_elapsed += f'{elapsed // 3600} 시간 '
    visual_elapsed += f'{elapsed % 3600 // 60} 분 '
    visual_elapsed += f'{elapsed % 60} 초'
    return visual_elapsed


async def toggle_pause(interaction):
    uid = interaction.user.id
    study_times[uid].append(time())


async def stop_study(interaction, resting, record_grades):
    uid = interaction.user.id
    timestamps = study_times[uid]
    timestamps.append(time())
    if resting:
        timestamps.append(time())
    total_time = int(timestamps[-1] - timestamps[0])
    break_time = int(sum(timestamps[2::2]) - sum(timestamps[1::2]) + timestamps[-1])
    actual_time = total_time - break_time
    score, total = None, None
    big, middle, small, 교재, 내용, 종류 = study_infos[uid]
    embed = Embed(color=0x00b2ff, title='공부하느라 수고 많았어요!')
    embedname = '이번에 한 공부'
    embed.add_field(name=embedname, value=f'{big}-{middle}-{small}분야에서 {교재}로 {내용}의 {종류}를 했어요!')
    embed.add_field(name='공부한 시간',
                    value=f'{to_visual_elapsed(total_time)} 중 {to_visual_elapsed(actual_time)}만큼 공부했고 {to_visual_elapsed(break_time)}만큼을 쉼')
    await interaction.response.send_message(embed=embed)
    if record_grades:
        await interaction.channel.send("기록할 성적을 **a/b** 의 꼴로 입력해 주세요.")
        message_waiting[interaction.user.id] = interaction.channel.id
        while interaction.user.id in message_waiting:
            await asyncio.sleep(1)
        await asyncio.sleep(0.5)
        msg = message_output[interaction.user.id]
        check = 1
        if re.search('\d+/\d+', msg):
            try:
                score, total = map(int, msg.split('/'))
                if total < score:
                    check = 0
            except ValueError:
                check = 0
        else:
            check = 0
        if not check:
            await interaction.channel.send('성적을 인식할 수 없어요. 공부한 사실만 기록할게요.')
        else:
            await interaction.channel.send('성적 기록까지 완료했어요!')
    del study_messages[uid]
    del study_infos[uid]
    del study_times[uid]
    db.execute("INSERT INTO STUDY_DATA (USERID, BIG_SUBJECT, SUBJECT, SMALL_SUBJECT, SPECIFIC_CONTENT, BOOK_NAME, "
               "STUDY_TYPE, DURATION, STUDY_DATE, GRADE_GOT, GRADE_FULL) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
               interaction.user.id, big, middle,
               small, 내용, 교재, 종류, actual_time, (time() + 32400) // 86400, score, total)
    db.commit()


async def force_stop_study(interaction):
    uid = interaction.user.id
    del study_messages[uid]
    del study_infos[uid]
    del study_times[uid]
    await interaction.response.send_message('공부를 멈췄어요!')


async def fetch_work(interaction, search):
    if len(search) >= 2:
        embed = Embed(color=0x00b2ff, title="할 일 여러 개가 검색됐어요.")
        i = 1
        for do in search:
            embed.add_field(name=str(i),
                            value=f"{do[1]} 카테고리의 할 일 *{do[5]}*\n\n진행한 분량 {do[11]} / {do[8]} ({round(do[11] / do[8] * 100, 2)}%)\n\n{do[7]}까지 할 일",
                            inline=False)
            i += 1
        await interaction.channel.send("어느 걸 선택할지 굵은 글씨로 써있는 번호만 말해주세요.", embed=embed)
        message_waiting[interaction.user.id] = interaction.channel.id
        while interaction.user.id in message_waiting:
            await asyncio.sleep(1)
        await asyncio.sleep(0.5)
        msg = message_output[interaction.user.id]
        try:
            msg = int(msg)
        except ValueError:
            await interaction.channel.send('번호로만 입력해 주세요.')
            return
        if len(search) < msg:
            await interaction.channel.send("번호를 제대로 입력해 주세요.")
            return
        now = search[msg - 1]
    elif len(search) == 1:
        now = search[0]
    else:
        await interaction.channel.send("올바르지 않은 이름이에요.")
        return
    return now

class ButtonHi(ui.View):
    def __init__(self, timeout, user):
        super().__init__(timeout=timeout)
        self.user = user

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if self.user:
            if interaction.user != self.user:
                await interaction.response.send_message('이건 다른 사람이 실행한 명령어에요!', ephemeral=True)
                return False
        return True

    @ui.button(label='메인 메뉴로', style=ButtonStyle.secondary)
    async def button_hi(self, interaction, button):
        await main_function(interaction)


class MakeTaskButtons(ui.View):
    def __init__(self, timeout, user):
        super().__init__(timeout=timeout)
        self.user = user

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if self.user:
            if interaction.user != self.user:
                await interaction.response.send_message('이건 다른 사람이 실행한 명령어에요!', ephemeral=True)
                return False
        return True

    @ui.button(label='메인 메뉴로', style=ButtonStyle.secondary)
    async def button_hi(self, interaction, button):
        await main_function(interaction)

    # @ui.button(label='현재 할 일 목록 보러가기!', style=ButtonStyle.primary)
    # async def button_see_tasks(self, interaction, button):
    #    await display_tasks(interaction)


class ButtonsWhileStudying(ui.View):
    def __init__(self, user):
        super().__init__(timeout=86400.0)
        self.user = user

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if self.user:
            if interaction.user != self.user:
                await interaction.response.send_message('이건 다른 사람이 실행한 명령어에요!', ephemeral=True)
                return False
        return True

    @ui.button(label='쉬었다가 다시하기', style=ButtonStyle.green)
    async def button_pause(self, interaction, button):
        await toggle_pause(interaction)

    @ui.button(label='성적을 기록하고 공부 그만하기', style=ButtonStyle.red)
    async def button_stop1(self, interaction, button):
        await stop_study(interaction, False, True)

    @ui.button(label='성적을 기록하지 않고 공부 그만하기', style=ButtonStyle.red)
    async def button_stop2(self, interaction, button):
        await stop_study(interaction, False, False)

    @ui.button(label='공부 취소하기 (기록에 남지 않음)', style=ButtonStyle.red)
    async def button_stop3(self, interaction, button):
        await force_stop_study(interaction)


class ButtonsWhilePausing(ui.View):
    def __init__(self, user):
        super().__init__(timeout=86400.0)
        self.user = user

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if self.user:
            if interaction.user != self.user:
                await interaction.response.send_message('이건 다른 사람이 실행한 명령어에요!', ephemeral=True)
                return False
        return True

    @ui.button(label='다시 공부 시작하기', style=ButtonStyle.green)
    async def button_resume(self, interaction, button):
        await toggle_pause(interaction)

    @ui.button(label='성적을 기록하고 공부 그만하기', style=ButtonStyle.red)
    async def button_stop1(self, interaction, button):
        await stop_study(interaction, True, True)

    @ui.button(label='성적을 기록하지 않고 공부 그만하기', style=ButtonStyle.red)
    async def button_stop2(self, interaction, button):
        await stop_study(interaction, True, False)

    @ui.button(label='공부 취소하기 (기록에 남지 않음)', style=ButtonStyle.red)
    async def button_stop3(self, interaction, button):
        await force_stop_study(interaction)
