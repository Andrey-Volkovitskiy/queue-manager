from django.contrib.auth.mixins import (
            PermissionRequiredMixin,
            UserPassesTestMixin)
from django.views.generic import (View, UpdateView, ListView, DetailView)
from django.contrib.messages.views import SuccessMessageMixin
from queue_manager.ticket.models import Ticket as MODEL
from queue_manager.status.models import Status
from queue_manager.ticket.models import ITEM_NAME
from queue_manager.session.models import Session
from queue_manager.mixins import ContextMixinWithItemName
from queue_manager.mixins import TopNavMenuMixin
from queue_manager.ticket import forms
from django.shortcuts import redirect
from django.urls import reverse_lazy


class OperatorIsLastAssignedToPermis(UserPassesTestMixin):
    '''Allows access the ticket only the operator who was last assigned to.
    Or a user with "pretend_operator" permission'''
    def test_func(self):
        request_user = self.request.user
        if request_user.has_perm('user.pretend_operator'):
            return True

        ticket_id = int(self.kwargs['pk'])
        last_ticket_assigned_to_status = MODEL.objects.get(id=ticket_id)\
            .status_set.filter(assigned_to__isnull=False).last()
        if last_ticket_assigned_to_status and (
                last_ticket_assigned_to_status.assigned_to == request_user):
            return True
        return False


class OperatorWasAssignedToPermis(UserPassesTestMixin):
    '''Allows access the ticket only those operators to whom it was
    once assigned.
    Or a user with "pretend_operator" permission'''
    def test_func(self):
        request_user = self.request.user
        if request_user.has_perm('user.pretend_operator'):
            return True

        ticket_id = int(self.kwargs['pk'])
        if MODEL.objects.get(id=ticket_id)\
                .status_set.filter(assigned_to=request_user).exists():
            return True
        return False


class ItemListView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        TopNavMenuMixin,
        ListView):
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/list.html"
    paginate_by = 20
    permission_required = f'{ITEM_NAME}.view_{ITEM_NAME}'

    def get_queryset(self):
        return MODEL.objects\
            .filter(session=Session.objects.get_current_session())\
            .order_by('-id')


class TicketMarkCompletedView(
        OperatorIsLastAssignedToPermis,
        View):
    http_method_names = ["post", ]

    def post(self, request, *args, **kwargs):
        ticket = MODEL.objects.get(id=self.kwargs['pk'])
        ticket.mark_completed()
        assigned_by = ticket.status_set.last().assigned_by
        return redirect(reverse_lazy(
            'operator-personal', kwargs={'pk': assigned_by.id}))


class TicketMarkMissedView(
        OperatorIsLastAssignedToPermis,
        View):
    http_method_names = ["post", ]

    def post(self, request, *args, **kwargs):
        ticket = MODEL.objects.get(id=self.kwargs['pk'])
        ticket.mark_missed()
        assigned_by = ticket.status_set.last().assigned_by
        return redirect(reverse_lazy(
            'operator-personal', kwargs={'pk': assigned_by.id}))


class TicketRedirectView(
        OperatorIsLastAssignedToPermis,
        SuccessMessageMixin,
        TopNavMenuMixin,
        UpdateView):
    model = MODEL
    form_class = forms.TicketRedirectForm
    template_name = f"{ITEM_NAME}/redirect.html"
    success_message = "The ticket was successfully redirected"

    def get_success_url(self):
        redirected_by = self.request.GET.get('operator')
        return reverse_lazy(
            'operator-personal',
            kwargs={'pk': redirected_by})

    def form_valid(self, form):
        ticket = self.get_object()
        redirect_to = form.cleaned_data['redirect_to']
        ticket.redirect(redirect_to=redirect_to)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        redirected_by = self.request.GET.get('operator')
        if redirected_by:
            kwargs['redirected_by'] = redirected_by
        return kwargs


class TicketTakeAgainView(
        OperatorIsLastAssignedToPermis,
        TopNavMenuMixin,
        View):
    http_method_names = ["post", ]

    def post(self, request, *args, **kwargs):
        ticket = MODEL.objects.get(id=self.kwargs['pk'])
        last_operator = ticket.status_set\
            .filter(
                code=Status.objects.Codes.PROCESSING
            ).last().assigned_to
        ticket.redirect(redirect_to=last_operator)
        return redirect(reverse_lazy(
            'operator-personal', kwargs={'pk': last_operator.id}))


class ItemDetailView(
        OperatorWasAssignedToPermis,
        ContextMixinWithItemName,
        TopNavMenuMixin,
        DetailView):
    model = MODEL
    item_name = ITEM_NAME  # TODO permissions
    template_name = f"{ITEM_NAME}/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        redirecteble_statuses = (
            Status.objects.Codes.COMPLETED,
            Status.objects.Codes.MISSED
        )
        last_status = self.get_object().status_set.last()
        if last_status:
            context['ticket_is_redirectable'] = (
                last_status.code in redirecteble_statuses)
            context['last_operator'] = last_status.assigned_by
        return context
