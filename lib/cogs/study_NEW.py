from discord.ext.commands import Cog
from ..db import db
import uuid
from datetime import datetime, timedelta
from discord import app_commands, ui, SelectOption, Interaction, Embed, ButtonStyle
from typing import Optional
from types import GeneratorType
from collections import deque, defaultdict
from asyncio import sleep

root = {}
study_sessions = {}


def bootstrap(f, stack=[]):
    def wrappedfunc(*args, **kwargs):
        if stack:
            return f(*args, **kwargs)
        else:
            to = f(*args, **kwargs)
            while True:
                if type(to) is GeneratorType:
                    stack.append(to)
                    to = next(to)
                else:
                    stack.pop()
                    if not stack:
                        break
                    to = stack[-1].send(to)
            return to

    return wrappedfunc


class Node:
    def __init__(self, name, node_type, parent, created_by, _id=None):
        if _id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = _id
        self.name = name
        self.node_type = node_type
        self.created_by = created_by
        self.children = []
        if parent is None:
            self._parent = None
            self.path = 'root'
            self.name = 'root'
        elif parent:
            self.parent = parent
        if _id is None and self.__class__ is Node:
            self.insert_to_db()

    def insert_to_db(self):
        db.execute("INSERT OR IGNORE INTO NODE_DATA (id, name, node_type, parent, created_by)"
                   "VALUES (?, ?, ?, ?, ?)", self.id, self.name, self.node_type, None, self.created_by)
        db.commit()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent
        self.path = f"{parent.path} > {self.name}"
        self._parent.children.append(self)


class CategoryNode(Node):
    def __init__(self, name, node_type, parent, created_by, _id=None):
        super().__init__(name, node_type, parent, created_by, _id)
        if _id is None:
            self.insert_to_db()

    def insert_to_db(self):
        db.execute("INSERT OR IGNORE INTO NODE_DATA (id, name, node_type, parent, created_by)"
                   "VALUES (?, ?, ?, ?, ?)", self.id, self.name,
                   self.node_type, self._parent.id, self.created_by)
        db.commit()


class TaskNode(Node):
    def __init__(self, name, node_type, parent, created_by, deadline, amount_of_task, _id=None):
        super().__init__(name, node_type, parent, created_by, _id)
        self.deadline = deadline
        self.amount_of_task = amount_of_task
        self.progress = 0
        if _id is None:
            self.insert_to_db()

    def insert_to_db(self):
        db.execute("INSERT OR IGNORE INTO NODE_DATA (id, name, node_type, parent, created_by,"
                   "deadline, amount_of_task, progress) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   self.id, self.name, self.node_type, self._parent.id,
                   self.created_by, self.deadline, self.amount_of_task, self.progress)
        db.commit()


class RecordNode(Node):
    def __init__(self, name, node_type, parent, created_by, _id=None):
        super().__init__(name, node_type, parent, created_by, _id)
        self.started_at = datetime.now()
        self.finished_at = None
        self.grade_got = 0
        self.grade_full = 0

    def insert_to_db(self, timestamps):
        db.execute("INSERT OR IGNORE INTO NODE_DATA (id, name, node_type, parent, created_by,"
                   "started_at, finished_at, grade_got, grade_full) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   self.id, self.name, self.node_type, self._parent.id,
                   self.created_by, self.started_at, self.finished_at, self.grade_got, self.grade_full)
        for start, end in timestamps:
            record_id = str(uuid.uuid4())
            db.execute("INSERT INTO STUDY_INTERVALS (id, record_id, start_ts, end_ts) VALUES (?, ?, ?, ?)",
                    record_id, self.id, start, end)
        db.commit()


def find_node_by_name(name, uid):
    @bootstrap
    def dfs(cur, parent):
        nonlocal ret
        if cur.name == name:
            ret.append((cur.path, cur))
        for nxt in cur.children:
            if nxt == parent:
                continue
            yield dfs(nxt, cur)
        yield

    ret = []
    dfs(root[uid], None)
    return ret


class ParentSelectView(ui.View):
    def __init__(self, parents, child_name, user_id):
        super().__init__(timeout=60)
        self.parents = parents
        self.child_name = child_name
        self.user_id = user_id

        options = [
            SelectOption(
                label=node_obj.name,
                description=node_obj.path,
                value=str(i)
            )
            for i, (path, node_obj) in enumerate(parents)
        ]

        self.select = ui.Select(
            placeholder="Choose one node to continue.",
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: Interaction):
        idx = int(self.select.values[0])
        _, parent_node = self.parents[idx]

        new_node = CategoryNode(
            name=self.child_name,
            node_type=0,
            parent=parent_node,
            created_by=self.user_id
        )

        await interaction.response.send_message(
            f"Created **{self.child_name}** under **{parent_node.name}**.\n(Path: `{new_node.path}`)",
        )

        self.stop()


class TaskParentSelectView(ui.View):
    def __init__(self, parents, child_name, deadline, amount_of_task, user_id):
        super().__init__(timeout=60)
        self.parents = parents
        self.child_name = child_name
        self.deadline = deadline
        self.amount_of_task = amount_of_task
        self.user_id = user_id

        options = [
            SelectOption(
                label=node_obj.name,
                description=node_obj.path,
                value=str(i)
            )
            for i, (path, node_obj) in enumerate(parents)
        ]

        self.select = ui.Select(
            placeholder="Choose one node to attach the task to.",
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: Interaction):
        idx = int(self.select.values[0])
        _, parent_node = self.parents[idx]

        # Parse the deadline string into a datetime object
        try:
            deadline_dt = datetime.fromisoformat(self.deadline)
        except ValueError:
            await interaction.response.send_message(
                "Invalid deadline format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)."
            )
            return

        new_node = TaskNode(
            name=self.child_name,
            node_type=1,
            parent=parent_node,
            created_by=self.user_id,
            deadline=deadline_dt,
            amount_of_task=self.amount_of_task
        )

        await interaction.response.send_message(
            f"Created **{self.child_name}** under **{parent_node.name}**.\n(Path: `{new_node.path}`)\n"
            f"Deadline: `{new_node.deadline}`\nAmount of Tasks: `{new_node.amount_of_task}`"
        )

        self.stop()


class StudyParentSelectView(ui.View):
    def __init__(self, parents, study_name, user_id):
        super().__init__(timeout=60)
        self.parents = parents
        self.child_name = study_name
        self.user_id = user_id

        options = [
            SelectOption(
                label=node_obj.name,
                description=node_obj.path,
                value=str(i)
            )
            for i, (path, node_obj) in enumerate(parents)
        ]

        self.select = ui.Select(
            placeholder="Choose one node to continue.",
            min_values=1,
            max_values=1,
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: Interaction):
        idx = int(self.select.values[0])
        _, parent_node = self.parents[idx]
        self.stop()
        await process_study(interaction, parent_node, self.child_name, self.user_id)


async def process_study(interaction, parent_node, study_name, user_id):
    new_node = RecordNode(study_name, 2, parent_node, user_id)
    view = ButtonsWhileStudying(user=interaction.user)
    rest_view = ButtonsWhilePausing(user=interaction.user)
    embed = Embed(color=0xffd6fe, title='Study Info')
    embed.add_field(name='Study Name', value=study_name, inline=False)
    embed.add_field(name='Node Path', value=new_node.path, inline=False)
    embed.add_field(name='Started At', value=new_node.started_at, inline=False)
    embed.add_field(name='Time Elapsed', value='0h 0m 0s', inline=False)
    embed.add_field(name='Time Studied', value='0h 0m 0s', inline=False)
    study_sessions[user_id] = {"node": new_node, "intervals": [(new_node.started_at, None)], "pausing": False}
    await interaction.response.send_message(embed=embed, view=view)
    await sleep(5)
    while user_id in study_sessions:
        elapsed = (datetime.now() - study_sessions[user_id]["node"].started_at).seconds
        studied = 0
        for t1, t2 in study_sessions[user_id]["intervals"]:
            studied += (t2 - t1).seconds if t2 else (datetime.now() - t1).seconds
        embed = Embed(color=0xffd6fe, title='Study Info')
        embed.add_field(name='Study Name', value=study_name, inline=False)
        embed.add_field(name='Node Path', value=new_node.path, inline=False)
        embed.add_field(name='Started At', value=new_node.started_at, inline=False)
        embed.add_field(name='Time Elapsed', value=to_visual_elapsed(elapsed), inline=False)
        embed.add_field(name='Time Studied', value=to_visual_elapsed(studied), inline=False)
        if study_sessions[user_id]["pausing"]:
            await interaction.edit_original_response(embed=embed, view=rest_view)
        else:
            await interaction.edit_original_response(embed=embed, view=view)
        await sleep(5)


class ButtonsWhileStudying(ui.View):
    def __init__(self, user):
        super().__init__(timeout=86400.0)
        self.user = user

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if self.user:
            if interaction.user != self.user:
                await interaction.response.send_message('This session is not yours...', ephemeral=True)
                return False
        return True

    @ui.button(label='Pause', style=ButtonStyle.green)
    async def button_pause(self, interaction, button):
        await pause_study(interaction)

    @ui.button(label='Stop (record results)', style=ButtonStyle.red)
    async def button_stop1(self, interaction, button):
        await stop_study(interaction, True)

    @ui.button(label='Stop (do not record results)', style=ButtonStyle.red)
    async def button_stop2(self, interaction, button):
        await stop_study(interaction, False)

    @ui.button(label='Abort', style=ButtonStyle.red)
    async def button_stop3(self, interaction, button):
        await force_stop_study(interaction)


class ButtonsWhilePausing(ui.View):
    def __init__(self, user):
        super().__init__(timeout=86400.0)
        self.user = user

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if self.user:
            if interaction.user != self.user:
                await interaction.response.send_message('This session is not yours...', ephemeral=True)
                return False
        return True

    @ui.button(label='Resume', style=ButtonStyle.green)
    async def button_resume(self, interaction, button):
        await resume_study(interaction)

    @ui.button(label='Stop (record results)', style=ButtonStyle.red)
    async def button_stop1(self, interaction, button):
        await stop_study(interaction, True)

    @ui.button(label='Stop (do not record results)', style=ButtonStyle.red)
    async def button_stop2(self, interaction, button):
        await stop_study(interaction, False)

    @ui.button(label='Abort', style=ButtonStyle.red)
    async def button_stop3(self, interaction, button):
        await force_stop_study(interaction)


def to_visual_elapsed(elapsed):
    visual_elapsed = ''
    visual_elapsed += f'{elapsed // 3600}h '
    visual_elapsed += f'{elapsed % 3600 // 60}m '
    visual_elapsed += f'{elapsed % 60}s'
    return visual_elapsed


async def pause_study(interaction: Interaction):
    uid = interaction.user.id
    session = study_sessions.get(uid)
    if not session:
        await interaction.response.send_message('No active study session to pause.')
        return

    intervals = session["intervals"]

    # intervals의 마지막 구간을 닫아서 (start, pause_ts) 꼴로 만든다
    start_ts, _ = intervals[-1]
    pause_ts = datetime.now()
    intervals[-1] = (start_ts, pause_ts)

    await interaction.response.send_message('Study session paused.', ephemeral=True)
    study_sessions[uid]["pausing"] = True


async def resume_study(interaction: Interaction):
    uid = interaction.user.id
    session = study_sessions.get(uid)
    if not session:
        await interaction.response.send_message('No active study session to resume.')
        return

    intervals = session["intervals"]
    intervals.append((datetime.now(), None))
    await interaction.response.send_message('Study session resumed.', ephemeral=True)
    study_sessions[uid]["pausing"] = False


async def stop_study(interaction: Interaction, record_results: bool):
    uid = interaction.user.id
    session = study_sessions.get(uid)
    if not session:
        await interaction.response.send_message('No active study session to stop.')
        return

    # intervals 가져오기
    intervals = session["intervals"]
    node = session["node"]

    # 아직 열려 있는 마지막 구간이 있다면 닫는다
    if intervals and intervals[-1][1] is None:
        start_ts, _ = intervals[-1]
        intervals[-1] = (start_ts, datetime.now())

    # 전체 세션 범위(RecordNode)
    node.finished_at = datetime.now()

    # 실제 공부 시간(초) 계산
    actual_time = timedelta(seconds=0)
    for (s, e) in intervals:
        actual_time += (e - s)

    # 성적 입력 처리 (옵션)
    if record_results:
        await interaction.channel.send("Please send your scores in **a/b** form. (`q` to cancel)")

        def check_author(msg):
            return msg.author.id == uid and msg.channel.id == interaction.channel.id

        try:
            msg = await interaction.client.wait_for("message", timeout=120, check=check_author)
            txt = msg.content.strip().lower()
            if txt != 'q' and '/' in txt:
                got_str, full_str = txt.split('/')
                node.grade_got = int(got_str)
                node.grade_full = int(full_str)
        except:
            pass

    # 메모리 정리
    study_sessions[uid]["node"].insert_to_db(study_sessions[uid]["intervals"])
    del study_sessions[uid]

    # 결과 보여주기
    actual_time = actual_time.total_seconds()
    embed = Embed(title="Study Session Finished", color=0xffd6fe)
    embed.add_field(name="Started at", value=node.started_at, inline=False)
    embed.add_field(name="Finished at", value=node.finished_at, inline=False)
    embed.add_field(name="Actual Study Time", value=to_visual_elapsed(actual_time), inline=False)

    if node.grade_full and node.grade_full > 0:
        embed.add_field(
            name="Grade",
            value=f"{node.grade_got}/{node.grade_full} = {round(node.grade_got / node.grade_full * 100, 2)}%",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


async def force_stop_study(interaction):
    uid = interaction.user.id
    del study_sessions[uid]["node"]
    del study_sessions[uid]
    await interaction.response.send_message('Aborted study session.')


class StudyNew(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='build_category_node',
        description=(
                'Makes a new category node. '
                'If parent_name is not specified, the node will be created under root.'
        )
    )
    async def build_category_node(self, interaction: Interaction, parent_name: Optional[str], child_name: str):
        if not parent_name:
            if interaction.user.id not in root:
                root[interaction.user.id] = Node('', -1, None, interaction.user.id)
            parents_tmp = [('root', root[interaction.user.id])]
        else:
            parents_tmp = find_node_by_name(parent_name, interaction.user.id)

        parents = []
        for path, p in parents_tmp:
            # Check if a child with the same name already exists under this parent
            if any(child.name == child_name for child in p.children):
                continue
            parents.append((path, p))

        if not parents:
            await interaction.response.send_message(
                f'Parent node "{parent_name}" not found or already has a child named "{child_name}".', ephemeral=True)
            return
        elif len(parents) == 1:
            _, parent_node = parents[0]
            new_node = CategoryNode(child_name, 0, parent_node, interaction.user.id)
            await interaction.response.send_message(
                f"Created **{child_name}** under **{parent_node.name}**.\n(Path: `{new_node.path}`)"
            )
        else:
            view = ParentSelectView(parents, child_name, interaction.user.id)
            await interaction.response.send_message(
                f"There are {len(parents)} nodes with the name \"{parent_name}\". Please select the parent node:",
                view=view
            )

    @app_commands.command(
        name='build_task_node',
        description='Makes a new task node. Requires a deadline and the number of tasks.'
    )
    async def build_task_node(
            self,
            interaction: Interaction,
            parent_name: str,
            task_name: str,
            deadline: Optional[str] = '9999-12-31T23:59:59',
            amount_of_task: Optional[int] = 1
    ):
        """
        Creates a new TaskNode.

        Parameters:
        - parent_name: (Optional) The name of the parent node. If not provided, defaults to root.
        - child_name: The name of the task node to create.
        - deadline: The deadline for the task in ISO format (e.g., 2024-12-31T23:59:59).
        - amount_of_task: The number of tasks.
        """
        parents_tmp = find_node_by_name(parent_name, interaction.user.id)

        # Filter out parents that already have a child with the same name
        parents = []
        for path, p in parents_tmp:
            if any(child.name == task_name for child in p.children):
                continue
            parents.append((path, p))

        if not parents:
            await interaction.response.send_message(
                f'Parent node "{parent_name}" not found or already has a child named "{task_name}".',
                ephemeral=True
            )
            return
        elif len(parents) == 1:
            _, parent_node = parents[0]
            # Parse the deadline string into a datetime object
            try:
                deadline_dt = datetime.fromisoformat(deadline)
            except ValueError:
                await interaction.response.send_message(
                    "Invalid deadline format. Please use ISO format (YYYY-MM-DDTHH:MM:SS).",
                    ephemeral=True
                )
                return

            new_node = TaskNode(
                name=task_name,
                node_type=1,  # Assuming 1 represents TaskNode
                parent=parent_node,
                created_by=interaction.user.id,
                deadline=deadline_dt,
                amount_of_task=amount_of_task
            )
            await interaction.response.send_message(
                f"Created **{task_name}** under **{parent_node.name}**.\n(Path: `{new_node.path}`)\n"
                f"Deadline: `{new_node.deadline}`\nAmount of Tasks: `{new_node.amount_of_task}`"
            )
        else:
            view = TaskParentSelectView(parents, task_name, deadline, amount_of_task, interaction.user.id)
            await interaction.response.send_message(
                f"There are {len(parents)} nodes with the name \"{parent_name}\". Please select the parent node:",
                view=view
            )

    @app_commands.command(
        name='start_study',
        description='Begins a study session. '
                    'A record node will be created after the session.')
    async def start_study_command(self, interaction: Interaction, parent_name: str, study_name: str):
        if interaction.user.id in study_sessions:
            await interaction.response.send_message('You are already in a study session.', ephemeral=True)
            return
        parents_tmp = find_node_by_name(parent_name, interaction.user.id)
        parents = []
        for path, p in parents_tmp:
            if any(child.name == study_name for child in p.children):
                continue
            parents.append((path, p))

        if not parents:
            await interaction.response.send_message(
                f'Parent node "{parent_name}" not found or already has a child named "{study_name}".',
                ephemeral=True
            )
            return
        elif len(parents) == 1:
            await process_study(interaction, parents[0][1], study_name, interaction.user.id)
        else:
            view = StudyParentSelectView(parents, study_name, interaction.user.id)
            await interaction.response.send_message(
                f"There are {len(parents)} nodes with the name \"{parent_name}\". Please select the parent node:",
                view=view
            )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print('25W god_life')


async def setup(bot):
    await bot.add_cog(StudyNew(bot))
    print('NEW study cog ready')
    node_data = db.records("SELECT * FROM NODE_DATA")
    g = defaultdict(list)
    for (node_id, name, node_type, parent, created_at, created_by, deadline, amount_of_task, progress,
         started_at, finished_at, grade_got, grade_full) in node_data:
        if parent is None:
            root[created_by] = Node(name, node_type, None, created_by, node_id)
        elif amount_of_task is not None:
            g[parent].append(TaskNode(name, node_type, '', created_by, deadline, amount_of_task, node_id))
        elif progress is not None:
            g[parent].append(RecordNode(name, node_type, '', created_by, node_id))
        else:
            g[parent].append(CategoryNode(name, node_type, '', created_by, node_id))
    for r in root:
        q = deque([root[r]])
        while q:
            cur = q.popleft()
            for nxt in g.get(cur.id, []):
                q.append(nxt)
                nxt.parent = cur
