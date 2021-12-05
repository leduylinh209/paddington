from django.utils import timezone


def log_interaction_middleware(get_response):

    def middleware(request):
        response = get_response(request)

        # Update last_interaction_at
        if request.method == 'GET' and request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile:
                profile.last_interaction_at = timezone.now()
                profile.save_without_signals()

        return response

    return middleware
