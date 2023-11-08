from django.urls import path
from queue_manager.user import operator_views

ITEM_NAME = 'operator'


urlpatterns = [
    path('', operator_views.OperatorEnterView.as_view(),
         name='operator-enter'),
    path('<int:pk>/', operator_views.OperatorPersonalView.as_view(),
         name='operator-personal'),
    path('no_permission/',
         operator_views.OperatorNoPermissionView.as_view(),
         name='operator-no-permission'),
    path('select/',
         operator_views.OperatorSelectView.as_view(),
         name='operator-select'),
    path('<int:pk>/service_start/',
         operator_views.OperatorStartServiceView.as_view(),
         name='service-start'),
    path('manage/',
         operator_views.ItemListView.as_view(),
         name=f'{ITEM_NAME}-list'),
    path('manage/create/',
         operator_views.ItemCreateView.as_view(),
         name=f'{ITEM_NAME}-create'),
    path('manage/<int:pk>/update/',
         operator_views.ItemUpdateView.as_view(),
         name=f'{ITEM_NAME}-update'),
    path('manage/<int:pk>/pass_change/',
         operator_views.UpdatePassView.as_view(),
         name=f'{ITEM_NAME}-pass-change'),
    path('manage/<int:pk>/delete/',
         operator_views.ItemSoftDeleteView.as_view(),
         name=f'{ITEM_NAME}-delete'),
]
