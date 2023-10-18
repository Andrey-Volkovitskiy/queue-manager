from django.urls import path
from queue_manager.user import operator_views

ITEM_NAME = 'operator'


urlpatterns = [
    path('manage/', operator_views.ItemListView.as_view(),
         name=f'{ITEM_NAME}-list'),
    path('manage/create/', operator_views.ItemCreateView.as_view(),
         name=f'{ITEM_NAME}-create'),
    path('manage/<int:pk>/update/',
         operator_views.ItemUpdateView.as_view(),
         name=f'{ITEM_NAME}-update'),
    path('manage/<int:pk>/pass_change/',
         operator_views.UpdatePassView.as_view(),
         name=f'{ITEM_NAME}-pass-change'),
    path('manage/<int:pk>/delete/', operator_views.ItemDeleteView.as_view(),
         name=f'{ITEM_NAME}-delete'),
]
