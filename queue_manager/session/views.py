from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (View, TemplateView, ListView)
from django.urls import reverse_lazy
from django.shortcuts import redirect
from queue_manager.session.models import ITEM_NAME
from queue_manager.mixins import ContextMixinWithItemName
from queue_manager.mixins import TopNavMenuMixin
from queue_manager.session.models import Session as MODEL


class ItemListView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        TopNavMenuMixin,
        ListView):
    model = MODEL
    paginate_by = 10
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/list.html"
    ordering = ['-started_at']
    permission_required = f'{ITEM_NAME}.view_{ITEM_NAME}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.model.objects.get_current_session():
            context['active_session_exists'] = True
        else:
            context['active_session_exists'] = False
        return context


class ItemStartView(
        PermissionRequiredMixin,
        TopNavMenuMixin,
        View):
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


class ItemFinishView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        TopNavMenuMixin,
        TemplateView):
    model = MODEL
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/finish.html"
    success_url = reverse_lazy("supervisor-enter")
    permission_required = (f'{ITEM_NAME}.change_{ITEM_NAME}', )

    def post(self, request):
        try:
            MODEL.objects.finish_active_session(self.request.user)
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
        if MODEL.objects.get_current_session():
            return super().get(request, *args, **kwargs)
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                (f"The {ITEM_NAME} can't be finished" +
                 " because there is no active session")
            )
            return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = self.model.objects.get_current_session()
        return context
