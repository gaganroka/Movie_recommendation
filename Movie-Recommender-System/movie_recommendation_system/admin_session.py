from django.conf import settings

class AdminSessionMiddleware:
    """Switch session cookie for admin routes"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # For admin routes, use a different session cookie name
        if request.path.startswith('/admin-panel/'):
            request.session_cookie_name = 'admin_sessionid'
        else:
            request.session_cookie_name = 'sessionid'
        response = self.get_response(request)
        # Set cookie with the right name
        cookie_name = getattr(request, 'session_cookie_name', 'sessionid')
        if hasattr(request, 'session') and request.session.session_key:
            if cookie_name == 'admin_sessionid':
                # Admin cookie settings (different path/domain if needed)
                pass
        return response
