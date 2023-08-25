from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'index.html', context={
        'who': "Andrey"
    })


def test_error(request):
    a = None
    a.hello()  # Creating an error with an invalid line of code
    return HttpResponse("Rollbar error tracking test.")
