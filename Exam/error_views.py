from django.shortcuts import render


def page_not_found(request, *args, **kwargs):
    return render(request, 'errors/not_found.html')


def bad_request(request, *args, **kwargs):
    return render(request, 'errors/bad_request.html')


def permission_denied(request, *args, **kwargs):
    return render(request, 'errors/permission_denied.html')


def server_error(request, *args, **kwargs):
    return render(request, 'errors/server_error.html')
