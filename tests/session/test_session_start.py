from datetime import datetime, timezone
import pytest
import conftest
from session import conftest as package_conftest
from queue_manager.session.models import Session as PackageModel
from session.test_model import get_todays_date_str
from html import escape

TESTED_URL = package_conftest.ITEM_START_URL
SUCCESS_URL = package_conftest.ITEM_LIST_URL
SUCCESS_MESSAGE = "The session was successfully started"
ERROR_MESSAGE = ("The session can't be started" +
                 " because another active session exists")


@pytest.mark.django_db
def test_start_new_session_success(client, get_supervisors):
    client.force_login(get_supervisors[0])
    item_creation_time = datetime.now(timezone.utc)
    response = client.post(TESTED_URL, None, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert SUCCESS_MESSAGE in response_content
    new_session = PackageModel.objects.last()
    assert new_session.code == get_todays_date_str() + 'A'
    assert new_session.is_active is True
    time_difference = new_session.started_at - item_creation_time
    assert time_difference.total_seconds() <= 1
    assert new_session.started_by == get_supervisors[0]
    assert new_session.finished_at is None
    assert new_session.finished_by is None


@pytest.mark.django_db
def test_start_new_session_with_active_session_in_db(client, get_supervisors):
    client.force_login(get_supervisors[0])
    response = client.post(TESTED_URL, None, follow=True)
    item_creation_time = datetime.now(timezone.utc)

    response = client.post(TESTED_URL, None, follow=True)
    assert response.redirect_chain == [
        (SUCCESS_URL, 302)
    ]
    response_content = response.content.decode()
    assert escape(ERROR_MESSAGE) in response_content
    assert PackageModel.objects.filter(
        started_at__gte=item_creation_time).exists() is False


@pytest.mark.django_db
def test_with_anonymous_user(client):
    response = client.post(TESTED_URL, None, follow=True)
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split('?')[0] == conftest.LOGIN_URL


@pytest.mark.django_db
def test_with_incorrect_user(client, get_operators):
    client.force_login(get_operators[0])
    response = client.post(TESTED_URL, None, follow=True)
    assert response.status_code == 403
