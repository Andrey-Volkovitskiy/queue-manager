from django.urls import path

from queue_manager.user import supervisor_views


urlpatterns = [
    path('', supervisor_views.SupervisorHomeView.as_view(),
         name='supervisor-home'),
]
