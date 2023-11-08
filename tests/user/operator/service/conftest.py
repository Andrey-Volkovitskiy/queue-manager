import pytest
from tests.fixtures.test_users_base import add_base_users
from tests.fixtures.test_services_base import add_base_services
from django.core.management import call_command


@pytest.fixture(autouse=True)
def default_db_setup():
    '''Populates the database with test data'''
    add_base_users()
    call_command('loaddata', 'tests/fixtures/test_tasks_base.json')
    add_base_services()
