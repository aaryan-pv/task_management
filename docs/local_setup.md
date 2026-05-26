# Local Development Setup Guide

This guide explains how to fully set up the Task CRUD API project locally for development and testing.
 
# 1. Clone Repository

```bash
git clone <repo_url>
cd TASK-CRUD-API
```

---

# 2. Create Virtual Environment

## Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

 

# 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 4. PostgreSQL Setup

---

## Create Database

Open PostgreSQL / pgAdmin.

Run:

```sql
CREATE DATABASE task_db;
```

---

## Verify PostgreSQL Port

Default:

```text
5432
```

---

# 5. Environment Variables

Project already contains `.env` for reviewer convenience.

Example:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/task_db

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

DEBUG=True
APP_VERSION=1.0.0
```

---

# 6. Start Redis

Redis is used for:
- caching
- celery broker

---

## Start Redis Using Docker

```bash
docker run -d --name redis-container -p 6379:6379 redis:7
```

---

## Verify Redis Running

```bash
docker ps
```

You should see:

```text
redis-container
```

---

# 7. Verify Redis Connection

Install redis client:

```bash
pip install redis
```

---

## Test Redis

Create:

```python
# redis_test.py

import redis

client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

client.set("test", "working")

print(client.get("test"))
```

Run:

```bash
python redis_test.py
```

Expected:

```text
working
```

---

# 8. Start FastAPI Server

```bash
uvicorn app.main:app --reload
```

Expected:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

# 9. Open Swagger Docs

```text
http://127.0.0.1:8000/docs
```

Use Swagger to test all APIs.

---

# 10. Start Celery Worker

Celery processes background jobs.

---

## Windows

```bash
celery -A app.core.celery_worker.celery_app worker --pool=solo -l info
```

---

## Linux / Mac

```bash
celery -A app.core.celery_worker.celery_app worker -l info
```

---

# 11. Verify Celery Working

Update task status to:

```json
{
  "status": "completed"
}
```

Worker logs should show:

```text
Task completion processed successfully
```

---

# 12. Verify Redis Cache

---

## Open Redis CLI

```bash
docker exec -it redis-container redis-cli
```

---

## List Keys

```bash
KEYS *
```

Expected:

```text
task:1
tasks:user:1
```

---

# 13. Verify Cache Hit/Miss

Check FastAPI logs.

---

## First Request

Expected:

```text
Cache miss
Fetching from DB
```

---

## Second Request

Expected:

```text
Cache hit
Returning cached response
```

---

# 14. Verify Celery Queue

Trigger task completion.

Redis queue will temporarily store task messages.

Worker consumes them automatically.

---

# 15. Verify PostgreSQL Data

---

## Using pgAdmin

Open:

```text
Servers
  → PostgreSQL
    → Databases
      → task_db
        → Schemas
          → public
            → Tables
```

---

## View Table Data

Right click:

```text
Table → View/Edit Data → All Rows
```

---

# Common Development Commands

---

# Run FastAPI

```bash
uvicorn app.main:app --reload
```

---

# Run Celery

## Windows

```bash
celery -A app.core.celery_worker.celery_app worker --pool=solo -l info
```

## Linux/Mac

```bash
celery -A app.core.celery_worker.celery_app worker -l info
```

---

# Run Redis

```bash
docker start redis-container
```

---

# Stop Redis

```bash
docker stop redis-container
```

 

# Development Workflow

```mermaid
flowchart LR

    StartServer --> TestAPI

    TestAPI --> CheckRedis

    TestAPI --> CheckPostgreSQL

    UpdateTask --> TriggerCelery

    TriggerCelery --> WorkerLogs
```

---

# Recommended Testing Flow

1. Create users
2. Create tasks
3. Fetch tasks
4. Verify cache
5. Update task status
6. Verify celery execution
7. Verify DB changes
8. Test bulk APIs

---

# Useful URLs

| Service | URL |
|---|---|
| FastAPI | http://127.0.0.1:8000 |
| Swagger | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

---

# Production Concepts Practiced

- Layered Architecture
- Repository Pattern
- Service Layer
- Redis Caching
- Celery Workers
- Async Processing
- Optimistic Locking
- Concurrency Control
- State Machine Validation
- Bulk Operations
- Graceful Fallbacks
- Structured Logging