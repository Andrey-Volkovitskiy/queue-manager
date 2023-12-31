from datetime import datetime, timezone
import pytest
from tests import conftest
from . import conftest as package_conftest
from queue_manager.session.models import Session as PackageModel
from html import escape

TESTED_URL = package_conftest.ITEM_FINISH_URL
SUCCESS_URL = '/supervisor/'
SUCCESS_MESSAGE = "The session was successfully finished"
ERROR_MESSAGE = ("The session can't be finished" +
                 " because there is no active session")


@pytest.mark.django_db
def test_finish_session_success(client, get_supervisors):
    client.force_login(get_supervisors[0])
    item_prestart_time = datetime.now(timezone.utc)
    response = client.post(package_conftest.ITEM_START_URL, None, follow=True)

    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Sessions" in content
    assert "Finish session" in content
    assert "Yes, finish" in content
    assert "No, don't finish" in content
    assert "Are you sure you want to finish current session" in content
    active_session = PackageModel.objects.last()
    assert active_session.code in content
    assert active_session.started_by.get_full_name() in content
    assert active_session.started_at >= item_prestart_time

    item_prefinish_time = datetime.now(timezone.utc)
    response = client.post(TESTED_URL, None, follow=True)
    assert (SUCCESS_URL, 302) in response.redirect_chain
    response_content = response.content.decode()
    assert escape(SUCCESS_MESSAGE) in response_content
    last_session = PackageModel.objects.get(code=active_session.code)
    assert last_session.finished_at >= item_prefinish_time
    assert last_session.finished_by == get_supervisors[0]


@pytest.mark.django_db
def test_finish_session_get_without_active_session_in_db(
            client, get_supervisors):
    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL, follow=True)
    assert (SUCCESS_URL, 302) in response.redirect_chain
    response_content = response.content.decode()
    assert escape(ERROR_MESSAGE) in response_content


@pytest.mark.django_db
def test_finish_session_post_without_active_session_in_db(
            client, get_supervisors):
    client.force_login(get_supervisors[0])
    response = client.post(TESTED_URL, None, follow=True)
    assert (SUCCESS_URL, 302) in response.redirect_chain
    response_content = response.content.decode()
    assert escape(ERROR_MESSAGE) in response_content


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
