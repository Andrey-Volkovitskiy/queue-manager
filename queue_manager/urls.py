"""
URL configuration for queue_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('task/', include('queue_manager.task.urls')),
    path('session/', include('queue_manager.session.urls')),
    path('ticket/', include('queue_manager.ticket.urls')),
    path('client/', include('queue_manager.client.urls')),
    path('supervisor/', include('queue_manager.user.supervisor_urls')),
    path('operator/', include('queue_manager.user.operator_urls')),
    path('login/', views.SiteLoginView.as_view(), name='login'),
    path('logout/', views.SiteLogoutView.as_view(), name='logout'),
    path('error/', views.intendent_error),  # Rollbarr debug page
    path('debug/', views.Debug.as_view()),  # Permission debug page
    path("__debug__/", include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
]
