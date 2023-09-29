import pytest
from queue_manager.user.models import Supervisor
from queue_manager.user.models import Operator


@pytest.mark.django_db
def test_supervisor_queryset(get_supervisors):
    expected_supervisor = get_supervisors[0]
    first_supervisor = Supervisor.objects.first()
    assert first_supervisor == expected_supervisor


@pytest.mark.django_db
def test_operator_queryset(get_operators):
    expected_operators = get_operators
    proxy_model_operators = Operator.objects.all()
    assert len(proxy_model_operators) == len(expected_operators)
    for i in range(len(expected_operators)):
        assert expected_operators[i] in proxy_model_operators
