import pytest
from tests import conftest
from . import conftest as package_conftest
from queue_manager.task.models import Task as PackageModel
from bs4 import BeautifulSoup
from django.utils import timezone

TESTED_URL = package_conftest.ITEM_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, get_supervisors):
    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Tasks" in content
    assert "Create new task" in content
    assert "Letter code" in content
    assert "Name" in content
    assert "Description" in content
    assert "Currently serviced by" in content
    assert "Can be serviced by" in content


@pytest.mark.django_db
def test_all_items_are_displayed(client, get_supervisors):
    default_items_in_db = list(PackageModel.objects.all())

    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()

    # All items from database are dispayed
    for item in default_items_in_db:
        assert str(item.id) in content
        assert item.name in content
        assert item.description in content

    # No redundant items are displayed
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (len(default_items_in_db)
                         + package_conftest.ITEM_LIST_HEADER_ROWS)


@pytest.mark.django_db
def test_softdeleted_item_not_shown(client, get_supervisors):
    soft_deleted_item = PackageModel.objects.create(
        name='Inactive name',
        description='Inactive description',
        letter_code='J',
        deleted_at=timezone.now(),
    )

    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()

    assert soft_deleted_item.name not in content
    assert soft_deleted_item.description not in content


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
