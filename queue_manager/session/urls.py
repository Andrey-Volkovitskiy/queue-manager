from django.urls import path

from queue_manager.session import views


urlpatterns = [
    path('', views.SessionListView.as_view(),
         name='session-list'),
    path('start/', views.SessionStartView.as_view(),
         name='session-start'),
    path('finish/', views.SessionFinishView.as_view(),
         name='session-finish'),
]
