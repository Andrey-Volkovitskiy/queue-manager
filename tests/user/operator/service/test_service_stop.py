import pytest
from tests.conftest import LOGIN_URL
from .. import conftest as package_conftest

URL_PREFIX = package_conftest.ITEM_ENTER_URL
START_POSTFIX_URL = package_conftest.SERVICE_START_POSTFIX_URL
STOP_POSTFIX_URL = package_conftest.SERVICE_STOP_POSTFIX_URL


@pytest.mark.django_db
def test_service_stop_success(client, get_operators):
    operator = get_operators[1]
    client.force_login(operator)
    PERSONAL_PAGE_URL = f"{URL_PREFIX}{operator.id}/"
    START_URL = f"{PERSONAL_PAGE_URL}{START_POSTFIX_URL}"
    STOP_URL = f"{PERSONAL_PAGE_URL}{STOP_POSTFIX_URL}"
    available_tasks = operator.task_set.all().order_by('id')

    # START SERVING
    form_data = {
        'primary_task': available_tasks[0].id,
        'secondary_tasks': (
            available_tasks[0].id,
            available_tasks[1].id,
            available_tasks[2].id,
        )
    }
    response = client.post(START_URL, form_data, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (PERSONAL_PAGE_URL, 302)
    ]
    assert "Stop service" in content

    # STOP SERVING
    response = client.post(STOP_URL, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (PERSONAL_PAGE_URL, 302)
    ]
    assert "Stop service" not in content
    assert "Start service" in content


@pytest.mark.django_db
def test_service_stop_success_with_supervisor(
            client, get_operators, get_supervisors):
    operator = get_operators[1]
    client.force_login(get_supervisors[1])
    PERSONAL_PAGE_URL = f"{URL_PREFIX}{operator.id}/"
    START_URL = f"{PERSONAL_PAGE_URL}{START_POSTFIX_URL}"
    STOP_URL = f"{PERSONAL_PAGE_URL}{STOP_POSTFIX_URL}"
    available_tasks = operator.task_set.all().order_by('id')

    # START SERVING
    form_data = {
        'primary_task': available_tasks[0].id,
        'secondary_tasks': (
            available_tasks[0].id,
            available_tasks[1].id,
            available_tasks[2].id,
        )
    }
    response = client.post(START_URL, form_data, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (PERSONAL_PAGE_URL, 302)
    ]
    assert "Stop service" in content

    # STOP SERVING
    response = client.post(STOP_URL, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (PERSONAL_PAGE_URL, 302)
    ]
    assert "Stop service" not in content
    assert "Start service" in content


@pytest.mark.django_db
def test_service_stop_with_incorrect_operator(
        client,
        get_operators):
    correct_operator = get_operators[0]
    incorrect_operator = get_operators[1]
    client.force_login(correct_operator)

    PERSONAL_PAGE_URL = f"{URL_PREFIX}{correct_operator.id}/"
    START_URL = f"{PERSONAL_PAGE_URL}{START_POSTFIX_URL}"
    STOP_URL = f"{PERSONAL_PAGE_URL}{STOP_POSTFIX_URL}"
    available_tasks = correct_operator.task_set.all().order_by('id')

    # START SERVING
    form_data = {
        'primary_task': available_tasks[0].id,
        'secondary_tasks': (
            available_tasks[0].id,
            available_tasks[1].id,
            available_tasks[2].id,
        )
    }
    response = client.post(START_URL, form_data, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (PERSONAL_PAGE_URL, 302)
    ]
    assert "Stop service" in content

    # STOP SERVING
    client.force_login(incorrect_operator)
    response = client.post(STOP_URL, follow=True)
    assert response.status_code == 403


@pytest.mark.django_db
def test_service_stop_with_anonymous_user(client, get_operators):
    correct_operator = get_operators[0]
    client.force_login(correct_operator)

    PERSONAL_PAGE_URL = f"{URL_PREFIX}{correct_operator.id}/"
    START_URL = f"{PERSONAL_PAGE_URL}{START_POSTFIX_URL}"
    STOP_URL = f"{PERSONAL_PAGE_URL}{STOP_POSTFIX_URL}"
    available_tasks = correct_operator.task_set.all().order_by('id')

    # START SERVING
    form_data = {
        'primary_task': available_tasks[0].id,
        'secondary_tasks': (
            available_tasks[0].id,
            available_tasks[1].id,
            available_tasks[2].id,
        )
    }
    response = client.post(START_URL, form_data, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (PERSONAL_PAGE_URL, 302)
    ]
    assert "Stop service" in content

    # STOP SERVING
    client.logout()
    response = client.post(STOP_URL, follow=True)
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split(
        '?')[0] == LOGIN_URL
