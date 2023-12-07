import pytest
from queue_manager.session.models import Session
from tests import conftest
from . import conftest as package_conftest
from tests.session.conftest import ITEM_START_URL as SESSION_START_URL
from queue_manager.task.models import Task
from queue_manager.ticket.models import Ticket

TESTED_URL = package_conftest.SCREEN_URL
NEW_TICKECTS_NUM = 9
VISIBLE_TICKETS_QUAN = 7


@pytest.mark.django_db
def test_basic_content(client):
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert response.status_code == 200
    assert "Last called tickets" in content


@pytest.mark.django_db
def test_show_list_of_tickets(client, get_supervisors, get_operators):

    client.force_login(get_supervisors[0])
    client.post(SESSION_START_URL, None, follow=True)

    old_ticket_codes = list(
        Ticket.objects.all().values_list('code', flat=True))
    old_task_codes = set((code[0] for code in old_ticket_codes))
    new_tasks = Task.objects.all().exclude(letter_code__in=old_task_codes)
    new_tickets = []
    current_task_index = 0
    for _ in range(NEW_TICKECTS_NUM):
        new_tickets.append(conftest.add_general_ticket(
            task=new_tasks[current_task_index]
        ))
        if current_task_index < len(new_tasks) - 1:
            current_task_index += 1
        else:
            current_task_index = 0
    conftest.complete_tickets(
                    tickets=new_tickets,
                    completed_by=get_operators[2])
    new_tickets_visible = new_tickets[-VISIBLE_TICKETS_QUAN:]
    new_tickets_invisible = (
        new_tickets[:len(new_tickets) - VISIBLE_TICKETS_QUAN])

    # Assert
    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert response.status_code == 200

    for visible_tiket in new_tickets_visible:
        assert visible_tiket.code in content

    for invisible_tiket in new_tickets_invisible:
        assert invisible_tiket.code not in content

    for old_ticket_code in old_ticket_codes:
        assert old_ticket_code not in content


@pytest.mark.django_db
def test_show_clients_ticket(client, get_supervisors):
    expected_ticket_code = 'F001'

    client.force_login(get_supervisors[0])
    client.post(SESSION_START_URL, None, follow=True)

    chosen_task = Task.objects.get(letter_code=expected_ticket_code[0])
    chosen_task_prefix = (package_conftest.TASK_CODE_PREFIX
                          + chosen_task.letter_code)

    response = client.post(
        package_conftest.PRINT_TICKET_URL,
        {chosen_task_prefix: ''},
        follow=True)
    content = response.content.decode()
    assert response.status_code == 200
    assert expected_ticket_code in content
    expected_ticket_id = Ticket.objects.get(
        code=expected_ticket_code,
        session=Session.objects.get_current_session()).id
    expected_url = f'/client/screen/?track_ticket={expected_ticket_id}'
    assert expected_url in content

    response = client.get(expected_url, follow=True)
    content = response.content.decode()
    assert response.status_code == 200
    assert expected_ticket_code in content


@pytest.mark.django_db
def test_show_last_assigned_ticket(client, get_supervisors):
    client.force_login(get_supervisors[0])
    client.post(SESSION_START_URL, None, follow=True)
    last_assigned_ticket = conftest.add_completed_ticket(
        task=Task.objects.get(letter_code='F'))

    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()
    assert response.status_code == 200
    assert last_assigned_ticket.code in content
