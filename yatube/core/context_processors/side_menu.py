from posts.models import Group


def groups(request):
    return {'groups': Group.objects.all(), }
