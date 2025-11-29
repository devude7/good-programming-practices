def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data.get("hello") == "world"