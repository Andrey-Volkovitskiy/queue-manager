from django.urls import path

from queue_manager.client import views


urlpatterns = [
    path('', views.PrintTicketView.as_view(),
         name='print-ticket'),
    path('<int:pk>/', views.PrintedTicketDetailView.as_view(),
         name='printed-ticket-detail'),
    path('no_active_session', views.NoActiveSessionView.as_view(),
         name='printer-no-active-session'),
]
