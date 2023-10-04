from django.contrib.auth.models import User, Group, Permission


GROUP_ID = {
    "supervisors": 1,
    "operators": 2
}

OPERATORS = (
    {
        "id": 1,
        "username": "operator_A",
        "first_name": "Name_A",
        "last_name": "Surname_A",
        "password": "password_A"
    },
    {
        "id": 2,
        "username": "operator_B",
        "first_name": "Name_B",
        "last_name": "Surname_B",
        "password": "password_B"
    },
    {
        "id": 3,
        "username": "operator_C",
        "first_name": "Name_C",
        "last_name": "Surname_C",
        "password": "password_C"
    },

)

SUPERVISORS = (
    {
        "id": 4,
        "username": "supervisor_A",
        "first_name": "Super_name_A",
        "last_name": "Super_surname_A",
        "password": "super_password_A"
    },
)

PERMISSIONS_FOR_OPERATORS = (
    'view_ticket',
)

PERMISSIONS_FOR_SUPERVISORS = (
    'view_supervisor',
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


def get_permission_ids(code_list):
    permission_ids = []
    for permission_code in code_list:
        permission_ids.append(
            Permission.objects.filter(codename=permission_code).order_by(
                'content_type_id').last())
    return permission_ids


def create_user(user, groups):
    User.objects.create(
            id=user['id'],
            username=user['username'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            password=user['password'],
            ).groups.set(groups)


def add_base_users():
    for group_name in GROUP_ID:
        Group.objects.create(
            id=GROUP_ID[group_name],
            name=group_name)

    for operator in OPERATORS:
        create_user(user=operator, groups=(GROUP_ID['operators'], ))

    for supervisor in SUPERVISORS:
        create_user(user=supervisor, groups=(GROUP_ID['supervisors'], ))

    Group.objects.get(name='operators').permissions.set(
        get_permission_ids(PERMISSIONS_FOR_OPERATORS))
    Group.objects.get(name='supervisors').permissions.set(
        get_permission_ids(PERMISSIONS_FOR_SUPERVISORS))
