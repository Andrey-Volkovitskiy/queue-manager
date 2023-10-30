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
        'add_operator',
        'change_operator',
        'view_operator',
        'delete_operator',
        'add_task',
        'change_task',
        'view_task',
        'delete_task',
        'add_session',
        'change_session',
        'view_session',
        'view_ticket',
    )
