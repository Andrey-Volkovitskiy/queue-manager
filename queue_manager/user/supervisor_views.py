from django.views.generic import (TemplateView, DetailView, View)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from queue_manager.mixins import PersonalPagePermissions
from queue_manager.user.models import Supervisor as MODEL


class SupervisorEnterView(View):
    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        is_supervisor = MODEL.objects.filter(id=user_id).exists()
        if is_supervisor:
            return redirect(reverse_lazy(
                'supervisor-personal',
                kwargs={'pk': user_id}))
        return redirect(reverse_lazy('supervisor-no-permission'))


class SupervisorPersonalView(
        PersonalPagePermissions,
        DetailView):
    model = MODEL
    template_name = "supervisor/personal.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     user_id = self.request.user.id
    #     context['permissions'] = MODEL.objects.get(
    #         id=user_id).get_all_permissions()
    #     return context


class SupervisorNoPermissionView(TemplateView):
    template_name = 'supervisor/no_permission.html'
