import pytest
from queue_manager.user.models import Operator, Supervisor
from queue_manager.ticket.models import QManager
from queue_manager.session.models import Session
from queue_manager.task.models import Task, Service
from queue_manager.ticket.models import Ticket
from queue_manager.status.models import Status


def setup_db():
    supervisor = Supervisor.objects.first()
    operA, operB, operC, operD = Operator.objects.all().order_by('id')
    taskC = Task.objects.get(letter_code='C')
    Session.objects.finish_active_session(finished_by=supervisor)
    session = Session.objects.start_new_session(started_by=supervisor)

    # OperA: is_free, has no processed tickets
    Service.objects.create(
        operator=operA,
        task=taskC,
        is_servicing=True,
        priority_for_operator=9)

    # OperB: is_bussy, has a ticket in processing
    Service.objects.create(
        operator=operB,
        task=taskC,
        is_servicing=True,
        priority_for_operator=9
    )
    ticket_in_processing = Ticket.objects.create(
        task=taskC,
        session=session,
        code=Ticket.objects._get_new_ticket_code(
            session=session,
            task=taskC
        ))
    Status.objects.create_initial(ticket=ticket_in_processing)
    Status.objects.create_additional(
        ticket=ticket_in_processing,
        new_code=Status.objects.Codes.PROCESSING,
        assigned_to=operB,)

    # OperC: is_free, has a processed ticket, priority=1
    Service.objects.create(
        operator=operC,
        task=taskC,
        is_servicing=True,
        priority_for_operator=1
    )
    ticket_processed = Ticket.objects.create(
        task=taskC,
        session=session,
        code=Ticket.objects._get_new_ticket_code(
            session=session,
            task=taskC
        ))
    Status.objects.create_initial(ticket=ticket_processed)
    Status.objects.create_additional(
        ticket=ticket_processed,
        new_code=Status.objects.Codes.PROCESSING,
        assigned_to=operC)
    Status.objects.create_additional(
        ticket=ticket_processed,
        new_code=Status.objects.Codes.COMPLETED,
        assigned_by=operC,
        assigned_to=operC)

    # OperD: is_servicing = False
    Service.objects.create(
        operator=operD,
        task=taskC,
        is_servicing=False,
        priority_for_operator=None
    )

    expected_free_operators_ids = sorted((
        operA.id,
        operC.id))
    return expected_free_operators_ids


@pytest.mark.django_db
def test_get_free_operators():
    taskC = Task.objects.get(letter_code='C')
    expected_free_operators_ids = setup_db()

    free_operators_ids = QManager._get_free_operators(task=taskC).values_list(
        'id', flat=True).order_by('id')
    assert list(free_operators_ids) == expected_free_operators_ids


@pytest.mark.django_db
def test_general_ticket_appeared_success(client, get_supervisors):
    client.force_login(get_supervisors[1])
    taskC = Task.objects.get(letter_code='C')
    expected_free_operators_ids = setup_db()

    # Check 1st ticket assignment
    first_ticket = Ticket.objects.create_ticket(taskC)
    last_status = first_ticket.status_set.last()
    assert last_status.code == Status.objects.Codes.PROCESSING
    first_assigned_to_operator = last_status.assigned_to
    assert first_assigned_to_operator.id in expected_free_operators_ids

    # Check 2nd ticket assignment
    second_ticket = Ticket.objects.create_ticket(taskC)
    last_status = second_ticket.status_set.last()
    assert last_status.code == Status.objects.Codes.PROCESSING
    second_assigned_to_operator = last_status.assigned_to
    expected_second_operator_id = (set(expected_free_operators_ids) - set((
        first_assigned_to_operator.id, ))).pop()
    assert second_assigned_to_operator.id == expected_second_operator_id

    # Check TicketCompletedView with Supervisor
    ticket_completed_URL = f'/ticket/{second_ticket.id}/mark_completed/'
    response = client.post(ticket_completed_URL, follow=True)
    assert response.redirect_chain == [
        ('/operator/', 302),
        ('/operator/select/', 302)
    ]
    last_status = second_ticket.status_set.last()
    assert last_status.code == Status.objects.Codes.COMPLETED

    # Check TicketCompletedView with incorrect Operator
    client.logout()
    incorrect_operator = second_assigned_to_operator
    client.force_login(incorrect_operator)
    ticket_completed_URL = f'/ticket/{first_ticket.id}/mark_completed/'
    response = client.post(ticket_completed_URL, follow=True)
    assert response.status_code == 403

    # Check TicketCompletedView with correct Operator
    client.logout()
    correct_operator = first_assigned_to_operator
    client.force_login(correct_operator)
    ticket_completed_URL = f'/ticket/{first_ticket.id}/mark_completed/'
    response = client.post(ticket_completed_URL, follow=True)
    assert response.redirect_chain == [
        ('/operator/', 302),
        (f'/operator/{first_assigned_to_operator.id}/', 302)
    ]
    last_status = first_ticket.status_set.last()
    assert last_status.code == Status.objects.Codes.COMPLETED
