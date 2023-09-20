import pytest
from django.core.management import call_command
from django.contrib.auth.models import User
from fixtures.test_users_base import add_base_users
from fixtures.test_users_base import GROUP_ID

ITEM_LIST_HEADER_ROWS = 1

ITEM_NAME = "task"

ITEM_LIST_URL = f"/{ITEM_NAME}/"
ITEM_CREATE_URL = f"/{ITEM_NAME}/create/"
CREATE_OK_MESSAGE = f"The {ITEM_NAME} was successfully created"


@pytest.fixture(autouse=True)
def default_db_setup():
    '''Populates the database with test data'''
    call_command('loaddata', f'tests/fixtures/test_{ITEM_NAME}s_base.json')
    add_base_users()


@pytest.fixture
def get_supervisors():
    return User.objects.filter(groups=GROUP_ID['supervisors']).order_by('id')

@pytest.fixture
def get_operators():
    return User.objects.filter(groups=GROUP_ID['operators']).order_by('id')
