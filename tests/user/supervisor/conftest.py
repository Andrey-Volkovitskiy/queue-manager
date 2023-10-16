import pytest
from tests.fixtures.test_users_base import add_base_users

ITEM_LIST_HEADER_ROWS = 1

ITEM_NAME = "supervisor"

ITEM_ENTER_URL = f"/{ITEM_NAME}/"


@pytest.fixture(autouse=True)
def default_db_setup():
    '''Populates the database with test data'''
    add_base_users()
