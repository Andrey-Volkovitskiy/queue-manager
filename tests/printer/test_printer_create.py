import pytest
from . import conftest as package_conftest
from tests.session.conftest import ITEM_FINISH_URL as SESSION_FINISH_URL
from queue_manager.task.models import Task
from queue_manager.ticket.models import Ticket
from queue_manager.session.models import Session


TESTED_URL = package_conftest.ITEM_CREATE_URL
TASK_CODE_PREFIX = "task_code:"


@pytest.mark.django_db
def test_basic_content(client, get_supervisors):
    client.force_login(get_supervisors[0])
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Welcome dear client!" in content
    assert "Please select the purpose" in content
    expected_tasks = Task.objects.filter(is_active=True)
    for task in expected_tasks:
        assert task.name in content


@pytest.mark.django_db
def test_successfuly_created_with_C002_ticket(client):
    existing_tickets_count = Ticket.objects.all().count()
    chosen_task = Task.objects.filter(is_active=True).last()
    chosen_task_prefix = TASK_CODE_PREFIX + chosen_task.letter_code
    EXPECTED_CODE = "C002"

    response = client.post(TESTED_URL, {chosen_task_prefix: ''}, follow=True)
    content = response.content.decode()

    # Is only one item added to the database?
    assert Ticket.objects.all().count() == existing_tickets_count + 1

    # Is correct data added to db?
    created_ticket = Ticket.objects.last()
    assert created_ticket.session == Session.objects.get_current_session()
    assert created_ticket.task == chosen_task
    assert created_ticket.code == EXPECTED_CODE
    assert created_ticket.status_set.first().code == 'U'

    # Is received page correct?
    assert EXPECTED_CODE in content
    assert "Your ticket:" in content
    assert "you will be redirected" in content
    assert response.redirect_chain == [
        (f"/printer/{created_ticket.id}/", 302)
    ]


@pytest.mark.django_db
def test_successfuly_created_with_A001_ticket(client):
    chosen_task = Task.objects.filter(is_active=True).first()
    chosen_task_prefix = TASK_CODE_PREFIX + chosen_task.letter_code
    EXPECTED_CODE = "A001"

    response = client.post(TESTED_URL, {chosen_task_prefix: ''}, follow=True)
    content = response.content.decode()

    created_ticket = Ticket.objects.last()
    assert created_ticket.code == EXPECTED_CODE
    assert EXPECTED_CODE in content


@pytest.mark.django_db
def test_print_ticket_get_without_active_session(client, get_supervisors):
    client.force_login(get_supervisors[0])
    client.post(SESSION_FINISH_URL, None, follow=True)

    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert "Please wait until service begins" in content
    assert "Refresh" in content
    assert TESTED_URL in content


@pytest.mark.django_db
def test_print_ticket_post_without_active_session(client, get_supervisors):
    client.force_login(get_supervisors[0])
    client.post(SESSION_FINISH_URL, None, follow=True)
    chosen_task = Task.objects.filter(is_active=True).first()
    chosen_task_prefix = TASK_CODE_PREFIX + chosen_task.letter_code

    response = client.post(TESTED_URL, {chosen_task_prefix: ''}, follow=True)
    content = response.content.decode()
    assert "Please wait until service begins" in content
    assert "Refresh" in content
    assert TESTED_URL in content
