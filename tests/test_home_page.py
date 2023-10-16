import pytest
from tests import conftest


TESTED_URL = conftest.HOME_URL


@pytest.mark.django_db
def test_basic_content(client):
    responce = client.get(TESTED_URL)
    content = responce.content.decode()
    assert responce.status_code == 200
    assert "Try the app" in content
