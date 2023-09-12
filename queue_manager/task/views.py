from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from queue_manager.task.models import Task
from queue_manager.task.forms import TaskForm
from django.urls import reverse_lazy


class TaskListView(ListView):
    model = Task
    template_name = "task/list.html"
    ordering = ['id']


class TaskCreateView(
        SuccessMessageMixin,
        CreateView):
    form_class = TaskForm
    template_name = "task/create.html"
    success_url = reverse_lazy("task-list")
    success_message = "The task was successfully created"


class TaskUpdateView(
        SuccessMessageMixin,
        UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "task/update.html"
    success_url = reverse_lazy("task-list")
    success_message = "The task was successfully updated"


class TaskDeleteView(
        SuccessMessageMixin,
        DeleteView):
    model = Task
    fields = []
    template_name = "task/delete.html"
    success_url = reverse_lazy("task-list")
    success_message = "The task was successfully deleted"
