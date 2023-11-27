from django.views.generic import (TemplateView, DetailView, ListView)
from django.shortcuts import redirect
from queue_manager.ticket.models import Ticket
from queue_manager.session.models import Session
from queue_manager.task.models import Task
from queue_manager.status.models import Status
from queue_manager.mixins import TopNavMenuMixin
from django.urls import reverse_lazy

from tests.client.test_screen import VISIBLE_TICKETS_QUAN


class PrintTicketView(TopNavMenuMixin, TemplateView):
    TASK_CODE_PREFIX = "task_code:"
    template_name = "client/print_ticket.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = Task.objects\
            .filter(is_active=True).order_by('letter_code')
        context['code_prefix'] = self.TASK_CODE_PREFIX
        return context

    def get(self, request, *args, **kwargs):
        if not Session.objects.get_current_session():
            return redirect(reverse_lazy('printer-no-active-session'))
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        task_code = None
        for key in request.POST.keys():
            if (key.startswith(self.TASK_CODE_PREFIX)
                    and len(key) == len(self.TASK_CODE_PREFIX) + 1):
                task_code = key[len(self.TASK_CODE_PREFIX)]

        try:
            ticket = Ticket.objects.create_ticket(
                task=Task.objects.get(letter_code=task_code))
            return redirect(reverse_lazy(
                'printed-ticket-detail',
                kwargs={'pk': ticket.id}))
        except Session.objects.NoActiveSessionsError:
            return redirect(reverse_lazy('printer-no-active-session'))


class PrintedTicketDetailView(TopNavMenuMixin, DetailView):
    model = Ticket
    template_name = "client/printed_ticket_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['link_to_screen'] = (f"{reverse_lazy('screen')}"
                                     f"?track_ticket={self.get_object().code}")
        return context


class NoActiveSessionView(TopNavMenuMixin, TemplateView):
    template_name = "client/no-active-session.html"


class ScreenView(TopNavMenuMixin, ListView):
    VISIBLE_TICKETS_QUAN = 7
    template_name = "client/screen.html"

    def get_queryset(self):
        return Status.objects\
            .filter(
                ticket__session__is_active=True,
                code=Status.objects.Codes.PROCESSING)\
            .order_by('-assigned_at')[:VISIBLE_TICKETS_QUAN]
