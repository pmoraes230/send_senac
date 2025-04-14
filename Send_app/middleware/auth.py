from django.shortcuts import redirect
from django.urls import reverse
from ..views import get_user_profile

class AuthRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        public_urls = [reverse('login')]
        context = get_user_profile(request)
        is_authenticated = context.get('is_authenticated', False)

        if is_authenticated:
            if request.path == reverse('login'):
                return redirect('home')
        else:
            if request.path not in public_urls:
                return redirect('login')

        return self.get_response(request)