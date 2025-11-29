from src.models import Link


def test_get_links_list(client, db_session):
    db_session.query(Link).delete()
    db_session.commit()
    l1 = Link(movieId=1, imdbId="imdb1", tmdbId="tmdb1")
    l2 = Link(movieId=2, imdbId="imdb2", tmdbId="tmdb2")
    db_session.add_all([l1, l2])
    db_session.commit()
    response = client.get("/links")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    ids = {item["movieId"] for item in data}
    assert ids == {1, 2}


def test_get_link_item_found(client, db_session):
    db_session.query(Link).delete()
    db_session.commit()
    link = Link(movieId=11, imdbId="imdb11", tmdbId="tmdb11")
    db_session.add(link)
    db_session.commit()
    response = client.get("/links/11")
    assert response.status_code == 200
    data = response.json()
    assert data["movieId"] == 11
    assert data["imdbId"] == "imdb11"
    assert data["tmdbId"] == "tmdb11"


def test_get_link_item_not_found(client, db_session):
    db_session.query(Link).delete()
    db_session.commit()
    response = client.get("/links/999")
    assert response.status_code == 404


def test_post_link_creates_new(client, db_session):
    db_session.query(Link).delete()
    db_session.commit()
    payload = {"movieId": 3, "imdbId": "imdb3", "tmdbId": "tmdb3"}
    response = client.post("/links", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["movieId"] == 3
    assert data["imdbId"] == "imdb3"
    assert data["tmdbId"] == "tmdb3"
    db_link = db_session.query(Link).filter(Link.movieId == 3).first()
    assert db_link is not None
    assert db_link.imdbId == "imdb3"
    assert db_link.tmdbId == "tmdb3"


def test_put_link_updates(client, db_session):
    db_session.query(Link).delete()
    db_session.commit()
    link = Link(movieId=4, imdbId="oldimdb", tmdbId="oldtmdb")
    db_session.add(link)
    db_session.commit()
    payload = {"imdbId": "newimdb", "tmdbId": "newtmdb"}
    response = client.put("/links/4", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["movieId"] == 4
    assert data["imdbId"] == "newimdb"
    assert data["tmdbId"] == "newtmdb"
    db_link = db_session.query(Link).filter(Link.movieId == 4).first()
    assert db_link.imdbId == "newimdb"
    assert db_link.tmdbId == "newtmdb"


def test_delete_link_removes(client, db_session):
    db_session.query(Link).delete()
    db_session.commit()
    link = Link(movieId=5, imdbId="delimdb", tmdbId="deltmdb")
    db_session.add(link)
    db_session.commit()
    response = client.delete("/links/5")
    assert response.status_code == 204
    db_link = db_session.query(Link).filter(Link.movieId == 5).first()
    assert db_link is None
    response_get = client.get("/links/5")
    assert response_get.status_code == 404
