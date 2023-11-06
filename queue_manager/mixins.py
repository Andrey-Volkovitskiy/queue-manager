from django.views.generic.base import ContextMixin


class ContextMixinWithItemName(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_name'] = self.item_name
        return context
