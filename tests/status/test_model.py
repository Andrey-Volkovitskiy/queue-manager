import pytest
from queue_manager.status.models import Status
from queue_manager.ticket.models import Ticket
from queue_manager.task.models import Task
from queue_manager.user.models import Operator
from datetime import datetime, timezone


@pytest.mark.django_db
def test_init_status():
    task = Task.objects.last()
    new_ticket = Ticket.objects.create_ticket(task=task)
    assert new_ticket.status_set.last().code == 'U'


@pytest.mark.django_db
def test_additional_status_U_success():
    user = Operator.objects.first()
    task = Task.objects.last()
    ticket = Ticket.objects.create_ticket(task=task)

    item_creation_time = datetime.now(timezone.utc)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='P',
        assigned_by=None,
        assigned_to=user
    )

    new_status = Status.objects.filter(ticket=ticket).last()
    assert new_status.code == 'P'
    assert new_status.assigned_at >= item_creation_time
    assert new_status.assigned_by is None
    assert new_status.assigned_to == user
    old_status = Status.objects.filter(ticket=ticket).first()
    assert old_status.code == 'U'


@pytest.mark.django_db
def test_additional_status_U_with_wrong_codes():
    WRONG_CODES = ('C', 'M', 'R', 'U')
    user = Operator.objects.first()
    task = Task.objects.last()
    ticket = Ticket.objects.create_ticket(task=task)

    for wrong_code in WRONG_CODES:
        with pytest.raises(Status.objects.StatusFlowViolated):
            Status.objects.create_additional(
                ticket=ticket,
                new_code=wrong_code,
                assigned_by=user,
                assigned_to=user
            )


@pytest.mark.django_db
def test_additional_status_P_to_C_success():
    user = Operator.objects.first()
    task = Task.objects.last()
    ticket = Ticket.objects.create_ticket(task=task)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='P',
        assigned_by=None,
        assigned_to=user
    )

    item_creation_time = datetime.now(timezone.utc)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='C',
        assigned_by=user,
        assigned_to=None
    )

    new_status = Status.objects.filter(ticket=ticket).last()
    assert new_status.code == 'C'
    assert new_status.assigned_at >= item_creation_time
    assert new_status.assigned_by == user
    assert new_status.assigned_to is None


@pytest.mark.django_db
def test_additional_status_P_to_M_success():
    user = Operator.objects.first()
    task = Task.objects.last()
    ticket = Ticket.objects.create_ticket(task=task)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='P',
        assigned_by=None,
        assigned_to=user
    )

    item_creation_time = datetime.now(timezone.utc)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='M',
        assigned_by=user,
        assigned_to=None
    )

    new_status = Status.objects.filter(ticket=ticket).last()
    assert new_status.code == 'M'
    assert new_status.assigned_at >= item_creation_time
    assert new_status.assigned_by == user
    assert new_status.assigned_to is None


@pytest.mark.django_db
def test_additional_status_P_with_wrong_codes():
    WRONG_CODES = ('U', 'P')
    user = Operator.objects.first()
    task = Task.objects.last()
    ticket = Ticket.objects.create_ticket(task=task)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='P',
        assigned_by=None,
        assigned_to=user
    )

    for wrong_code in WRONG_CODES:
        with pytest.raises(Status.objects.StatusFlowViolated):
            Status.objects.create_additional(
                ticket=ticket,
                new_code=wrong_code,
                assigned_by=user,
                assigned_to=user
            )


@pytest.mark.django_db
def test_additional_status_C_to_R_success():
    user = Operator.objects.first()
    task = Task.objects.last()
    ticket = Ticket.objects.create_ticket(task=task)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='P',
        assigned_by=None,
        assigned_to=user
    )
    Status.objects.create_additional(
        ticket=ticket,
        new_code='C',
        assigned_by=None,
        assigned_to=user
    )

    item_creation_time = datetime.now(timezone.utc)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='R',
        assigned_by=user,
        assigned_to=user
    )

    new_status = Status.objects.filter(ticket=ticket).last()
    assert new_status.code == 'R'
    assert new_status.assigned_at >= item_creation_time
    assert new_status.assigned_by == user
    assert new_status.assigned_to == user


@pytest.mark.django_db
def test_additional_status_C_with_wrong_codes():
    WRONG_CODES = ('C', 'U', 'M', 'P')
    user = Operator.objects.first()
    task = Task.objects.last()
    ticket = Ticket.objects.create_ticket(task=task)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='P',
        assigned_by=None,
        assigned_to=user
    )
    Status.objects.create_additional(
        ticket=ticket,
        new_code='C',
        assigned_by=None,
        assigned_to=user
    )

    for wrong_code in WRONG_CODES:
        with pytest.raises(Status.objects.StatusFlowViolated):
            Status.objects.create_additional(
                ticket=ticket,
                new_code=wrong_code,
                assigned_by=user,
                assigned_to=user
            )


@pytest.mark.django_db
def test_additional_status_M_to_R_success():
    user = Operator.objects.first()
    task = Task.objects.last()
    ticket = Ticket.objects.create_ticket(task=task)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='P',
        assigned_by=None,
        assigned_to=user
    )
    Status.objects.create_additional(
        ticket=ticket,
        new_code='M',
        assigned_by=None,
        assigned_to=user
    )

    item_creation_time = datetime.now(timezone.utc)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='R',
        assigned_by=user,
        assigned_to=user
    )

    new_status = Status.objects.filter(ticket=ticket).last()
    assert new_status.code == 'R'
    assert new_status.assigned_at >= item_creation_time
    assert new_status.assigned_by == user
    assert new_status.assigned_to == user


@pytest.mark.django_db
def test_additional_status_M_with_wrong_codes():
    WRONG_CODES = ('C', 'U', 'M', 'P')
    user = Operator.objects.first()
    task = Task.objects.last()
    ticket = Ticket.objects.create_ticket(task=task)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='P',
        assigned_by=None,
        assigned_to=user
    )
    Status.objects.create_additional(
        ticket=ticket,
        new_code='M',
        assigned_by=None,
        assigned_to=user
    )

    for wrong_code in WRONG_CODES:
        with pytest.raises(Status.objects.StatusFlowViolated):
            Status.objects.create_additional(
                ticket=ticket,
                new_code=wrong_code,
                assigned_by=user,
                assigned_to=user
            )


@pytest.mark.django_db
def test_additional_status_R_to_P_success():
    user = Operator.objects.first()
    task = Task.objects.last()
    ticket = Ticket.objects.create_ticket(task=task)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='P',
        assigned_by=None,
        assigned_to=user
    )
    Status.objects.create_additional(
        ticket=ticket,
        new_code='M',
        assigned_by=user,
        assigned_to=None
    )
    Status.objects.create_additional(
        ticket=ticket,
        new_code='R',
        assigned_by=user,
        assigned_to=user
    )

    item_creation_time = datetime.now(timezone.utc)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='P',
        assigned_by=None,
        assigned_to=user
    )

    new_status = Status.objects.filter(ticket=ticket).last()
    assert new_status.code == 'P'
    assert new_status.assigned_at >= item_creation_time
    assert new_status.assigned_by is None
    assert new_status.assigned_to == user


@pytest.mark.django_db
def test_additional_status_R_with_wrong_codes():
    WRONG_CODES = ('C', 'U', 'M', 'R')
    user = Operator.objects.first()
    task = Task.objects.last()
    ticket = Ticket.objects.create_ticket(task=task)
    Status.objects.create_additional(
        ticket=ticket,
        new_code='P',
        assigned_by=None,
        assigned_to=user
    )
    Status.objects.create_additional(
        ticket=ticket,
        new_code='M',
        assigned_by=user,
        assigned_to=None
    )
    Status.objects.create_additional(
        ticket=ticket,
        new_code='R',
        assigned_by=user,
        assigned_to=user
    )

    for wrong_code in WRONG_CODES:
        with pytest.raises(Status.objects.StatusFlowViolated):
            Status.objects.create_additional(
                ticket=ticket,
                new_code=wrong_code,
                assigned_by=user,
                assigned_to=user
            )
