import pytest
from tests.conftest import LOGIN_URL
from . import conftest as package_conftest

URL_PREFIX = package_conftest.ITEM_ENTER_URL


@pytest.mark.django_db
def test_supervisor_personal_basic_content(client, get_supervisors):
    correct_supervisor = get_supervisors[0]
    client.force_login(correct_supervisor)
    TESTED_URL = f"{URL_PREFIX}{correct_supervisor.id}/"

    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()

    assert "Supervisor dashboard" in content


@pytest.mark.django_db
def test_supervisor_personal_with_anonymous_user(client, get_supervisors):
    existing_supervisor = get_supervisors[0]
    TESTED_URL = f"{URL_PREFIX}{existing_supervisor.id}/"

    response = client.get(TESTED_URL, follow=True)
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == LOGIN_URL


@pytest.mark.django_db
def test_supervisor_enter_with_operator(client, get_operators,
                                        get_supervisors):
    existing_supervisor = get_supervisors[0]
    TESTED_URL = f"{URL_PREFIX}{existing_supervisor.id}/"

    incorrect_user = get_operators[0]
    client.force_login(incorrect_user)

    response = client.get(TESTED_URL, follow=True)
    assert response.status_code == 403


@pytest.mark.django_db
def test_supervisor_enter_with_another_supervisor(
        client,
        get_supervisors):
    correct_supervisor = get_supervisors[0]
    TESTED_URL = f"{URL_PREFIX}{correct_supervisor.id}/"

    incorrect_supervisor = get_supervisors[1]
    client.force_login(incorrect_supervisor)

    response = client.get(TESTED_URL, follow=True)
    assert response.status_code == 403
