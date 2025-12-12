"""
Comprehensive tests for A/B test implementation.

Tests variant selection, event logging, and full user flows.
"""
from django.test import TestCase, Client
from unittest.mock import patch
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
    """Test variant selection logic (force, session, random)."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.abtest_url = '/218b7ae/'
        self.browser_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.nav_headers = {
            'HTTP_USER_AGENT': self.browser_ua,
            'HTTP_SEC_FETCH_DEST': 'document',
            'HTTP_SEC_FETCH_MODE': 'navigate',
            'HTTP_SEC_FETCH_SITE': 'same-origin',
        }
    
    def test_force_variant_a_overrides_session(self):
        """Test that variant is assigned via session (force_variant removed)."""
        # First assign a variant via normal flow
        response1 = self.client.get(self.abtest_url, **self.nav_headers)
        session_variant = response1.context['variant']
        
        # Second request should use same variant from session
        response = self.client.get(self.abtest_url, **self.nav_headers)
        
        self.assertEqual(response.status_code, 200)
        
        # Check context variant is same as first request (session-based)
        self.assertEqual(response.context['variant'], session_variant)
    
    def test_force_variant_b_overrides_session(self):
        """Test that variant persists in session (force_variant removed)."""
        # First assign a variant via normal flow
        response1 = self.client.get(self.abtest_url, **self.nav_headers)
        variant1 = response1.context['variant']
        
        # Second request should use same variant from session
        response = self.client.get(self.abtest_url, **self.nav_headers)
        
        self.assertEqual(response.status_code, 200)
        
        # Variant should remain the same (session-based)
        self.assertEqual(response.context['variant'], variant1)
    
    def test_session_persists_variant(self):
        """Test that session persists variant across requests."""
        # First request without force param
        response1 = self.client.get(self.abtest_url, **self.nav_headers)
        self.assertEqual(response1.status_code, 200)
        
        # Get variant from first response
        variant1 = response1.context['variant']
        self.assertIn(variant1, ['kudos', 'thanks'])
        
        # Second request (same session) - should keep same variant
        response2 = self.client.get(self.abtest_url, **self.nav_headers)
        self.assertEqual(response2.status_code, 200)
        
        # Variant should be the same
        variant2 = response2.context['variant']
        self.assertEqual(variant1, variant2, "Session should persist variant across requests")
    
    @patch('core.views.random.choice')
    def test_session_assignment_uses_random_choice(self, mock_choice):
        """Test that first visit uses random.choice for 50/50 assignment."""
        # Mock random.choice to return 'kudos'
        mock_choice.return_value = 'kudos'
        
        # First request - should use mocked random.choice
        response = self.client.get(self.abtest_url, **self.nav_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['variant'], 'kudos')
        mock_choice.assert_called_once_with(['kudos', 'thanks'])
        
        # Second request - should NOT call random.choice again (uses session)
        mock_choice.reset_mock()
        response2 = self.client.get(self.abtest_url, **self.nav_headers)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.context['variant'], 'kudos')
        mock_choice.assert_not_called()  # Should use session, not random
    
    @patch('core.views.random.choice')
    def test_session_assignment_random_choice_returns_thanks(self, mock_choice):
        """Test that random.choice returning 'thanks' is stored in session."""
        # Mock random.choice to return 'thanks'
        mock_choice.return_value = 'thanks'
        
        # First request
        response = self.client.get(self.abtest_url, **self.nav_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['variant'], 'thanks')
        
        # Verify it's stored in session by checking a second request
        response2 = self.client.get(self.abtest_url, **self.nav_headers)
        self.assertEqual(response2.context['variant'], 'thanks')
    
    def test_random_assignment_produces_both_variants_over_many_requests(self):
        """Test that random assignment produces both variants over many requests."""
        kudos_count = 0
        thanks_count = 0
        
        # Make 50 requests with new clients (new sessions) each time
        for _ in range(50):
            client = Client()  # New client = new session
            nav_headers = {
                'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'HTTP_SEC_FETCH_DEST': 'document',
                'HTTP_SEC_FETCH_MODE': 'navigate',
                'HTTP_SEC_FETCH_SITE': 'same-origin',
            }
            response = client.get(self.abtest_url, **nav_headers)
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
        # Browser User-Agent and headers for tests (to pass bot filtering)
        self.browser_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.nav_headers = {
            'HTTP_USER_AGENT': self.browser_ua,
            'HTTP_SEC_FETCH_DEST': 'document',
            'HTTP_SEC_FETCH_MODE': 'navigate',
            'HTTP_SEC_FETCH_SITE': 'same-origin',
        }
        self.ajax_headers = {
            'HTTP_USER_AGENT': self.browser_ua,
            'HTTP_SEC_FETCH_MODE': 'cors',
            'HTTP_SEC_FETCH_SITE': 'same-origin',
        }
        # Clear all events before each test
        ABTestEvent.objects.all().delete()
    
    def test_first_get_logs_single_exposure(self):
        """Test that first GET logs exactly ONE Exposure."""
        # Clear events
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # GET the A/B test page with browser UA - should log ONE exposure
        response = self.client.get(self.abtest_url, HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0")
        self.assertEqual(response.status_code, 200)
        
        # Should have exactly ONE exposure, NO conversion
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 0)
    
    def test_reload_does_not_log_extra_exposure(self):
        """Test that reloading does not log additional Exposure."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        # First GET - logs one exposure
        response1 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        
        # Second GET (reload) - should NOT log additional exposure
        response2 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1, "Reload should not create duplicate exposure")
    
    def test_click_logs_conversion_without_extra_exposure(self):
        """Test that click logs conversion without creating extra exposure."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        # GET - logs one exposure
        response_get = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(response_get.status_code, 200)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 0)
        
        # POST click - logs conversion only, NO new exposure
        response_click = self.client.post(self.click_url, data={})
        self.assertEqual(response_click.status_code, 200)
        
        # Should still have exactly 1 exposure, and now 1 conversion
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
    
    def test_click_endpoint_uses_session_variant_not_post_data(self):
        """Test that click endpoint uses session variant, ignoring untrusted POST data."""
        nav_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'HTTP_SEC_FETCH_DEST': 'document',
            'HTTP_SEC_FETCH_MODE': 'navigate',
            'HTTP_SEC_FETCH_SITE': 'same-origin',
        }
        ajax_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'HTTP_SEC_FETCH_MODE': 'cors',
            'HTTP_SEC_FETCH_SITE': 'same-origin',
        }
        
        # First, assign a variant via GET request
        response = self.client.get(self.abtest_url, **nav_headers)
        session_variant = response.context['variant']
        self.assertIn(session_variant, ['kudos', 'thanks'])
        
        # Now POST with a DIFFERENT variant in POST data - should use session variant, not POST data
        wrong_variant = 'thanks' if session_variant == 'kudos' else 'kudos'
        response_click = self.client.post(
            self.click_url,
            data={'variant': wrong_variant},  # Wrong variant in POST data
            **ajax_headers
        )
        
        # Should succeed (200) because variant comes from session, not POST
        self.assertEqual(response_click.status_code, 200)
        
        # Check that conversion event uses the SESSION variant, not the POST variant
        conversion_events = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION)
        self.assertEqual(conversion_events.count(), 1)
        
        conversion_event = conversion_events.first()
        self.assertEqual(conversion_event.variant, session_variant, 
                        "Conversion should use session variant, not untrusted POST data")
        self.assertNotEqual(conversion_event.variant, wrong_variant,
                           "Conversion should NOT use the wrong variant from POST data")
    
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
        # Browser User-Agent and headers for tests (to pass bot filtering)
        self.browser_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.nav_headers = {
            'HTTP_USER_AGENT': self.browser_ua,
            'HTTP_SEC_FETCH_DEST': 'document',
            'HTTP_SEC_FETCH_MODE': 'navigate',
            'HTTP_SEC_FETCH_SITE': 'same-origin',
        }
        self.ajax_headers = {
            'HTTP_USER_AGENT': self.browser_ua,
            'HTTP_SEC_FETCH_MODE': 'cors',
            'HTTP_SEC_FETCH_SITE': 'same-origin',
        }
        ABTestEvent.objects.all().delete()
    
    def test_full_flow_exposure_on_get_then_conversion_on_click(self):
        """Test full flow: exposure on GET, then conversion on click."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        # Clear DB
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # Step 1: GET the A/B test page - should log ONE exposure
        response = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(response.status_code, 200)
        
        # Get variant from response context
        variant = response.context['variant']
        self.assertIn(variant, ['kudos', 'thanks'])
        
        # Should have ONE exposure from GET, NO conversion
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 0)
        
        # Step 2: Click - should log conversion only (no new exposure)
        response_click = self.client.post(
            self.click_url,
            data={},
        )
        
        self.assertEqual(response_click.status_code, 200,
                        f"Expected 200, got {response_click.status_code}. Response: {response_click.content.decode()[:200]}")
        
        # Should now have exactly one exposure (from GET) and one conversion (from click)
        exposure_events = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE)
        self.assertEqual(exposure_events.count(), 1)
        
        conversion_events = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION)
        self.assertEqual(conversion_events.count(), 1)
        
        exposure_event = exposure_events.first()
        conversion_event = conversion_events.first()
        
        self.assertEqual(exposure_event.experiment_name, 'button_label_kudos_vs_thanks')
        self.assertEqual(exposure_event.variant, variant)
        self.assertEqual(exposure_event.event_type, ABTestEvent.EVENT_TYPE_EXPOSURE)
        self.assertEqual(exposure_event.endpoint, '/218b7ae/')
        
        self.assertEqual(conversion_event.experiment_name, 'button_label_kudos_vs_thanks')
        self.assertEqual(conversion_event.variant, variant)
        self.assertEqual(conversion_event.event_type, ABTestEvent.EVENT_TYPE_CONVERSION)
        self.assertEqual(conversion_event.endpoint, '/218b7ae/')
        
        # Both events should have the same variant
        self.assertEqual(exposure_event.variant, conversion_event.variant)
        self.assertEqual(exposure_event.experiment_name, conversion_event.experiment_name)
    
    def test_reload_does_not_log_extra_exposure(self):
        """Test that reloading does not log additional Exposure."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        # First GET - logs one exposure
        response1 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        variant1 = response1.context['variant']
        self.assertIn(variant1, ['kudos', 'thanks'])
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        
        # Second GET (reload) - should NOT log additional exposure
        response2 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        variant2 = response2.context['variant']
        self.assertEqual(variant1, variant2)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1, "Reload should not create duplicate exposure")
        
        # Third GET - still only one exposure
        response3 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        variant3 = response3.context['variant']
        self.assertEqual(variant1, variant3)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1, "Third GET should not create duplicate exposure")


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
        
        # Check for gtag calls (exposure removed from page load, only click remains)
        self.assertIn('gtag("event", "ab_button_click"', content)
        self.assertIn('experiment:', content)  # Check for experiment parameter
