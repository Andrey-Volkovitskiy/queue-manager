from django.urls import path

from queue_manager.session import views


urlpatterns = [
    path('', views.ItemListView.as_view(),
         name='session-list'),
    # path('<int:pk>/', views.SessionShowView.as_view(),
    #      name='session-show'),
    path('start/', views.SessionStartView.as_view(),
         name='session-start'),
    # path('<int:pk>/finish/', views.SessionFinishView.as_view(),
    #      name='session-finish'),
]
