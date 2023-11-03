from django.shortcuts import render
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.contrib.auth.models import User


class SiteLoginView(SuccessMessageMixin, LoginView):
    redirect_authenticated_user = True
    template_name = "login.html"
    success_message = "You are logged in"

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return super().dispatch(request, *args, **kwargs)


class SiteLogoutView(LogoutView):

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.add_message(request, messages.INFO, "You are logged out")
        return response


def index(request):
    return render(request, 'index.html')


def intendent_error(request):
    '''Service page to check error tracking at Rollbar.com'''
    a = None
    a.call_intendent_error()


class Debug(TemplateView):
    template_name = 'debug.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        context['permissions'] = User.objects.get(
            id=user_id).get_all_permissions()
        return context
