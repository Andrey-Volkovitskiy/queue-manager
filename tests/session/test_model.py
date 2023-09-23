import pytest
from queue_manager.session.models import Session
from datetime import datetime, timezone


def test_split_code_to_date_and_letter_with_std_id():
    date_str, letters = Session.objects._split_code_to_date_and_letter(
        '2023-09-22A')
    assert date_str == '2023-09-22'
    assert letters == 'A'


def test_split_code_to_date_and_letter_with_long_id():
    date_str, letters = Session.objects._split_code_to_date_and_letter(
        '2023-09-22ABCDEF')
    assert date_str == '2023-09-22'
    assert letters == 'ABCDEF'


def test_split_code_to_date_and_letter_with_to_short_id():
    date_str, letters = Session.objects._split_code_to_date_and_letter(
        '2023-09-2')
    assert date_str == ''
    assert letters == ''


def test_split_code_to_date_and_letter_without_letters():
    date_str, letters = Session.objects._split_code_to_date_and_letter(
        '2023-09-22')
    assert date_str == '2023-09-22'
    assert letters == ''


def get_todays_date_str():
    date_utc = datetime.now(timezone.utc)
    date_local = date_utc.astimezone()
    return date_local.strftime('%Y-%m-%d')


@pytest.mark.django_db
def test_get_new_session_code_with_empty_db():
    id = Session.objects._get_new_session_code()
    assert id == get_todays_date_str() + "A"


@pytest.mark.django_db
def test_get_new_session_code_with_old_code_in_db(
            default_db_setup, get_supervisors):
    OLD_CODE = '2023-09-20A'
    Session.objects.create(
        code=OLD_CODE,
        started_by=get_supervisors[0])
    id = Session.objects._get_new_session_code()
    assert id == get_todays_date_str() + "A"


@pytest.mark.django_db
def test_new_session_code_with_empty_db(
            default_db_setup, get_supervisors):
    new_session = Session.objects.create(started_by=get_supervisors[0])
    assert new_session.code == get_todays_date_str() + "A"


@pytest.mark.django_db
def test_new_session_code_with_old_code_in_db(
            default_db_setup, get_supervisors):
    OLD_CODE = '2023-09-20A'
    Session.objects.create(
        code=OLD_CODE,
        started_by=get_supervisors[0])
    new_session = Session.objects.create(started_by=get_supervisors[0])
    assert new_session.code == get_todays_date_str() + "A"


@pytest.mark.django_db
def test_new_session_code_with_today_code_without_letters(
            default_db_setup, get_supervisors):
    TODAY_ID = get_todays_date_str()
    Session.objects.create(
        code=TODAY_ID,
        started_by=get_supervisors[0])
    new_session = Session.objects.create(started_by=get_supervisors[0])
    assert new_session.code == get_todays_date_str() + "A"


@pytest.mark.django_db
def test_new_session_code_with_today_code_in_db(
            default_db_setup, get_supervisors):
    TODAY_ID = get_todays_date_str() + "A"
    Session.objects.create(
        code=TODAY_ID,
        started_by=get_supervisors[0])
    new_session = Session.objects.create(started_by=get_supervisors[0])
    assert new_session.code == get_todays_date_str() + "B"


@pytest.mark.django_db
def test_new_session_code_with_today_big_code_in_db(
            default_db_setup, get_supervisors):
    TODAY_ID = get_todays_date_str() + "ZZ"
    Session.objects.create(
        code=TODAY_ID,
        started_by=get_supervisors[0])
    new_session = Session.objects.create(started_by=get_supervisors[0])
    assert new_session.code == get_todays_date_str() + "ZZA"


@pytest.mark.django_db
def test_get_current_session_with_active_session_in_db(
            default_db_setup, get_supervisors):
    TODAY_ID = get_todays_date_str() + "A"
    active_session = Session.objects.create(
        code=TODAY_ID,
        started_by=get_supervisors[0],
        is_active=True)
    current_session = Session.objects.get_current_session()
    assert current_session == active_session


@pytest.mark.django_db
def test_get_current_session_with_empty_db():
    current_session = Session.objects.get_current_session()
    assert current_session is None


@pytest.mark.django_db
def test_get_current_session_with_only_nonactive_sessions_in_db(
            default_db_setup, get_supervisors):
    TODAY_ID = get_todays_date_str() + "A"
    Session.objects.create(
        code=TODAY_ID,
        started_by=get_supervisors[0],
        is_active=False)
    current_session = Session.objects.get_current_session()
    assert current_session is None
