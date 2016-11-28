from django.conf import settings as s


def settings(request):
    return {
        'GA_ID': s.GA_ID,
        'PROJECT_TITLE': s.PROJECT_TITLE
    }
