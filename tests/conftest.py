import os

# Ensure required env vars exist before pydantic Settings loads.
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:root@localhost:5433/task_tests_db")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_DB", "0")
from app.workers import task_worker
import fakeredis

# Patch redis_client BEFORE any service imports the module. cache_service uses
# `from app.core.redis import redis_client`, so swapping the attribute on
# app.core.redis here means the cache layer talks to fakeredis throughout.
import app.core.redis as redis_module

fake_redis_client = fakeredis.FakeRedis(decode_responses=True)
redis_module.redis_client = fake_redis_client

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, get_db
from app.core.celery_app import celery_app

from app.models.user import User
from app.models.task import Task

# cache_service may have already imported the original redis_client by name.
# Rebind it on the module so the tests definitely use fakeredis.
import app.services.cache_service as cache_service_module
cache_service_module.redis_client = fake_redis_client


TEST_DATABASE_URL = (
    "postgresql://postgres:root@localhost:5433/task_test_db"
)

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# Run Celery tasks in-process when invoked via .delay()/.apply_async().
# Tests that need to assert "delay was queued without running" patch
# `process_task_completion.delay` directly, which bypasses this.
celery_app.conf.task_always_eager = False
celery_app.conf.task_eager_propagates = True


def _seed_users():
    """Seed a deterministic set of users for the whole test session."""

    db = TestingSessionLocal()

    try:

        seed_data = [
            (1, "Test User 1", "user1@test.com", True),
            (2, "Test User 2", "user2@test.com", True),
            (3, "Inactive User", "user3@test.com", False),
        ]

        for user_id, username, email, is_active in seed_data:

            existing = db.query(User).filter(
                User.id == user_id
            ).first()

            if existing:

                # Keep is_active in sync if a previous run flipped it.
                if existing.is_active != is_active:
                    existing.is_active = is_active

                continue

            db.add(
                User(
                    id=user_id,
                    username=username,
                    email=email,
                    is_active=is_active
                )
            )

        db.commit()

    finally:

        db.close()


_seed_users()


@pytest.fixture(autouse=True)
def _reset_state():
    """Wipe tasks and flush fakeredis before each test for determinism."""

    db = TestingSessionLocal()

    try:
        db.query(Task).delete()
        db.commit()

    finally:
        db.close()

    fake_redis_client.flushall()

    yield


@pytest.fixture
def db_session():
    """Direct SQLAlchemy session for service-level assertions."""

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()

@pytest.fixture(autouse=True)
def override_worker_db(db_session):

    original_session_local = task_worker.SessionLocal

    task_worker.SessionLocal = lambda: db_session

    yield

    task_worker.SessionLocal = original_session_local

@pytest.fixture
def fake_redis():
    """Expose the fakeredis instance to tests that inspect cache state."""

    return fake_redis_client
