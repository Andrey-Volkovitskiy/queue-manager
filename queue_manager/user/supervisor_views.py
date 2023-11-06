from django.views.generic import (TemplateView, DetailView, View)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from queue_manager.user.models import Supervisor as MODEL


class SupervisorEnterView(View):
    '''Redirects the supervisor to they Personal dashboard page'''
    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        is_supervisor = MODEL.objects.filter(id=user_id).exists()
        if is_supervisor:
            return redirect(reverse_lazy(
                'supervisor-personal',
                kwargs={'pk': user_id}))
        return redirect(reverse_lazy('supervisor-no-permission'))


class PersonalSupervPagePermissions(UserPassesTestMixin):
    '''Allows only the user to access his personal page'''
    def test_func(self):
        subject_user = self.request.user
        object_user = self.get_object()
        if subject_user == object_user:
            return True
        else:
            return False


class SupervisorPersonalView(
        PersonalSupervPagePermissions,
        DetailView):
    model = MODEL
    template_name = "supervisor/personal.html"


class SupervisorNoPermissionView(TemplateView):
    template_name = 'supervisor/no_permission.html'
