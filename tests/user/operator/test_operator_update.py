import pytest
from tests import conftest
from . import conftest as package_conftest
from queue_manager.user.models import Operator as PackageModel
from copy import deepcopy
from tests.fixtures.test_users_additional import TEST_ITEMS

TESTED_URL_PATTERN = "/operator/manage/<pk>/update/"
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
    assert "Edit operator" in content
    assert "First name" in content
    assert "Last name" in content
    assert "Username" in content
    assert "Save" in content
    assert "Change password" in content
    assert "Delete" in content

    assert INITIAL_ITEM['first_name'] in content
    assert INITIAL_ITEM['last_name'] in content
    assert INITIAL_ITEM['username'] in content


@pytest.mark.django_db
def test_successfuly_updated(client, get_supervisors):
    count_default_items_in_db = PackageModel.objects.all().count()
    client.force_login(get_supervisors[0])
    INITIAL_ITEM = deepcopy(TEST_ITEMS[0])
    UPDATED_ITEM = deepcopy(TEST_ITEMS[1])
    pre_response = client.post(
        package_conftest.ITEM_CREATE_URL,
        INITIAL_ITEM,
        follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)

    response = client.post(TESTED_URL, UPDATED_ITEM, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert "The operator was successfully updated" in response_content

    # Is new item added to the database?
    assert PackageModel.objects.filter(
        username=UPDATED_ITEM['username']).exists()

    # Is old item removed from the database?
    with pytest.raises(PackageModel.DoesNotExist):
        PackageModel.objects.get(username=INITIAL_ITEM['username'])

    # Is number of items the same as before the update?
    assert PackageModel.objects.all().count() == count_default_items_in_db + 1


@pytest.mark.django_db
def test_with_incorrect_existing_name(client, get_supervisors):
    client.force_login(get_supervisors[0])
    INITIAL_ITEM = deepcopy(TEST_ITEMS[0])
    EXISTING_ITEM = deepcopy(TEST_ITEMS[1])

    pre_response1 = client.post(
        package_conftest.ITEM_CREATE_URL,
        EXISTING_ITEM,
        follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response1.content.decode()

    pre_response2 = client.post(
        package_conftest.ITEM_CREATE_URL,
        INITIAL_ITEM,
        follow=True)
    assert package_conftest.CREATE_OK_MESSAGE in pre_response2.content.decode()

    TESTED_URL = conftest.get_tested_url_for_max_id(
        TESTED_URL_PATTERN, PackageModel)

    ###
    ITEM_WITH_EXISTING_NAME = deepcopy(TEST_ITEMS[2])
    ITEM_WITH_EXISTING_NAME['username'] = EXISTING_ITEM['username']

    response = client.post(TESTED_URL, ITEM_WITH_EXISTING_NAME, follow=True)

    assert response.status_code == 200
    assert response.redirect_chain == []
    response_content = response.content.decode()
    assert ("already exists.") in response_content


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
