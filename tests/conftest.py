import pytest
from queue_manager.user.models import Operator, Supervisor
from queue_manager.session.models import Session
from queue_manager.task.models import Service
from queue_manager.ticket.models import Ticket
from queue_manager.status.models import Status

HOME_URL = "/"
LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"


@pytest.fixture
def client():
    from django.test.client import Client
    return Client()


@pytest.mark.django_db
def get_tested_url_for_max_id(url_pattern, Model):
    url_begin, url_end = url_pattern.split('<pk>')
    max_id = Model.objects.latest('id').id
    full_url = url_begin + str(max_id) + url_end
    return full_url


@pytest.fixture
def get_supervisors():
    return Supervisor.objects.all().order_by('id')


@pytest.fixture
def get_operators():
    return Operator.objects.all().order_by('id')


@pytest.mark.django_db
def add_personal_ticket(task, assigned_to):
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
        assigned_to=assigned_to)
    return ticket


@pytest.mark.django_db
def add_general_ticket(task):
    session = Session.objects.get_current_session()
    ticket = Ticket.objects.create(
        task=task,
        session=session,
        code=Ticket.objects._get_new_ticket_code(
            session=session,
            task=task
        ))
    Status.objects.create_initial(ticket=ticket)
    return ticket


@pytest.mark.django_db
def add_completed_ticket(task):
    compliting_operator = Operator.objects.last()
    session = Session.objects.get_current_session()
    ticket = Ticket.objects.create(
        task=task,
        session=session,
        code=Ticket.objects._get_new_ticket_code(
            session=session,
            task=task
        ))
    Status.objects.create_initial(ticket=ticket)
    Status.objects.create_additional(
        ticket=ticket,
        new_code=Status.objects.Codes.PROCESSING,
        assigned_to=compliting_operator,)
    Status.objects.create_additional(
        ticket=ticket,
        new_code=Status.objects.Codes.COMPLETED,
        assigned_by=compliting_operator)
    return ticket


@pytest.mark.django_db
def complete_tickets(tickets, completed_by):
    for ticket in tickets:
        Service.objects.\
            filter(
                task=ticket.task,
                operator=completed_by)\
            .update(
                is_servicing=True,
                priority_for_operator=9,
            )
        Status.objects.create_initial(ticket=ticket)
        Status.objects.create_additional(
            ticket=ticket,
            new_code=Status.objects.Codes.PROCESSING,
            assigned_to=completed_by,)
        Status.objects.create_additional(
            ticket=ticket,
            new_code=Status.objects.Codes.COMPLETED,
            assigned_by=completed_by)
