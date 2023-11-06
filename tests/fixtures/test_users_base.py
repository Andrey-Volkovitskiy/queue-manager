from django.contrib.auth.models import User, Group, Permission


GROUP_ID = {
    "supervisors": 1,
    "operators": 2
}

OPERATORS = (
    {
        "username": "operator_A",
        "first_name": "Name_A",
        "last_name": "Surname_A",
        "password": "password_A"
    },
    {
        "username": "operator_B",
        "first_name": "Name_B",
        "last_name": "Surname_B",
        "password": "password_B"
    },
    {
        "username": "operator_C",
        "first_name": "Name_C",
        "last_name": "Surname_C",
        "password": "password_C"
    },

)

SUPERVISORS = (
    {
        "username": "supervisor_A",
        "first_name": "Super_name_A",
        "last_name": "Super_surname_A",
        "password": "super_password_A"
    },
    {
        "username": "supervisor_B",
        "first_name": "Super_name_B",
        "last_name": "Super_surname_B",
        "password": "super_password_B"
    },
)

PERMISSIONS_FOR_OPERATORS = (
    'view_ticket',
)

PERMISSIONS_FOR_SUPERVISORS = (
    'add_operator',
    'change_operator',
    'view_operator',
    'delete_operator',
    'pretend_operator',
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
            username=user['username'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            password=user['password'],
            ).groups.set(groups)


def add_base_users():
    for operator in OPERATORS:
        create_user(user=operator, groups=(
            Group.objects.get(name='operators'), ))

    for supervisor in SUPERVISORS:
        create_user(user=supervisor, groups=(
            Group.objects.get(name='supervisors'), ))

    Group.objects.get(name='operators').permissions.set(
        get_permission_ids(PERMISSIONS_FOR_OPERATORS))
    Group.objects.get(name='supervisors').permissions.set(
        get_permission_ids(PERMISSIONS_FOR_SUPERVISORS))
