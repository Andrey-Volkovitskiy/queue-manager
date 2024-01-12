from django.views.generic import (TemplateView, DetailView, View)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from queue_manager.mixins import TopNavMenuMixin
from queue_manager.session.models import Session
from queue_manager.task.models import Task
from queue_manager.ticket.models import Ticket
from queue_manager.user.models import Supervisor, Operator
from django.db.models import Subquery


class SupervisorEnterView(View):
    '''Redirects a supervisor to they Personal dashboard page'''
    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        is_supervisor = Supervisor.objects.filter(id=user_id).exists()
        if is_supervisor:
            return redirect(reverse_lazy(
                'supervisor-personal',
                kwargs={'pk': user_id}))
        return redirect(reverse_lazy('supervisor-no-permission'))


class SupervisorNoPermissionView(TopNavMenuMixin, TemplateView):
    template_name = 'supervisor/no_permission.html'


class SupervPersonalPagePermissions(UserPassesTestMixin):
    '''Allows only the user to access his personal page'''
    def test_func(self):
        subject_user_id = self.request.user.id
        object_user_id = self.kwargs.get('pk')
        return True if subject_user_id == object_user_id else False


class SupervisorPersonalView(
        SupervPersonalPagePermissions,
        TopNavMenuMixin,
        DetailView):
    '''Personal dashboard page for the supervisor'''
    model = Supervisor
    template_name = "supervisor/personal.html"
    TICKETS_SHOWN = 20  # Max number of last issued tickets shown on page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = Session.objects.get_current_session()
        context['tasks'] = Task.objects\
            .filter(deleted_at__isnull=True).order_by('letter_code')
        context['servicing_operators'] = Operator.objects\
            .filter(service__priority__gt=0)\
            .distinct().order_by('first_name', 'last_name')

        last_session = Subquery(
            Session.objects
            .order_by('-id')
            .values('id')[:1])
        context['last_tickets'] = Ticket.objects\
            .filter(session=last_session)\
            .order_by('-id')[0: self.TICKETS_SHOWN]
        return context
