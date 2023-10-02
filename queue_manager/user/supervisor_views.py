from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (TemplateView)
from queue_manager.session.models import Session as MODEL


class SupervisorHomeView(
        PermissionRequiredMixin,
        TemplateView):
    model = MODEL
    ITEM_NAME = 'supervisor'
    template_name = f"{ITEM_NAME}/home.html"
    permission_required = (f'{ITEM_NAME}.view_{ITEM_NAME}', )
