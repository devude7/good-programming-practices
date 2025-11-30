import sys
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import src.utils.auth as auth_utils
from src.main import app, get_db, hash_password
from src.models import Base, User


SQLALCHEMY_DATABASE_URL = "sqlite://"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # kluczowe
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="session")
def TestingSessionLocal(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def override_dependency(TestingSessionLocal):
    def _get_test_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[auth_utils.get_db] = _get_test_db


@pytest.fixture
def db_session(TestingSessionLocal):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def make_user(db_session):
    def _create_user(username=None, password="password", roles=None):
        roles = roles or ["ROLE_USER"]
        user = User(
            username=username or f"user_{uuid4().hex[:6]}",
            password_hash=hash_password(password),
            roles=",".join(roles),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def auth_headers(client, make_user):
    def _make_headers(username=None, password="password", roles=None):
        user = make_user(username=username, password=password, roles=roles)
        response = client.post("/login", json={"username": user.username, "password": password})
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make_headers


@pytest.fixture(scope="session")
def client():
    return TestClient(app)
