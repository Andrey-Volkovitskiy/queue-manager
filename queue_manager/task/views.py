from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from queue_manager.task.models import Task as MODEL
from queue_manager.task.models import ITEM_NAME, Service
from queue_manager.session.models import Session
from queue_manager.user.models import Operator
from queue_manager.task.forms import TaskForm as FORM
from queue_manager.mixins import ContextMixinWithItemName
from queue_manager.mixins import TopNavMenuMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Prefetch


class ItemListView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        TopNavMenuMixin,
        ListView):
    model = MODEL
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/list.html"
    permission_required = f'{ITEM_NAME}.view_{ITEM_NAME}'

    def get_queryset(self):
        '''An optimized query to get all data from DB in one step'''

        prim_served_by = Operator.objects\
            .filter(service__priority=Service.HIGHEST_PRIORITY)\
            .distinct()\
            .order_by('first_name', 'last_name')

        scnd_served_by = Operator.objects\
            .filter(
                service__priority__lt=Service.HIGHEST_PRIORITY,
                service__priority__gt=Service.NOT_IN_SERVICE)\
            .distinct()\
            .order_by('first_name', 'last_name')

        return self.model.objects\
            .all()\
            .prefetch_related(
                'can_be_served_by',
                Prefetch(
                    'can_be_served_by',
                    queryset=prim_served_by,
                    to_attr='prim_served_by'),
                Prefetch(
                    'can_be_served_by',
                    queryset=scnd_served_by,
                    to_attr='scnd_served_by'))\
            .order_by('letter_code')


class ItemCreateView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        TopNavMenuMixin,
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
        TopNavMenuMixin,
        UpdateView):
    model = MODEL
    form_class = FORM
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/update.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully updated"
    permission_required = f'{ITEM_NAME}.change_{ITEM_NAME}'

    def form_valid(self, form):
        '''A letter code can't be modified while
        there is an active session (it can cause integrity conflicts)'''
        letter_code_in_object = self.get_object().letter_code
        letter_code_in_form = form.cleaned_data['letter_code']
        if Session.objects.get_current_session() and (
                letter_code_in_form != letter_code_in_object):
            messages.add_message(
                self.request,
                messages.ERROR,
                ("The letter code can't be modified while "
                 "there is an active session.")
            )
            return redirect('task-list')
        return super().form_valid(form)


class ItemDeleteView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        TopNavMenuMixin,
        DeleteView):
    model = MODEL
    fields = []
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/delete.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully deleted"
    permission_required = f'{ITEM_NAME}.delete_{ITEM_NAME}'

    def form_valid(self, form):
        '''A task can't be deleted while
        there is an active session (it can cause integrity conflicts)'''
        if Session.objects.get_current_session():
            messages.add_message(
                self.request,
                messages.ERROR,
                ("A task can't be deleted while "
                 "there is an active session.")
            )
            return redirect('task-list')
        return super().form_valid(form)
