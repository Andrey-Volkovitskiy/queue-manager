class DefaultDBData:
    '''Data used to populate an empty DB with users, groups and permissions'''

    groups = {
        'SUPERVISORS': 'supervisors',
        'OPERATORS': 'operators',
    }

    default_supervisor = {
        'username': 'default_supervisor',
        'password': 'default_pass',
        'first_name': 'Default',
        'last_name': 'Supervisor',
    }

    permissions_for_supervisors = (
        'add_operator',
        'change_operator',
        'view_operator',
        'delete_operator',
        'pretend_operator',
        'add_task',
        'change_task',
        'view_task',
        'delete_task',
        'session.add_session',
        'session.change_session',
        'session.view_session',
        'view_ticket',
    )


def add_completed_tickets(qty, task_letter):
    '''Adds to DB some quantity of tickets with "U, P, C" statuses.
    Used for test purpuses.

    Arguments:
        qty - the quantity of tickets to insert
        task_letter - task.letter_code'''

    from queue_manager.ticket.models import Ticket
    from queue_manager.status.models import Status
    from queue_manager.task.models import Task
    from queue_manager.session.models import Session
    from queue_manager.user.models import Operator

    PROCESSED_BY_OPERATOR_ID = 3
    SESSION_ID = None

    operator = Operator.objects.get(id=PROCESSED_BY_OPERATOR_ID)
    if SESSION_ID:
        session = Session.objects.get(id=SESSION_ID)
    else:
        session = Session.objects.get_current_session()
    task = Task.objects.get(letter_code=task_letter)
    ticket_new_code = Ticket.objects._get_new_ticket_code(
        session=session,
        task=task
    )
    last_ticket_number = int(ticket_new_code[1:]) - 1

    for i in range(qty):
        ticket_new_code = Ticket.objects._get_new_ticket_code(
            session=session,
            task=task,
            last_ticket_number=last_ticket_number
           )
        new_ticket = Ticket.objects.create(
                code=ticket_new_code,
                session=session,
                task=task
            )
        last_ticket_number += 1

        Status.objects.create_initial(ticket=new_ticket)

        Status.objects.create_additional(
            ticket=new_ticket,
            new_code=Status.PROCESSING.code,
            assigned_to=operator)

        Status.objects.create_additional(
            ticket=new_ticket,
            new_code=Status.COMPLETED.code,
            assigned_by=operator)

        if i % 1000 == 0:
            print(f'{i} tickets created')


def add_finished_sessions(qty):
    '''Adds to DB some quantity of finished sessions.
    Used for test purpuses.

    Arguments:
        qty - the quantity of tickets to insert'''
    from queue_manager.session.models import Session
    from queue_manager.user.models import Supervisor
    from datetime import datetime, timedelta, timezone

    BY_SUPERVISOR_ID = 2
    CTRATED_AT = '2022-09-21 14:55:26'
    INCREMENT_TIME = timedelta(microseconds=5)
    CODE_PREFIX = 'auto-'
    MAX_PREV_CODE = 'auto-2001'

    time = datetime.fromisoformat(CTRATED_AT)\
        .replace(tzinfo=timezone.utc)
    supervisor = Supervisor.objects.get(id=BY_SUPERVISOR_ID)

    prev_code = int(MAX_PREV_CODE[len(CODE_PREFIX):])

    if Session.objects.get_current_session():
        Session.objects.finish_current_session(supervisor)

    for i in range(qty):
        session = Session.objects.create(
            code=f"{CODE_PREFIX}{prev_code + 1 + i}",
            started_by=supervisor)

        session.finished_by = supervisor
        session.started_at = time
        time += INCREMENT_TIME
        session.finished_at = time
        time += INCREMENT_TIME
        session.save()
