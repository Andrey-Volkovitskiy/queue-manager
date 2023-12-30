from django.views.generic import (TemplateView, DetailView, ListView, View)
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Subquery
from queue_manager.ticket.models import Ticket
from queue_manager.session.models import Session
from queue_manager.task.models import Task
from queue_manager.status.models import Status
from queue_manager.mixins import TopNavMenuMixin
from django.urls import reverse_lazy
import random


class PrintTicketView(TopNavMenuMixin, TemplateView):
    '''Issuing a new ticket to a client'''
    TASK_CODE_PREFIX = "task_code:"
    template_name = "client/print_ticket.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = Task.objects.order_by('letter_code')
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
        chosen_task = Task.objects.get(letter_code=task_code)

        try:
            ticket = Ticket.objects.create_ticket(task=chosen_task)
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
                                     f"?track_ticket={self.get_object().id}")
        return context


class NoActiveSessionView(TopNavMenuMixin, TemplateView):
    template_name = "client/no-active-session.html"


class ScreenView(TopNavMenuMixin, ListView):
    VISIBLE_TICKETS_QUAN = 7
    template_name = "client/screen.html"

    def get_queryset(self):
        last_session_id = Subquery(
            Session.objects.order_by('-started_at').values('id')[:1])
        return Status.objects\
            .filter(
                ticket__session__id=last_session_id,
                code=Status.objects.Codes.PROCESSING)\
            .order_by('-assigned_at')[:self.VISIBLE_TICKETS_QUAN]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        track_ticket_id = self.request.GET.get('track_ticket')
        track_ticket = Ticket.objects.filter(id=track_ticket_id).last()
        if track_ticket:
            context['track_ticket'] = track_ticket
        return context


class Print10TicketsView(View):
    http_method_names = ["post", ]

    def post(self, *args, **kwargs):
        for _ in range(10):
            random_task = random.choice(Task.objects.all())
            Ticket.objects.create_ticket(random_task)

        messages.add_message(
                self.request,
                messages.SUCCESS,
                "10 random tickets were successfully added to the queue"
            )
        return redirect(reverse_lazy('home'))
