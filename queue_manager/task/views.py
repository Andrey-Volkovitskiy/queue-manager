from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from queue_manager.task.models import Task as MODEL
from queue_manager.task.models import ITEM_NAME
from queue_manager.task.forms import TaskForm as FORM
from django.urls import reverse_lazy


class ItemListView(ListView):
    model = MODEL
    template_name = f"{ITEM_NAME}/list.html"
    ordering = ['letter_code']

    def get_context_data(self, **kwargs):
        context = super(ItemListView, self).get_context_data(**kwargs)
        context['item_name'] = ITEM_NAME
        return context


class ItemCreateView(
        SuccessMessageMixin,
        CreateView):
    form_class = FORM
    template_name = f"{ITEM_NAME}/create.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully created"

    def get_context_data(self, **kwargs):
        context = super(ItemCreateView, self).get_context_data(**kwargs)
        context['item_name'] = ITEM_NAME
        return context


class ItemUpdateView(
        SuccessMessageMixin,
        UpdateView):
    model = MODEL
    form_class = FORM
    template_name = f"{ITEM_NAME}/update.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully updated"


class ItemDeleteView(
        SuccessMessageMixin,
        DeleteView):
    model = MODEL
    fields = []
    template_name = f"{ITEM_NAME}/delete.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully deleted"
