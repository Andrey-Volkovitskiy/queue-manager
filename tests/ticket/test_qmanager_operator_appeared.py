import pytest
from queue_manager.user.models import Operator, Supervisor
from queue_manager.ticket.models import QManager
from queue_manager.session.models import Session
from queue_manager.task.models import Task, Service
from queue_manager.ticket.models import Ticket
from queue_manager.status.models import Status


def setup_db():
    supervisor = Supervisor.objects.first()
    operators = Operator.objects.all().order_by('id')
    taskA = Task.objects.get(letter_code='A')
    taskB = Task.objects.get(letter_code='B')
    Session.objects.finish_active_session(finished_by=supervisor)
    Session.objects.start_new_session(started_by=supervisor)

    for operator in operators:
        # TaskA, is_servicing=False
        Service.objects.create(
            operator=operator,
            task=taskA,
            is_servicing=False,
            priority_for_operator=None
        )

        # TaskB, is_servicing=False
        Service.objects.create(
            operator=operator,
            task=taskB,
            is_servicing=False,
            priority_for_operator=None
        )


def add_personal_ticket(task, assidned_to):
    redirecting_operator = Operator.objects.last()
    session = Session.objects.get_current_session()
    ticket = Ticket.objects.create(
        task=task,
        session=session,
        code=Ticket.objects._get_new_ticket_code(
            session=session,
            task=task
        ))
    Service.objects.filter(
        task=task, operator=redirecting_operator).update(
        is_servicing=True,
        priority_for_operator=9,
    )
    Status.objects.create_initial(ticket=ticket)
    Status.objects.create_additional(
        ticket=ticket,
        new_code=Status.objects.Codes.PROCESSING,
        assigned_to=redirecting_operator,)
    Status.objects.create_additional(
        ticket=ticket,
        new_code=Status.objects.Codes.REDIRECTED,
        assigned_to=assidned_to)
    return ticket


@pytest.mark.django_db
def test_get_next_personal_ticket_with_one_ticket():
    taskA = Task.objects.get(letter_code='A')
    tested_operator = Operator.objects.first()
    setup_db()

    expected_ticket = add_personal_ticket(
        task=taskA,
        assidned_to=tested_operator
    )
    next_personal_ticket = QManager._get_next_personal_ticket(tested_operator)
    assert next_personal_ticket == expected_ticket


@pytest.mark.django_db
def test_get_next_personal_ticket_with_three_tickets():
    taskA = Task.objects.get(letter_code='A')
    tested_operator = Operator.objects.first()
    setup_db()

    ticket1 = add_personal_ticket(
        task=taskA,
        assidned_to=tested_operator
    )
    add_personal_ticket(
        task=taskA,
        assidned_to=tested_operator
    )
    add_personal_ticket(
        task=taskA,
        assidned_to=tested_operator
    )
    next_personal_ticket = QManager._get_next_personal_ticket(tested_operator)
    assert next_personal_ticket == ticket1


@pytest.mark.django_db
def test_get_next_personal_ticket_with_old_R_status():
    taskA = Task.objects.get(letter_code='A')
    tested_operator = Operator.objects.first()
    setup_db()

    ticket1 = add_personal_ticket(
        task=taskA,
        assidned_to=tested_operator
    )
    Status.objects.create_additional(
        ticket=ticket1,
        new_code=Status.objects.Codes.PROCESSING,
        assigned_to=tested_operator,)
    Status.objects.create_additional(
        ticket=ticket1,
        new_code=Status.objects.Codes.COMPLETED,
        assigned_to=tested_operator,)

    ticket2 = add_personal_ticket(
        task=taskA,
        assidned_to=tested_operator
    )
    add_personal_ticket(
        task=taskA,
        assidned_to=tested_operator
    )
    next_personal_ticket = QManager._get_next_personal_ticket(tested_operator)
    assert next_personal_ticket == ticket2
