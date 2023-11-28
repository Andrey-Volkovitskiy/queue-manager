from django.views.generic.base import ContextMixin
from django.urls import reverse_lazy
from queue_manager.default_db_data import DefaultDBData
from queue_manager.user.models import Operator


class ContextMixinWithItemName(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_name'] = self.item_name
        return context


class TopNavMenuMixin(ContextMixin):  # TODO Refactor
    def get_context_data(self, **kwargs):  # noqa C901
        context = super().get_context_data(**kwargs)
        if self.request.method != 'GET':
            return context

        menu_items = []
        path = self.request.path

        if path != '/':
            menu_items.append(('Home', reverse_lazy('home')))

        if path.startswith('/client/') and len(path) > len('/client/'):
            menu_items.append(('Client', reverse_lazy('print-ticket')))

        elif path.startswith('/supervisor/'):
            pass

        elif path.startswith('/task/'):
            menu_items.append(
                ('Supervisor', reverse_lazy('supervisor-enter')))

        elif path.startswith('/session/'):
            menu_items.append(
                ('Supervisor', reverse_lazy('supervisor-enter')))

        elif path.startswith('/operator/'):
            if 'select' in path or 'no_permission' in path:
                pass
            elif 'manage' in path:
                menu_items.append(
                    ('Supervisor', reverse_lazy('supervisor-enter')))
            else:
                request_by_supervisor = self.request.user.groups.filter(
                        name=DefaultDBData.groups['SUPERVISORS']).exists()
                if request_by_supervisor and len(path) > len('/operator/'):
                    pretend_id = int(path.split('/')[2])
                    menu_items.append(('Operator',
                                       reverse_lazy('operator-enter')))
                    menu_items.append((
                        Operator.objects.get(id=pretend_id).get_full_name(),
                        reverse_lazy('operator-personal',
                                     kwargs={'pk': pretend_id})
                        ))
                else:
                    menu_items.append(
                        ('Operator', reverse_lazy('operator-enter')))

        elif path.startswith('/ticket/'):
            if len(path) > len('/ticket/'):
                menu_items.append(('Operator',
                                   reverse_lazy('operator-enter')))

                pretend_operator_id = self.request.GET.get('operator')
                request_by_supervisor = self.request.user.groups.filter(
                            name=DefaultDBData.groups['SUPERVISORS']).exists()
                if pretend_operator_id and request_by_supervisor:
                    menu_items.append((
                        Operator.objects.get(
                                id=int(pretend_operator_id)).get_full_name(),
                        reverse_lazy('operator-personal',
                                     kwargs={'pk': int(pretend_operator_id)})
                        ))

        context['top_nav_menu'] = menu_items
        return context
