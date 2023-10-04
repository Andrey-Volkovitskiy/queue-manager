from django.urls import path

from queue_manager.ticket import views
from queue_manager.ticket.models import ITEM_NAME


urlpatterns = [
    path('', views.ItemListView.as_view(),
         name=f'{ITEM_NAME}-list'),
#     path('create/', views.ItemCreateView.as_view(),
#          name=f'{ITEM_NAME}-create'),
]
