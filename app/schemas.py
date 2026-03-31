from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel, Field

from .models import TaskPriority, TaskStatus, TaskType


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    task_type: TaskType = TaskType.backlog
    status: TaskStatus = TaskStatus.pending
    priority: TaskPriority = TaskPriority.medium
    due_date: date | None = None
    alert_time: time | None = None
    is_recurring: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int

    class Config:
        from_attributes = True
