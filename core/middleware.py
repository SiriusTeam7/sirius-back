from rest_framework.authentication import TokenAuthentication

from core.models import Student


class StudentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, "user") or not request.user.is_authenticated:
            auth = TokenAuthentication()
            try:
                user_auth_tuple = auth.authenticate(request)
                if user_auth_tuple:
                    request.user = user_auth_tuple[0]
            except Exception:
                request.user = None
        if request.user and request.user.is_authenticated:
            try:
                request.student = request.user.student
            except Student.DoesNotExist:
                request.student = None
        else:
            request.student = None
        return self.get_response(request)
