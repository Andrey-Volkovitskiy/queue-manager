from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (ListView,
                                  CreateView,
                                  )
from queue_manager.ticket.models import Ticket as MODEL
from queue_manager.ticket.models import ITEM_NAME
from queue_manager.session.models import Session
from queue_manager.mixins import ContextMixinWithItemName
from django.urls import reverse_lazy


class ItemListView(
        PermissionRequiredMixin,
        ContextMixinWithItemName,
        ListView):
    model = MODEL
    queryset = MODEL.objects.filter(
        session=Session.objects.get_current_session())
    item_name = ITEM_NAME
    template_name = f"{ITEM_NAME}/list.html"
    ordering = ['-code']
    permission_required = f'{ITEM_NAME}.view_{ITEM_NAME}'


# class ItemCreateView(
#         PermissionRequiredMixin,
#         ContextMixinWithItemName,
#         SuccessMessageMixin,
#         CreateView):
#     form_class = FORM
#     item_name = ITEM_NAME
#     template_name = f"{ITEM_NAME}/create.html"
#     success_url = reverse_lazy(f"{ITEM_NAME}-list")
#     success_message = f"The {ITEM_NAME} was successfully created"
#     permission_required = f'{ITEM_NAME}.add_{ITEM_NAME}'
