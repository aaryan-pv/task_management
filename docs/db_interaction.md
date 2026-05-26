# Database Interaction Flow

This document explains how PostgreSQL, Redis and Celery interact together.

---

# Complete Interaction Flow

```mermaid
flowchart TB

    Client --> API

    API --> RedisCheck

    RedisCheck -->|Cache Hit| ReturnResponse

    RedisCheck -->|Cache Miss| PostgreSQL

    PostgreSQL --> SaveRedis

    SaveRedis --> ReturnResponse

    API --> QueueTask

    QueueTask --> RedisBroker

    RedisBroker --> CeleryWorker

    CeleryWorker --> PostgreSQL
```

---

# PostgreSQL Responsibilities

PostgreSQL is the source of truth.

Stores:
- users
- tasks
- assignments
- task states

---

# Redis Responsibilities

Redis used for:

---

## 1. Caching

Stores:
- task details
- user task lists

### Cache Keys

```text
task:{task_id}

tasks:user:{user_id}
```

### TTL

```text
300 seconds
```

---

## 2. Celery Broker

Redis also acts as:

```text
message queue
```

Stores celery tasks until worker consumes them.

---

# Celery Responsibilities

Celery handles:
- async processing
- retries
- idempotent execution

---

# Celery Task Flow

```mermaid
sequenceDiagram

    participant API
    participant Redis
    participant CeleryWorker
    participant PostgreSQL

    API->>Redis: Push Task

    CeleryWorker->>Redis: Consume Task

    CeleryWorker->>PostgreSQL: Process DB Work

    PostgreSQL-->>CeleryWorker: Success
```

---

# Cache Invalidation Flow

```mermaid
flowchart LR

    UpdateTask --> UpdatePostgreSQL

    UpdatePostgreSQL --> DeleteRedisCache

    DeleteRedisCache --> NextRead

    NextRead --> FetchFreshDBData

    FetchFreshDBData --> RepopulateRedis
```

---

# Graceful Fallback

If Redis fails:

```text
API automatically falls back to PostgreSQL
```

This prevents API downtime.

---

# Why This Architecture

Benefits:
- faster reads
- scalable background jobs
- reduced DB load
- async processing
- production-grade separation