from queue_manager.user.models import Operator
from queue_manager.task.models import Task


def add_base_services():
    operators = Operator.objects.all().order_by('id')
    tasks = Task.objects.all().order_by('id')

    operators[0].task_set.set((
        tasks[0],
        tasks[1],
        tasks[2],
    ))

    operators[1].task_set.set((
        tasks[0],
        tasks[1],
        tasks[2],
        tasks[3],
    ))

    operators[2].task_set.set((
        tasks[0],
    ))
