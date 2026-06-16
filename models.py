from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    id: Optional[int] = None
    chat_id: int = 0
    title: str = ""
    description: str = ""
    category: int = 1
    scheduled_at: Optional[datetime] = None
    completed: bool = False
    reminded: bool = False
    calendar_event_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Expense:
    id: Optional[int] = None
    chat_id: int = 0
    amount: float = 0.0
    currency: str = "UZS"
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ParsedVoice:
    type: str  # "task" | "expense" | "unknown"
    # task fields
    title: str = ""
    description: str = ""
    category: int = 1
    scheduled_at: Optional[datetime] = None
    # expense fields
    amount: float = 0.0
    currency: str = "UZS"
    expense_description: str = ""
    # raw transcript
    transcript: str = ""
