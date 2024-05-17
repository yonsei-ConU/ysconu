import math

from discord.ext.commands import Cog, command
from typing import Optional
from discord import Embed, Member, DMChannel

from .achieve import grant, grant_check
from ..db import db
from asyncio import TimeoutError
from math import fabs
from re import compile


class Omok(Cog):
    def __init__(self, bot):
        self.bot = bot

    def draw_board(self, now_omok):
        omok_board = "┏　ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯ\n　１┏┳┳┳┳┳┳┳┳┳┳┳┳┳┓\n　２┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　３┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                     "　４┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　５┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　６┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　７┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                     "　８┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　９┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１０┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１１┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                     "１２┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１３┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１４┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１５┗┴┴┴┴┴┴┴┴┴┴┴┴┴┛ \n​"
        print(omok_board)
        omok_board = list(omok_board)
        for x in range(1, 16):
            num = 18 * x + 2
            for y in range(15):
                if now_omok[x - 1][y] == 0:
                    pass
                elif now_omok[x - 1][y] == 1:
                    omok_board[num] = "○"
                elif now_omok[x - 1][y] == 2:
                    omok_board[num] = "●"
                num += 1
        return ''.join(omok_board)

    async def ask_omok(self, now_turn, black, white, now_omok, a2, timeout, a3, mmr_ckdl, su):
        await now_turn.send(f"{timeout}초 안에 다음번 수를 착수해 주세요. (영어)(숫자) 의 형식으로 입력하셔야 해요! `H7` 또는 `g8` 처럼요.")
        try:
            next_su = await self.bot.wait_for(
                "message",
                timeout=timeout,
                check=lambda message: message.author.id == now_turn.id and isinstance(message.channel, DMChannel)
            )
            next_su = next_su.content
        except TimeoutError:
            if now_turn == black:
                await black.send("시간초과로 인해 졌어요...")
                await white.send("상대의 시간초과로 인해 이겼어요!")
                mmrdelta = mmr_ckdl // 20
                db.execute("UPDATE games SET omok_mmr = omok_mmr + ? WHERE UserID = ?", 15 - mmrdelta, white.id)
                db.execute("UPDATE games SET omok_mmr = omok_mmr - ? WHERE UserID = ?", 15 - mmrdelta, black.id)
            else:
                await white.send("시간초과로 인해 졌어요...")
                await black.send("상대의 시간초과로 인해 이겼어요!")
                mmrdelta = mmr_ckdl // 20
                db.execute("UPDATE games SET omok_mmr = omok_mmr + ? WHERE UserID = ?", 15 + mmrdelta, black.id)
                db.execute("UPDATE games SET omok_mmr = omok_mmr - ? WHERE UserID = ?", 15 + mmrdelta, white.id)
            db.execute("UPDATE games SET room_number = NULL WHERE UserID = ? OR UserID = ?", black.id, white.id)
            db.execute("UPDATE rooms SET people_in = NULL, people_out = NULL WHERE room_number = ?", a2)
            db.commit()
            return
        if "\\" in next_su:
            await now_turn.send("올바르지 않은 입력이에요! 수를 다시 입력해 주세요")
            return await self.ask_omok(now_turn, black, white, now_omok, a2, int(timeout / 3), a3, mmr_ckdl, su)
        proper_su = compile("[abcdefghijklmnoABCDEFGHIJKLMNO]\d{1,2}")
        if not proper_su.match(next_su):
            await now_turn.send("올바르지 않은 입력이에요! 수를 다시 입력해 주세요")
            return await self.ask_omok(now_turn, black, white, now_omok, a2, int(timeout / 3), a3, mmr_ckdl, su)
        else:
            al = next_su[0].lower()
            nu = int(next_su[1:])
            al_id = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o"].index(al)
            nu_id = nu - 1
            if nu_id > 14:
                await now_turn.send("올바르지 않은 입력이에요! 수를 다시 입력해 주세요")
                return await self.ask_omok(now_turn, black, white, now_omok, a2, int(timeout / 3), a3, mmr_ckdl, su)
            if now_omok[nu_id][al_id] != 0:
                await now_turn.send("그곳엔 이미 돌이 있어요! 다른 곳으로 선택해 주세요.")
                return await self.ask_omok(now_turn, black, white, now_omok, a2, int(timeout / 3), a3, mmr_ckdl, su)
            else:
                if now_turn == black:
                    now_omok[nu_id][al_id] = 1
                    turn_constant = 1
                else:
                    now_omok[nu_id][al_id] = 2
                    turn_constant = 2
                win_check = self.check_win(turn_constant, now_omok, nu_id, al_id)
                omok_board = self.draw_board(now_omok)
                embed = Embed(color=0xbf88f8, title=f"{a2} 번 방에서의 대국 - {su + 1} 수까지 진행됨")
                embed.add_field(name="흑돌 대국자", value=str(black))
                embed.add_field(name="백돌 대국자", value=str(white))
                embed.add_field(name="최근 착수자", value=str(now_turn))
                embed.add_field(name="현재 오목판", value=omok_board)
                embed.add_field(name="최근 착수된 자리", value=next_su, inline=False)
                su += 1
                if 4500 <= a2 < 6000:
                    embed.set_footer(text="\"오목룰(자유룰)\"로 진행되는 방이에요.\n흑: 33 가능, 44 가능, 장목 가능\n백: 33 가능, 44 가능, 장목 가능")
                elif 6000 <= a2 < 8000:
                    embed.set_footer(
                        text="\"우리들의 룰\"로 진행되는 방이에요.\n흑: 33 불가, 44 가능, 장목 가능하지만 승리로 취급되지 않음\n백: 33 불가, 44 가능, 장목 가능하지만 승리로 취급되지 않음")
                elif 8000 <= a2 < 10000:
                    embed.set_footer(text="\"렌주룰\"로 진행되는 방이에요.\n흑: 33 불가, 44 불가, 장목 불가\n백: 33 가능, 44 가능, 장목 가능")
                await black.send(embed=embed)
                await white.send(embed=embed)
                if win_check == 1:
                    await black.send("5를 만들어서 이겼어요!")
                    await white.send("상대가 먼저 5를 만들어서 졌어요...")
                    await black.send(embed=embed)
                    await white.send(embed=embed)
                    mmrdelta = mmr_ckdl // 20
                    db.execute("UPDATE rooms SET people_in = NULL, people_out = NULL WHERE room_number = ?", a2)
                    db.execute("UPDATE games SET room_number = NULL WHERE UserID = ? OR UserID = ?", black.id, white.id)
                    db.execute("UPDATE games SET omok_mmr = omok_mmr + ? WHERE UserID = ?", 15 + mmrdelta, black.id)
                    db.execute("UPDATE games SET omok_mmr = omok_mmr - ? WHERE UserID = ?", 15 + mmrdelta, white.id)
                    db.commit()
                    spectate = db.record("SELECT people_out FROM rooms WHERE room_number = ?", a2)
                    try:
                        spectate = spectate[0].split(",")
                        for channels in spectate:
                            to_send = self.bot.get_channel(int(channels))
                            await to_send.send(embed=embed)
                    except AttributeError:
                        pass
                    return
                elif win_check == 2:
                    await white.send("5를 만들어서 이겼어요!")
                    await black.send("상대가 먼저 5를 만들어서 졌어요...")
                    await black.send(embed=embed)
                    await white.send(embed=embed)
                    mmrdelta = mmr_ckdl // 20
                    db.execute("UPDATE rooms SET people_in = NULL, people_out = NULL WHERE room_number = ?", a2)
                    db.execute("UPDATE games SET room_number = NULL WHERE UserID = ? OR UserID = ?", black.id, white.id)
                    db.execute("UPDATE games SET omok_mmr = omok_mmr - ? WHERE UserID = ?", 15 - mmrdelta, white.id)
                    db.execute("UPDATE games SET omok_mmr = omok_mmr + ? WHERE UserID = ?", 15 - mmrdelta, black.id)
                    db.commit()
                    spectate = db.record("SELECT people_out FROM rooms WHERE room_number = ?", a2)
                    try:
                        spectate = spectate[0].split(",")
                        for channels in spectate:
                            to_send = self.bot.get_channel(int(channels))
                            await to_send.send(embed=embed)
                    except AttributeError:
                        pass
                    return
                # elif win_check == -1:
                #     await now_turn.send("그 자리는 육목이라서 금수자리에요!")
                #     return await self.ask_omok(now_turn, black, white, now_omok, a2, 10)
                else:
                    if 6000 <= a2 < 8000:
                        ban_check = self.check_banned(turn_constant, now_omok, al_id, nu_id)
                        if ban_check == 33:
                            await now_turn.send("그 자리는 33이라서 금수자리에요!")
                            now_omok[nu_id][al_id] = 0
                            return await self.ask_omok(now_turn, black, white, now_omok, a2, 10, a3, mmr_ckdl, su)
                    elif 8000 <= a2 < 10000 and now_turn == black:
                        ban_check = self.check_banned(turn_constant, now_omok, al_id, nu_id)
                        if ban_check == 33:
                            await now_turn.send("그 자리는 33이라서 금수자리에요!")
                            now_omok[nu_id][al_id] = 0
                            return await self.ask_omok(now_turn, black, white, now_omok, a2, 10, a3, mmr_ckdl, su)
                        elif ban_check == 44:
                            await now_turn.send("그 자리는 44라서 금수자리에요!")
                            now_omok[nu_id][al_id] = 0
                            return await self.ask_omok(now_turn, black, white, now_omok, a2, 10, a3, mmr_ckdl, su)
                    spectate = db.record("SELECT people_out FROM rooms WHERE room_number = ?", a2)
                    try:
                        spectate = spectate[0].split(",")
                        for channels in spectate:
                            await self.bot.get_channel(int(channels)).send(embed=embed)
                    except AttributeError:
                        pass
                    if now_turn == black:
                        await white.send(f"상대방은 방금 전에 {next_su}자리에 착수했어요")
                        return await self.ask_omok(white, black, white, now_omok, a2, a3, a3, mmr_ckdl, su)
                    else:
                        await black.send(f"상대방은 방금 전에 {next_su}자리에 착수했어요")
                        return await self.ask_omok(black, black, white, now_omok, a2, a3, a3, mmr_ckdl, su)

    def check_win(self, turn_constant, now_omok, x, y):
        score = 0
        a = x
        b = y
        while now_omok[a][b] == turn_constant:
            a += 1
            score += 1
            if a > 14:
                break
        a = x - 1
        while now_omok[a][b] == turn_constant:
            a -= 1
            score += 1
            if a < 0:
                break
        if score == 5:
            return turn_constant
        elif score > 5:
            return -1
        score = 0
        a = x
        b = y
        while now_omok[a][b] == turn_constant:
            b += 1
            score += 1
            if b > 14:
                break
        b = y - 1
        while now_omok[a][b] == turn_constant:
            b -= 1
            score += 1
            if b < 0:
                break
        if score == 5:
            return turn_constant
        elif score > 5:
            return -1
        score = 0
        a = x
        b = y
        while now_omok[a][b] == turn_constant:
            b += 1
            a += 1
            score += 1
            if b > 14 or a > 14:
                break
        b = y - 1
        a = x - 1
        while now_omok[a][b] == turn_constant:
            b -= 1
            a -= 1
            score += 1
            if b < 0 or a < 0:
                break
        if score == 5:
            return turn_constant
        elif score > 5:
            return -1
        score = 0
        a = x
        b = y
        while now_omok[a][b] == turn_constant:
            a -= 1
            b += 1
            score += 1
            if b > 14 or a < 0:
                break
        b = y - 1
        if x != 14:
            a = x + 1
        else:
            a = 14
        while now_omok[a][b] == turn_constant:
            a += 1
            b -= 1
            score += 1
            if b < 0 or a > 14:
                break
        if score == 5:
            return turn_constant
        elif score > 5:
            return -1
        else:
            return 0

    def check_banned(self, turn_constant, now_omok, y, x):
        x_start = max(x - 4, 0)
        x_end = min(x + 4, 14)
        y_start = max(y - 4, 0)
        y_end = min(y + 4, 14)
        l1, l2, l3, l4, c = [], [], [], [], []
        for a in range(x_start, x_end + 1):
            l1.append(str(now_omok[a][y]))
        if len(l1) == 5:
            c.append(0)
        else:
            c.append(self.check_once(l1, turn_constant))
        for b in range(y_start, y_end + 1):
            l2.append(str(now_omok[x][b]))
        if len(l2) == 5:
            c.append(0)
        else:
            c.append(self.check_once(l2, turn_constant))
        if c.count(3) == 2:
            return 33
        r = 7 + min(14 - x_end, x_start, 14 - y_end, y_start)
        xs = x_start
        ys = y_start
        for i in range(r):
            try:
                l3.append(str(now_omok[xs][ys]))
            except IndexError:
                break
            xs += 1
            ys += 1
        if len(l3) == 5:
            c.append(0)
        else:
            c.append(self.check_once(l3, turn_constant))
        if c.count(3) == 2:
            return 33
        xs = x_start
        ys = y_end
        for i in range(r):
            try:
                l4.append(str(now_omok[xs][ys]))
            except IndexError:
                break
            xs += 1
            ys -= 1
        if len(l4) == 5:
            c.append(0)
        else:
            c.append(self.check_once(l4, turn_constant))
        if c.count(3) == 2:
            return 33
        if c.count(4) == 2:
            return 44
        return 0

    def check_once(self, ln, t):
        ln = ''.join(ln)
        u = 3 - t
        if f"0{t}{t}{t}0" in ln:
            return 3
        if f"{u}{t}{t}{t}" in ln:
            return 0
        if f"{t}{t}{t}{u}" in ln:
            return 0
        if f"0{t}0{t}{t}0" in ln:
            return 3
        if f"{u}{t}{t}{t}{t}{u}" in ln:
            return 0
        if f"{t}{t}{t}{t}{u}" in ln:
            return 4
        if f"{u}{t}{t}{t}{t}" in ln:
            return 4
        if f"{t}{t}{t}{t}{u}" in ln:
            return 0
        if f"0{t}{t}0{t}0" in ln:
            return 3
        if f"{u}{t}0{t}{t}" in ln:
            return 0
        if f"{u}{t}{t}0{t}" in ln:
            return 0
        if f"{t}0{t}{t}{u}" in ln:
            return 0
        if f"{t}{t}0{t}{u}" in ln:
            return 0
        return 69

    @command(name="오목")
    async def omok_command(self, ctx, a1: Optional[str], a1_: Optional[Member], a2: Optional[int],
                           a3: Optional[int] = 60, a4: Optional[str] = ''):
        embed = Embed(color=0xbf88f8)
        if not a1:
            a1 = "도움"
        if a1 == "도움":
            embed.add_field(name="커뉴봇 오목 기능 도움!",
                            value="`커뉴야 오목 도움`: 이 도움말을 표시해요.\n`커뉴야 오목 규칙`: 커뉴봇 오목에 적용되는 규칙을 설명해요.\n`커뉴야 오목 테스트`: 지금 오목을 실행해도 되는지 판단해요.\n`커뉴야 오목 입장`: 오목 게임에 입장할 수 있어요. `커뉴야 오목 입장 (방번호)`로 입장해 주세요.\n`커뉴야 오목 목록`: 현재 비어 있지 않은 방들의 목록을 표시해요.\n`커뉴야 오목 관전`: `커뉴야 오목 관전 (방번호)` 로 게임 중인 방을 관전할 수 있어요.\n`커뉴야 오목 점수`: 현재 오목 점수를 표시해요. (기본 1000점) 점수별 티어나 리더보드는 현 점수 시스템의 밸런스를 먼저 확인하고 다음 업데이트 정도에 추가될 예정이에요.")
            await ctx.send(embed=embed)
        elif a1 == "규칙":
            embed.add_field(name="커뉴봇 오목 기능 규칙!",
                            value="1. 오목은 15*15 오목판에서 진행됩니다.\n\n2. 현재까지의 커뉴봇 오목은 두 가지 규칙으로 진행됩니다.\n\n2.1. 자유룰은 흑백 모두 어떠한 경우에도 금수처리가 안 뜨는 규칙이며, 4500 ~ 5999번 방에 들어가시면 이 룰로 진행됩니다.\n\n2.2. 학교룰은 흑백 모두 33은 금수지만 44는 가능하고, 장목은 가능하지만 승리 처리는 안되는 규칙이며, 6000, 7000번대 방에 들어가시면 이 룰로 진행됩니다.")
            await ctx.send(embed=embed)
        elif a1 == "테스트":
            await ctx.send("이글자들이한줄이라면시작하셔도됩니다")
        elif a1 == "관전":
            if a1_:
                a2 = int(a1_.display_name)
            if not a2:
                await ctx.send("`커뉴야 오목 관전 (방번호)`로 입력해 주세요! 현재 있는 방들의 목록은 `커뉴야 오목 목록`으로 확인하실 수 있어요.")
                return
            if 4500 <= a2 < 10000:
                maybe_room = db.record("SELECT people_in FROM rooms WHERE room_number = ?", a2)
                if maybe_room[0] and len(maybe_room[0]) < 37:
                    await ctx.send("그 방은 게임이 진행중이지 않은 것 같아요!")
                    return
                await ctx.send("관전을 하실 건가요? `네`라고 입력해서 관전을 시작하세요")
                try:
                    responded = await self.bot.wait_for(
                        "message",
                        timeout=30,
                        check=lambda
                            message: message.author.id == ctx.author.id and message.channel.id == ctx.channel.id
                    )
                except TimeoutError:
                    await ctx.send("관전하지 않기로 했어요.")
                    return
                if responded.content == "네":
                    spectate = db.record("SELECT people_out FROM rooms WHERE room_number = ?", a2)
                    await ctx.send("관전을 시작했어요! 이 방에서 게임 중인 사람들이 수를 둘 때마다 이 채널에 오목판이 보내질 거에요.")
                    if not spectate[0]:
                        db.execute("UPDATE rooms SET people_out = ? WHERE room_number = ?", ctx.channel.id, a2)
                    else:
                        db.execute("UPDATE rooms SET people_out = people_out + ? WHERE room_number = ?",
                                   f",{ctx.channel.id}", a2)
                    db.commit()
                    l = grant_check("맛있는 팝콘", ctx.author.id)
                    if l == 1:
                        await grant(ctx, "맛있는 팝콘", "이루어지고 있는 오목 대국을 관전하기")
                    return
                else:
                    return
        elif a1 == "입장":
            await ctx.send("오목을 시작한다면 당신은 DM 받는 걸 허용했다고 가정하며, DM 보내는 데 실패할 시 자동으로 실격패 처리 된다는 것에 동의합니다.")
            if a1_:
                a2 = int(a1_.display_name)
            if not a2:
                await ctx.send("`커뉴야 오목 입장 (방번호)`로 입력해 주세요! 현재 있는 방들의 목록은 `커뉴야 오목 목록`으로 확인하실 수 있어요.")
                return
            if 4500 <= a2 < 10000:
                now_room = db.record("SELECT room_number FROM games WHERE UserID = ?", ctx.author.id)
                room = db.records("SELECT * FROM rooms WHERE room_number = ?", a2)
                try:
                    now_room = now_room[0]
                except TypeError:
                    db.execute("INSERT INTO games (UserID) VALUES (?)", ctx.author.id)
                    db.commit()
                    now_room = None
                room = room[0]
                if now_room:
                    await ctx.send("이미 어딘가에서 매칭을 기다리고 있거나 게임을 진행하고 있어요!")
                    return
                if room[2] is not None:
                    try:
                        people_in = str(room[2]).split(",")
                    except AttributeError:
                        people_in = []
                else:
                    people_in = []
                if not people_in:
                    await ctx.send(f"{a2}번 방에 입장했어요! 이 방에서 매칭을 기다리는 중이에요")
                    db.execute("UPDATE rooms SET people_in = ? WHERE room_number = ?", str(ctx.author.id), a2)
                    db.execute("UPDATE games SET room_number = ? WHERE UserID = ?", a2, ctx.author.id)
                    db.commit()
                    return
                if len(people_in) >= 2:
                    await ctx.send("그 방은 이미 다 차서 입장할 수 없어요!")
                    return
                else:
                    db.execute("UPDATE rooms SET people_in = ? WHERE room_number = ?",
                               f"{people_in[0]},{ctx.author.id}", a2)
                    db.execute("UPDATE games SET room_number = ? WHERE UserID = ?", a2, ctx.author.id)
                    db.commit()
                    your_mmr = db.record("SELECT omok_mmr FROM games WHERE UserID = ?", ctx.author.id)
                    your_mmr = your_mmr[0]
                    opponent_mmr = db.record("SELECT omok_mmr FROM games WHERE UserID = ?", int(people_in[0]))
                    opponent_mmr = opponent_mmr[0]
                    mmr_ckdl = math.fabs(your_mmr - opponent_mmr)
                    if fabs(your_mmr - opponent_mmr) > 200:
                        await ctx.send("현재 이 방에 있는 사람과 실력 차이가 많이 나는 것 같아요! 다른 방에 들어가 주세요")
                        return
                    else:
                        if your_mmr >= opponent_mmr:
                            black = int(people_in[0])
                            white = ctx.author.id
                        else:
                            black = ctx.author.id
                            white = int(people_in[0])

                        black = self.bot.get_user(black)
                        white = self.bot.get_user(white)

                        omok_board = "┏　ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯ\n　１┏┳┳┳┳┳┳┳┳┳┳┳┳┳┓\n　２┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　３┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                                     "　４┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　５┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　６┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　７┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                                     "　８┣╋╋╋╋╋╋○╋╋╋╋╋╋┫\n　９┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１０┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１１┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                                     "１２┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１３┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１４┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１５┗┴┴┴┴┴┴┴┴┴┴┴┴┴┛ "
                        now_omok = [[0 for i in range(15)] for j in range(15)]
                        now_omok[7][7] = 1
                        embed = Embed(color=0xbf88f8, title=f"{a2} 번 방에서의 대국")
                        embed.add_field(name="흑돌 대국자", value=str(black))
                        embed.add_field(name="백돌 대국자", value=str(white))
                        embed.add_field(name="최근 착수자", value=str(black))
                        embed.add_field(name="현재 오목판", value=omok_board)
                        embed.add_field(name="최근 착수된 자리", value="첫 턴이므로 없음", inline=False)
                        await black.send(embed=embed)
                        await white.send(embed=embed)
                        await black.send("매칭이 잡혔어요! 자동으로 천원점에 첫 수를 두었어요.")
                        await self.ask_omok(white, black, white, now_omok, a2, a3, a3, mmr_ckdl, 1)
            else:
                await ctx.send("오목 방번호는 4500에서 9999만 이용 가능해요!")
                return
        elif a1 == "목록":
            rooms = db.records(
                "SELECT room_number, people_in FROM rooms WHERE people_in IS NOT NULL AND 6 <= room_type <= 8 ORDER BY RANDOM() LIMIT 20")
            tjfaud = "`방 번호: 그 안에 있는 사람` 의 형식이에요\n안에 사람이 한 명만 있는 방에 입장이 가능합니다\n"
            for room in rooms:
                u = ''
                for person in room[1].split(","):
                    u += f"{self.bot.get_user(int(person))} "
                tjfaud += f"{str(room[0])}: {u}"
                tjfaud += "\n"
            if not tjfaud:
                await ctx.send("현재 매칭을 기다리고 있는 오목 방이 없어요!")
                return
            await ctx.send(tjfaud)
            # for i in range(3, 100): 남는방
            #     db.execute("INSERT INTO rooms (room_number, room_type) VALUES (?, 0)", i)
            #     db.commit()
            # for i in range(100, 1000): 끝말
            #     db.execute("INSERT INTO rooms (room_number, room_type) VALUES (?, 4)", i)
            #     db.commit()
            # for i in range(1000, 4500): 랜덤
            #     db.execute("INSERT INTO rooms (room_number, room_type) VALUES (?, 5)", i)
            #     db.commit()
            # for i in range(4500, 6000): 자유룰_오목
            #     db.execute("INSERT INTO rooms (room_number, room_type) VALUES (?, 6)", i)
            #     db.commit()
            # for i in range(6000, 8000): 오목룰_오목
            #     db.execute("INSERT INTO rooms (room_number, room_type) VALUES (?, 7)", i)
            #     db.commit()
            # for i in range(8000, 10000): 렌주룰_오목
            #     db.execute("INSERT INTO rooms (room_number, room_type) VALUES (?, 8)", i)
            #     db.commit()
            # for i in range(10000, 11500): 오프닝룰_오목
            #     db.execute("INSERT INTO rooms (room_number, room_type) VALUES (?, 9)", i)
            #     db.commit()
        elif a1 == "점수":
            mmr = db.record("SELECT omok_mmr FROM games WHERE UserID = ?", ctx.author.id)
            mmr = mmr[0]
            await ctx.send(embed=Embed(color=0xffd6fe, title=f"{ctx.author.display_name}님의 오목 점수", description=mmr))
        elif a1 in ["퇴장", "매칭취소"]:
            now_room = db.record("SELECT room_number FROM games WHERE userID = ?", ctx.author.id)
            try:
                now_room = now_room[0]
            except TypeError:
                return
            if 4500 <= now_room < 10000:
                await ctx.send(f"{now_room}번 방에서 빠져나왔어요.")
                db.execute("UPDATE games SET room_number = NULL WHERE userID = ?", ctx.author.id)
                db.commit()
        elif a1 == "자동매칭":
            automatch = db.record("SELECT user_setting FROM games WHERE UserID = ?", ctx.author.id)[0]
            if automatch & 8 == 0:
                await ctx.send("잠겨 있는 기능이에요! `커뉴야 뀨 구매 오목 자동 매칭`으로 기능을 먼저 해금하신 후 이용해 주세요")
                return
            if a4 in ["자유룰", "오목룰"]:
                r = 4001
                t = 6
            elif a4 in ["학교룰", "우리들의 룰"]:
                r = 4002
                t = 7
            elif a4 == "렌주룰":
                r = 4003
                t = 8
            elif not a4:
                r = 4004
                t = 69
            else:
                await ctx.send("존재하지 않는 규칙명이에요!")
                return
            auto = db.record("SELECT people_in FROM rooms WHERE room_number = ?", r)[0]
            if auto:
                empty_room = db.record(
                    "SELECT room_number FROM rooms WHERE room_type = ? AND people_in is NULL ORDER BY RANDOM() LIMIT 1",
                    t)[0]
                db.execute("UPDATE rooms SET people_in = ? WHERE room_number = ?", f"{auto},{ctx.author.id}",
                           empty_room)
                db.execute("UPDATE games SET room_number = ? WHERE UserID = ?", empty_room, int(auto))
                db.execute("UPDATE games SET room_number = ? WHERE UserID = ?", empty_room, ctx.author.id)
                db.commit()
                your_mmr = db.record("SELECT omok_mmr FROM games WHERE UserID = ?", ctx.author.id)
                your_mmr = your_mmr[0]
                opponent_mmr = db.record("SELECT omok_mmr FROM games WHERE UserID = ?", int(auto))
                opponent_mmr = opponent_mmr[0]
                mmr_ckdl = math.fabs(your_mmr - opponent_mmr)
                if your_mmr >= opponent_mmr:
                    black = int(auto)
                    white = ctx.author.id
                else:
                    black = ctx.author.id
                    white = int(auto)
                black = self.bot.get_user(black)
                white = self.bot.get_user(white)
                omok_board = "┏　ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯ\n　１┏┳┳┳┳┳┳┳┳┳┳┳┳┳┓\n　２┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　３┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                             "　４┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　５┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　６┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　７┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                             "　８┣╋╋╋╋╋╋○╋╋╋╋╋╋┫\n　９┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１０┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１１┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                             "１２┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１３┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１４┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１５┗┻┻┻┻┻┻┻┻┻┻┻┻┻┛ "
                now_omok = [[0 for i in range(15)] for j in range(15)]
                now_omok[7][7] = 1
                embed = Embed(color=0xbf88f8, title=f"{a2} 번 방에서의 대국")
                embed.add_field(name="흑돌 대국자", value=str(black))
                embed.add_field(name="백돌 대국자", value=str(white))
                embed.add_field(name="최근 착수자", value=str(black))
                embed.add_field(name="현재 오목판", value=omok_board)
                embed.add_field(name="최근 착수된 자리", value="첫 턴이므로 없음", inline=False)
                await black.send(embed=embed)
                await white.send(embed=embed)
                await black.send("매칭이 잡혔어요! 자동으로 천원점에 첫 수를 두었어요.")
                await self.ask_omok(white, black, white, now_omok, a2, a3, a3, mmr_ckdl, 1)
                return
            pending = db.records("SELECT room_number, people_in FROM rooms WHERE room_type = ?", t)
            for p in pending:
                if p[1]:
                    m = p[1].split(",")
                    if len(m) == 1:
                        break
            else:
                await ctx.send("자동매칭을 잡았어요! 누군가 당신이 원한 룰에 해당하는 방에 들어오거나 같은 룰로 자동매칭을 잡으면 매칭이 잡혀요.")
                db.execute("UPDATE games SET room_number = ? WHERE UserID = ?", r, ctx.author.id)
                db.execute("UPDATE rooms SET People_in = ? WHERE room_number = ?", ctx.author.id, r)
                db.commit()
                return
            auto = int(m[0])
            empty_room = db.record(
                "SELECT room_number FROM rooms WHERE room_type = ? AND people_in is NULL ORDER BY RANDOM() LIMIT 1", t)[
                0]
            db.execute("UPDATE rooms SET people_in = ? WHERE room_number = ?", f"{auto},{ctx.author.id}")
            db.execute("UPDATE games SET room_number = ? WHERE UserID = ?", empty_room, ctx.author.id)
            db.commit()
            your_mmr = db.record("SELECT omok_mmr FROM games WHERE UserID = ?", ctx.author.id)
            your_mmr = your_mmr[0]
            opponent_mmr = db.record("SELECT omok_mmr FROM games WHERE UserID = ?", int(auto))
            opponent_mmr = opponent_mmr[0]
            mmr_ckdl = math.fabs(your_mmr - opponent_mmr)
            if your_mmr >= opponent_mmr:
                black = int(auto)
                white = ctx.author.id
            else:
                black = ctx.author.id
                white = int(auto)
            black = self.bot.get_user(black)
            white = self.bot.get_user(white)
            omok_board = "┏　ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯ\n　１┏┳┳┳┳┳┳┳┳┳┳┳┳┳┓\n　２┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　３┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                         "　４┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　５┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　６┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n　７┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                         "　８┣╋╋╋╋╋╋○╋╋╋╋╋╋┫\n　９┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１０┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１１┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n" \
                         "１２┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１３┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１４┣╋╋╋╋╋╋╋╋╋╋╋╋╋┫\n１５┗┻┻┻┻┻┻┻┻┻┻┻┻┻┛ "
            now_omok = [[0 for i in range(15)] for j in range(15)]
            now_omok[7][7] = 1
            embed = Embed(color=0xbf88f8, title=f"{a2} 번 방에서의 대국")
            embed.add_field(name="흑돌 대국자", value=str(black))
            embed.add_field(name="백돌 대국자", value=str(white))
            embed.add_field(name="최근 착수자", value=str(black))
            embed.add_field(name="현재 오목판", value=omok_board)
            embed.add_field(name="최근 착수된 자리", value="첫 턴이므로 없음", inline=False)
            await black.send(embed=embed)
            await white.send(embed=embed)
            await black.send("매칭이 잡혔어요! 자동으로 천원점에 첫 수를 두었어요.")
            await self.ask_omok(white, black, white, now_omok, a2, a3, a3, mmr_ckdl, 1)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("omok")
            # await sleep(1)
            # now_omok = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
            # print(self.draw_board(now_omok))
            # self.check_banned(1, now_omok, 7, 5)


def setup(bot):
    bot.add_cog(Omok(bot))
