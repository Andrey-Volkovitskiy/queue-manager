from django.urls import path

from queue_manager.printer import views


urlpatterns = [
    path('', views.ItemCreateView.as_view(),
         name='printer-create'),
    path('no_active_session', views.NoActiveSessionView.as_view(),
         name='printer-no-active-session'),
]
