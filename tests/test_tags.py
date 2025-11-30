from src.models import Tag


def test_get_tags_list(client, db_session, auth_headers):
    db_session.query(Tag).delete()
    db_session.commit()
    t1 = Tag(userId=1, movieId=1, tag="tag1", timestamp=10)
    t2 = Tag(userId=2, movieId=2, tag="tag2", timestamp=20)
    db_session.add_all([t1, t2])
    db_session.commit()
    headers = auth_headers()
    response = client.get("/tags", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    tags = {item["tag"] for item in data}
    assert tags == {"tag1", "tag2"}


def test_get_tag_item_found(client, db_session, auth_headers):
    db_session.query(Tag).delete()
    db_session.commit()
    tag = Tag(userId=1, movieId=1, tag="tagx", timestamp=100)
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    tag_id = tag.id
    headers = auth_headers()
    response = client.get(f"/tags/{tag_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tag_id
    assert data["tag"] == "tagx"
    assert data["userId"] == 1


def test_get_tag_item_not_found(client, db_session, auth_headers):
    db_session.query(Tag).delete()
    db_session.commit()
    headers = auth_headers()
    response = client.get("/tags/999", headers=headers)
    assert response.status_code == 404


def test_post_tag_creates_new(client, db_session, auth_headers):
    db_session.query(Tag).delete()
    db_session.commit()
    payload = {"userId": 3, "movieId": 3, "tag": "newtag", "timestamp": 300}
    headers = auth_headers()
    response = client.post("/tags", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == 3
    assert data["movieId"] == 3
    assert data["tag"] == "newtag"
    db_tag = db_session.query(Tag).filter(Tag.userId == 3, Tag.movieId == 3).first()
    assert db_tag is not None
    assert db_tag.tag == "newtag"


def test_put_tag_updates(client, db_session, auth_headers):
    db_session.query(Tag).delete()
    db_session.commit()
    tag = Tag(userId=4, movieId=4, tag="old", timestamp=400)
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    tag_id = tag.id
    payload = {"tag": "updated", "timestamp": 500}
    headers = auth_headers()
    response = client.put(f"/tags/{tag_id}", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tag_id
    assert data["tag"] == "updated"
    assert data["timestamp"] == 500
    db_tag = db_session.query(Tag).filter(Tag.id == tag_id).first()
    db_session.refresh(db_tag)
    assert db_tag.tag == "updated"
    assert db_tag.timestamp == 500


def test_delete_tag_removes(client, db_session, auth_headers):
    db_session.query(Tag).delete()
    db_session.commit()
    tag = Tag(userId=5, movieId=5, tag="del", timestamp=600)
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    tag_id = tag.id
    headers = auth_headers()
    response = client.delete(f"/tags/{tag_id}", headers=headers)
    assert response.status_code == 204
    db_tag = db_session.query(Tag).filter(Tag.id == tag_id).first()
    assert db_tag is None
    response_get = client.get(f"/tags/{tag_id}", headers=headers)
    assert response_get.status_code == 404
