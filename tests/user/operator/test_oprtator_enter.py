import pytest
from tests.conftest import LOGIN_URL
from . import conftest as package_conftest

TESTED_URL = package_conftest.ITEM_ENTER_URL
NO_PERMISSION_URL = TESTED_URL + 'no_permission/'
SELECT_URL = TESTED_URL + 'select/'


@pytest.mark.django_db
def test_operator_enter_success(client, get_operators):
    correct_operator = get_operators[0]
    client.force_login(correct_operator)
    expected_url = f"{TESTED_URL}{correct_operator.id}/"

    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()

    assert response.redirect_chain == [
        (expected_url, 302)
    ]
    assert "Operator dashboard" in content


@pytest.mark.django_db
def test_operator_enter_with_anonymous_user(client):
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == NO_PERMISSION_URL
    assert "Sorry, you do not have the permission" in content
    assert f"{LOGIN_URL}?next={TESTED_URL}" in content


@pytest.mark.django_db
def test_operator_enter_with_supervisor(
            client, get_operators, get_supervisors):
    all_operator = get_operators
    supervisor = get_supervisors[0]
    client.force_login(supervisor)

    response = client.get(TESTED_URL, follow=True)
    assert supervisor.has_perm('user.pretend_operator')
    content = response.content.decode()
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == SELECT_URL

    for operator in all_operator:
        assert operator.first_name in content
        assert operator.last_name in content
        assert f'{TESTED_URL}{operator.id}' in content
