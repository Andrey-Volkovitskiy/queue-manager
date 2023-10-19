import pytest
from tests.fixtures.test_users_base import add_base_users

ITEM_LIST_HEADER_ROWS = 1

ITEM_NAME = "operator"

ITEM_ENTER_URL = f"/{ITEM_NAME}/"
ITEM_LIST_URL = f"{ITEM_ENTER_URL}manage/"
ITEM_CREATE_URL = f"{ITEM_ENTER_URL}manage/create/"
CREATE_OK_MESSAGE = f"The {ITEM_NAME} was successfully created"


@pytest.fixture(autouse=True)
def default_db_setup():
    '''Populates the database with test data'''
    add_base_users()
