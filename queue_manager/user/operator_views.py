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
from queue_manager.user import forms
from queue_manager.mixins import (ContextMixinWithItemName,
                                  PersonalPagePermissions,)
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


class OperatorPersonalView(
        PersonalPagePermissions,
        DetailView):
    model = MODEL
    template_name = "operator/personal.html"


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
