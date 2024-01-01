from django.views.generic import (TemplateView, DetailView, View)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from queue_manager.mixins import TopNavMenuMixin
from queue_manager.session.models import Session
from queue_manager.task.models import Task
from queue_manager.ticket.models import Ticket
from queue_manager.user.models import Supervisor, Operator


class SupervisorEnterView(View):
    '''Redirects the supervisor to they Personal dashboard page'''
    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        is_supervisor = Supervisor.objects.filter(id=user_id).exists()
        if is_supervisor:
            return redirect(reverse_lazy(
                'supervisor-personal',
                kwargs={'pk': user_id}))
        return redirect(reverse_lazy('supervisor-no-permission'))


class SupervPersonalPagePermissions(UserPassesTestMixin):
    '''Allows only the user to access his personal page'''
    def test_func(self):
        subject_user = self.request.user
        object_user = self.get_object()
        if subject_user == object_user:
            return True
        else:
            return False


class SupervisorNoPermissionView(TopNavMenuMixin, TemplateView):
    template_name = 'supervisor/no_permission.html'


class SupervisorPersonalView(
        SupervPersonalPagePermissions,
        TopNavMenuMixin,
        DetailView):
    model = Supervisor
    template_name = "supervisor/personal.html"
    TICKETS_SHOWN = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = Session.objects.get_current_session()
        context['tasks'] = Task.objects\
            .filter(deleted_at__isnull=True).order_by('letter_code')
        context['servicing_operators'] = Operator.objects\
            .filter(service__priority__gt=0)\
            .distinct().order_by('first_name', 'last_name')
        context['last_tickets'] = Ticket.objects\
            .filter(session=Session.objects.last())\
            .order_by('-id')[0: self.TICKETS_SHOWN]
        return context
