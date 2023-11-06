import pytest
from tests.conftest import LOGIN_URL
from . import conftest as package_conftest

URL_PREFIX = package_conftest.ITEM_ENTER_URL


@pytest.mark.django_db
def test_operator_personal_basic_content(client, get_operators):
    correct_operator = get_operators[0]
    client.force_login(correct_operator)
    TESTED_URL = f"{URL_PREFIX}{correct_operator.id}/"

    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()

    assert "Operator dashboard" in content


@pytest.mark.django_db
def test_operator_personal_with_anonymous_user(client, get_operators):
    existing_operator = get_operators[0]
    TESTED_URL = f"{URL_PREFIX}{existing_operator.id}/"

    response = client.get(TESTED_URL, follow=True)
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == LOGIN_URL


@pytest.mark.django_db
def test_operator_enter_with_incorrect_operator(
        client,
        get_operators):
    correct_operator = get_operators[0]
    TESTED_URL = f"{URL_PREFIX}{correct_operator.id}/"

    incorrect_operator = get_operators[1]
    client.force_login(incorrect_operator)

    response = client.get(TESTED_URL, follow=True)
    assert response.status_code == 403


@pytest.mark.django_db
def test_operator_personal_with_supervisor(
            client, get_operators, get_supervisors):
    operator = get_operators[0]
    supervisor = get_supervisors[0]
    client.force_login(supervisor)
    TESTED_URL = f"{URL_PREFIX}{operator.id}/"

    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()

    assert "Operator dashboard" in content
