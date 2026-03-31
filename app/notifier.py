from __future__ import annotations

import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx

from .crud import tasks_for_notification
from .db import session_scope
from .models import Task

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")
APP_NAME = os.getenv("APP_NAME", "Backlog System")
NOTIFY_COOLDOWN_HOURS = int(os.getenv("NOTIFY_COOLDOWN_HOURS", "12"))


def should_skip(task: Task, now: datetime) -> bool:
    if task.last_notified_at is None:
        return False
    return now - task.last_notified_at < timedelta(hours=NOTIFY_COOLDOWN_HOURS)


def build_message(task: Task, today) -> str:
    if task.task_type.value == "daily":
        context = "Tarefa diária pendente"
    elif task.due_date and task.due_date < today:
        context = "Tarefa atrasada"
    else:
        context = "Tarefa agendada para hoje"

    due_text = task.due_date.strftime("%d/%m/%Y") if task.due_date else "Sem data"
    alert_text = task.alert_time.strftime("%H:%M") if task.alert_time else "Sem horário"
    description = task.description or "Sem descrição"

    return (
        f"📌 {context}\n"
        f"Sistema: {APP_NAME}\n"
        f"Título: {task.title}\n"
        f"Descrição: {description}\n"
        f"Tipo: {task.task_type.value}\n"
        f"Prioridade: {task.priority.value}\n"
        f"Status: {task.status.value}\n"
        f"Data: {due_text}\n"
        f"Horário: {alert_text}"
    )


def send_webhook(message: str) -> None:
    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL não configurada")

    with httpx.Client(timeout=20.0) as client:
        response = client.post(WEBHOOK_URL, json={"text": message})
        response.raise_for_status()


def run() -> None:
    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    today = now.date()
    current_time = now.time().replace(second=0, microsecond=0)

    with session_scope() as db:
        tasks = tasks_for_notification(db, today, current_time)
        for task in tasks:
            if should_skip(task, now):
                continue
            message = build_message(task, today)
            send_webhook(message)
            task.last_notified_at = now.replace(tzinfo=None)
            db.add(task)


if __name__ == "__main__":
    run()
