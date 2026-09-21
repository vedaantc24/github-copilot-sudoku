import pytest

from app import app


@pytest.fixture
def client():
    with app.test_client() as test_client:
        yield test_client
