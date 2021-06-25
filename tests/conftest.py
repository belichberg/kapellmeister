import pytest
from fastapi.testclient import TestClient

from main import app


#
# @pytest.fixture
# def env() -> EnvYAML:
#     return EnvYAML(strict=False)


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        # set auth token for all queries
        c.headers[
            "Authorization"
        ] = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZWZhdWx0dXNlciIsImV4cCI6MTYyNTA2MDg0M30.9VQcrKorSlDXc70k5XopxBbMLPs7FgYGrX0gWVujdaI"
        #         # c.headers["Authorization"] = f"Bearer {env_['TEST_TOKEN']}"

        # yield test client
        yield c


# @pytest.fixture(autouse=True)
# def run_before_tests():
#
#     # before test
#     client.post("/api/v1/login/", data=dumps({"username": "defaultuser", "password": "defaultpassword"}))
#
#     yield  # run test
