import asyncio
import copy
import re
import matplotlib.pyplot as plt
import numpy as np
from anytree import AnyNode
from anytree.exporter import JsonExporter
from anytree.importer import JsonImporter
from anytree import RenderTree
from scipy.interpolate import make_interp_spline
from asyncio import sleep
from calendar import monthrange
from datetime import datetime, timedelta
from time import time
from typing import Optional
from random import randint
from discord import Embed, File, HTTPException
from discord.ext.commands import Cog, command
from PIL import Image, ImageDraw, ImageFont
from ..db import db
from discord.app_commands import command as slash, choices, Choice
from ..utils.send import send


class Study(Cog):
    def __init__(self, bot):
        self.bot = bot

    def add_cross_to(self, im, color):
        draw = ImageDraw.Draw(im)
        draw.line((0, 0) + im.size, fill=color, width=10)
        draw.line((0, im.size[1], im.size[0], 0), fill=color, width=10)
        return im

    def add_rectangle_to(self, im, tl, br, color):
        draw = ImageDraw.Draw(im)
        draw.rectangle((tl, br), color)
        return im

    def add_text(self, im, text, tl, size, color):
        font = ImageFont.truetype(r'C:\Users\namon\PycharmProjects\discordbot\lib\fonts\SDMisaeng.ttf', size)
        draw = ImageDraw.Draw(im)
        draw.text(tl, text, font=font, fill=color)
        return im

    @command(name="타이머")
    async def timer(self, ctx, *args):
        if not args:
            await ctx.channel.send("명령어의 모든 요소를 입력해 주세요!\n올바른 사용법: `커뉴야 타이머 <기간>`")
            return
        duration = 0
        msg = ""
        for arg in args:
            if arg.endswith("d") or arg.endswith("일"):
                try:
                    arg = float(arg[:-1])
                    duration += 86400 * arg
                except ValueError:
                    pass
            elif arg.endswith("h"):
                try:
                    arg = float(arg[:-1])
                    duration += 3600 * arg
                except ValueError:
                    pass
            elif arg.endswith("시간"):
                try:
                    arg = float(arg[:-2])
                    duration += 3600 * arg
                except ValueError:
                    pass
            elif arg.endswith("m") or arg.endswith("분"):
                try:
                    arg = float(arg[:-1])
                    duration += 60 * arg
                except ValueError:
                    pass
            elif arg.endswith("s") or arg.endswith("초"):
                try:
                    arg = float(arg[:-1])
                    duration += arg
                except ValueError:
                    pass
            else:
                msg += f" {arg}"
        if duration > 86400 * 7:
            await ctx.channel.send("기간이 너무 길어요! (이렇게 긴 기간이라면 중간에 봇이 꺼질 가능성이 있어요)")
            return
        await ctx.channel.send("설정을 완료했어요! 시간이 지나면 디엠으로 말해드릴게요 (중간에 봇이 꺼진다면 누락될 가능성도 약간 있어요 유의 부탁드려요)")
        await sleep(duration)
        try:
            if not msg:
                await ctx.author.send("시간이 종료되었어요!")
            else:
                await ctx.author.send(msg)
        except AttributeError:
            return

    @command(name='스톱워치')
    async def stopwatch(self, ctx, activity: Optional[str] = "도움", *, t: Optional[str]):
        if activity == "도움":
            await ctx.channel.send(embed=Embed(color=0xffd6fe, title="커뉴봇 스톱워치 기능 도움!",
                                               description="`커뉴야 스톱워치 도움`: 이 도움말을 표시합니다.\n`커뉴야 스톱워치 시작`: 스톱워치를 시작합니다.\n`커뉴야 스톱워치 종료`: 스톱워치를 종료합니다.\n`커뉴야 스톱워치 기록`: 스톱워치가 진행되고 있는 동안 중간중간에 기록을 합니다."))
        elif activity == "시작":
            if not t:
                t = f'{ctx.author.name}님의 스톱워치'
            if t.startswith("자세히 "):
                await ctx.channel.send("제목으로 설정할 수 없는 이름이에요!")
                return
            if db.record("SELECT * FROM stopwatch WHERE UserID = ? AND end_time IS NULL", ctx.author.id):
                await ctx.channel.send("이미 스톱워치가 돌아가고 있어요!")
                return
            time_text = (datetime.now()).strftime("%Y/%m/%d %H:%M:%S")
            await ctx.channel.send(f"{time_text}\n스톱워치 설정을 완료했어요!")
            if t:
                db.execute("INSERT INTO stopwatch (UserID, start_time, title) VALUES (?, ?, ?)", ctx.author.id,
                           time_text, t)
            else:
                db.execute("INSERT INTO stopwatch (UserID, start_time) VALUES (?, ?)", ctx.author.id, time_text)
            db.commit()
        elif activity == "종료":  # 일시정지 도중 종료하는 경우도 고쳐보자.
            current = db.record("SELECT * FROM stopwatch WHERE UserID = ? AND end_time IS NULL", ctx.author.id)
            if not current:
                await ctx.channel.send("설정해 둔 스톱워치가 없어요!")
                return
            embed = Embed(color=0xffd6fe, title="스톱워치 종료됨")
            embed.add_field(name="시작한 시각", value=current[1], inline=False)
            try:
                records = current[2].split(',')
                tjfaud = ""
                type = ""
                count = 1
                time_check = re.compile("\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}")
                for i in range(30):
                    try:
                        if records[i] == "p":
                            type = "일시정지"
                        elif records[i] == "r":
                            type = "재개"
                        elif not time_check.match(records[i]):
                            type = records[i]
                            count += 1
                        else:
                            if type:
                                tjfaud += f"\n{type}: {records[i]}"
                                type = ""
                            else:
                                tjfaud += f"\n{count}. {records[i]}"
                                count += 1
                    except IndexError:
                        break
                else:
                    tjfaud += "\n그리고 더 많은 기록들..."
                embed.add_field(name="중간중간 한 기록들", value=tjfaud, inline=False)
            except:
                pass
            final_time = (datetime.now()) - datetime.strptime(current[1], "%Y/%m/%d %H:%M:%S")
            if current[2]:
                pauses = list(filter(lambda x: records[x] == "p", range(len(records))))
                for p in pauses:
                    t = datetime.strptime(records[p + 3], "%Y/%m/%d %H:%M:%S") - datetime.strptime(records[p + 1],
                                                                                                   "%Y/%m/%d %H:%M:%S")
                    final_time -= t
            time_text = (datetime.now()).strftime("%Y/%m/%d %H:%M:%S")
            embed.add_field(name="종료된 시각", value=time_text, inline=False)
            embed.add_field(name="측정된 시간", value=str(final_time), inline=False)
            await ctx.channel.send(embed=embed)
            db.execute("UPDATE stopwatch SET end_time = ? WHERE UserID = ? AND end_time is NULL", time_text,
                       ctx.author.id)
            db.commit()
        elif activity == "기록":
            current = db.record("SELECT * FROM stopwatch WHERE UserID = ? AND end_time IS NULL", ctx.author.id)
            if not current:
                await ctx.channel.send("설정해 둔 스톱워치가 없어요!")
                return
            try:
                records = current[2].split(',')
            except:
                records = []
            if len(records) >= 2 and records[len(records) - 2] == "p":
                await ctx.channel.send("일시정지된 상태에요! 먼저 일시정지를 풀고 기록해 주세요")
                return
            time_passed = str(
                (datetime.now()) - datetime.strptime(current[1], "%Y/%m/%d %H:%M:%S"))
            await ctx.channel.send(f"기록을 완료했어요! 현재까지 지난 시간은 {time_passed} (이)에요.")
            if t:
                records.append(t)
            records.append((datetime.now()).strftime("%Y/%m/%d %H:%M:%S"))
            records = ",".join(records)
            db.execute("UPDATE stopwatch SET records = ? WHERE UserID = ? AND end_time IS NULL", records, ctx.author.id)
            db.commit()
        elif activity in ["일시정지", "재개"]:
            current = db.record("SELECT * FROM stopwatch WHERE UserID = ? AND end_time IS NULL", ctx.author.id)
            if not current:
                await ctx.channel.send("설정해 둔 스톱워치가 없어요!")
                return
            try:
                records = current[2].split(",")
            except AttributeError:
                records = []
            t = 0
            if "p" in records:
                if records.count("p") - records.count("r"):
                    t = 2
                else:
                    t = 1
            if t <= 1 and activity == "일시정지":
                await ctx.channel.send("일시정지를 완료했어요!")
                try:
                    records = current[2].split(',')
                except:
                    records = []
                records.append("p")
                records.append((datetime.now()).strftime("%Y/%m/%d %H:%M:%S"))
                records = ",".join(records)
                db.execute("UPDATE stopwatch SET records = ? WHERE UserID = ? AND end_time IS NULL", records,
                           ctx.author.id)
                db.commit()
            elif t == 2:
                await ctx.channel.send("재개를 완료했어요!")
                try:
                    records = current[2].split(',')
                except:
                    records = []
                records.append("r")
                records.append((datetime.now()).strftime("%Y/%m/%d %H:%M:%S"))
                records = ",".join(records)
                db.execute("UPDATE stopwatch SET records = ? WHERE UserID = ? AND end_time IS NULL", records,
                           ctx.author.id)
                db.commit()
        elif activity == "내역":
            if t and t.startswith("자세히 "):
                buy = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
                if buy & 4 == 0:
                    await ctx.channel.send("사용할 수 없는 기능이에요! `커뉴야 뀨 구매 자세한 스톱워치`로 기능을 해금하세요")
                id_ = t.split(" ")[1]
                current = db.record("SELECT * FROM stopwatch WHERE id = ?", id_)
                embed = Embed(color=0xffd6fe, title=f'{id_} 아이디로 조회된 스톱워치 내역!')
                embed.add_field(name="시작한 시각", value=current[1], inline=False)
                r = []
                try:
                    records = current[2].split(',')
                    tjfaud = ""
                    type = ""
                    count = 1
                    time_check = re.compile("\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}")
                    for i in range(30):
                        try:
                            if records[i] == "p":
                                type = "일시정지"
                            elif records[i] == "r":
                                type = "재개"
                            elif not time_check.match(records[i]):
                                type = records[i]
                                count += 1
                            else:
                                if type:
                                    tjfaud += f"\n{type}: {records[i]}"
                                    type = ""
                                else:
                                    tjfaud += f"\n{count}. {records[i]}"
                                    count += 1
                                r.append(records[i])
                        except IndexError:
                            break
                    else:
                        tjfaud += "\n그리고 더 많은 기록들..."
                    embed.add_field(name="중간중간 한 기록들", value=tjfaud, inline=False)
                except:
                    pass
                time_text = current[3]
                final_time = datetime.strptime(current[3], "%Y/%m/%d %H:%M:%S") - datetime.strptime(current[1],
                                                                                                    "%Y/%m/%d %H:%M:%S")
                embed.add_field(name="종료된 시각", value=time_text, inline=False)
                embed.add_field(name="측정된 시간", value=str(final_time), inline=False)
                if current[2]:
                    pauses = list(filter(lambda x: records[x] == "p", range(len(records))))
                    for p in pauses:
                        t = datetime.strptime(records[p + 3], "%Y/%m/%d %H:%M:%S") - datetime.strptime(records[p + 1],
                                                                                                       "%Y/%m/%d %H:%M:%S")
                        final_time -= t
                if buy & 4:
                    if r:
                        u = self.analyze(current, r)
                        tjfaud = ''
                        w = 1
                        for v in u:
                            if u.index(v) == len(u) - 1:
                                tjfaud += f"\n이후 종료까지 걸린 시간은 {v}에요."
                            else:
                                tjfaud += f"\n{w}번째 기록까지 걸린 시간은 {v}이고,"
                            w += 1
                        embed.add_field(name='구간별 분석', value=tjfaud, inline=False)
                    # x = db.records("SELECT * FROM stopwatch WHERE UserID = ? AND title = ?", ctx.author.id, current[4])
                    # for y in x:
                    #     if len(y[2].split(',')) == len(current[2].split(',')):
                    #
                await ctx.channel.send(embed=embed)
                return
            if not t:
                sts = db.records(
                    "SELECT start_time, title, id FROM stopwatch WHERE UserID = ? ORDER BY start_time DESC LIMIT 25",
                    ctx.author.id)
            else:
                sts = db.records(
                    "SELECT start_time, 0 FROM stopwatch WHERE UserID = ? AND title = ? ORDER BY start_time DESC",
                    ctx.author.id, t)
            if not sts:
                await ctx.channel.send("조회된 스톱워치가 없어요!")
                return
            embed = Embed(color=0xffd6fe, title=f"{t}로 저장한 스톱워치 내역" if t else "스톱워치 내역")
            for st in sts:
                embed.add_field(name=st[1] if st[1] else t, value=f"{st[0]}에 시작된 기록, 아이디 {st[2]}", inline=False)
            await ctx.channel.send(embed=embed)

    def analyze(self, current, r):
        s = []
        for r_ in r:
            s.append(datetime.strptime(r_, "%Y/%m/%d %H:%M:%S"))
        u = []
        for t in s:
            if t == s[0]:
                u.append(t - datetime.strptime(current[1], "%Y/%m/%d %H:%M:%S"))
            else:
                u.append(t - s[s.index(t) - 1])
        else:
            u.append(datetime.strptime(current[3], "%Y/%m/%d %H:%M:%S") - t)
        return u

    @command(name="할거", aliases=["할일"])
    async def todo(self, ctx, *args):
        cnpr = db.record("SELECT time_constant FROM attends WHERE UserID = ? AND attend_date = ?", ctx.author.id,
                         ((time() + 32400) // 86400))
        if not cnpr:
            await ctx.channel.send('이 기능은 출석체크 이후에 사용 가능해요! 먼저 출석체크를 하시고 이 명령어를 다시 사용해 주세요')
            return
        args = list(args)
        if not args or args[0] == "도움":
            await ctx.channel.send(
                embed=Embed(color=0xff8585, title='명령어 도움', description='첫 인수를 무엇으로 설정하냐에 따라 인식법이 달라집니다. '
                                                                        '정보량이 많은 명령어다 보니 *두 번째 인수부터는 인수끼리 '
                                                                        '따옴표로 묶으셔야 정상적으로 작동됩니다.*\n\n`커뉴야 '
                                                                        '할거 추가`: 할 일을 추가합니다. 차례로 카테고리 ('
                                                                        '과목), 자세한 할 일, 기간, 분량을 인수로 받습니다. '
                                                                        '참고로 기간은 n일 뒤까지 에서 n을 입력하시면 됩니다. ('
                                                                        '예시: `커뉴야 할거 추가 "수학" "지수로그함수 연습문제" '
                                                                        '"3" "24"`)\n\n`커뉴야 할거 진행`: 미리 추가해 '
                                                                        '놓은 할 일을 진행합니다. 차례로 카테고리(선택), 할일, '
                                                                        '분량을 인수로 받습니다. 카테고리는 굳이 입력하지 않아도 '
                                                                        '되며 할 일 인수는 검색 기능을 지원하지 때문에 몇 글자만 '
                                                                        '입력해도 됩니다.\n\n`커뉴야 할거 현재`: 현재 등록해 '
                                                                        '놓은 할 일들의 목록을 최대 25개까지 급한 순서대로 '
                                                                        '표시합니다. 중간목표를 설정했다면 중간목표에 대한 정보도 '
                                                                        '출력합니다.\n\n`커뉴야 할거 초기화`: 만들어 놓았던 '
                                                                        '모든 할 것들을 초기화시킵니다.\n\n`커뉴야 할거 '
                                                                        '중간목표`: `커뉴야 할거 진행`처럼 뒤에 할 일 인수를 '
                                                                        '간략하게 입력하면 검색되고, 검색된 할 일에 대해 중간 '
                                                                        '목표를 지정합니다. 언제까지 얼마만큼의 분량을 끝낼지 정할 '
                                                                        '수 있습니다.'))
        elif args[0] in ['추가', '정기']:
            if 3 <= len(args) <= 5:
                if len(args) == 3:
                    args.append(0)
                    args.append(0)
                elif len(args) == 4:
                    args.append(0)
                try:
                    args[3] = int(args[3])
                except ValueError:
                    await ctx.channel.send("\"기간\" 변수가 잘못 들어갔어요! 분량은 정수로만 입력 가능해요")
                    return
                try:
                    args[4] = int(args[4])
                except ValueError:
                    await ctx.channel.send("\"분량\" 변수가 잘못 들어갔어요! 분량은 정수로만 입력 가능해요")
                    return
                if args[3] < 1:
                    await ctx.channel.send("기간은 자연수여야만 해요!")
                    return
                if args[0] == '정기' and args[3] > 31:
                    await ctx.channel.send("기간이 너무 길어요! 31일 이내로 기간을 설정해 주세요")
                    return
                if args[4] < 1:
                    await ctx.channel.send("분량은 자연수여야만 해요!")
                    return
                # args[1]: 과목(카테고리) args[2]: 자세한 할거 args[3]: 기간 (언제까지) args[4]: 분량
                if '%' in args[2] or '_' in args[2]:
                    await ctx.channel.send('들어가면 안 되는 특수문자가 들어가 있어요!')
                    return
                embed = Embed(color=0xff8585, title="할거 추가 완료")
                embed.set_footer(text="처음이시라면 `커뉴야 할거 도움`을 꼭 입력해 주세요! 다른 명령어들과 입력방식이 다릅니다.")
                embed.add_field(name="카테고리", value=args[1])
                embed.add_field(name="할 일", value=args[2])
                expire_date = args[3] + ((time() + 32400) // 86400)
                if args[0] == '추가':
                    expire_text = (datetime.now() + timedelta(days=args[3])).strftime("%y년 %m월 %d일")
                    embed.add_field(name="기간", value=expire_text)

                else:
                    embed.add_field(name="기간", value=f'{args[3]}일마다 하는 정기적 할 일')
                embed.add_field(name="분량", value=str(args[4]))
                await ctx.channel.send(embed=embed)
                if args[0] == '추가':
                    db.execute("INSERT INTO todo (UserID, subject, content, until, quantity) VALUES (?, ?, ? ,?, ?)",
                               ctx.author.id, args[1], args[2], expire_date, args[4])
                else:
                    db.execute(
                        "INSERT INTO todo (UserID, subject, content, until, quantity, collab_type) VALUES (?, ?, ? ,?, ?, ?)",
                        ctx.author.id, args[1], args[2], expire_date - 1, args[4], args[3])
                db.commit()
            else:
                await ctx.channel.send("올바르지 않은 개수의 인수가 입력되었어요!")
                return
        elif args[0] == "진행":
            if len(args) == 3:
                search = db.records(
                    "SELECT * FROM todo WHERE ? in (UserID, partner1, partner2, partner3, partner4, partner5) AND content LIKE ?",
                    ctx.author.id,
                    f"%{args[1]}%")
                quantity = args[2]
            elif len(args) == 4:
                search = db.records(
                    "SELECT * FROM todo WHERE ? in (UserID, partner1, partner2, partner3, partner4, partner5) AND subject = ? AND content LIKE ?",
                    ctx.author.id, args[1], f"%{args[2]}%")
                quantity = args[3]
            else:
                await ctx.channel.send(
                    "올바르지 않은 개수의 인수가 입력되었어요!\n\n사용법: `커뉴야 할거 진행 \"과목\" \"할일\" \"분량\"\n\n과목은 굳이 입력하지 않아도 되며 할일을 자세하게 입력할 필요는 없습니다. 할일도 처음에 정한 이름 그대로 입력할 필요는 없으며 검색이 가능합니다.")
                return
            quantity = int(quantity)
            if not (now := await self.fetch_work(ctx, search)):
                return
            embed = Embed(color=0xff8585, title="할거 진행 완료")
            embed.add_field(name="카테고리", value=now[1])
            embed.add_field(name="할 일", value=now[2])
            new = list(copy.deepcopy(now))
            # now 유저아이디 과목 내용 분량 진행도 기한 중간목표기한 중간목표진행 콜랍타입 콜랍그룹
            new[4] += quantity
            if new[4] >= now[3]:
                new[3] = new[4]
                embed.add_field(name="진행한 분량", value=str(now[3] - now[4]))
                embed.add_field(name="진행도", value=f"{now[3]} / {now[3]} (100%)")
            else:
                embed.add_field(name="진행한 분량", value=str(quantity))
                embed.add_field(name="진행도", value=f"{new[4]} / {now[3]} ({round((new[4] / now[3]) * 100, 2)}%)")
            cc = 0
            if now[6]:
                if new[4] >= now[7]:
                    embed.add_field(name='중간 목표 완료', value=f'설정한 중간 목표: {now[7]}')
                    cc = 1
                else:
                    embed.add_field(name='중간 목표 진행', value=f'설정한 중간 목표: {now[7]}')
                    embed.add_field(name='남은 중간 목표 제한시간', value=f"{int(now[6] - ((time() + 32400) // 86400))}일")
            embed.add_field(name='남은 제한 시간', value=f"{int(now[5] - ((time() + 32400) // 86400))}일")
            if now[8] and now[8] < 6400 and (now[8] % 32 == 0 or now[8] > 3200):
                embed.add_field(name='같이모드의 할 일', value='이 일을 같이 진행하기로 한 사람들 모두가 이만큼 할 일을 진행했어요')
            await ctx.channel.send(embed=embed)
            if not cc:
                db.execute(
                    "UPDATE todo SET progress = ? WHERE ? in (UserID, partner1, partner2, partner3, partner4, partner5) AND subject = ? AND content = ? AND quantity = ? AND progress = ? AND until = ?",
                    new[4], ctx.author.id, now[1], now[2], now[3], now[4], now[5])
            else:
                db.execute(
                    "UPDATE todo SET progress = ?, checkpoint_until = NULL, checkpoint_progress = NULL WHERE ? in (UserID, partner1, partner2, partner3, partner4, partner5) AND subject = ? AND content = ? AND quantity = ? AND progress = ? AND until = ?",
                    new[4], ctx.author.id, now[1], now[2], now[3], now[4], now[5])
            db.commit()
            await ctx.channel.send('방금 진행하신 할 일에 대해 성적을 기록할까요? 성적 기록을 원하시면 **맞은개수 / 문제수** 형식으로 입력해주세요.')
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=120,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
            except asyncio.TimeoutError:
                await ctx.channel.send("성적을 기록하지 않기로 했어요.")
                return
            await self.grades(ctx=ctx, subject=now[1], content=now[2], grade=msg.content)
        elif args[0] == "현재":
            todo_list = db.records(
                "SELECT subject, content, quantity, progress, until, checkpoint_until, checkpoint_progress FROM todo WHERE until >= ? AND ? IN (UserId, partner1, partner2, partner3, partner4, partner5) ORDER BY until ASC LIMIT 25",
                (time() + 32400) // 86400, ctx.author.id)
            embed = Embed(color=0xff8585, title=f"{str(ctx.author)}님의 현재 할 일 (급한 순 정렬)")
            for todo in todo_list:
                try:
                    tjfaud = f"진행한 분량 {todo[3]} / {todo[2]} ({round(todo[3] / todo[2] * 100, 2)}%)\n\n남은 제한 시간: {int(todo[4] - ((time() + 32400) // 86400))}일"
                except TypeError:
                    continue
                if todo[5]:
                    tjfaud += f"\n\n이 할 일에서 진행 중인 중간 목표:**{int(todo[5] - ((time() + 32400) // 86400))}일** 안에 **{todo[6] - todo[3]}** 만큼을 더 해야 함"
                embed.add_field(name=f"{todo[0]} 카테고리의 할 일 *{todo[1]}*", value=tjfaud, inline=False)
            await ctx.channel.send(embed=embed)
        elif args[0] == '초기화':
            await ctx.channel.send("정말로 할 일을 초기화하실 건가요? 초기화를 진행한다면 모든 할 일이 즉시 사라져요.\n`초기화`라고 입력해서 초기화를 진행하세요")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
            except TimeoutError:
                await ctx.channel.send("할 일을 초기화하지 않기로 했어요.")
                return
            if msg.content != '초기화':
                await ctx.channel.send("할 일을 초기화하지 않기로 했어요.")
                return
            db.execute("DELETE FROM todo WHERE UserID = ?", ctx.author.id)
            db.commit()
            await ctx.channel.send("할 일 초기화를 완료했어요!")
        elif args[0] == "중간목표":
            if len(args) == 2:
                search = db.records(
                    "SELECT * FROM todo WHERE ? in (UserID, partner1, partner2, partner3, partner4, partner5) AND content LIKE ?",
                    ctx.author.id,
                    f"%{args[1]}%")
            elif len(args) == 3:
                search = db.records(
                    "SELECT * FROM todo WHERE ? in (UserID, partner1, partner2, partner3, partner4, partner5) AND subject = ? AND content LIKE ?",
                    ctx.author.id, args[1], f"%{args[2]}%")
            else:
                await ctx.channel.send('올바르지 않은 개수의 인수가 입력되었어요!')
                return
            now = await self.fetch_work(ctx, search)
            if not now:
                return
            await ctx.channel.send("중간 목표를 몇 일 뒤까지로 설정할 건지 말해 주세요! (음이 아닌 정수 값으로만)")
            msg = await self.bot.wait_for(
                "message",
                timeout=20,
                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
            )
            try:
                msg = int(msg.content)
            except ValueError:
                msg = -1
            if msg < 0:
                await ctx.channel.send("올바르지 않은 입력이에요! 0 이상의 정수로 입력해 주세요")
                return
            await ctx.channel.send("중간 목표로 삼을 분량을 말해 주세요!")
            msg2 = await self.bot.wait_for(
                "message",
                timeout=30,
                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
            )
            try:
                msg2 = int(msg2.content)
            except ValueError:
                msg2 = 1
            if msg2 <= 1:
                await ctx.channel.send("올바르지 않은 입력이에요! 1 이상의 정수로 입력해 주세요")
                return
            db.execute(
                "UPDATE todo SET checkpoint_until = ?, checkpoint_progress = ? WHERE ? in (UserID, partner1, partner2, partner3, partner4, partner5) AND subject = ? AND content = ? AND quantity = ? AND progress = ? AND until = ?",
                msg + ((time() + 32400) // 86400), msg2 + now[4], now[0], now[1], now[2], now[3], now[4], now[5])
            await ctx.channel.send("중간 목표 설정을 완료했어요!")
            db.commit()
        elif args[0] == '진행순위':
            search = db.records(
                "SELECT * FROM todo WHERE UserID = ? AND ((32 < collab_type < 3200 AND collab_type % 32 != 0) OR 6400 < collab_type < 7000) AND content LIKE ?",
                ctx.author.id, f"%{args[1]}%")
            now = await self.fetch_work(ctx, search)
            if not now:
                return
            if (32 < now[8] < 3200 and now[8] % 32) or (6400 < now[8] < 7000):
                progresses = db.records(
                    "SELECT UserID, progress FROM todo WHERE collab_type = ? ORDER BY progress DESC", now[8])
                tjfaud = ''
                for progress in progresses:
                    tjfaud += f'\n{progresses.index(progress) + 1}. {str(self.bot.get_user(progress[0]))} (진행도 {progress[1]})'
                await ctx.channel.send(embed=Embed(color=0xff8585, title=f"{args[1]}에 대한 사람들의 진행도", description=tjfaud))
            else:
                await ctx.channel.send("각각모드의 할 일에 대해서만 순위를 볼 수 있어요!")
                return

    @command(name='같이공부')
    async def study_together(self, ctx, w: Optional[int]):
        if not w:
            await ctx.channel.send("누구와 같이 공부할지 말해주세요! 유저 ID의 형태로 입력해 주세요.")
            return
        check = self.bot.get_user(w)
        if not check:
            await ctx.channel.send("유효하지 않은 대상이에요!\n유저 아이디를 잘 입력했는지 또는 대상으로 삼은 유저와 커뉴봇이 같이 있는 서버가 하나라도 있는지 확인해보세요.")
            return
        st = db.record("SELECT study_with FROM games WHERE UserID = ?", ctx.author.id)[0]
        if st and w in st.split(","):
            await ctx.channel.send("이미 같이 공부하고 있는 사람이에요!")
            return
        if st:
            st = st.split(",")
        else:
            st = []
        confirm_code = randint(1000000, 9999999)
        await ctx.channel.send(
            f"정말로 같이 공부하기로 한 사람이 맞나 인증을 할게요... 5분 안에 같이 공부하기로 하신 {check.name}님께 커뉴봇이 볼 수 있는 곳에서 {confirm_code}를 입력하라고 말해주세요.")
        try:
            await self.bot.wait_for(
                "message",
                timeout=300,
                check=lambda message: message.author.id == w and message.content == str(confirm_code)
            )
        except asyncio.TimeoutError:
            await ctx.channel.send("인증에 실패했어요.")
            return
        await ctx.channel.send("인증을 완료했어요!")
        try:
            st = "".join(st) + f",{w}"
        except AttributeError:
            st = w
        try:
            m = db.record("SELECT study_with FROM games WHERE UserID = ?", w)[0].split(",")
        except AttributeError:
            m = ['']
        try:
            m = "".join(m) + f",{ctx.author.id}"
        except AttributeError:
            m = ctx.author.id
        db.execute("UPDATE games SET study_with = ? WHERE UserID = ?", st, ctx.author.id)
        db.execute("UPDATE games SET study_with = ? WHERE UserID = ?", m, w)
        db.commit()

    @command(name='같이할일')
    async def todo_together(self, ctx, *args):
        if len(args) == 1 and args[0] == "도움":
            await ctx.channel.send(embed=Embed(color=0xffd6fe, title='명령어 도움',
                                               description='다른 사람과 같이 할 일을 만듭니다. 진행하거나 조회하는 것은 `커뉴야 할거`명령어로 할 수 있습니다.\n`커뉴야 같이할일 도움`: 이 도움말을 표시합니다.\n`커뉴야 같이공부`: 같이 공부할 사람을 설정합니다.\n`커뉴야 같이할일 (카테고리) (할일) (기간) (분량) (타입) (사람(들))`: 다른 사람과 같이 할 일을 추가합니다. 타입에는 각각, 같이가 있으며 타입을 같이로 설정할 경우 한 명이 할 일을 실행하면 같은 할 일을 진행하는 모든 사람이 그 할 일을 진행하는 것처럼 됩니다. **`커뉴야 할거 추가`처럼 모든 인수를 따옴표로 구분해야 명령어가 제대로 작동됩니다.**'))
            return
        if len(args) < 6:
            await ctx.channel.send("올바르지 않은 개수의 인수가 입력되었어요! `커뉴야 같이할일 도움`을 참고하세요")
            return
        study_with = db.record("SELECT study_with FROM games WHERE userID = ?", ctx.author.id)[0]
        if not study_with:
            await ctx.channel.send("같이 공부하기로 되어 있는 사람이 없어요! `커뉴야 같이공부`로 같이 공부할 사람을 찾고 명령어를 사용해 주세요")
            return
        study_with = study_with.split(',')
        for p in args[5:]:
            if p not in study_with:
                await ctx.channel.send("같이 공부하기로 되어 있는 사람들만 같이 할 일을 설정할 수 있어요!")
                return
        if args[4] not in ['각각', '같이']:
            await ctx.channel.send("유효하지 않은 할 일 타입이에요! `커뉴야 같이할일 도움`을 참고해 주세요.")
            return
        args = list(args)
        try:
            args[2] = int(args[2])
        except ValueError:
            await ctx.channel.send("\"기간\" 변수가 잘못 들어갔어요! 분량은 정수로만 입력 가능해요")
            return
        try:
            args[3] = int(args[3])
        except ValueError:
            await ctx.channel.send("\"분량\" 변수가 잘못 들어갔어요! 분량은 정수로만 입력 가능해요")
            return
        if args[2] < 1:
            await ctx.channel.send("기간은 자연수여야만 해요!")
            return
        if args[3] < 1:
            await ctx.channel.send("분량은 자연수여야만 해요!")
            return
        if '%' in args[1] or '_' in args[1]:
            await ctx.channel.send('들어가면 안 되는 특수문자가 들어가 있어요!')
            return
        await ctx.channel.send('정기적으로 해야 하는 일인가요 한 번만 하면 되는 일인가요?\n한 번만 해도 되는 일이라면 0을, 정기적으로 해야 되는 일이라면 1을 입력해 주세요.')
        try:
            msg = await self.bot.wait_for(
                "message",
                timeout=20,
                check=lambda message: message.author == ctx.author and ctx.channel == message.channel
            )
        except asyncio.TimeoutError:
            await ctx.channel.send('같이 할 일을 추가하지 않기로 했어요.')
            return
        try:
            term = int(msg.content)
        except ValueError:
            await ctx.channel.send('올바르지 않은 입력 방식이에요!')
            return
        if term not in [0, 1]:
            await ctx.channel.send("올바르지 않은 입력이에요!")
            return
        if term and args[2] > 31:
            await ctx.channel.send("정기적인 할 일을 정할 때 기간은 31일을 넘을 수 없어요!")
            return
        if args[4] == '각각':
            if term:
                ct = 32 * randint(1, 99) + args[2]
            else:
                ct = randint(6401, 6999)
        else:
            if term:
                ct = 32 * randint(100, 199) + args[2]
            else:
                ct = 32 * randint(1, 100)
        embed = Embed(color=0xff8585, title="할거 추가 완료")
        embed.add_field(name='모드', value=f"{args[4]}모드")
        embed.add_field(name="카테고리", value=args[0])
        embed.add_field(name="할 일", value=args[1])
        expire_date = args[2] + ((time() + 32400) // 86400)
        if term == 0:
            expire_text = (datetime.now() + timedelta(days=args[2])).strftime("%y년 %m월 %d일")
            embed.add_field(name="기간", value=expire_text)
        else:
            embed.add_field(name="기간", value=f'{args[2]}일마다 하는 정기적 할 일')
        embed.add_field(name="분량", value=str(args[3]))
        await ctx.channel.send(embed=embed)
        if args[4] == '각각':
            db.execute(
                "INSERT INTO todo (UserID, subject, content, until, quantity, collab_type) VALUES (?, ?, ?, ?, ?, ?)",
                ctx.author.id, args[0], args[1], expire_date, args[3], ct)
            for partner in args[5:]:
                db.execute(
                    "INSERT INTO todo (UserID, subject, content, until, quantity, collab_type) VALUES (?, ?, ?, ?, ?, ?)",
                    int(partner), args[0], args[1], expire_date, args[3], ct)
        else:
            if len(args) < 10:
                while len(args) < 10:
                    args.append(None)
            db.execute(
                "INSERT INTO todo (UserID, subject, content, until, quantity, collab_type, partner1, partner2, partner3, partner4, partner5) VALUES (?, ?, ? ,?, ?, ?, ?, ?, ?, ?, ?)",
                ctx.author.id, args[0], args[1], expire_date, args[3], ct, args[5], args[6], args[7], args[8], args[9])
        db.commit()

    @command(name='일정')
    async def premium_todo(self, ctx, activity: Optional[str], *args):
        if activity == '표시':
            duration = args[0]
            valid_list = (
                '1일', '2일', '3일', '4일', '5일', '6일', '7일', '14일', '21일', '28일', '1주', '2주', '3주', '4주', '1달', '1개월')
            if duration not in valid_list:
                await ctx.channel.send('기간은 1~7, 14, 21, 28일, 1~4주, 1달 이라고만 입력 가능해요! 사진 규격 때문이니 이해해 주세요...')
                return
            if duration == '1달':
                with Image.open(r"C:\Users\namon\PycharmProjects\discordbot\lib\images\19201080.png") as im:
                    draw = ImageDraw.Draw(im, 'RGBA')
                    background = \
                        db.record('SELECT d0 FROM temp_data WHERE USERID = ? AND data_type = "공부설정"', ctx.author.id)[0]
                    t = bin(background)[2:].rjust(24, '0')
                    draw.rectangle(((0, 0), (1920, 1080)),
                                   (int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)),
                                   outline=(int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)))
                    if max(int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)) > 127:
                        defaultTextColor = (0, 0, 0, 255)
                    else:
                        defaultTextColor = (255, 255, 255, 255)
                    for i in range(1, 8):
                        draw.line(((i * 274 - 10, 0), (i * 274 - 10, 1080)), fill=defaultTextColor, width=20)

                    for i in range(1, 7):
                        draw.line(((0, i * 180 - 10), (1920, i * 180 - 10)), fill=defaultTextColor, width=20)
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
                        "SELECT subject, content, quantity, progress, until, color FROM todo WHERE UserID = ? and collab_type % 32 = 0",
                        ctx.author.id)
                    today = int((time() + 32400) // 86400)
                    day_to_check = today - a.day + 1
                    day1 = day_to_check
                    day_until = day_to_check + d - 1
                    colors = [0xffffff] * 7
                    month_list = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                                  [], [], [], [], [], [], [], [], [], []]
                    for task in todo_list:
                        task = list(task)
                        if task[4] > 1000000 and task[5] != 0xffffff:
                            task4 = map(int, list(str(task[4] // 1000000)))
                            for yoil in task4:
                                colors[yoil] = task[5]
                        if day1 <= task[4] <= day_until:
                            if month_list[task[4] - day1] == '':
                                month_list[task[4] - day1] = task
                            else:
                                month_list[task[4] - day1].append(task)
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
                            draw.rectangle(((x - 20, y - 20), (x + 234, y + 140)),fill=fill)
                        draw.text((x, y), str(i + 1), fill=defaultTextColor, font=font)
                        if len(month_list[i]):
                            t = []
                            u = 0
                            v = 0
                            for task in month_list[i]:
                                t.append(task[0])
                                u += task[3]
                                v += task[2]
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
                    await ctx.channel.send(file=File(u))
            if duration == '1일':
                if args[-1] == '세로':
                    with Image.open(r"C:\Users\namon\PycharmProjects\discordbot\lib\images\10802340.png") as im:
                        draw = ImageDraw.Draw(im, 'RGBA')
                        background = \
                            db.record('SELECT d0 FROM temp_data WHERE USERID = ? AND data_type = "공부설정"',
                                      ctx.author.id)[0]
                        t = bin(background)[2:].rjust(24, '0')
                        draw.rectangle(((0, 0), (1080, 2340)),
                                       (int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)),
                                       outline=(int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)))
                        if max(int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)) > 127:
                            defaultTextColor = (0, 0, 0, 255)
                        else:
                            defaultTextColor = (255, 255, 255, 255)
                        draw.line(((0, 240), (1080, 240)), fill=defaultTextColor, width=20)
                        a = datetime.now()
                        today = int((time() + 32400) // 86400)
                        today_todo = db.records(
                            "SELECT content, quantity, progress, subject FROM todo WHERE UserID = ? and until = ? AND collab_type % 32 = 0",
                            ctx.author.id, today)
                        tomorrow_todo = db.records(
                            "SELECT content, quantity, progress, subject FROM todo WHERE UserID = ? and until = ? AND collab_type % 32 = 0",
                            ctx.author.id, today + 1)
                        everyday_goal = db.records(
                            "SELECT content, quantity, progress, subject FROM todo WHERE UserID = ? AND until = ? AND collab_type % 32 = 1",
                            ctx.author.id, today)
                        colours = db.records(
                            "SELECT subject, color FROM todo WHERE UserID = ? AND until >= 1000000 and collab_type = 0",
                            ctx.author.id)
                        colors = dict()
                        for c in colours:
                            colors[c[0]] = c[1]
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
                                if t[3] in colors:
                                    c = bin(colors[t[3]])[2:].rjust(24, '0')
                                    fill = (int(c[0:8], 2), int(c[8:16], 2), int(c[16:], 2))
                                else:
                                    fill = defaultTextColor
                                draw.text((0, 450 + i * 100),
                                          f'{t[3]}: {t[0]} ({t[2]} / {t[1]}, {round(t[2] / t[1] * 100, 1)}%)',
                                          fill=fill, font=font2)
                                i += 1
                        draw.text((0, 970), '- 내일까지 할 일', fill=defaultTextColor, font=font)
                        i = 0
                        if tomorrow_todo:
                            for t in tomorrow_todo:
                                if t[3] in colors:
                                    c = bin(colors[t[3]])[2:].rjust(24, '0')
                                    fill = (int(c[0:8], 2), int(c[8:16], 2), int(c[16:], 2))
                                else:
                                    fill = defaultTextColor
                                draw.text((0, 1150 + i * 100),
                                          f'{t[3]}: {t[0]} ({t[2]} / {t[1]}, {round(t[2] / t[1] * 100, 1)}%)',
                                          fill=fill, font=font2)
                                i += 1
                        draw.text((0, 1670), '- 오늘의 매일 목표', fill=defaultTextColor, font=font)
                        i = 0
                        if everyday_goal:
                            for t in everyday_goal:
                                if t[3] in colors:
                                    c = bin(colors[t[3]])[2:].rjust(24, '0')
                                    fill = (int(c[0:8], 2), int(c[8:16], 2), int(c[16:], 2))
                                else:
                                    fill = defaultTextColor
                                draw.text((0, 1850 + i * 100),
                                          f'{t[3]}: {t[0]} ({t[2]} / {t[1]}, {round(t[2] / t[1] * 100, 1)}%)',
                                          fill=fill, font=font2)
                                i += 1
                        im.save(u := r"C:\Users\namon\PycharmProjects\discordbot\lib\images\19201080_temp.png")
                        await ctx.channel.send(file=File(u))
                else:
                    with Image.open(r"C:\Users\namon\PycharmProjects\discordbot\lib\images\19201080.png") as im:
                        draw = ImageDraw.Draw(im, 'RGBA')
                        background = \
                            db.record('SELECT d0 FROM temp_data WHERE USERID = ? AND data_type = "공부설정"',
                                      ctx.author.id)[0]
                        t = bin(background)[2:].rjust(24, '0')
                        draw.rectangle(((0, 0), (1920, 1080)),
                                       (int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)),
                                       outline=(int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)))
                        if max(int(t[:8], 2), int(t[8:16], 2), int(t[16:24], 2)) > 127:
                            defaultTextColor = (0, 0, 0, 255)
                        else:
                            defaultTextColor = (255, 255, 255, 255)
                        draw.line(((0, 120), (1920, 120)), fill=defaultTextColor, width=20)
                        a = datetime.now()
                        today = int((time() + 32400) // 86400)
                        today_todo = db.records(
                            "SELECT content, quantity, progress, subject FROM todo WHERE UserID = ? and until = ? AND collab_type % 32 = 0",
                            ctx.author.id, today)
                        tomorrow_todo = db.records(
                            "SELECT content, quantity, progress, subject FROM todo WHERE UserID = ? and until = ? AND collab_type % 32 = 0",
                            ctx.author.id, today + 1)
                        everyday_goal = db.records(
                            "SELECT content, quantity, progress, subject FROM todo WHERE UserID = ? AND until = ? AND collab_type % 32 = 1",
                            ctx.author.id, today)
                        colours = db.records(
                            "SELECT subject, color FROM todo WHERE UserID = ? AND until >= 1000000 and collab_type = 0",
                            ctx.author.id)
                        colors = dict()
                        for c in colours:
                            colors[c[0]] = c[1]
                        today_info = str(a.date()) + ' ' + list('월화수목금토일')[a.weekday()] + '요일'
                        font = ImageFont.truetype(
                            r'C:\Users\namon\PycharmProjects\discordbot\lib\fonts\SDMisaeng.ttf',
                            80)
                        draw.text((720, 20), today_info, fill=defaultTextColor, font=font)
                        draw.text((0, 125), '- 오늘까지 할 일', fill=defaultTextColor, font=font)
                        font2 = ImageFont.truetype(
                            r'C:\Users\namon\PycharmProjects\discordbot\lib\fonts\SDMisaeng.ttf',
                            62)
                        i = 0
                        if today_todo:
                            for t in today_todo:
                                if t[3] in colors:
                                    c = bin(colors[t[3]])[2:].rjust(24, '0')
                                    fill = (int(c[0:8], 2), int(c[8:16], 2), int(c[16:], 2))
                                else:
                                    fill = defaultTextColor
                                draw.text((0, 205 + i * 62),
                                          f'{t[3]}: {t[0]} ({t[2]} / {t[1]}, {round(t[2] / t[1] * 100, 1)}%)',
                                          fill=fill, font=font2)
                                i += 1
                        draw.text((0, 445), '- 내일까지 할 일', fill=defaultTextColor, font=font)
                        i = 0
                        if tomorrow_todo:
                            for t in tomorrow_todo:
                                if t[3] in colors:
                                    c = bin(colors[t[3]])[2:].rjust(24, '0')
                                    fill = (int(c[0:8], 2), int(c[8:16], 2), int(c[16:], 2))
                                else:
                                    fill = defaultTextColor
                                draw.text((0, 525 + i * 62),
                                          f'{t[3]}: {t[0]} ({t[2]} / {t[1]}, {round(t[2] / t[1] * 100, 1)}%)',
                                          fill=fill, font=font2)
                                i += 1
                        draw.text((0, 765), '- 오늘의 매일 목표', fill=defaultTextColor, font=font)
                        i = 0
                        if everyday_goal:
                            for t in everyday_goal:
                                if t[3] in colors:
                                    c = bin(colors[t[3]])[2:].rjust(24, '0')
                                    fill = (int(c[0:8], 2), int(c[8:16], 2), int(c[16:], 2))
                                else:
                                    fill = defaultTextColor
                                draw.text((0, 845 + i * 62),
                                          f'{t[3]}: {t[0]} ({t[2]} / {t[1]}, {round(t[2] / t[1] * 100, 1)}%)',
                                          fill=fill, font=font2)
                                i += 1
                        im.save(u := r"C:\Users\namon\PycharmProjects\discordbot\lib\images\19201080_temp.png")
                        await ctx.channel.send(file=File(u))
        elif activity == '등록':
            if args[0] == '요일':
                days = list(args[1])
                yoils = set()
                for d in days:
                    if d not in list('월화수목금토일'):
                        await ctx.channel.send('올바르지 않은 입력이에요!')
                        return
                    yoils.add(list('일월화수목금토').index(d))
                yoils = map(str, sorted(yoils, reverse=True))
                info = int(''.join(yoils) + '000000')
                await ctx.channel.send(
                    '구체적인 정보들을 알려주세요! 이 다음에 나올 **볼드체**한 정보들을 줄바꿈으로 구분해 말해주세요.\n**카테고리, 달력에 표시될 색깔, (여기서부터 선택) 자세한 내용, 분량**')
                try:
                    msg = await self.bot.wait_for(
                        "message",
                        timeout=150,
                        check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                    )
                except TimeoutError:
                    await ctx.channel.send("생성을 취소했어요.")
                    return
                ans = msg.content.split('\n')
                if len(ans) == 3:
                    try:
                        qnsfid = int(ans[2])
                        wktp = None
                    except ValueError:
                        qnsfid = None
                        wktp = ans[2]
                else:
                    try:
                        qnsfid = int(ans[2])
                        wktp = ans[3]
                    except ValueError:
                        try:
                            qnsfid = int(ans[3])
                            wktp = ans[2]
                        except ValueError:
                            await ctx.channel.send('올바르지 않은 입력이에요!')
                            return
                db.execute(
                    "INSERT INTO todo (USERID, subject, content, quantity, progress, until, color) VALUES (?, ?, ?, ?, 0, ?, ?)",
                    ctx.author.id, ans[0], wktp, qnsfid, info, int(ans[1], 16))
                db.commit()

    @command(name='공부기록')
    async def grades(self, ctx, subject, content, *, grade: Optional[str]):
        today = (time() + 32400) // 86400
        if not grade:
            db.execute('INSERT INTO temp_data (UserID, data_type, d0, d6, d9) VALUES (?, "성적", ?, ?, ?)', ctx.author.id,
                       today, subject, content)
        else:
            slash = re.compile('\d+ ?/ ?\d+')
            if not slash.match(grade):
                await ctx.channel.send('올바르지 않은 성적 정보에요!')
                return
            t = grade.split('/')
            score, total = map(int, t)
            if score > total:
                await ctx.channel.send('만점으로 설정된 값은 받은 점수로 설정된 값보다 클 수 없어요!')
                return
            db.execute('INSERT INTO temp_data (UserID, data_type, d0, d6, d9, d1, d2) VALUES (?, "성적", ?, ?, ?, ?, ?)',
                       ctx.author.id, today, subject, content, score, total)
        db.commit()
        await ctx.channel.send('성적 기록을 완료했어요!')

    @command(name='공부설정')
    async def study_settings(self, ctx, *args):
        data = db.record('SELECT * FROM temp_data WHERE USERID = ? AND data_type = "공부설정"', ctx.author.id)
        if not data:
            db.execute('INSERT INTO temp_data (USERID, data_type) VALUES (?, "공부설정")', ctx.author.id)
            db.commit()
            data = db.record('SELECT * FROM temp_data WHERE USERID = ? AND data_type = "공부설정"', ctx.author.id)
        if not args:
            reference = db.record('SELECT * FROM temp_data WHERE USERID = 0 AND d0 = "배경색"')
            embed = Embed(color=0x808080, title='현재 공부 설정')
            for i in range(3, len(data) + 1):
                try:
                    embed.add_field(name=reference[i], value=data[i])
                except:
                    pass
            await ctx.channel.send(embed=embed)
        elif args[0] == '배경색':
            try:
                color = int(args[1], 16)
            except:
                await ctx.channel.send('색도 입력해 주세요!')
                return
            db.execute('UPDATE temp_data SET d0 = ? WHERE USERID = ? AND data_type = "공부설정"', color, ctx.author.id)
            db.commit()

    @command(name='공부일지')
    async def life_journal(self, ctx, day: Optional[int] = -1):
        d = (time() + 32400) // 86400
        d += day
        grades = db.records(
            'SELECT d1, d2, d6, d9 FROM temp_data WHERE USerid = ? AND data_type = "성적" and d0 = ? and d1 is not null',
            ctx.author.id, d)
        a = datetime.now()
        text = str(a.date()) + ' ' + list('월화수목금토일')[a.weekday()] + '요일\n'
        subjects = dict()
        for i in range(len(grades)):
            try:
                subjects[grades[i][2]].append(i)
            except KeyError:
                subjects[grades[i][2]] = [i]
        for subject in subjects:
            text += '\n' + subject + '\n'
            for i in subjects[subject]:
                grade = grades[i]
                text += f'{grade[3]} (채점 {grade[0]}/{grade[1]} {int(grade[0] / grade[1] * 100)}%)\n'
        non_grades = db.records(
            'SELECT d6, d9 FROM temp_data WHERE USERID = ? and data_type = "성적" and d0 = ? and d1 is null',
            ctx.author.id, d)
        subjects = dict()
        for i in range(len(non_grades)):
            try:
                subjects[non_grades[i][0]].append(i)
            except KeyError:
                subjects[non_grades[i][0]] = [i]
        for subject in subjects:
            text += '\n' + subject + '\n'
            for i in subjects[subject]:
                non_grade = non_grades[i]
                text += f'{non_grade[1]}\n'
        while True:
            try:
                await ctx.channel.send(text[:2000])
            except HTTPException:
                break
            text = text[2000:]

    @command(name='성적그래프')
    async def grade_graph(self, ctx, duration: int = 7, *, rhkahr: Optional[str] = ''):
        today = (time() + 32400) // 86400
        if not rhkahr:
            top_text = '모든 과목의 날짜별 성적 정보'
            base_data = db.records(
                "SELECT sum(d1), sum(d2) FROM temp_data WHERE UserID = ? and data_type = '성적' and d0 > ? and d1 is not null GROUP BY d0 ORDER BY d0;",
                ctx.author.id, today - duration)
        else:
            tree = db.record("SELECT subsubjects FROM games WHERE USERID = ?", ctx.author.id)
            if not tree:
                base_data = db.records(
                    "SELECT sum(d1), sum(d2) FROM temp_data WHERE UserID = ? and data_type = '성적' and d0 > ? and d1 is not null and d6 = ? GROUP BY d0 ORDER BY d0;",
                    ctx.author.id, today - duration, rhkahr)
            else:
                importer = JsonImporter()
                root = importer.import_(tree[0])
                base__data = db.records(
                    "SELECT d0, sum(d1), sum(d2) FROM temp_data WHERE UserID = ? and data_type = '성적' and d0 > ? and d1 is not null and d6 = ? GROUP BY d0 ORDER BY d0;",
                    ctx.author.id, today - duration, rhkahr)
                for t in root.descendants:
                    if t.info == rhkahr:
                        for d in t.descendants:
                            base__data += db.records(
                                "SELECT d0, sum(d1), sum(d2) FROM temp_data WHERE UserID = ? and data_type = '성적' and d0 > ? and d1 is not null and d6 = ? GROUP BY d0 ORDER BY d0;",
                                ctx.author.id, today - duration, d.info)
                base_data = dict()
                for data in base__data:
                    try:
                        base_data[data[0]][0] += data[1]
                        base_data[data[0]][1] += data[2]
                    except KeyError:
                        base_data[data[0]] = list(data[1:])
                base_data = sorted(base_data.items(), key=lambda item: item[0])
                for i in range(len(base_data)):
                    base_data[i] = base_data[i][1]
            top_text = f'{rhkahr}의 날짜별 성적 정보 (설정해둔 하위 과목 포함)'
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
        await ctx.channel.send(file=File(u))

    @command(name='하위과목')
    async def sub_subject(self, ctx, parent, dmdmo):
        subsubject = db.record("SELECT subsubjects FROM games WHERE USERID = ?", ctx.author.id)[0]
        if subsubject:
            importer = JsonImporter()
            root = importer.import_(subsubject)
            for desc in root.descendants:
                if desc.info == parent:
                    s = AnyNode(info=dmdmo, parent=desc)
                    break
            else:
                r = AnyNode(info=parent, parent=root)
                s = AnyNode(info=dmdmo, parent=r)
        else:
            root = AnyNode(info='현재 설정해둔 과목들')
            r = AnyNode(info=parent, parent=root)
            s = AnyNode(info=dmdmo, parent=r)
        exporter = JsonExporter(indent=2, sort_keys=True, ensure_ascii=False)
        j = exporter.export(root)
        st = ''
        for pre, fill, node in RenderTree(root):
            st += "%s%s" % (pre, node.info) + '\n'
        await ctx.channel.send(st)
        db.execute("UPDATE games SET subsubjects = ? WHERE UserID = ?", j, ctx.author.id)
        db.commit()
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

    async def fetch_work(self, ctx, search):
        if len(search) >= 2:
            embed = Embed(color=0x7dffff, title="할 일 여러 개가 검색됨")
            i = 1
            for do in search:
                embed.add_field(name=str(i),
                                value=f"{do[1]} 카테고리의 할 일 *{do[2]}*\n\n진행한 분량 {do[4]} / {do[3]} ({round(do[4] / do[3] * 100, 2)}%)\n\n남은 제한 시간: {int(do[5] - ((time() + 32400) // 86400))}일",
                                inline=False)
                i += 1
            await ctx.channel.send("어느 할 일을 진행하시겠습니까? 굵은 글씨로 써 있는 번호를 말해 주세요", embed=embed)
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
            except TimeoutError:
                await ctx.channel.send("할 일을 진행하지 않기로 했어요.")
                return
            try:
                msg = int(msg.content)
            except ValueError:
                await ctx.channel.send("올바르지 않은 입력이에요!")
                return
            if len(search) < msg:
                await ctx.channel.send("번호가 너무 커요!")
                return
            now = search[msg - 1]
        elif len(search) == 1:
            now = search[0]
        else:
            await ctx.channel.send("해당 이름으로 검색된 할 일이 없어요!")
            return
        return now

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print('("study")')

    # @Cog.listener()
    # async def on_message(self, message):
    #     if message.channel.id not in [749224990209212419, 1013427327058845767] or message.author.bot:
    #         return
    #     cmd = message.content.split()
    #     if message.content.startswith('ㅋ'):
    #         return
    #     if cmd[0] == '할거추가':
    #         cmd_ = message.content.split('/')
    #         cmd_ = cmd_[1:]
    #         cmd_ = ['추가', cmd[1]] + cmd_
    #         await self.todo(message, *cmd_)
    #     elif message.content == '달력':
    #         await self.premium_todo(message, '표시', '1달')
    #     elif message.content == '오늘가로':
    #         await self.premium_todo(message, '표시', '1일', '가로')
    #     elif message.content == '오늘세로':
    #         await self.premium_todo(message, '표시', '1일', '세로')
    #     elif cmd[0] == '요일':
    #         await self.premium_todo(message, '등록', '요일', cmd[1])
    #     elif cmd[0] == '배경색':
    #         await self.study_settings(message, *cmd)
    #     elif cmd[0] == '일지':
    #         if len(cmd) == 1:
    #             await self.life_journal(message)
    #         else:
    #             try:
    #                 cmd[1] = int(cmd[1])
    #             except ValueError:
    #                 await message.channel.send('`일지 (양이 아닌 정수)`')
    #                 return
    #             await self.life_journal(message, cmd[1])
    #     elif cmd[0] == '그래프':
    #         if len(cmd) == 1:
    #             await self.grade_graph(message)
    #         else:
    #             try:
    #                 cmd[1] = int(cmd[1])
    #                 await self.grade_graph(message, cmd[1], *cmd[2:])
    #             except ValueError:
    #                 await self.grade_graph(message, 7, *cmd[1:])
    #     else:
    #         if len(cmd) == 1:
    #             return
    #         treecheck = db.record('SELECT subject FROM todo WHERE USERID = ? AND SUBJECT = ? LIMIT 1', message.author.id, cmd[1])
    #         if not treecheck:
    #             return
    #         await self.sub_subject(message, cmd[1], cmd[2])


async def setup(bot):
    await bot.add_cog(Study(bot))
