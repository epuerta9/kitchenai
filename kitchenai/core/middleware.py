from django.utils.cache import add_never_cache_headers

class HtmxNoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 'HX-Request' in request.headers:
            add_never_cache_headers(response)
        return response 