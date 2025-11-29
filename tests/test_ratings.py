from src.models import Rating


def test_get_ratings_list(client, db_session):
    db_session.query(Rating).delete()
    db_session.commit()
    r1 = Rating(userId=1, movieId=1, rating=4.5, timestamp=111)
    r2 = Rating(userId=2, movieId=2, rating=3.0, timestamp=222)
    db_session.add_all([r1, r2])
    db_session.commit()
    response = client.get("/ratings")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    ratings = {item["rating"] for item in data}
    assert ratings == {4.5, 3.0}


def test_get_rating_item_found(client, db_session):
    db_session.query(Rating).delete()
    db_session.commit()
    rating = Rating(userId=1, movieId=1, rating=5.0, timestamp=123)
    db_session.add(rating)
    db_session.commit()
    db_session.refresh(rating)
    rating_id = rating.id
    response = client.get(f"/ratings/{rating_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rating_id
    assert data["rating"] == 5.0
    assert data["userId"] == 1


def test_get_rating_item_not_found(client, db_session):
    db_session.query(Rating).delete()
    db_session.commit()
    response = client.get("/ratings/999")
    assert response.status_code == 404


def test_post_rating_creates_new(client, db_session):
    db_session.query(Rating).delete()
    db_session.commit()
    payload = {"userId": 3, "movieId": 3, "rating": 2.5, "timestamp": 333}
    response = client.post("/ratings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["userId"] == 3
    assert data["movieId"] == 3
    assert data["rating"] == 2.5
    db_rating = db_session.query(Rating).filter(Rating.userId == 3, Rating.movieId == 3).first()
    assert db_rating is not None
    assert db_rating.rating == 2.5


def test_put_rating_updates(client, db_session):
    db_session.query(Rating).delete()
    db_session.commit()
    rating = Rating(userId=4, movieId=4, rating=1.0, timestamp=100)
    db_session.add(rating)
    db_session.commit()
    db_session.refresh(rating)
    rating_id = rating.id
    payload = {"rating": 4.0, "timestamp": 200}
    response = client.put(f"/ratings/{rating_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rating_id
    assert data["rating"] == 4.0
    assert data["timestamp"] == 200
    db_rating = db_session.query(Rating).filter(Rating.id == rating_id).first()
    db_session.refresh(db_rating)
    assert db_rating.rating == 4.0
    assert db_rating.timestamp == 200


def test_delete_rating_removes(client, db_session):
    db_session.query(Rating).delete()
    db_session.commit()
    rating = Rating(userId=5, movieId=5, rating=3.5, timestamp=500)
    db_session.add(rating)
    db_session.commit()
    db_session.refresh(rating)
    rating_id = rating.id
    response = client.delete(f"/ratings/{rating_id}")
    assert response.status_code == 204
    db_rating = db_session.query(Rating).filter(Rating.id == rating_id).first()
    assert db_rating is None
    response_get = client.get(f"/ratings/{rating_id}")
    assert response_get.status_code == 404
