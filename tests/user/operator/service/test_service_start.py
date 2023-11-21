import pytest
from tests.conftest import LOGIN_URL
from .. import conftest as package_conftest
from queue_manager.task.models import Task

URL_PREFIX = package_conftest.ITEM_ENTER_URL
START_POSTFIX_URL = package_conftest.SERVICE_START_POSTFIX_URL


@pytest.mark.django_db
def test_service_basic_content(client, get_operators):
    correct_operator = get_operators[0]
    client.force_login(correct_operator)
    TESTED_URL = f"{URL_PREFIX}{correct_operator.id}/"

    response = client.get(TESTED_URL, follow=True)
    content = response.content.decode()

    assert "Operator dashboard" in content
    assert "Start service" in content


@pytest.mark.django_db
def test_service_start_success(client, get_operators):
    operator = get_operators[0]
    client.force_login(operator)
    PERSONAL_PAGE_URL = f"{URL_PREFIX}{operator.id}/"
    TESTED_URL = f"{PERSONAL_PAGE_URL}{START_POSTFIX_URL}"
    available_tasks = operator.task_set.all().order_by('id')
    unavailable_tasks = Task.objects.all().exclude(
        id__in=available_tasks.values_list("id", flat=True))

    # GET
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert "Start service tasks" in content
    assert "Primary task" in content
    assert "Secondary tasks" in content
    for available_task in available_tasks:
        assert available_task.name in content
    for unavailable_task in unavailable_tasks:
        assert unavailable_task.name not in content

    # POST
    form_data = {
        'primary_task': available_tasks[0].id,
        'secondary_tasks': (
            available_tasks[0].id,
            available_tasks[1].id,
            available_tasks[2].id,
        )
    }
    response = client.post(TESTED_URL, form_data, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (PERSONAL_PAGE_URL, 302)
    ]
    assert "Stop service" in content
    assert "Start service" not in content
    primary_string = f'Primary task "{available_tasks[0].letter_code}"'
    assert primary_string in content
    secondary_letter_codes = ','.join((
        available_tasks[1].letter_code,
        available_tasks[2].letter_code
    ))
    secondary_string = f'andsecondarytask(s):{secondary_letter_codes}'
    clean_content = content.replace("\n", "").replace(" ", "")
    assert secondary_string in clean_content


@pytest.mark.django_db
def test_service_start_success_with_supervisor(
            client, get_operators, get_supervisors):
    operator = get_operators[1]
    client.force_login(get_supervisors[1])
    PERSONAL_PAGE_URL = f"{URL_PREFIX}{operator.id}/"
    TESTED_URL = f"{PERSONAL_PAGE_URL}{START_POSTFIX_URL}"
    available_tasks = operator.task_set.all().order_by('id')
    unavailable_tasks = Task.objects.all().exclude(
        id__in=available_tasks.values_list("id", flat=True))

    # GET
    response = client.get(TESTED_URL)
    content = response.content.decode()
    assert "Start service tasks" in content
    assert "Primary task" in content
    assert "Secondary tasks" in content
    for available_task in available_tasks:
        assert available_task.name in content
    for unavailable_task in unavailable_tasks:
        assert unavailable_task.name not in content

    # POST
    form_data = {
        'primary_task': available_tasks[0].id,
        'secondary_tasks': (
            available_tasks[0].id,
            available_tasks[1].id,
            available_tasks[2].id,
        )
    }
    response = client.post(TESTED_URL, form_data, follow=True)
    content = response.content.decode()
    assert response.redirect_chain == [
        (PERSONAL_PAGE_URL, 302)
    ]
    assert "Stop service" in content
    assert "Start service" not in content
    primary_string = f'Primary task "{available_tasks[0].letter_code}"'
    assert primary_string in content
    secondary_letter_codes = ','.join((
        available_tasks[1].letter_code,
        available_tasks[2].letter_code
    ))
    secondary_string = f'andsecondarytask(s):{secondary_letter_codes}'
    clean_content = content.replace("\n", "").replace(" ", "")
    assert secondary_string in clean_content


@pytest.mark.django_db
def test_service_start_with_incorrect_operator(
        client,
        get_operators):
    correct_operator = get_operators[0]
    incorrect_operator = get_operators[1]
    client.force_login(incorrect_operator)

    PERSONAL_PAGE_URL = f"{URL_PREFIX}{correct_operator.id}/"
    TESTED_URL = f"{PERSONAL_PAGE_URL}{START_POSTFIX_URL}"

    response = client.get(TESTED_URL, follow=True)
    assert response.status_code == 403


@pytest.mark.django_db
def test_service_start_with_anonymous_user(client, get_operators):
    correct_operator = get_operators[0]
    PERSONAL_PAGE_URL = f"{URL_PREFIX}{correct_operator.id}/"
    TESTED_URL = f"{PERSONAL_PAGE_URL}{START_POSTFIX_URL}"

    response = client.get(TESTED_URL, follow=True)
    _ = response.content.decode()
    redirect_url_with_query, status_code = response.redirect_chain[0]
    assert status_code == 302
    assert redirect_url_with_query.split(
        '?')[0] == LOGIN_URL
