from django.views.generic.base import ContextMixin
from django.contrib.auth.mixins import UserPassesTestMixin


class ContextMixinWithItemName(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_name'] = self.item_name
        return context


class PersonalPagePermissions(UserPassesTestMixin):
    '''Allows only the user to access his personal page'''

    def test_func(self):
        subject_user = self.request.user
        object_user = self.get_object()
        if subject_user == object_user:
            return True
        else:
            return False
