from fastapi.testclient import TestClient

from app import crud, models
from app.db import get_db, SessionLocal
from app.main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_task_lifecycle():
    # cria nova tarefa
    payload = {
        "title": "pytest task",
        "description": "task created by pytest",
        "task_type": "backlog",
        "status": "pending",
        "priority": "medium",
        "due_date": "",  # opcional
        "alert_time": "",
        "is_recurring": "false",
    }

    response = client.post("/tasks/new", data=payload, allow_redirects=False)
    assert response.status_code == 303

    # busca na base para obter id
    db = SessionLocal()
    try:
        tasks = crud.list_tasks(db, status="pending", task_type="backlog")
        assert len(tasks) > 0
        task = next((t for t in tasks if t.title == "pytest task"), None)
        assert task is not None
        task_id = task.id

        # marcar como concluida
        response = client.post(f"/tasks/{task_id}/done", allow_redirects=False)
        assert response.status_code == 303

        task_done = crud.get_task(db, task_id)
        assert task_done is not None
        assert task_done.status == models.TaskStatus.done

        # apagar tarefa
        response = client.post(f"/tasks/{task_id}/delete", allow_redirects=False)
        assert response.status_code == 303

        assert crud.get_task(db, task_id) is None

    finally:
        db.close()
