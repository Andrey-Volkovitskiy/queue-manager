from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from queue_manager.task.models import Task as MODEL
from queue_manager.task.models import ITEM_NAME
from queue_manager.task.forms import TaskForm as FORM
from queue_manager.mixins import ContextMixinWithItemName
from django.urls import reverse_lazy


class ItemListView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        ListView):
    model = MODEL
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/list.html"
    ordering = ['letter_code']
    permission_required = f'{ITEM_NAME}.view_{ITEM_NAME}'


class ItemCreateView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        CreateView):
    form_class = FORM
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/create.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully created"
    permission_required = f'{ITEM_NAME}.add_{ITEM_NAME}'


class ItemUpdateView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        UpdateView):
    model = MODEL
    form_class = FORM
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/update.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully updated"
    permission_required = f'{ITEM_NAME}.change_{ITEM_NAME}'
    # TODO Task letter code can't be modified or deleted while
    # there is an active session


class ItemDeleteView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        DeleteView):
    model = MODEL
    fields = []
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/delete.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully deleted"
    permission_required = f'{ITEM_NAME}.delete_{ITEM_NAME}'
