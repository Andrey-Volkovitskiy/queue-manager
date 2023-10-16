from django.urls import path

from queue_manager.user import supervisor_views


urlpatterns = [
    path('', supervisor_views.SupervisorEnterView.as_view(),
         name='supervisor-enter'),
    path('<int:pk>/', supervisor_views.SupervisorPersonalView.as_view(),
         name='supervisor-personal'),
    path('no_permission/',
         supervisor_views.SupervisorNoPermissionView.as_view(),
         name='supervisor-no-permission'),
]
