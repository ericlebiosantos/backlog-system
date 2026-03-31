from __future__ import annotations

from datetime import datetime

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from .models import Task, TaskStatus, TaskType
from .schemas import TaskCreate, TaskUpdate


SORT_PRIORITY = {
    "high": 0,
    "medium": 1,
    "low": 2,
}


def create_task(db: Session, payload: TaskCreate) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, payload: TaskUpdate) -> Task:
    for key, value in payload.model_dump().items():
        setattr(task, key, value)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def list_tasks(db: Session, status: str | None = None, task_type: str | None = None) -> list[Task]:
    stmt = select(Task)
    if status:
        stmt = stmt.where(Task.status == status)
    if task_type:
        stmt = stmt.where(Task.task_type == task_type)
    stmt = stmt.order_by(asc(Task.due_date), asc(Task.created_at))
    tasks = list(db.execute(stmt).scalars().all())
    tasks.sort(key=lambda t: (t.due_date or datetime.max.date(), SORT_PRIORITY[t.priority.value], t.created_at))
    return tasks


def mark_done(db: Session, task: Task) -> Task:
    task.status = TaskStatus.done
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def tasks_for_notification(db: Session, today, now_time) -> list[Task]:
    stmt = select(Task).where(Task.status != TaskStatus.done)
    tasks = list(db.execute(stmt).scalars().all())
    result: list[Task] = []
    for task in tasks:
        should_notify = False

        if task.task_type == TaskType.daily:
            should_notify = True
        elif task.due_date:
            if task.due_date < today:
                should_notify = True
            elif task.due_date == today:
                if task.alert_time is None or task.alert_time <= now_time:
                    should_notify = True

        if should_notify:
            result.append(task)

    return result
