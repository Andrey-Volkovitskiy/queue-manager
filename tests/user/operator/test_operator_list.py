import pytest
from tests import conftest
from . import conftest as package_conftest
from queue_manager.user.models import Operator as PackageModel
from queue_manager.task.models import Task
from bs4 import BeautifulSoup

TESTED_URL = package_conftest.ITEM_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, get_supervisors):
    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Operators" in content
    assert "Create new operator" in content
    assert "Full name" in content
    assert "Username" in content
    assert "Can serve tasks" in content


@pytest.mark.django_db
def test_all_items_are_displayed(client, get_supervisors):
    default_items_in_db = list(PackageModel.objects.all())

    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()

    # All items from database are dispayed
    for item in default_items_in_db:
        assert item.first_name in content
        assert item.last_name in content
        assert item.username in content

    # No redundant items are displayed
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (len(default_items_in_db)
                         + package_conftest.ITEM_LIST_HEADER_ROWS)


@pytest.mark.django_db
def test_inactive_item_doesnt_shown(client, get_supervisors, get_operators):
    active_item = get_operators[1]
    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert active_item.username in content

    inactive_item = get_operators[1]
    inactive_item.is_active = False
    inactive_item.save()
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert active_item.username not in content


@pytest.mark.django_db
def test_with_related_tasks(client, get_supervisors):
    default_items_in_db = list(PackageModel.objects.all())
    item_with_tasks = default_items_in_db[0]
    expected_task = Task.objects.first()
    unexpected_tasks = Task.objects.all().exclude(id=expected_task.id)
    item_with_tasks.task_set.set((expected_task, ))

    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()

    assert expected_task.name in content
    for unexpected_task in unexpected_tasks:
        assert unexpected_task.name not in content
    assert '= No one =' in content


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
