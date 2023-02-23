from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def server_error(request, reason=''):
    return render(request, 'core/403csrf.html', status=403)