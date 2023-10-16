import pytest
from tests import conftest
from . import conftest as package_conftest
from queue_manager.task.models import Task as PackageModel
from copy import deepcopy
from tests.fixtures.test_tasks_additional import TEST_ITEMS
from datetime import datetime, timezone

TESTED_URL = package_conftest.ITEM_CREATE_URL
SUCCESS_URL = package_conftest.ITEM_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, get_supervisors):
    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Create new task" in content
    assert "Name" in content
    assert "Description" in content
    assert "Letter code" in content
    assert "Create" in content


@pytest.mark.django_db
def test_successfuly_created(client, get_supervisors):
    count_default_items_in_db = PackageModel.objects.all().count()
    client.force_login(get_supervisors[0])
    CORRECT_ITEM = deepcopy(TEST_ITEMS[0])
    item_creation_time = datetime.now(timezone.utc)

    response = client.post(TESTED_URL, CORRECT_ITEM, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Is only one item added to the database?
    assert PackageModel.objects.all().count() == count_default_items_in_db + 1

    # Is the item added to the database?
    db_item = PackageModel.objects.last()
    assert db_item.name == CORRECT_ITEM['name']
    assert db_item.description == CORRECT_ITEM['description']
    assert db_item.letter_code == CORRECT_ITEM['letter_code']
    assert db_item.is_active is True
    time_difference = db_item.created_at - item_creation_time
    assert time_difference.total_seconds() < 1


@pytest.mark.django_db
def test_with_incorrect_existing_name(client, get_supervisors):
    count_default_items_in_db = PackageModel.objects.all().count()
    client.force_login(get_supervisors[0])
    CORRECT_ITEM = deepcopy(TEST_ITEMS[0])

    INCORRECT_ITEM_1 = deepcopy(TEST_ITEMS[1])
    INCORRECT_ITEM_1['name'] = (
        CORRECT_ITEM['name'][0].lower() + CORRECT_ITEM['name'][1:])

    INCORRECT_ITEM_2 = deepcopy(TEST_ITEMS[1])
    INCORRECT_ITEM_2['letter_code'] = CORRECT_ITEM['letter_code'].lower()

    response = client.post(TESTED_URL, CORRECT_ITEM)
    response = client.post(TESTED_URL, INCORRECT_ITEM_1, follow=True)

    # assert response.redirect_chain == []
    assert response.status_code == 200
    response_content = response.content.decode()
    assert "already exists." in response_content

    response = client.post(TESTED_URL, INCORRECT_ITEM_2, follow=True)

    assert response.redirect_chain == []
    assert response.status_code == 200
    response_content = response.content.decode()
    assert "already exists." in response_content

    # Is only one item added to the database?
    assert PackageModel.objects.all().count() == count_default_items_in_db + 1


@pytest.mark.django_db
def test_with_anonymous_user(client):
    response = client.get(TESTED_URL, follow=True)
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == conftest.LOGIN_URL


@pytest.mark.django_db
def test_with_incorrect_user(client, get_operators):
    client.force_login(get_operators[0])
    response = client.get(TESTED_URL)
    assert response.status_code == 403
