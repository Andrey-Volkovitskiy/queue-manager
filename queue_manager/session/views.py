from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (View, TemplateView, ListView)
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Count
from queue_manager.session.models import ITEM_NAME
from queue_manager.mixins import ContextMixinWithItemName
from queue_manager.mixins import TopNavMenuMixin
from queue_manager.session.models import Session as MODEL


class SessionListView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        TopNavMenuMixin,
        ListView):
    model = MODEL
    paginate_by = 10
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/list.html"
    permission_required = f'{ITEM_NAME}.view_{ITEM_NAME}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_session_exists'] = bool(
            self.model.objects.get_current_session())
        return context

    def get_queryset(self):
        return self.model.objects\
            .all()\
            .select_related('started_by', 'finished_by')\
            .annotate(num_tickets_issued=Count('ticket'))\
            .only(
                'code',
                'started_at',
                'finished_at',
                'started_by__first_name',
                'started_by__last_name',
                'finished_by__first_name',
                'finished_by__last_name')\
            .order_by('-started_at')


class SessionStartView(
        PermissionRequiredMixin,
        TopNavMenuMixin,
        View):
    '''Every day a supervisor starts a new session.
    If there is an active session, clients can print new tickets.'''
    success_url = reverse_lazy("supervisor-enter")
    permission_required = (f'{ITEM_NAME}.add_{ITEM_NAME}', )

    def post(self, request):
        try:
            MODEL.objects.start_new_session(self.request.user)
            messages.add_message(
                self.request,
                messages.SUCCESS,
                f"The {ITEM_NAME} was successfully started"
            )
        except MODEL.objects.ActiveSessionAlreadyExistsError:
            messages.add_message(
                self.request,
                messages.ERROR,
                (f"The {ITEM_NAME} can't be started" +
                 " because another active session exists")
            )
        return redirect(self.success_url)


class SessionFinishView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        TopNavMenuMixin,
        TemplateView):
    '''If a supervisor finished the session, clients can't print no more
    tickets. But issued tickets still can be served by operators.'''
    model = MODEL
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/finish.html"
    success_url = reverse_lazy("supervisor-enter")
    permission_required = (f'{ITEM_NAME}.change_{ITEM_NAME}', )

    def post(self, request):
        try:
            MODEL.objects.finish_current_session(self.request.user)
            messages.add_message(
                self.request,
                messages.SUCCESS,
                f"The {ITEM_NAME} was successfully finished"
            )
        except MODEL.objects.NoActiveSessionsError:
            messages.add_message(
                self.request,
                messages.ERROR,
                (f"The {ITEM_NAME} can't be finished" +
                 " because there is no active session")
            )
        return redirect(self.success_url)

    def get(self, request, *args, **kwargs):
        current_session = MODEL.objects\
            .filter(finished_at__isnull=True)\
            .select_related('started_by')\
            .first()
        if current_session:
            context = self.get_context_data(**kwargs)
            context['current_session'] = current_session
            return self.render_to_response(context)
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                (f"The {ITEM_NAME} can't be finished" +
                 " because there is no active session")
            )
            return redirect(self.success_url)
