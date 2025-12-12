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

