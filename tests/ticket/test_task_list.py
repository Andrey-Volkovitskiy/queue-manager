import pytest
import conftest
from ticket import conftest as package_conftest
from queue_manager.ticket.models import Ticket as PackageModel
from queue_manager.session.models import Session
from bs4 import BeautifulSoup

TESTED_URL = package_conftest.ITEM_LIST_URL


@pytest.mark.django_db
def test_basic_content(client, get_supervisors):
    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Tickets" in content
    assert "Code" in content
    assert "Only tickets from the current session are displayed" in content


@pytest.mark.django_db
def test_all_items_are_displayed(client, get_supervisors):
    expected_items_from_db = list(PackageModel.objects.filter(
        session=Session.objects.get_current_session()
    ))

    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()

    # All items from database are dispayed
    for item in expected_items_from_db:
        assert item.code in content

    # No redundant items are displayed
    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.find_all('tr')
    assert len(rows) == (len(expected_items_from_db)
                         + package_conftest.ITEM_LIST_HEADER_ROWS)


@pytest.mark.django_db
def test_with_anonymous_user(client):
    response = client.get(TESTED_URL, follow=True)
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == conftest.LOGIN_URL


@pytest.mark.django_db
def test_with_operator_user(client, get_operators):
    client.force_login(get_operators[0])
    response = client.get(TESTED_URL)
    assert response.status_code == 200
