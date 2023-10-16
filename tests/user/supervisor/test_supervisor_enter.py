import pytest
from tests.conftest import LOGIN_URL
from . import conftest as package_conftest

TESTED_URL = package_conftest.ITEM_ENTER_URL
NO_PERMISSION_URL = TESTED_URL + 'no_permission/'


@pytest.mark.django_db
def test_supervisor_enter_success(client, get_supervisors):
    correct_supervisor = get_supervisors[0]
    client.force_login(correct_supervisor)
    expected_url = f"{TESTED_URL}{correct_supervisor.id}/"

    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()

    assert response.redirect_chain == [
        (expected_url, 302)
    ]
    assert "Supervisor dashboard" in content


@pytest.mark.django_db
def test_supervisor_enter_with_anonymous_user(client):
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == NO_PERMISSION_URL
    assert "Sorry, you do not have the permission" in content
    assert f"{LOGIN_URL}?next={TESTED_URL}" in content


@pytest.mark.django_db
def test_supervisor_enter_with_operator(client, get_operators):
    incorrect_user = get_operators[0]
    client.force_login(incorrect_user)

    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == NO_PERMISSION_URL
    assert "Sorry, you do not have the permission" in content
    assert f"{LOGIN_URL}?next={TESTED_URL}" in content
