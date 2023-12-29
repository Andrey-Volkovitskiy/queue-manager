from django.views.generic.base import ContextMixin
from django.urls import reverse_lazy
from queue_manager.default_db_data import DefaultDBData
from queue_manager.user.models import Operator


class ContextMixinWithItemName(ContextMixin):
    def get_context_data(self, **kwargs):
        '''Get ItemName to use in universal Add, Upd, Del templates.'''
        context = super().get_context_data(**kwargs)
        context['item_name'] = self.item_name
        return context


class TopNavMenuMixin(ContextMixin):
    def get_context_data(self, **kwargs):  # noqa C901
        '''Creates items for navigation menu at the top of any page.

        Returns: list of items (tuples of name and link)'''

        context = super().get_context_data(**kwargs)

        menu_items = []
        path = self.request.path.split('/')[1:]

        if len(path[0]) > 0:
            menu_items.append(('Home', reverse_lazy('home')))

            if path[0] == 'client':
                if path[1]:
                    menu_items.append(('Client', reverse_lazy('print-ticket')))

            elif path[0] == 'supervisor':
                pass

            elif path[0] in ('task', 'session'):
                menu_items.append(
                    ('Supervisor', reverse_lazy('supervisor-enter')))

            elif path[0] == 'operator':
                if path[1] in ('select', 'no_permission'):
                    pass
                elif path[1] == 'manage':
                    menu_items.append(
                        ('Supervisor', reverse_lazy('supervisor-enter')))
                else:
                    menu_items.append(
                        ('Operator', reverse_lazy('operator-enter')))
                    request_by_supervisor = self.request.user.groups.filter(
                            name=DefaultDBData.groups['SUPERVISORS']).exists()
                    if request_by_supervisor:
                        pretend_id = int(path[1])
                        menu_items.append((
                            Operator.objects.get(id=pretend_id)
                                    .get_full_name(),
                            reverse_lazy('operator-personal',
                                         kwargs={'pk': pretend_id})))

            elif path[0] == 'ticket':
                pretend_operator_id = self.request.GET.get('operator')
                if pretend_operator_id:
                    menu_items.append(('Operator',
                                      reverse_lazy('operator-enter')))

                    request_by_supervisor = self.request.user.groups.filter(
                            name=DefaultDBData.groups['SUPERVISORS']).exists()
                    if request_by_supervisor:
                        pretend_id = int(pretend_operator_id)
                        menu_items.append((
                            Operator.objects.get(
                                id=pretend_id).get_full_name(),
                            reverse_lazy('operator-personal',
                                         kwargs={'pk': pretend_id})))

                else:
                    menu_items.append(
                        ('Supervisor', reverse_lazy('supervisor-enter')))

        context['top_nav_menu'] = menu_items
        return context
