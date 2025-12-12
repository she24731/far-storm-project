"""
Test URL routing to ensure /login/ does not route to abtest_view.
"""
from django.test import TestCase
from django.urls import resolve, reverse


class URLRoutingTest(TestCase):
    """Test critical URL routing to prevent conflicts."""
    
    def test_login_route_resolves_to_login_view(self):
        """Ensure /login/ resolves to login view, NOT abtest."""
        resolver_match = resolve('/login/')
        
        # Verify it resolves to login (check url_name, which is the critical check)
        self.assertEqual(resolver_match.url_name, 'login')
        self.assertEqual(resolver_match.route, 'login/')
        
        # Critical: ensure it's NOT abtest
        self.assertNotEqual(resolver_match.url_name, 'abtest')
        self.assertNotEqual(resolver_match.route, '218b7ae/')
    
    def test_abtest_route_resolves_to_abtest_view(self):
        """Ensure /218b7ae/ resolves to abtest view."""
        resolver_match = resolve('/218b7ae/')
        
        # Verify it resolves to abtest
        self.assertEqual(resolver_match.url_name, 'abtest')
        self.assertIn('abtest', str(resolver_match.func).lower())
        
        # Critical: ensure it's NOT login
        self.assertNotEqual(resolver_match.url_name, 'login')
    
    def test_login_url_reverse(self):
        """Test reverse lookup for login URL."""
        url = reverse('core:login')
        self.assertEqual(url, '/login/')
    
    def test_abtest_url_reverse(self):
        """Test reverse lookup for abtest URL."""
        url = reverse('abtest')
        self.assertEqual(url, '/218b7ae/')
    
    def test_abtest_view_has_no_cache_headers(self):
        """Test that abtest_view response includes no-cache headers to prevent variant stickiness."""
        from django.test import Client
        
        client = Client()
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        response = client.get('/218b7ae/', HTTP_USER_AGENT=browser_ua)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify cache-control headers are present
        self.assertIn('Cache-Control', response)
        cache_control = response['Cache-Control']
        self.assertIn('no-store', cache_control)
        self.assertIn('no-cache', cache_control)
        self.assertIn('must-revalidate', cache_control)
        self.assertIn('max-age=0', cache_control)
        
        # Verify Vary header includes Cookie
        self.assertIn('Vary', response)
        self.assertIn('Cookie', response['Vary'])
        
        # Verify Pragma and Expires headers
        self.assertEqual(response['Pragma'], 'no-cache')
        self.assertEqual(response['Expires'], '0')
    
    def test_abtest_click_has_no_cache_headers(self):
        """Test that abtest_click response includes no-cache headers."""
        from django.test import Client
        
        client = Client()
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        # First visit to get a session with variant
        client.get('/218b7ae/', HTTP_USER_AGENT=browser_ua)
        
        # Then click
        response = client.post('/218b7ae/click/')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify cache-control headers are present
        self.assertIn('Cache-Control', response)
        cache_control = response['Cache-Control']
        self.assertIn('no-store', cache_control)
        self.assertIn('no-cache', cache_control)
        
        # Verify Vary header includes Cookie
        self.assertIn('Vary', response)
        self.assertIn('Cookie', response['Vary'])

