from django.contrib.auth.mixins import (
            PermissionRequiredMixin,
            UserPassesTestMixin)
from django.views.generic import (View, ListView)
from queue_manager.ticket.models import Ticket as MODEL
from queue_manager.status.models import Status
from queue_manager.ticket.models import ITEM_NAME
from queue_manager.session.models import Session
from queue_manager.mixins import ContextMixinWithItemName
from django.shortcuts import redirect
from django.urls import reverse_lazy


class TicketCompletedViewPermissions(UserPassesTestMixin):
    '''Allows only the processing operator to mark the ticket as completed.
    Or user with "pretend_operator" permission can access it.'''
    def test_func(self):
        request_user = self.request.user
        ticket_id = int(self.kwargs['pk'])
        processing_user = MODEL.objects.get(id=ticket_id).status_set.filter(
            code=Status.objects.Codes.PROCESSING).last().assigned_to
        if request_user == processing_user or (
                request_user.has_perm('user.pretend_operator')):
            return True
        else:
            return False


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
        TicketCompletedViewPermissions,
        View):
    http_method_names = ["post", 'get']

    def post(self, request, *args, **kwargs):
        ticket = MODEL.objects.get(id=self.kwargs['pk'])
        ticket.mark_completed()
        return redirect(reverse_lazy('operator-enter'))  # TODO
