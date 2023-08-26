from django.shortcuts import render


def index(request):
    return render(request, 'index.html', context={
        'who': "Andrey"
    })


def intendent_error(request):
    '''Service page to check error tracking at Rollbar.com'''
    a = None
    a.call_intendent_error()
