from django.urls import path

from queue_manager.ticket import views
from queue_manager.ticket.models import ITEM_NAME


urlpatterns = [
    path('', views.ItemListView.as_view(),
         name=f'{ITEM_NAME}-list'),
    path('<int:pk>/mark_completed/',
         views.TicketMarkCompletedView.as_view(),
         name='ticket-mark-completed'),
    path('<int:pk>/mark_missed/',
         views.TicketMarkMissedView.as_view(),
         name='ticket-mark-missed'),
    path('<int:pk>/redirect/',
         views.TicketRedirectView.as_view(),
         name='ticket-redirect'),
]
