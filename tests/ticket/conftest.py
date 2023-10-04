import pytest
from django.core.management import call_command
from fixtures.test_users_base import add_base_users

ITEM_LIST_HEADER_ROWS = 1

ITEM_NAME = "ticket"

ITEM_LIST_URL = f"/{ITEM_NAME}/"
ITEM_CREATE_URL = f"/{ITEM_NAME}/create/"


@pytest.fixture(autouse=True)
def default_db_setup():
    '''Populates the database with test data'''
    add_base_users()
    call_command('loaddata', 'tests/fixtures/test_tasks_base.json')
    call_command('loaddata', 'tests/fixtures/test_sessions_base.json')
    call_command('loaddata', f'tests/fixtures/test_{ITEM_NAME}s_base.json')
    call_command(
        'loaddata', f'tests/fixtures/test_{ITEM_NAME}s_additional.json')
