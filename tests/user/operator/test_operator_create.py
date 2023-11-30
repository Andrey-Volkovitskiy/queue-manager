import pytest
from tests import conftest
from . import conftest as package_conftest
from queue_manager.user.models import Operator as PackageModel
from queue_manager.task.models import Task
from copy import deepcopy
from tests.fixtures.test_users_additional import TEST_ITEMS
from datetime import datetime, timezone

TESTED_URL = package_conftest.ITEM_CREATE_URL
SUCCESS_URL = package_conftest.ITEM_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, get_supervisors):
    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Create new operator" in content
    assert "Password" in content
    assert "Password confirmation" in content
    assert "First name" in content
    assert "Last name" in content
    assert "Create" in content
    assert "Can serve tasks" in content


@pytest.mark.django_db(transaction=True)
def test_successfuly_created(client, get_supervisors):
    count_default_items_in_db = PackageModel.objects.all().count()
    client.force_login(get_supervisors[0])
    CORRECT_ITEM = deepcopy(TEST_ITEMS[0])
    item_creation_time = datetime.now(timezone.utc)

    response = client.post(TESTED_URL, CORRECT_ITEM, follow=True)
    response_content = response.content.decode()
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Is only one item added to the database?
    assert PackageModel.objects.all().count() == count_default_items_in_db + 1

    # Is the item added to the database?
    db_item = PackageModel.objects.order_by('id').last()
    assert db_item.first_name == CORRECT_ITEM['first_name']
    assert db_item.last_name == CORRECT_ITEM['last_name']
    assert db_item.username == CORRECT_ITEM['username']
    assert db_item.is_active is True
    time_difference = db_item.date_joined - item_creation_time
    assert time_difference.total_seconds() < 1

    # Is new item present in ListView?
    assert CORRECT_ITEM['username'] in response_content


@pytest.mark.django_db
def test_with_related_tasks(client, get_supervisors):
    client.force_login(get_supervisors[0])
    CORRECT_ITEM = deepcopy(TEST_ITEMS[0])
    expected_tasks = (
        Task.objects.order_by('id').first(),
        Task.objects.order_by('id').last()
    )
    CORRECT_ITEM['task_set'] = (
        expected_tasks[0].id,
        expected_tasks[1].id,
        )

    response = client.post(TESTED_URL, CORRECT_ITEM, follow=True)
    response_content = response.content.decode()
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    assert package_conftest.CREATE_OK_MESSAGE in response_content

    # Is the item added to the database?
    db_item = PackageModel.objects.order_by('id').last()
    assert db_item.task_set.order_by('id')[0].id == expected_tasks[0].id
    assert db_item.task_set.order_by('id')[1].id == expected_tasks[1].id


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
