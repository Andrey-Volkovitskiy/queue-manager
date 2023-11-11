from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (View, ListView)
from queue_manager.ticket.models import Ticket as MODEL
from queue_manager.ticket.models import ITEM_NAME
from queue_manager.session.models import Session
from queue_manager.mixins import ContextMixinWithItemName
from django.shortcuts import redirect
from django.urls import reverse_lazy


class ItemListView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        ListView):
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/list.html"
    ordering = ['-code']
    permission_required = f'{ITEM_NAME}.view_{ITEM_NAME}'

    def get_queryset(self):
        return MODEL.objects.filter(
            session=Session.objects.get_current_session())


class TicketCompletedView(
        View):  # TODO Add permissions
    http_method_names = ["post", ]

    def post(self, request, *args, **kwargs):
        ticket = MODEL.objects.get(id=self.kwargs['pk'])
        ticket.mark_completed()
        return redirect(reverse_lazy('operator-enter'))  # TODO
