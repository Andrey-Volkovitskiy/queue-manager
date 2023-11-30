import pytest
from tests import conftest
from . import conftest as package_conftest
from queue_manager.user.models import Operator as PackageModel
from copy import deepcopy
from tests.fixtures.test_users_additional import TEST_ITEMS

TESTED_URL_PATTERN = "/operator/manage/<pk>/pass_change/"
SUCCESS_URL = package_conftest.ITEM_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, get_supervisors):
    client.force_login(get_supervisors[0])
    INITIAL_ITEM = deepcopy(TEST_ITEMS[0])
    pre_response = client.post(
        package_conftest.ITEM_CREATE_URL,
        INITIAL_ITEM,
        follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)

    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert INITIAL_ITEM['username'] in content
    assert "New password" in content
    assert "New password confirmation" in content
    assert "Save" in content


@pytest.mark.django_db
def test_successfuly_updated(client, get_supervisors):
    client.force_login(get_supervisors[0])
    INITIAL_ITEM = deepcopy(TEST_ITEMS[0])
    UPDATED_ITEM = deepcopy(TEST_ITEMS[0])
    new_password = TEST_ITEMS[1]['password1']
    UPDATED_ITEM['new_password1'] = new_password
    UPDATED_ITEM['new_password2'] = new_password
    pre_response = client.post(
        package_conftest.ITEM_CREATE_URL,
        INITIAL_ITEM,
        follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)

    response = client.post(TESTED_URL, UPDATED_ITEM, follow=True)
    response_content = response.content.decode()
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    assert "The operator was successfully updated" in response_content

    db_user = PackageModel.objects.order_by('id').last()
    assert db_user.check_password(new_password)


@pytest.mark.django_db
def test_with_anonymous_user(client):
    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)
    response = client.get(TESTED_URL, follow=True)
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == conftest.LOGIN_URL


@pytest.mark.django_db
def test_with_incorrect_user(client, get_operators):
    client.force_login(get_operators[0])
    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)
    response = client.get(TESTED_URL)
    assert response.status_code == 403
