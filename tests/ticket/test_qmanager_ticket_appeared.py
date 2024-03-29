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
    Session.objects.finish_current_session(finished_by=supervisor)
    session = Session.objects.start_new_session(started_by=supervisor)

    # OperA: is_free, has no processed tickets
    Service.objects.create(
        operator=operA,
        task=taskC,
        priority=9)

    # OperB: is_bussy, has a ticket in processing
    Service.objects.create(
        operator=operB,
        task=taskC,
        priority=9
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
        new_code=Status.PROCESSING.code,
        assigned_to=operB,)

    # OperC: is_free, has a processed ticket, priority=1
    Service.objects.create(
        operator=operC,
        task=taskC,
        priority=1
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
        new_code=Status.PROCESSING.code,
        assigned_to=operC)
    Status.objects.create_additional(
        ticket=ticket_processed,
        new_code=Status.COMPLETED.code,
        assigned_by=operC,
        assigned_to=operC)

    # OperD: isn't servicing
    Service.objects.create(
        operator=operD,
        task=taskC,
        priority=0
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
    assert last_status.code == Status.PROCESSING.code
    first_assigned_to_operator = last_status.assigned_to
    assert first_assigned_to_operator.id in expected_free_operators_ids

    # Check 2nd ticket assignment
    second_ticket = Ticket.objects.create_ticket(taskC)
    last_status = second_ticket.status_set.last()
    assert last_status.code == Status.PROCESSING.code
    second_assigned_to_operator = last_status.assigned_to
    expected_second_operator_id = (set(expected_free_operators_ids) - set((
        first_assigned_to_operator.id, ))).pop()
    assert second_assigned_to_operator.id == expected_second_operator_id

    # Check TicketCompletedView with Supervisor
    ticket_completed_URL = f'/ticket/{second_ticket.id}/mark_completed/'
    response = client.post(ticket_completed_URL, follow=True)
    assert response.redirect_chain == [
        (f'/operator/{second_assigned_to_operator.id}/', 302),
    ]
    last_status = second_ticket.status_set.last()
    assert last_status.code == Status.COMPLETED.code

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
        (f'/operator/{first_assigned_to_operator.id}/', 302)
    ]
    last_status = first_ticket.status_set.last()
    assert last_status.code == Status.COMPLETED.code


@pytest.mark.django_db
def test_redirect_ticket_success(client, get_supervisors):
    client.force_login(get_supervisors[1])
    taskC = Task.objects.get(letter_code='C')
    expected_free_operators_ids = setup_db()

    # Assign the tiket to initial operator
    ticket = Ticket.objects.create_ticket(taskC)
    first_assignment_status = ticket.status_set.last()
    initial_operator = first_assignment_status.assigned_to
    operator_personal_page_url = f'/operator/{initial_operator.id}/'
    response = client.get(operator_personal_page_url)
    content = response.content.decode()
    redirect_url = (f'/ticket/{ticket.id}/redirect/'
                    f'?operator={initial_operator.id}')
    assert redirect_url in content

    # Redirect the ticket to another operator
    # GET
    response = client.get(redirect_url)
    content = response.content.decode()
    assert 'Redirect ticket' in content
    assert ticket.code in content
    all_servicing_operators = Operator.objects.filter(
        service__priority__gt=0).distinct()
    all_operators_except_initial = all_servicing_operators.exclude(
        id=initial_operator.id)
    for redirect_to_option in all_operators_except_initial:
        assert redirect_to_option.get_full_name() in content
    assert f'{initial_operator.get_full_name()}</option>' not in content

    # POST
    redirected_to_id = (set(expected_free_operators_ids) - set((
        initial_operator.id, ))).pop()
    response = client.post(
        redirect_url,
        {'redirect_to': redirected_to_id},
        follow=True)
    content = response.content.decode()
    assert response.status_code == 200
    assert 'The ticket was successfully redirected' in content

    # Was the ticket Redirected?
    next_statuses = Status.objects.filter(
        assigned_at__gt=first_assignment_status.assigned_at).order_by(
            'assigned_at')
    redirect_status = next_statuses[0]
    second_assigment_status = next_statuses[1]
    assert redirect_status.code == Status.REDIRECTED.code
    assert redirect_status.assigned_by == initial_operator
    assert redirect_status.assigned_to.id == redirected_to_id

    # Was the ticket Assigned to another operator?
    assert second_assigment_status.code == Status.PROCESSING.code
    assert second_assigment_status.assigned_to.id == redirected_to_id

    # Can the initial operator get new general tickets?
    new_ticket = Ticket.objects.create_ticket(taskC)
    last_ststus_of_new_ticket = new_ticket.status_set.last()
    assert last_ststus_of_new_ticket.code == Status.PROCESSING.code
    assert last_ststus_of_new_ticket.assigned_to == initial_operator


@pytest.mark.django_db
def test_mark_ticket_missed_success(client, get_supervisors):
    client.force_login(get_supervisors[1])
    taskC = Task.objects.get(letter_code='C')
    setup_db()

    # Assign the tiket to initial operator
    ticket = Ticket.objects.create_ticket(taskC)
    first_assignment_status = ticket.status_set.last()
    initial_operator = first_assignment_status.assigned_to
    operator_personal_page_url = f'/operator/{initial_operator.id}/'
    response = client.get(operator_personal_page_url)
    content = response.content.decode()
    assert 'Mark missed' in content

    # Mark missed
    missed_url = f'/ticket/{ticket.id}/mark_missed/'
    response = client.post(missed_url, follow=True)
    last_status = ticket.status_set.last()
    assert last_status.code == Status.MISSED.code
    assert last_status.assigned_by == initial_operator
