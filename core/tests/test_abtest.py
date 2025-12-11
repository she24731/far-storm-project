"""
Comprehensive tests for A/B test implementation.

Tests variant selection, event logging, and full user flows.
"""
from django.test import TestCase, Client
from core.models import ABTestEvent


class ABTestEventModelTest(TestCase):
    """Test ABTestEvent model constants and choices."""
    
    def test_only_two_event_types_defined(self):
        """Test that only exposure and conversion event types are defined."""
        choices = dict(ABTestEvent.EVENT_TYPE_CHOICES)
        self.assertEqual(set(choices.keys()), {"exposure", "conversion"})
    
    def test_event_type_constants(self):
        """Test that event type constants are correct."""
        self.assertEqual(ABTestEvent.EVENT_TYPE_EXPOSURE, "exposure")
        self.assertEqual(ABTestEvent.EVENT_TYPE_CONVERSION, "conversion")


class ABTestVariantSelectionTest(TestCase):
    """Test variant selection logic (force, cookie, random)."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.abtest_url = '/218b7ae/'
    
    def test_force_variant_a_overrides_cookie(self):
        """Test that ?force_variant=a overrides existing cookie."""
        # Set cookie to 'thanks'
        self.client.cookies['ab_variant'] = 'thanks'
        
        # Request with force_variant=a
        response = self.client.get(f'{self.abtest_url}?force_variant=a')
        
        self.assertEqual(response.status_code, 200)
        
        # Check context variant is 'kudos'
        self.assertEqual(response.context['variant'], 'kudos')
        
        # Check cookie is set to 'kudos' (overridden)
        self.assertEqual(response.cookies['ab_variant'].value, 'kudos')
    
    def test_force_variant_b_overrides_cookie(self):
        """Test that ?force_variant=b overrides existing cookie."""
        # Set cookie to 'kudos'
        self.client.cookies['ab_variant'] = 'kudos'
        
        # Request with force_variant=b
        response = self.client.get(f'{self.abtest_url}?force_variant=b')
        
        self.assertEqual(response.status_code, 200)
        
        # Check context variant is 'thanks'
        self.assertEqual(response.context['variant'], 'thanks')
        
        # Check cookie is set to 'thanks' (overridden)
        self.assertEqual(response.cookies['ab_variant'].value, 'thanks')
    
    def test_cookie_persists_variant(self):
        """Test that cookie persists variant across requests."""
        # First request without cookie or force param
        response1 = self.client.get(self.abtest_url)
        self.assertEqual(response1.status_code, 200)
        
        # Get variant from first response
        variant1 = response1.context['variant']
        self.assertIn(variant1, ['kudos', 'thanks'])
        
        # Get cookie value from first response
        cookie_value = response1.cookies.get('ab_variant')
        self.assertIsNotNone(cookie_value)
        cookie_variant = cookie_value.value
        
        # Second request with cookie set (simulate browser behavior)
        self.client.cookies['ab_variant'] = cookie_variant
        response2 = self.client.get(self.abtest_url)
        self.assertEqual(response2.status_code, 200)
        
        # Variant should be the same
        variant2 = response2.context['variant']
        self.assertEqual(variant1, variant2)
        self.assertEqual(variant2, cookie_variant)
    
    def test_random_assignment_produces_both_variants_over_many_requests(self):
        """Test that random assignment produces both variants over many requests."""
        kudos_count = 0
        thanks_count = 0
        
        # Make 50 requests without cookies or force param
        for _ in range(50):
            client = Client()  # New client each time (no cookies)
            response = client.get(self.abtest_url)
            self.assertEqual(response.status_code, 200)
            
            variant = response.context['variant']
            if variant == 'kudos':
                kudos_count += 1
            elif variant == 'thanks':
                thanks_count += 1
        
        # Both variants should appear
        self.assertGreater(kudos_count, 0, "Should see at least one 'kudos' variant")
        self.assertGreater(thanks_count, 0, "Should see at least one 'thanks' variant")
        self.assertEqual(kudos_count + thanks_count, 50)


class ABTestEventLoggingTest(TestCase):
    """Test server-side event logging (exposure and conversion)."""
    
    def setUp(self):
        """Set up test client and clear events."""
        self.client = Client()
        self.abtest_url = '/218b7ae/'
        self.click_url = '/218b7ae/click/'
        # Browser User-Agent for tests (to pass bot filtering)
        self.browser_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        # Clear all events before each test
        ABTestEvent.objects.all().delete()
    
    def test_exposure_event_logged_on_page_view(self):
        """Test that exposure event is logged when page is viewed."""
        # Clear events
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # GET the A/B test page with force_variant=a
        response = self.client.get(f'{self.abtest_url}?force_variant=a')
        self.assertEqual(response.status_code, 200)
        
        # Note: Forced variants don't log exposure events (see view code)
        # So we need to test without force_variant
        ABTestEvent.objects.all().delete()
        
        # GET without force_variant (normal flow) - with browser User-Agent
        response = self.client.get(self.abtest_url, HTTP_USER_AGENT=self.browser_ua)
        self.assertEqual(response.status_code, 200)
        
        # Should have exactly one exposure event
        events = ABTestEvent.objects.all()
        self.assertEqual(events.count(), 1)
        
        event = events.first()
        self.assertEqual(event.experiment_name, 'button_label_kudos_vs_thanks')
        self.assertIn(event.variant, ['kudos', 'thanks'])
        self.assertEqual(event.event_type, ABTestEvent.EVENT_TYPE_EXPOSURE)
        self.assertEqual(event.endpoint, '/218b7ae/')
    
    def test_conversion_event_logged_on_click_endpoint(self):
        """Test that conversion event is logged when click endpoint is called."""
        # Clear events
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # POST to click endpoint with variant='kudos' - with browser User-Agent
        # Django test client automatically handles form-urlencoded
        response = self.client.post(
            self.click_url,
            data={'variant': 'kudos'},
            HTTP_USER_AGENT=self.browser_ua
        )
        
        self.assertEqual(response.status_code, 200, 
                        f"Expected 200, got {response.status_code}. Response: {response.content.decode()[:200]}")
        
        # Should have exactly one conversion event
        events = ABTestEvent.objects.all()
        self.assertEqual(events.count(), 1)
        
        event = events.first()
        self.assertEqual(event.experiment_name, 'button_label_kudos_vs_thanks')
        self.assertEqual(event.variant, 'kudos')
        self.assertEqual(event.event_type, ABTestEvent.EVENT_TYPE_CONVERSION)
        self.assertEqual(event.endpoint, '/218b7ae/')
    
    def test_conversion_event_with_thanks_variant(self):
        """Test conversion event logging with 'thanks' variant."""
        # Clear events
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # POST to click endpoint with variant='thanks' - with browser User-Agent
        response = self.client.post(
            self.click_url,
            data={'variant': 'thanks'},
            HTTP_USER_AGENT=self.browser_ua
        )
        
        self.assertEqual(response.status_code, 200,
                        f"Expected 200, got {response.status_code}. Response: {response.content.decode()[:200]}")
        
        # Should have exactly one conversion event
        events = ABTestEvent.objects.all()
        self.assertEqual(events.count(), 1)
        
        event = events.first()
        self.assertEqual(event.variant, 'thanks')
        self.assertEqual(event.event_type, ABTestEvent.EVENT_TYPE_CONVERSION)
    
    def test_click_endpoint_rejects_invalid_variant(self):
        """Test that click endpoint rejects invalid variant."""
        # POST with invalid variant
        response = self.client.post(
            self.click_url,
            data={'variant': 'invalid'}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ABTestEvent.objects.count(), 0)
    
    def test_click_endpoint_rejects_get_method(self):
        """Test that click endpoint only accepts POST."""
        response = self.client.get(self.click_url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(ABTestEvent.objects.count(), 0)


class ABTestIntegrationTest(TestCase):
    """Integration tests for full A/B test flow."""
    
    def setUp(self):
        """Set up test client and clear events."""
        self.client = Client()
        self.abtest_url = '/218b7ae/'
        self.click_url = '/218b7ae/click/'
        ABTestEvent.objects.all().delete()
    
    def test_full_flow_exposure_then_conversion(self):
        """Test full flow: exposure event on page view, then conversion on click."""
        # Clear DB
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # Step 1: GET the A/B test page (no force param, no cookie) - with browser User-Agent
        response = self.client.get(self.abtest_url, HTTP_USER_AGENT=self.browser_ua)
        self.assertEqual(response.status_code, 200)
        
        # Get variant from response context
        variant = response.context['variant']
        self.assertIn(variant, ['kudos', 'thanks'])
        
        # Get cookie value
        cookie_value = response.cookies.get('ab_variant').value
        self.assertEqual(cookie_value, variant)
        
        # Should have exactly one exposure event
        exposure_events = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE)
        self.assertEqual(exposure_events.count(), 1)
        
        exposure_event = exposure_events.first()
        self.assertEqual(exposure_event.experiment_name, 'button_label_kudos_vs_thanks')
        self.assertEqual(exposure_event.variant, variant)
        self.assertEqual(exposure_event.event_type, ABTestEvent.EVENT_TYPE_EXPOSURE)
        self.assertEqual(exposure_event.endpoint, '/218b7ae/')
        
        # Step 2: Simulate button click (POST to click endpoint)
        # Set cookie for the click request
        self.client.cookies['ab_variant'] = variant
        
        response_click = self.client.post(
            self.click_url,
            data={'variant': variant},
            HTTP_USER_AGENT=self.browser_ua
        )
        
        self.assertEqual(response_click.status_code, 200,
                        f"Expected 200, got {response_click.status_code}. Response: {response_click.content.decode()[:200]}")
        
        # Should now have exactly one exposure and one conversion
        self.assertEqual(ABTestEvent.objects.count(), 2)
        
        conversion_events = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION)
        self.assertEqual(conversion_events.count(), 1)
        
        conversion_event = conversion_events.first()
        self.assertEqual(conversion_event.experiment_name, 'button_label_kudos_vs_thanks')
        self.assertEqual(conversion_event.variant, variant)
        self.assertEqual(conversion_event.event_type, ABTestEvent.EVENT_TYPE_CONVERSION)
        self.assertEqual(conversion_event.endpoint, '/218b7ae/')
        
        # Both events should have the same variant
        self.assertEqual(exposure_event.variant, conversion_event.variant)
        self.assertEqual(exposure_event.experiment_name, conversion_event.experiment_name)
    
    def test_multiple_exposures_same_variant(self):
        """Test that multiple page views with same cookie log multiple exposures."""
        browser_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        # First request
        response1 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        variant1 = response1.context['variant']
        
        # Set cookie for subsequent requests
        self.client.cookies['ab_variant'] = variant1
        
        # Second request (same cookie)
        response2 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        variant2 = response2.context['variant']
        
        # Third request (same cookie)
        response3 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        variant3 = response3.context['variant']
        
        # All should be the same variant
        self.assertEqual(variant1, variant2)
        self.assertEqual(variant2, variant3)
        
        # Should have 3 exposure events
        exposure_events = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE)
        self.assertEqual(exposure_events.count(), 3)
        
        # All should have the same variant
        for event in exposure_events:
            self.assertEqual(event.variant, variant1)


class ABTestPublicAccessTest(TestCase):
    """Test that A/B test endpoint is publicly accessible."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.abtest_url = '/218b7ae/'
    
    def test_abtest_endpoint_is_public(self):
        """Test that A/B test endpoint is publicly accessible (no login required)."""
        response = self.client.get(self.abtest_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'far-storm')
        self.assertContains(response, 'Chun-Hung Yeh')
        self.assertContains(response, 'Celine (Qijing) Li')
        self.assertContains(response, 'Denise Wu')
    
    def test_abtest_button_id_and_text(self):
        """Test that button has correct id and text is either 'kudos' or 'thanks'."""
        response = self.client.get(self.abtest_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="abtest"')
        
        # Check that button text is either 'kudos' or 'thanks'
        content = response.content.decode('utf-8')
        
        # Find the button and extract its text
        import re
        button_match = re.search(r'<button[^>]*id="abtest"[^>]*>([^<]+)</button>', content)
        
        self.assertIsNotNone(button_match, "Button with id='abtest' not found")
        
        button_text = button_match.group(1).strip()
        self.assertIn(button_text, ['kudos', 'thanks'], 
                     f"Button text '{button_text}' is not 'kudos' or 'thanks'")
    
    def test_abtest_view_uses_correct_template(self):
        """Test that A/B test view uses the correct template."""
        response = self.client.get(self.abtest_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/abtest.html')
    
    def test_abtest_analytics_script_present(self):
        """Test that analytics tracking script is present in the template."""
        response = self.client.get(self.abtest_url)
        
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # Check for gtag calls (using double quotes as per updated template)
        self.assertIn('gtag("event", "ab_exposure"', content)
        self.assertIn('gtag("event", "ab_button_click"', content)
        self.assertIn('experiment:', content)  # Check for experiment parameter
