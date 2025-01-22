from django.utils.cache import add_never_cache_headers
from django.core.cache import cache
from django.apps import apps
from asgiref.sync import sync_to_async, iscoroutinefunction, markcoroutinefunction
import logging
from django.conf import settings
import time

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 300  # 5 minutes

class HtmxNoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 'HX-Request' in request.headers:
            add_never_cache_headers(response)
        return response 
 

class MockMiddleware:
    """Middleware for testing that logs requests and adds custom data"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'MOCK_MIDDLEWARE_ENABLED', True)
        
    def mock_operation(self):
        """Simulate some work"""
        time.sleep(0.1)  # Small delay
        return "test-value"
        
    def log_request(self, method, path):
        """Log the request"""
        logger.info(f"MOCK: {method} {path}")

    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)
            
        # Add custom field to request object
        request.mock_data = {
            'timestamp': time.time(),
            'test_value': self.mock_operation(),
            'is_mock': True
        }
        
        # Log the request
        self.log_request(request.method, request.path)
        
        # Get the response
        response = self.get_response(request)
        
        # Add response headers
        response['X-Mock-Response'] = request.mock_data['test_value']
        response['X-Mock-Timestamp'] = str(request.mock_data['timestamp'])
        
        return response
 

class AsyncOrganizationMiddleware:
    """Async middleware that fetches and caches organization data"""
    
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)
            
    @sync_to_async
    def get_cache(self, key):
        return cache.get(key)
        
    @sync_to_async
    def set_cache(self, key, value, timeout):
        cache.set(key, value, timeout)
        
    async def get_user_org_data(self, user_id):
        """Fetch organization data for user"""
        OrganizationMember = apps.get_model(settings.AUTH_ORGANIZATIONMEMBER_MODEL)
        org_member = await OrganizationMember.objects.filter(
            user_id=user_id
        ).select_related('organization').afirst()
        
        if org_member:
            return {
                'org_id': org_member.organization.id,
                'org_name': org_member.organization.name,
                'org_slug': org_member.organization.slug,
                'is_admin': org_member.is_admin,
                'user_id': user_id
            }
        return None
        
    async def __call__(self, request):
        if hasattr(request, 'user') and await sync_to_async(lambda: request.user.is_authenticated)():
            cache_key = f"user_org_{request.user.id}"
            
            # Try to get from cache first
            org_data = await self.get_cache(cache_key)
            
            if org_data is None:
                # Not in cache, fetch from database
                logger.debug(f"Cache miss for user {request.user.id} org data")
                org_data = await self.get_user_org_data(request.user.id)
                
                if org_data:
                    # Store in cache
                    await self.set_cache(cache_key, org_data, CACHE_TIMEOUT)
                    logger.debug(f"Cached org data for user {request.user.id}")
            else:
                logger.debug(f"Cache hit for user {request.user.id} org data")
            
            # Add to request
            request.org_data = org_data
        
        # Get response
        response = await self.get_response(request)
        
        # Optionally add org info to response headers
        if getattr(request, 'org_data', None):
            response['X-Organization'] = request.org_data['org_slug']
        
        return response
 

 