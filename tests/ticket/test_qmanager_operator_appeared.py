import pytest
from tests import conftest
from queue_manager.user.models import Operator, Supervisor
from queue_manager.ticket.models import QManager
from queue_manager.session.models import Session
from queue_manager.task.models import Task, Service
from queue_manager.status.models import Status


def _setup_db():
    supervisor = Supervisor.objects.first()
    operators = Operator.objects.all().order_by('id')
    tasks = (
        Task.objects.get(letter_code='A'),
        Task.objects.get(letter_code='B'),
        Task.objects.get(letter_code='C'),
    )
    Session.objects.finish_active_session(finished_by=supervisor)
    Session.objects.start_new_session(started_by=supervisor)

    for operator in operators:
        for task in tasks:
            # TaskN, is_servicing=False
            Service.objects.create(
                operator=operator,
                task=task,
                is_servicing=False,
                priority_for_operator=None
            )


# _get_next_personal_ticket #######################
@pytest.mark.django_db
def test_get_next_personal_ticket_with_one_ticket():
    taskA = Task.objects.get(letter_code='A')
    tested_operator = Operator.objects.first()
    _setup_db()

    expected_ticket = conftest.add_personal_ticket(
        task=taskA,
        assigned_to=tested_operator
    )
    next_personal_ticket = QManager._get_next_personal_ticket(tested_operator)
    assert next_personal_ticket == expected_ticket


@pytest.mark.django_db
def test_get_next_personal_ticket_with_three_tickets():
    taskA = Task.objects.get(letter_code='A')
    tested_operator = Operator.objects.first()
    _setup_db()

    ticket1 = conftest.add_personal_ticket(
        task=taskA,
        assigned_to=tested_operator
    )
    conftest.add_personal_ticket(
        task=taskA,
        assigned_to=tested_operator
    )
    conftest.add_personal_ticket(
        task=taskA,
        assigned_to=tested_operator
    )
    next_personal_ticket = QManager._get_next_personal_ticket(tested_operator)
    assert next_personal_ticket == ticket1


@pytest.mark.django_db
def test_get_next_personal_ticket_with_old_R_status():
    taskA = Task.objects.get(letter_code='A')
    tested_operator = Operator.objects.first()
    _setup_db()

    ticket1 = conftest.add_personal_ticket(
        task=taskA,
        assigned_to=tested_operator
    )
    Status.objects.create_additional(
        ticket=ticket1,
        new_code=Status.objects.Codes.PROCESSING,
        assigned_to=tested_operator,)
    Status.objects.create_additional(
        ticket=ticket1,
        new_code=Status.objects.Codes.COMPLETED,
        assigned_to=tested_operator,)

    ticket2 = conftest.add_personal_ticket(
        task=taskA,
        assigned_to=tested_operator
    )
    conftest.add_personal_ticket(
        task=taskA,
        assigned_to=tested_operator
    )
    next_personal_ticket = QManager._get_next_personal_ticket(tested_operator)
    assert next_personal_ticket == ticket2


# _get_next_primary_ticket #######################
@pytest.mark.django_db
def test_get_next_primary_ticket():
    taskA = Task.objects.get(letter_code='A')
    tested_operator = Operator.objects.first()
    _setup_db()

    conftest.add_completed_ticket(task=taskA)
    expected_ticket = conftest.add_general_ticket(task=taskA)
    conftest.add_general_ticket(task=taskA)
    conftest.add_general_ticket(task=taskA)

    next_primary_ticket = QManager._get_next_primary_ticket(
        operator=tested_operator,
        primary_task_id=taskA.id)
    assert next_primary_ticket == expected_ticket


# _get_next_secondary_ticket #######################
@pytest.mark.django_db
def test_get_next_secondary_ticket():
    taskA = Task.objects.get(letter_code='A')
    taskB = Task.objects.get(letter_code='B')
    tested_operator = Operator.objects.first()
    _setup_db()

    conftest.add_completed_ticket(task=taskA)
    expected_ticket = conftest.add_general_ticket(task=taskB)
    conftest.add_general_ticket(task=taskA)
    conftest.add_general_ticket(task=taskB)
    conftest.add_general_ticket(task=taskA)
    conftest.add_general_ticket(task=taskB)

    next_secondary_ticket = QManager._get_next_secondary_ticket(
        operator=tested_operator,
        secondery_tasks_ids=(
            taskA.id,
            taskB.id))
    assert next_secondary_ticket == expected_ticket


# END TO END TESTS #######################
@pytest.mark.django_db
def test_operator_appeared_end_to_end_success(client, get_supervisors):
    task_primary = Task.objects.get(letter_code='A')
    task_second_1 = Task.objects.get(letter_code='B')
    task_second_2 = Task.objects.get(letter_code='C')
    operator_1 = Operator.objects.first()
    operator_2 = Operator.objects.last()
    _setup_db()
    client.force_login(get_supervisors[0])

    # Make operator1 busy
    conftest.add_completed_ticket(task=task_primary)
    first_tiket = conftest.add_general_ticket(task=task_primary)
    response = client.post(
        f'/operator/{operator_1.id}/service_start/',
        {
            'primary_task': task_primary.id,
            'secondary_tasks': (
                task_second_1.id,
                task_second_2.id
            )
        },
        follow=True
    )
    assert response.status_code == 200
    assert operator_1.current_ticket == first_tiket

    # Add prim & second tickets
    fourth_ticket = conftest.add_general_ticket(task=task_second_1)
    fifth_ticket = conftest.add_general_ticket(task=task_second_2)
    sixth_ticket = conftest.add_general_ticket(task=task_second_1)
    second_ticket = conftest.add_general_ticket(task=task_primary)
    third_ticket = conftest.add_general_ticket(task=task_primary)

    # Add personal tickets
    personal_ticket_1 = conftest.add_personal_ticket(
        task=task_second_2, assigned_to=operator_1)
    personal_ticket_2 = conftest.add_personal_ticket(
        task=task_primary,  assigned_to=operator_1)

    # Are all tickets visualized on operators personal page?
    response = client.get(f'/operator/{operator_1.id}', follow=True)
    content = response.content.decode()
    assert second_ticket.code in content
    assert third_ticket.code in content
    assert fourth_ticket.code in content
    assert fifth_ticket.code in content
    assert sixth_ticket.code in content
    assert personal_ticket_1.code in content
    assert personal_ticket_2.code in content

    # Make operator1 free and getting tickets
    response = client.post(
        f'/ticket/{first_tiket.id}/mark_completed/',
        follow=True)
    assert response.status_code == 200
    assert operator_1.current_ticket == personal_ticket_1

    response = client.post(
        f'/ticket/{personal_ticket_1.id}/mark_completed/',
        follow=True)
    assert response.status_code == 200
    assert operator_1.current_ticket == personal_ticket_2

    response = client.post(
        f'/ticket/{personal_ticket_2.id}/mark_completed/',
        follow=True)
    assert response.status_code == 200
    assert operator_1.current_ticket == second_ticket

    # Start service by operator2 (service together)
    response = client.post(
        f'/operator/{operator_2.id}/service_start/',
        {
            'primary_task': task_primary.id,
            'secondary_tasks': (
                task_second_1.id,
                task_second_2.id
            )
        },
        follow=True
    )
    assert response.status_code == 200
    assert operator_2.current_ticket == third_ticket
    assert operator_1.current_ticket == second_ticket

    response = client.post(
        f'/ticket/{second_ticket.id}/mark_completed/',
        follow=True)
    assert response.status_code == 200
    assert operator_1.current_ticket == fourth_ticket

    response = client.post(
        f'/ticket/{third_ticket.id}/mark_completed/',
        follow=True)
    assert response.status_code == 200
    assert operator_2.current_ticket == fifth_ticket

    # Stop service by operator1 and complete current ticket
    response = client.post(
        f'/operator/{operator_1.id}/service_stop/', follow=True)
    assert response.status_code == 200
    response = client.post(
        f'/ticket/{fourth_ticket.id}/mark_completed/',
        follow=True)
    assert response.status_code == 200
    assert operator_1.current_ticket is None

    # Service last ticket by operator2
    response = client.post(
        f'/ticket/{fifth_ticket.id}/mark_completed/',
        follow=True)
    assert response.status_code == 200
    assert operator_2.current_ticket == sixth_ticket


@pytest.mark.django_db
def test_take_again_and_redirect(client, get_supervisors):
    task_primary = Task.objects.get(letter_code='A')
    operator_1 = Operator.objects.first()
    operator_2 = Operator.objects.last()
    _setup_db()
    client.force_login(get_supervisors[0])

    # Make Operator2 busy
    ticket_busy = conftest.add_general_ticket(task=task_primary)
    response = client.post(
        f'/operator/{operator_2.id}/service_start/',
        {'primary_task': task_primary.id},
        follow=True
    )
    assert response.status_code == 200
    assert operator_2.current_ticket == ticket_busy

    # Operator1 - Complete ticket_0
    ticket_0 = conftest.add_general_ticket(task=task_primary)
    response = client.post(
        f'/operator/{operator_1.id}/service_start/',
        {'primary_task': task_primary.id},
        follow=True
    )
    assert response.status_code == 200
    assert operator_1.current_ticket == ticket_0
    response = client.post(
        f'/ticket/{ticket_0.id}/mark_completed/',
        follow=True)
    assert response.status_code == 200
    assert operator_1.current_ticket is None

    # Operator1 - Take ticket_0 again
    response = client.post(
        f'/ticket/{ticket_0.id}/take_again/',
        follow=True)
    assert response.status_code == 200
    assert operator_1.current_ticket == ticket_0

    # Operator1 - Redirect ticket_1 to Operator 2
    response = client.post(
        f'/ticket/{ticket_0.id}/redirect/?operator={operator_1.id}',
        {'redirect_to': operator_2.id},
        follow=True)
    assert response.status_code == 200
    assert operator_1.current_ticket is None

    # Make Operator 2 free and take ticket_0
    response = client.post(
        f'/ticket/{ticket_busy.id}/mark_completed/',
        follow=True)
    assert response.status_code == 200
    assert operator_2.current_ticket == ticket_0
