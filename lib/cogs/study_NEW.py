from discord.ext.commands import Cog
from ..db import db
import uuid
from datetime import datetime


class Node:
    def __init__(self, name, node_type, parent, created_by):
        self.id = str(uuid.uuid4())
        self.name = name
        self.node_type = node_type
        self.parent = parent
        self.parent.children.append(self)
        self.created_by = created_by


class CategoryNode(Node):
    def __init__(self, name, node_type, parent, created_by):
        super().__init__(name, node_type, parent, created_by)
        db.execute("INSERT OR IGNORE INTO NODE_DATA (id, name, node_type, parent, created_by)"
                   "VALUES (?, ?, ?, ?, ?)", self.id, name, node_type, parent, created_by)
        db.commit()


class TaskNode(Node):
    def __init__(self, name, node_type, parent, created_by, deadline, amount_of_task):
        super().__init__(name, node_type, parent, created_by)
        self.deadline = deadline
        self.amount_of_task = amount_of_task
        self.progress = 0
        db.execute("INSERT OR IGNORE INTO NODE_DATA (id, name, node_type, parent, created_by,"
                   "deadline, amount_of_task, progress) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   self.id, name, node_type, parent, created_by, deadline, amount_of_task, self.progress)
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
                   self.id, name, node_type, parent, created_by, self.started_at, self.finished_at,
                   self.grade_got, self.grade_full)
        db.commit()


class StudyNew(Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(StudyNew(bot))
    print('NEW study cog ready')
