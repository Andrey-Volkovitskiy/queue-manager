class DefaultDBData:
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
        'user.add_operator',
        'user.change_operator',
        'user.view_operator',
        'user.delete_operator',
        'task.add_task',
        'task.change_task',
        'task.view_task',
        'task.delete_task',
        'session.add_session',
        'session.change_session',
        'session.view_session',
        'ticket.view_ticket',
    )
