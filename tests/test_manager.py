from json import dumps, loads

from fastapi.testclient import TestClient


def test_get_projects(client: TestClient):
    response = client.get("/api/v1/projects/")
    assert response.status_code == 200
    # assert response.json() == []


def test_set_project(client: TestClient):
    response = client.post(
        "/api/v1/projects/",
        json={"name": "project", "slug": "project", "description": "Some Project"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "name": "project",
        "slug": "project",
        "description": "Some Project",
        "channels": [],
    }


def test_set_channel(client: TestClient):
    response = client.post(
        "/api/v1/channels/",
        json={"name": "channel", "slug": "channel", "description": "Some Channel", "project_id": 2},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 3,
        "name": "channel",
        "slug": "channel",
        "description": "Some Channel",
        "project_id": 2,
    }


def test_delete_channel(client: TestClient):
    response = client.delete("/api/v1/channels/3/")

    assert response.status_code == 200
    assert response.json() == {
        "id": 3,
        "name": "channel",
        "slug": "channel",
        "description": "Some Channel",
        "project_id": 2,
    }


def test_delete_project(client: TestClient):
    response = client.delete("/api/v1/projects/2/")

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "name": "project",
        "slug": "project",
        "description": "Some Project",
        "channels": [],
    }


def test_get_containers(client: TestClient):
    response = client.get("/api/v1/proj/chan/", headers={"Authorization": "bvHEdYZG9nIQQyhLo3RMf0Q4G3CW4ttE110UznNW"})
    assert response.status_code == 200


def test_get_containers_unauthorized(client: TestClient):
    response = client.get("/api/v1/proj/chan/", headers={"Authorization": ""})
    assert response.status_code == 401


def test_set_container(client: TestClient):
    with open("tests/data/container.json") as f:
        data = loads(f.read())

    response = client.post(
        "/api/v1/proj/chan/", headers={"Authorization": "xwPjyiF2v4gFJJ9UEhXe8YhNrW9pMoawC8QW4s90"}, data=dumps(data)
    )
    assert response.status_code == 200


def test_set_container_read_only(client: TestClient):
    with open("tests/data/container.json") as f:
        data = loads(f.read())

    response = client.post(
        "/api/v1/proj/chan/", headers={"Authorization": "bvHEdYZG9nIQQyhLo3RMf0Q4G3CW4ttE110UznNW"}, data=dumps(data)
    )
    assert response.status_code == 403


def test_delete_container(client: TestClient):
    response = client.delete("/api/v1/proj/chan/some-container/")

    assert response.status_code == 200
