import pytest

HOME_URL = "/"
LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"


@pytest.fixture
def client():
    from django.test.client import Client
    return Client()
