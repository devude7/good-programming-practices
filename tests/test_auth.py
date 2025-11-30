from src.models import User
from src.main import hash_password
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def create_user(db_session: Session, username: str, password: str, roles: list[str]) -> User:
    u = User(
        username=username,
        password_hash=hash_password(password),
        roles=",".join(roles),
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


def get_token(client: TestClient, username: str, password: str) -> str:
    response = client.post("/login", json={"username": username, "password": password})
    assert response.status_code == 200
    data = response.json()
    return data["access_token"]


def test_login_success(client, db_session):
    db_session.query(User).delete()
    db_session.commit()
    create_user(db_session, "admin", "secret", ["ROLE_ADMIN"])
    response = client.post("/login", json={"username": "admin", "password": "secret"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, db_session):
    db_session.query(User).delete()
    db_session.commit()
    create_user(db_session, "user", "password", ["ROLE_USER"])
    response = client.post("/login", json={"username": "user", "password": "wrong"})
    assert response.status_code == 401


def test_create_user_as_admin(client, db_session):
    db_session.query(User).delete()
    db_session.commit()
    create_user(db_session, "admin", "secret", ["ROLE_ADMIN"])
    token = get_token(client, "admin", "secret")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"username": "newuser", "password": "pass", "roles": ["ROLE_USER"]}
    response = client.post("/users", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data
    db_user = db_session.query(User).filter(User.username == "newuser").first()
    assert db_user is not None
    assert db_user.roles == "ROLE_USER"


def test_create_user_without_admin_role_forbidden(client, db_session):
    db_session.query(User).delete()
    db_session.commit()
    create_user(db_session, "user", "password", ["ROLE_USER"])
    token = get_token(client, "user", "password")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"username": "another", "password": "pass", "roles": ["ROLE_USER"]}
    response = client.post("/users", json=payload, headers=headers)
    assert response.status_code == 403


def test_user_details_with_token(client, db_session):
    db_session.query(User).delete()
    db_session.commit()
    create_user(db_session, "user", "password", ["ROLE_USER"])
    token = get_token(client, "user", "password")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/user_details", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user"
    assert "roles" in data
    assert "ROLE_USER" in data["roles"]


def test_user_details_without_token(client, db_session):
    db_session.query(User).delete()
    db_session.commit()
    response = client.get("/user_details")
    assert response.status_code in (401, 403)
