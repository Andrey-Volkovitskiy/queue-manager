from django.views.generic import TemplateView
from queue_manager.session.models import ITEM_NAME
from queue_manager.mixins import ContextMixinWithItemName


class SessionStartView(TemplateView, ContextMixinWithItemName):
    template_name = f"{ITEM_NAME}/start.html"
    item_name = ITEM_NAME

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['new_id'] = Session.objects._get_new_id()
    #     return context
