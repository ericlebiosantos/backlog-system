from __future__ import annotations

import os
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .db import Base, engine, get_db

APP_NAME = os.getenv("APP_NAME", "Backlog System")
TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title=APP_NAME)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# =========================
# HOME
# =========================
@app.get("/")
def index(
    request: Request,
    status: str | None = None,
    task_type: str | None = None,
    db: Session = Depends(get_db),
):
    tasks = crud.list_tasks(db, status=status, task_type=task_type)
    now = datetime.now(ZoneInfo(TIMEZONE))

    pending_count = sum(1 for task in tasks if task.status == models.TaskStatus.pending)
    done_count = sum(1 for task in tasks if task.status == models.TaskStatus.done)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "tasks": tasks,
            "status_filter": status,
            "type_filter": task_type,
            "task_types": list(models.TaskType),
            "task_statuses": list(models.TaskStatus),
            "priorities": list(models.TaskPriority),
            "app_name": APP_NAME,
            "now": now,
            "pending_count": pending_count,
            "done_count": done_count,
        },
    )


# =========================
# CREATE
# =========================
@app.get("/tasks/new")
def new_task(request: Request):
    return templates.TemplateResponse(
        "create_task.html",
        {
            "request": request,
            "task_types": list(models.TaskType),
            "task_statuses": list(models.TaskStatus),
            "priorities": list(models.TaskPriority),
            "app_name": APP_NAME,
        },
    )


@app.post("/tasks/new")
def create_task(
    title: str = Form(...),
    description: str = Form(""),
    task_type: str = Form(...),
    status: str = Form(...),
    priority: str = Form(...),
    due_date: str = Form(""),
    alert_time: str = Form(""),
    is_recurring: bool = Form(False),
    db: Session = Depends(get_db),
):
    payload = schemas.TaskCreate(
        title=title,
        description=description or None,
        task_type=task_type,
        status=status,
        priority=priority,
        due_date=due_date or None,
        alert_time=alert_time or None,
        is_recurring=is_recurring,
    )

    crud.create_task(db, payload)

    return RedirectResponse(url="/", status_code=303)


# =========================
# EDIT
# =========================
@app.get("/tasks/{task_id}/edit")
def edit_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return templates.TemplateResponse(
        "edit_task.html",
        {
            "request": request,
            "task": task,
            "task_types": list(models.TaskType),
            "task_statuses": list(models.TaskStatus),
            "priorities": list(models.TaskPriority),
            "app_name": APP_NAME,
        },
    )


@app.post("/tasks/{task_id}/edit")
def update_task(
    task_id: int,
    title: str = Form(...),
    description: str = Form(""),
    task_type: str = Form(...),
    status: str = Form(...),
    priority: str = Form(...),
    due_date: str = Form(""),
    alert_time: str = Form(""),
    is_recurring: bool = Form(False),
    db: Session = Depends(get_db),
):
    task = crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    payload = schemas.TaskUpdate(
        title=title,
        description=description or None,
        task_type=task_type,
        status=status,
        priority=priority,
        due_date=due_date or None,
        alert_time=alert_time or None,
        is_recurring=is_recurring,
    )

    crud.update_task(db, task, payload)

    return RedirectResponse(url="/", status_code=303)


# =========================
# DONE
# =========================
@app.post("/tasks/{task_id}/done")
def done_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    crud.mark_done(db, task)

    return RedirectResponse(url="/", status_code=303)


# =========================
# DELETE
# =========================
@app.post("/tasks/{task_id}/delete")
def remove_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    crud.delete_task(db, task)

    return RedirectResponse(url="/", status_code=303)


# =========================
# FAVICON
# =========================
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


# =========================
# HEALTHCHECK
# =========================
@app.get("/health")
def health():
    return {"status": "ok", "app": APP_NAME}