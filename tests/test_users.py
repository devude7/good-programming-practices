from src.models import User


def test_login_success(client, db_session, make_user):
    db_session.query(User).delete()
    db_session.commit()

    user = make_user(username="admin_login", password="secret", roles=["ROLE_ADMIN"])
    response = client.post("/login", json={"username": user.username, "password": "secret"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, db_session, make_user):
    db_session.query(User).delete()
    db_session.commit()

    user = make_user(username="user_login", password="password", roles=["ROLE_USER"])
    response = client.post("/login", json={"username": user.username, "password": "wrong"})
    assert response.status_code == 401


def test_create_user_as_admin(client, db_session, auth_headers):
    db_session.query(User).delete()
    db_session.commit()

    headers = auth_headers(username="admin_create", password="secret", roles=["ROLE_ADMIN"])
    payload = {"username": "newuser", "password": "pass", "roles": ["ROLE_USER"]}
    response = client.post("/users", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data
    assert data["roles"] == ["ROLE_USER"]

    db_user = db_session.query(User).filter(User.username == "newuser").first()
    assert db_user is not None
    assert db_user.roles == "ROLE_USER"


def test_create_user_without_admin_role_forbidden(client, db_session, auth_headers):
    db_session.query(User).delete()
    db_session.commit()

    headers = auth_headers(username="regular_user", password="password", roles=["ROLE_USER"])
    payload = {"username": "another", "password": "pass", "roles": ["ROLE_USER"]}
    response = client.post("/users", json=payload, headers=headers)
    assert response.status_code == 403


def test_user_details_with_token(client, db_session, auth_headers):
    db_session.query(User).delete()
    db_session.commit()

    headers = auth_headers(username="details_user", password="password", roles=["ROLE_USER"])
    response = client.get("/user_details", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "details_user"
    assert "roles" in data
    assert "ROLE_USER" in data["roles"]
    assert "user_id" in data


def test_user_details_without_token(client, db_session):
    db_session.query(User).delete()
    db_session.commit()

    response = client.get("/user_details")
    assert response.status_code in (401, 403)
