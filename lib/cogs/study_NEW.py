from discord.ext.commands import Cog
from ..db import db
import uuid
from datetime import datetime
from discord import app_commands, ui, SelectOption, Interaction
from typing import Optional
from types import GeneratorType


root = {}


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
    def __init__(self, name, node_type, parent, created_by):
        self.id = str(uuid.uuid4())
        self.name = name
        self.node_type = node_type
        self.parent = parent
        self.created_by = created_by
        self.children = []
        if not parent:
            self.path = 'root'
            self.name = 'root'
            db.execute("INSERT OR IGNORE INTO NODE_DATA (id, name, node_type, parent, created_by)"
                       "VALUES (?, ?, ?, ?, ?)", self.id, self.name, self.node_type, None, self.created_by)
        else:
            self.path = f"{parent.path} > {self.name}"
            self.parent.children.append(self)


class CategoryNode(Node):
    def __init__(self, name, node_type, parent, created_by):
        super().__init__(name, node_type, parent, created_by)
        db.execute("INSERT OR IGNORE INTO NODE_DATA (id, name, node_type, parent, created_by)"
                   "VALUES (?, ?, ?, ?, ?)", self.id, name, node_type, parent.id, created_by)
        db.commit()


class TaskNode(Node):
    def __init__(self, name, node_type, parent, created_by, deadline, amount_of_task):
        super().__init__(name, node_type, parent, created_by)
        self.deadline = deadline
        self.amount_of_task = amount_of_task
        self.progress = 0
        db.execute("INSERT OR IGNORE INTO NODE_DATA (id, name, node_type, parent, created_by,"
                   "deadline, amount_of_task, progress) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   self.id, name, node_type, parent.id, created_by, deadline, amount_of_task, self.progress)
        db.commit()


class RecordNode(Node):
    def __init__(self, name, node_type, parent, created_by):
        super().__init__(name, node_type, parent, created_by)
        self.started_at = datetime.now().isoformat()
        self.finished_at = None
        self.grade_got = 0
        self.grade_full = 0
        db.execute("INSERT OR IGNORE INTO NODE_DATA (id, name, node_type, parent, created_by,"
                   "started_at, finished_at, grade_got, grade_full) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   self.id, name, node_type, parent.id, created_by, self.started_at, self.finished_at,
                   self.grade_got, self.grade_full)
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
                description=node_obj.path[:50],
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

        new_node = Node(
            name=self.child_name,
            node_type=0,
            parent=parent_node,
            created_by=self.user_id
        )

        await interaction.response.send_message(
            f"Created **{self.child_name}** under **{parent_node.name}**.\n(Path: `{new_node.path}`)",
            ephemeral=True
        )

        self.stop()


class StudyNew(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='build_category_node', description='Makes a new category node.'
                                                                  'If parent_name is not specified, '
                                                                  'the node will be created under root.')
    async def build_category_node(self, interaction, parent_name: Optional[str], child_name: str):
        if not parent_name:
            if interaction.user.id not in root:
                root[interaction.user.id] = Node('', -1, None, interaction.user.id)
            parents = [('root', root[interaction.user.id])]
        else:
            parents = find_node_by_name(parent_name, interaction.user.id)
        if not parents:
            await interaction.response.send_message(f'parent node {parent_name} not found')
            return
        elif len(parents) == 1:
            _, parent_node = parents[0]
            new_node = CategoryNode(child_name, 0, parent_node, interaction.user.id)
            await interaction.response.send_message(
                f"Created **{child_name}** under **{parent_node.name}**.\n(Path: `{new_node.path}`)",
                ephemeral=True
            )
        else:
            view = ParentSelectView(parents, child_name, interaction.user.id)
            await interaction.response.send_message(
                f"There are {len(parents)} nodes with name {parent_name}",
                view=view,
                ephemeral=True
            )

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print('25W god_life')


async def setup(bot):
    await bot.add_cog(StudyNew(bot))
    print('NEW study cog ready')
