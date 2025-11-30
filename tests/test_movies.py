from src.models import Movie


def test_get_movies_list(client, db_session, auth_headers):
    db_session.query(Movie).delete()
    db_session.commit()
    m1 = Movie(movieId=1, title="Movie 1", genres="Action")
    m2 = Movie(movieId=2, title="Movie 2", genres="Comedy")
    db_session.add_all([m1, m2])
    db_session.commit()
    headers = auth_headers()
    response = client.get("/movies", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    ids = {item["movieId"] for item in data}
    assert ids == {1, 2}


def test_get_movie_item_found(client, db_session, auth_headers):
    db_session.query(Movie).delete()
    db_session.commit()
    movie = Movie(movieId=10, title="Movie X", genres="Drama")
    db_session.add(movie)
    db_session.commit()
    headers = auth_headers()
    response = client.get("/movies/10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["movieId"] == 10
    assert data["title"] == "Movie X"
    assert data["genres"] == "Drama"


def test_get_movie_item_not_found(client, db_session, auth_headers):
    db_session.query(Movie).delete()
    db_session.commit()
    headers = auth_headers()
    response = client.get("/movies/999", headers=headers)
    assert response.status_code == 404


def test_post_movie_creates_new(client, db_session, auth_headers):
    db_session.query(Movie).delete()
    db_session.commit()
    payload = {"movieId": 5, "title": "New Movie", "genres": "Sci-Fi"}
    headers = auth_headers()
    response = client.post("/movies", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["movieId"] == 5
    assert data["title"] == "New Movie"
    assert data["genres"] == "Sci-Fi"
    db_movie = db_session.query(Movie).filter(Movie.movieId == 5).first()
    assert db_movie is not None
    assert db_movie.title == "New Movie"
    assert db_movie.genres == "Sci-Fi"


def test_put_movie_updates(client, db_session, auth_headers):
    db_session.query(Movie).delete()
    db_session.commit()
    movie = Movie(movieId=7, title="Old", genres="OldGenre")
    db_session.add(movie)
    db_session.commit()
    payload = {"title": "Updated", "genres": "NewGenre"}
    headers = auth_headers()
    response = client.put("/movies/7", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["movieId"] == 7
    assert data["title"] == "Updated"
    assert data["genres"] == "NewGenre"
    db_movie = db_session.query(Movie).filter(Movie.movieId == 7).first()
    assert db_movie.title == "Updated"
    assert db_movie.genres == "NewGenre"


def test_delete_movie_removes(client, db_session, auth_headers):
    db_session.query(Movie).delete()
    db_session.commit()
    movie = Movie(movieId=8, title="ToDelete", genres="Genre")
    db_session.add(movie)
    db_session.commit()
    headers = auth_headers()
    response = client.delete("/movies/8", headers=headers)
    assert response.status_code == 204
    db_movie = db_session.query(Movie).filter(Movie.movieId == 8).first()
    assert db_movie is None
    response_get = client.get("/movies/8", headers=headers)
    assert response_get.status_code == 404
