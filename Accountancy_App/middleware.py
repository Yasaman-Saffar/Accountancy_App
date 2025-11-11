from django.shortcuts import redirect
from django.urls import reverse

allowed_paths = [
    '/admin_or_user/',
    '/admin_login/',
    '/banker_login/',
    '/admin/',
    '/scoreboard/',
]

class BankerAndAdminAccessControl:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        path = request.path
        
        if any(path.startswith(p) for p in allowed_paths):
            return self.get_response(request)

        if not (request.session.get('is_admin') or request.session.get('is_banker')):
            return redirect(reverse('core:admin_or_user'))
        
        return self.get_response(request)
