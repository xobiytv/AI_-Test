import aiosqlite
from datetime import datetime, date
from typing import List, Optional
from config import DATABASE_PATH
from models import Task, Expense


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                category INTEGER NOT NULL DEFAULT 1,
                scheduled_at TEXT,
                completed INTEGER DEFAULT 0,
                reminded INTEGER DEFAULT 0,
                calendar_event_id TEXT,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'UZS',
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()


async def save_task(task: Task) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO tasks (chat_id, title, description, category, scheduled_at,
               completed, reminded, calendar_event_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task.chat_id,
                task.title,
                task.description,
                task.category,
                task.scheduled_at.isoformat() if task.scheduled_at else None,
                int(task.completed),
                int(task.reminded),
                task.calendar_event_id,
                task.created_at.isoformat(),
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def save_expense(expense: Expense) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO expenses (chat_id, amount, currency, description, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                expense.chat_id,
                expense.amount,
                expense.currency,
                expense.description,
                expense.created_at.isoformat(),
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def get_today_tasks(chat_id: int) -> List[Task]:
    today = date.today().isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT * FROM tasks WHERE chat_id=? AND DATE(created_at)=?
               ORDER BY scheduled_at ASC""",
            (chat_id, today),
        )
        rows = await cursor.fetchall()
    return [_row_to_task(r) for r in rows]


async def get_today_expenses(chat_id: int) -> List[Expense]:
    today = date.today().isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT * FROM expenses WHERE chat_id=? AND DATE(created_at)=?
               ORDER BY created_at ASC""",
            (chat_id, today),
        )
        rows = await cursor.fetchall()
    return [_row_to_expense(r) for r in rows]


async def get_upcoming_unreminded_tasks() -> List[Task]:
    """Get tasks scheduled within next 15 minutes that haven't been reminded."""
    from datetime import timedelta
    now = datetime.now()
    soon = (now + timedelta(minutes=15)).isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT * FROM tasks WHERE reminded=0 AND completed=0
               AND scheduled_at IS NOT NULL
               AND scheduled_at <= ? AND scheduled_at >= ?""",
            (soon, now.isoformat()),
        )
        rows = await cursor.fetchall()
    return [_row_to_task(r) for r in rows]


async def mark_reminded(task_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE tasks SET reminded=1 WHERE id=?", (task_id,))
        await db.commit()


async def mark_completed(task_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
        await db.commit()


async def get_all_chat_ids() -> List[int]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT DISTINCT chat_id FROM tasks")
        rows = await cursor.fetchall()
        cursor2 = await db.execute("SELECT DISTINCT chat_id FROM expenses")
        rows2 = await cursor2.fetchall()
    ids = set(r[0] for r in rows) | set(r[0] for r in rows2)
    return list(ids)


def _row_to_task(row) -> Task:
    return Task(
        id=row["id"],
        chat_id=row["chat_id"],
        title=row["title"],
        description=row["description"],
        category=row["category"],
        scheduled_at=datetime.fromisoformat(row["scheduled_at"]) if row["scheduled_at"] else None,
        completed=bool(row["completed"]),
        reminded=bool(row["reminded"]),
        calendar_event_id=row["calendar_event_id"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def _row_to_expense(row) -> Expense:
    return Expense(
        id=row["id"],
        chat_id=row["chat_id"],
        amount=row["amount"],
        currency=row["currency"],
        description=row["description"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )
