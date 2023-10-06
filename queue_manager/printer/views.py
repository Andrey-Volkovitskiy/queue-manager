from django.views.generic import (View, TemplateView)
from django.shortcuts import redirect, render
# from queue_manager.ticket.models import Ticket
from queue_manager.session.models import Session
from queue_manager.task.models import Task
from django.urls import reverse_lazy

TASK_CODE_PREFIX = "task_code:"


class ItemCreateView(View):
    template_name = "printer/create.html"

    def get(self, request, *args, **kwargs):
        if not Session.objects.get_current_session():
            return redirect(reverse_lazy('printer-no-active-session'))
        context = {
            'tasks': Task.objects.filter(
                is_active=True).order_by('letter_code'),
            'code_prefix': TASK_CODE_PREFIX
            }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        task_code = None
        for key in request.POST.keys():
            if (key.startswith(TASK_CODE_PREFIX)
                    and len(key) == len(TASK_CODE_PREFIX) + 1):
                task_code = key[len(TASK_CODE_PREFIX)]

        return render(
            request, self.template_name, context={'task_code': task_code})


class NoActiveSessionView(TemplateView):
    template_name = "printer/no-active-session.html"
