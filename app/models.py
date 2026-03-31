from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SqlEnum, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class TaskType(str, Enum):
    backlog = "backlog"
    scheduled = "scheduled"
    daily = "daily"


class TaskStatus(str, Enum):
    pending = "pending"
    doing = "doing"
    done = "done"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[TaskType] = mapped_column(SqlEnum(TaskType), default=TaskType.backlog, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(SqlEnum(TaskStatus), default=TaskStatus.pending, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(SqlEnum(TaskPriority), default=TaskPriority.medium, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    alert_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    is_recurring: Mapped[bool] = mapped_column(default=False, nullable=False)
    last_notified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
