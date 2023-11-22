from django.views.generic import (TemplateView, DetailView)
from django.shortcuts import redirect
from queue_manager.ticket.models import Ticket
from queue_manager.session.models import Session
from queue_manager.task.models import Task
from queue_manager.mixins import TopNavMenuMixin
from django.urls import reverse_lazy

TASK_CODE_PREFIX = "task_code:"


class PrintTicketView(TopNavMenuMixin, TemplateView):
    template_name = "client/print_ticket.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = Task.objects\
            .filter(is_active=True).order_by('letter_code')
        context['code_prefix'] = TASK_CODE_PREFIX
        return context

    def get(self, request, *args, **kwargs):
        if not Session.objects.get_current_session():
            return redirect(reverse_lazy('printer-no-active-session'))
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        task_code = None
        for key in request.POST.keys():
            if (key.startswith(TASK_CODE_PREFIX)
                    and len(key) == len(TASK_CODE_PREFIX) + 1):
                task_code = key[len(TASK_CODE_PREFIX)]

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


class NoActiveSessionView(TopNavMenuMixin, TemplateView):
    template_name = "client/no-active-session.html"
