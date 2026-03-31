# Backlog System

Sistema simples de backlog com FastAPI, PostgreSQL, interface web e notificação por webhook.

## Funcionalidades
- Cadastro de tarefas de backlog, agendadas e diárias
- Edição, exclusão e conclusão de tarefas
- Filtro por status e tipo
- Notificação automática por webhook para tarefas do dia, atrasadas e diárias pendentes
- Deploy pronto para Railway

## Requisitos
- Python 3.11+
- PostgreSQL

## Como rodar localmente
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Variáveis de ambiente
Veja `.env.example`.

## Como executar o notificador localmente
```bash
python -m app.notifier
```

## Deploy no Railway
1. Crie um projeto no Railway
2. Conecte este repositório
3. Adicione um serviço PostgreSQL
4. Configure a variável `DATABASE_URL`
5. Configure a variável `WEBHOOK_URL`
6. Faça deploy do serviço web
7. Crie um segundo serviço/cron job para rodar:
   ```bash
   python -m app.notifier
   ```
8. Configure a frequência do cron job conforme desejar

## Estrutura
```text
app/
  main.py
  db.py
  models.py
  schemas.py
  crud.py
  notifier.py
  templates/
  static/
```
