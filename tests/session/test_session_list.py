import pytest
import conftest
from session import conftest as package_conftest
from queue_manager.session.models import Session as PackageModel
from bs4 import BeautifulSoup

TESTED_URL = package_conftest.ITEM_LIST_URL


# TODO Finish current session button
@pytest.mark.django_db
def test_basic_content(client, get_supervisors):
    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Sessions" in content
    assert "Start new session" in content
    assert "Code" in content
    assert "Is active" in content
    assert "Started at" in content
    assert "Started by" in content
    assert "Finished at" in content
    assert "Finished by" in content


@pytest.mark.django_db
def test_all_items_are_displayed_without_active(client, get_supervisors):
    default_items_in_db = list(PackageModel.objects.all())

    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()

    # All items from database are dispayed
    for item in default_items_in_db:
        assert item.code in content
        is_active = 'Yes' if item.is_active else 'No'
        assert is_active in content
        assert item.started_at.strftime("%-H:%M") in content
        strted_by = f'{item.started_by.first_name} {item.started_by.last_name}'
        assert strted_by in content
        assert item.finished_at.strftime("%-H:%M") in content
        finished_by = (f'{item.finished_by.first_name}' +
                       f' {item.finished_by.last_name}')
        assert finished_by in content
        assert "bg-primary" not in content

    # No redundant items are displayed
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (len(default_items_in_db)
                         + package_conftest.ITEM_LIST_HEADER_ROWS)


@pytest.mark.django_db
def test_all_items_are_displayed_with_active(client, get_supervisors):
    client.force_login(get_supervisors[0])
    response = client.post(package_conftest.ITEM_START_URL, None, follow=True)
    response_content = response.content.decode()
    assert package_conftest.START_OK_MESSAGE in response_content

    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert 'Yes' in content
    assert "None" not in content
    assert "bg-primary" in content


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
