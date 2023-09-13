from django.urls import path

from queue_manager.task import views
from queue_manager.task.models import ITEM_NAME


urlpatterns = [
    path('', views.ItemListView.as_view(),
         name=f'{ITEM_NAME}-list'),
    path('create/', views.ItemCreateView.as_view(),
         name=f'{ITEM_NAME}-create'),
    path('<int:pk>/update/', views.ItemUpdateView.as_view(),
         name=f'{ITEM_NAME}-update'),
    path('<int:pk>/delete/', views.ItemDeleteView.as_view(),
         name=f'{ITEM_NAME}-delete'),
]
