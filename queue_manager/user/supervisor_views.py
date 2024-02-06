from django.views.generic import (TemplateView, DetailView, View)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from queue_manager.mixins import TopNavMenuMixin
from queue_manager.session.models import Session
from queue_manager.status.models import Status
from queue_manager.task.models import Task, Service
from queue_manager.ticket.models import Ticket
from queue_manager.user.models import Supervisor, Operator
from django.db.models import Prefetch


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
    '''Personal dashboard page for a supervisor'''
    model = Supervisor
    template_name = "supervisor/personal.html"
    TICKETS_SHOWN = 20  # Max number of last issued tickets shown on page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Session
        context['current_session'] = Session.objects.get_current_session()

        # Tasks
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

        context['tasks'] = Task.objects\
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
            .annotate(
                count_tickets_unproc=Task.subq_count_tickets_unprocessed(),
                count_tickets_compl=Task.subq_count_tickets_completed())\
            .order_by('letter_code')

        # Operators
        prim_served_tasks = Task.objects\
            .filter(service__priority=Service.HIGHEST_PRIORITY)\
            .distinct()\
            .only('letter_code')

        scnd_served_tasks = Task.objects\
            .filter(
                service__priority__lt=Service.HIGHEST_PRIORITY,
                service__priority__gt=Service.NOT_IN_SERVICE)\
            .distinct()\
            .order_by('letter_code')\
            .only('letter_code')

        context['servicing_operators'] = Operator.objects\
            .filter(service__priority__gt=0)\
            .distinct()\
            .order_by('first_name', 'last_name')\
            .annotate(
                curr_ticket_code=Operator.subq_current_ticket_code(),
                count_tickets_compl=Operator.subq_count_tickets_completed())\
            .prefetch_related(
                Prefetch(
                    'task_set',
                    queryset=prim_served_tasks,
                    to_attr='prim_served_tasks'),
                Prefetch(
                    'task_set',
                    queryset=scnd_served_tasks,
                    to_attr='scnd_served_tasks'))\
            .only('first_name', 'last_name')

        # Tickets
        context['last_tickets'] = Ticket.objects\
            .filter(session=Session.objects.subq_last_session_id())\
            .only('code')\
            .prefetch_related(
                Prefetch(
                    'status_set',
                    queryset=Status.objects.order_by('-assigned_at')[:1],
                    to_attr='last_status'),)\
            .order_by('-id')[0: self.TICKETS_SHOWN]
        return context
