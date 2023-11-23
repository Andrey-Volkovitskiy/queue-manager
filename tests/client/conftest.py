import pytest
from django.core.management import call_command
from tests.fixtures.test_users_base import add_base_users

ITEM_LIST_HEADER_ROWS = 1
TASK_CODE_PREFIX = "task_code:"

PRINT_TICKET_URL = "/client/"
SCREEN_URL = "/client/screen/"


@pytest.fixture(autouse=True)
def default_db_setup():
    '''Populates the database with test data'''
    add_base_users()
    call_command('loaddata', 'tests/fixtures/test_tasks_base.json')
    call_command('loaddata', 'tests/fixtures/test_sessions_base.json')
    call_command('loaddata', 'tests/fixtures/test_tickets_base.json')


@pytest.fixture()
def print_ticket_db_setup():
    call_command(
        'loaddata', 'tests/fixtures/test_tickets_additional.json')
