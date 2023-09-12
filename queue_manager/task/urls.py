from django.urls import path

from queue_manager.task import views

# urlpatterns = [
#     path('', views.index),
# ]

urlpatterns = [
    path('', views.TaskListView.as_view(), name='task-list'),
    path('create/', views.TaskCreateView.as_view(), name='task-create'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(),
         name='task-update'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(),
         name='task-delete'),
]
