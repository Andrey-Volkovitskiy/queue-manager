from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView,
                                  DetailView,
                                  TemplateView,
                                  View,)
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from queue_manager.user.models import Operator as MODEL
from queue_manager.task.models import Service, Task
from queue_manager.user import forms
from queue_manager.mixins import ContextMixinWithItemName
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages

ITEM_NAME = 'operator'


class OperatorEnterView(View):
    '''Redirects the operator to they Personal dashboard page.
    Or gives to a supervisor ability to select desired Operator dashboard.'''
    def get(self, request, *args, **kwargs):
        if self.request.user.has_perm('user.pretend_operator'):
            return redirect(reverse_lazy('operator-select'))

        user_id = self.request.user.id
        is_operator = MODEL.objects.filter(id=user_id).exists()
        if is_operator:
            return redirect(reverse_lazy(
                'operator-personal',
                kwargs={'pk': user_id}))

        return redirect(reverse_lazy('operator-no-permission'))


class PersonalOperPagePermissions(UserPassesTestMixin):
    '''Allows only the operator to access his personal page.
    Or user with "pretend_operator" permission can access it.'''
    def test_func(self):
        subject_user = self.request.user
        object_user = self.get_object()
        if subject_user == object_user or (
                subject_user.has_perm('user.pretend_operator')):
            return True
        else:
            return False


class OperatorPersonalView(
        PersonalOperPagePermissions,
        DetailView):
    model = MODEL
    template_name = "operator/personal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        available_services = self.get_object().service_set
        context['is_servicing'] = available_services.filter(
            is_servicing=True).exists()

        active_services = self.get_object().service_set.filter(
            is_servicing=True)
        primary_service = active_services.filter(
            priority_for_operator=Service.HIGHEST_PRIORITY).last()
        if primary_service:
            context['primary_task'] = primary_service.task
            secondaty_services = active_services.exclude(
                id=primary_service.id)
            if secondaty_services:
                context['secondary_tasks'] = Task.objects.filter(
                    service__in=secondaty_services)
        return context


class OperatorNoPermissionView(TemplateView):
    template_name = 'operator/no_permission.html'


class OperatorSelectView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        ListView):
    model = MODEL
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/select.html"
    ordering = ['first_name', 'last_name']
    permission_required = 'user.pretend_operator'


class OperatorStartServiceView(
        PersonalOperPagePermissions,
        UpdateView):
    model = MODEL
    form_class = forms.OperatorStartServiceForm
    template_name = "operator/service_start.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_tasks'] = self.get_object().task_set.all()
        return context

    def get_success_url(self):
        return reverse_lazy(
            'operator-personal', kwargs={'pk': self.kwargs['pk']})


class ItemListView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        ListView):
    model = MODEL
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/list.html"
    ordering = ['first_name', 'last_name']
    permission_required = f'user.view_{ITEM_NAME}'


class ItemCreateView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        CreateView):
    form_class = forms.OperatorCreateForm
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/create.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully created"
    permission_required = f'user.add_{ITEM_NAME}'


class ItemUpdateView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        UpdateView):
    model = MODEL
    form_class = forms.OperatorUpdateForm
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/update.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully updated"
    permission_required = f'user.change_{ITEM_NAME}'


class UpdatePassView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        UpdateView):
    model = MODEL
    form_class = forms.OperatorChangePasswordForm
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/pass_change.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully updated"
    permission_required = f'user.change_{ITEM_NAME}'


class ItemSoftDeleteView(
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
    permission_required = f'user.delete_{ITEM_NAME}'

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_active = False
        self.object.save()
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return HttpResponseRedirect(success_url)
