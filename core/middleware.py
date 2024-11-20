from core.models import Student


class StudentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                request.student = request.user.student
            except Student.DoesNotExist:
                request.student = None
        else:
            request.student = None
        return self.get_response(request)
