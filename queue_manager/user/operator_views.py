from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from queue_manager.mixins import TopNavMenuMixin
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView,
                                  DetailView,
                                  TemplateView,
                                  View,)
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from queue_manager.session.models import Session
from queue_manager.user.models import Operator as MODEL
from queue_manager.task.models import Service, Task
from queue_manager.status.models import Status
from queue_manager.user import forms
from queue_manager.mixins import ContextMixinWithItemName
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Prefetch

ITEM_NAME = 'operator'


class OperatorEnterView(View):
    '''Redirects the operator to they Personal dashboard page.
    Or gives to a supervisor ability to select desired Operator dashboard.'''
    def get(self, request, *args, **kwargs):
        if self.request.user.has_perm('user.pretend_operator'):
            return redirect(reverse_lazy('operator-select'))

        user_id = self.request.user.id
        is_operator = MODEL.objects.filter(id=user_id).exists()
        if is_operator:
            return redirect(reverse_lazy(
                'operator-personal',
                kwargs={'pk': user_id}))

        return redirect(reverse_lazy('operator-no-permission'))


class OperatorPersonalPagePermissions(UserPassesTestMixin):
    '''Allows only the operator to access his personal page.
    Or user with "pretend_operator" permission can access it.'''
    def test_func(self):
        subject_user = self.request.user
        object_user_id = self.kwargs.get('pk')
        if subject_user.id == object_user_id or (
                subject_user.has_perm('user.pretend_operator')):
            return True
        else:
            return False


class OperatorPersonalView(
        OperatorPersonalPagePermissions,
        TopNavMenuMixin,
        DetailView):
    '''Personal dashboard page for an operator'''
    QUEUE_LEN_LIMIT = 6  # Max number tickets to be processed shown
    PROCESSED_STATUSES_LIMIT = 9  # Max number of processed tickets (statuses)
    model = MODEL
    template_name = "operator/personal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        operator = self.object

        # Currently serviced tasks
        active_services = operator.service_set.filter(
            priority__gt=0)
        context['is_servicing'] = bool(active_services)

        primary_service = active_services.filter(
            priority=Service.HIGHEST_PRIORITY).last()
        if primary_service:
            context['primary_task'] = primary_service.task
            secondary_services = active_services.exclude(
                id=primary_service.id)
            if secondary_services:
                context['secondary_tasks'] = Task.objects.filter(
                    service__in=secondary_services).order_by('id')

        # Queues
        context['queue_len_limit'] = self.QUEUE_LEN_LIMIT
        context['personal_tickets'] = operator\
            .get_personal_tickets(limit=self.QUEUE_LEN_LIMIT)
        context['primary_tickets'] = operator\
            .get_primary_tickets(limit=self.QUEUE_LEN_LIMIT)
        context['secondary_tickets'] = operator\
            .get_secondary_tickets(limit=self.QUEUE_LEN_LIMIT)

        # Processed tickets
        last_session = Session.objects.last()
        context['processed_statuses_limit'] = self.PROCESSED_STATUSES_LIMIT

        context['completed_statuses'] = Status.objects\
            .filter(
                code=Status.objects.Codes.COMPLETED,
                assigned_by=operator,
                ticket__session=last_session)\
            .select_related('ticket')\
            .only('ticket__code', 'code')\
            .order_by('-assigned_at')[:self.PROCESSED_STATUSES_LIMIT]

        context['missed_statuses'] = Status.objects\
            .filter(
                code=Status.objects.Codes.MISSED,
                assigned_by=operator,
                ticket__session=last_session)\
            .select_related('ticket')\
            .only('ticket__code', 'code')\
            .order_by('-assigned_at')[:self.PROCESSED_STATUSES_LIMIT]

        context['redirected_statuses'] = Status.objects\
            .filter(
                code=Status.objects.Codes.REDIRECTED,
                assigned_by=operator,
                ticket__session=last_session)\
            .select_related('ticket')\
            .only('ticket__code', 'code')\
            .order_by('-assigned_at')[:self.PROCESSED_STATUSES_LIMIT]

        return context


class OperatorNoPermissionView(TopNavMenuMixin, TemplateView):
    template_name = 'operator/no_permission.html'


class OperatorSelectView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        TopNavMenuMixin,
        ListView):
    '''Gives to a supervisor ability to select desired Operator dashboard'''
    model = MODEL
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/select.html"
    ordering = ['first_name', 'last_name']
    permission_required = 'user.pretend_operator'


class OperatorStartServiceView(
        OperatorPersonalPagePermissions,
        TopNavMenuMixin,
        UpdateView):
    '''The operator starts to serve seleced tasks'''
    model = MODEL
    form_class = forms.OperatorStartServiceForm
    template_name = "operator/service_start.html"

    def get_success_url(self):
        return reverse_lazy(
            'operator-personal', kwargs={'pk': self.kwargs['pk']})


class OperatorStopServiceView(
        OperatorPersonalPagePermissions,
        View):
    '''The operator stops to serve all tasks'''
    http_method_names = ["post", ]

    def post(self, request, *args, **kwargs):
        operator_id = self.kwargs['pk']
        active_services = Service.objects\
            .filter(
                operator_id=operator_id,
                priority__gt=0)
        if active_services:
            active_services.update(priority=Service.NOT_IN_SERVICE)
        return redirect(reverse_lazy(
            'operator-personal', kwargs={'pk': operator_id}))


class ItemListView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        TopNavMenuMixin,
        ListView):
    '''Show list of operators'''
    model = MODEL
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/list.html"
    permission_required = f'user.view_{ITEM_NAME}'

    def get_queryset(self):
        prim_served_tasks = Task.objects\
            .filter(service__priority=Service.HIGHEST_PRIORITY)\
            .distinct()

        scnd_served_tasks = Task.objects\
            .filter(
                service__priority__lt=Service.HIGHEST_PRIORITY,
                service__priority__gt=Service.NOT_IN_SERVICE)\
            .distinct()\
            .order_by('letter_code')

        return self.model.objects\
            .all()\
            .prefetch_related(
                'task_set',
                Prefetch(
                    'task_set',
                    queryset=prim_served_tasks,
                    to_attr='prim_served_tasks'),
                Prefetch(
                    'task_set',
                    queryset=scnd_served_tasks,
                    to_attr='scnd_served_tasks'))\
            .order_by('first_name', 'last_name')


class ItemCreateView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        TopNavMenuMixin,
        CreateView):
    '''Create a new operator'''
    form_class = forms.OperatorCreateForm
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/create.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully created"
    permission_required = f'user.add_{ITEM_NAME}'


class ItemUpdateView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        TopNavMenuMixin,
        UpdateView):
    '''Update an operator'''
    model = MODEL
    form_class = forms.OperatorUpdateForm
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/update.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully updated"
    permission_required = f'user.change_{ITEM_NAME}'


class UpdatePassView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        TopNavMenuMixin,
        UpdateView):
    '''Update a password for an operator'''
    model = MODEL
    form_class = forms.OperatorChangePasswordForm
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/pass_change.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully updated"
    permission_required = f'user.change_{ITEM_NAME}'


class ItemSoftDeleteView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        SuccessMessageMixin,
        TopNavMenuMixin,
        DeleteView):
    '''Delete an operator'''
    model = MODEL
    fields = []
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/delete.html"
    success_url = reverse_lazy(f"{ITEM_NAME}-list")
    success_message = f"The {ITEM_NAME} was successfully deleted"
    permission_required = f'user.delete_{ITEM_NAME}'

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_active = False
        self.object.save()
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return HttpResponseRedirect(success_url)
