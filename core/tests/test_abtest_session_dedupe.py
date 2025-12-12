"""
Tests for session-based A/B test assignment and deduplication.

Tests per-session variant assignment, exposure deduplication, and variant consistency.
"""
from django.test import TestCase, Client
from unittest.mock import patch
from core.models import ABTestEvent


# Browser User-Agent for realistic tests
BROWSER_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def get_navigation_headers():
    """Get realistic Sec-Fetch headers for navigation requests."""
    return {
        'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'HTTP_SEC_FETCH_DEST': 'document',
        'HTTP_SEC_FETCH_MODE': 'navigate',
        'HTTP_SEC_FETCH_SITE': 'same-origin',
    }


def get_ajax_headers():
    """Get realistic headers for AJAX POST requests."""
    return {
        'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'HTTP_SEC_FETCH_MODE': 'cors',
        'HTTP_SEC_FETCH_SITE': 'same-origin',
        'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
    }


class ABTestSessionAssignmentTest(TestCase):
    """Test per-session variant assignment and exposure deduplication."""
    
    def setUp(self):
        """Set up test client and clear events."""
        self.client = Client()
        self.abtest_url = '/218b7ae/'
        self.click_url = '/218b7ae/click/'
        ABTestEvent.objects.all().delete()
    
    def test_first_get_assigns_variant_but_logs_no_exposure(self):
        """Test that first GET assigns variant but does NOT log exposure."""
        headers = get_navigation_headers()
        with patch('core.views.random.choice', return_value='kudos'):
            response = self.client.get(self.abtest_url, **headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['variant'], 'kudos')
        
        # Should have NO events logged from GET
        self.assertEqual(ABTestEvent.objects.count(), 0, "GET should NOT log exposure")
    
    def test_get_requests_never_log_exposure(self):
        """Test that GET requests never log exposure, even multiple times."""
        headers = get_navigation_headers()
        # First GET - should NOT log exposure
        response1 = self.client.get(self.abtest_url, **headers)
        variant1 = response1.context['variant']
        
        self.assertEqual(ABTestEvent.objects.count(), 0, "First GET should not log exposure")
        
        # Second GET in same session - should still NOT log exposure
        response2 = self.client.get(self.abtest_url, **headers)
        variant2 = response2.context['variant']
        
        # Variant should be same
        self.assertEqual(variant1, variant2)
        
        # Should still have NO events
        self.assertEqual(ABTestEvent.objects.count(), 0, "Multiple GETs should not log exposure")
    
    def test_first_click_logs_exposure_and_conversion(self):
        """Test that first click logs both exposure and conversion."""
        headers = get_navigation_headers()
        # GET - assigns variant but does NOT log exposure
        response1 = self.client.get(self.abtest_url, **headers)
        variant1 = response1.context['variant']
        
        # Should have NO events from GET
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # First click - should log BOTH exposure and conversion
        ajax_headers = get_ajax_headers()
        response_click = self.client.post(
            self.click_url,
            data={},
            **ajax_headers
        )
        self.assertEqual(response_click.status_code, 200)
        
        # Should have exactly one exposure and one conversion
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
        
        # Check variant consistency
        exposure = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).first()
        conversion = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).first()
        self.assertEqual(exposure.variant, variant1)
        self.assertEqual(conversion.variant, variant1)
        self.assertEqual(exposure.variant, conversion.variant)
    
    def test_second_click_logs_only_conversion(self):
        """Test that second click logs only conversion, not duplicate exposure."""
        headers = get_navigation_headers()
        ajax_headers = get_ajax_headers()
        
        # GET - no events
        self.client.get(self.abtest_url, **headers)
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # First click - logs exposure + conversion
        response1 = self.client.post(self.click_url, data={}, **ajax_headers)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
        
        # Second click - logs ONLY conversion
        response2 = self.client.post(self.click_url, data={}, **ajax_headers)
        self.assertEqual(response2.status_code, 200)
        
        # Should still have exactly 1 exposure, but now 2 conversions
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 2)
    
    def test_variant_consistency_across_requests(self):
        """Test that same session uses same variant for all requests."""
        headers = get_navigation_headers()
        # First GET - assigns variant, no events
        response1 = self.client.get(self.abtest_url, **headers)
        variant1 = response1.context['variant']
        
        # Second GET - same variant, still no events
        response2 = self.client.get(self.abtest_url, **headers)
        variant2 = response2.context['variant']
        self.assertEqual(variant1, variant2)
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # Click - logs events with same variant
        ajax_headers = get_ajax_headers()
        response_click = self.client.post(
            self.click_url,
            data={},
            **ajax_headers
        )
        self.assertEqual(response_click.status_code, 200)
        
        # Check all events for this session have same variant
        session_id = response1.wsgi_request.session.session_key
        all_events = ABTestEvent.objects.filter(session_id=session_id)
        
        for event in all_events:
            self.assertEqual(event.variant, variant1, 
                           f"All events for session {session_id} should use variant {variant1}")
    
    def test_untrusted_variant_cannot_override_session_variant(self):
        """Test that untrusted POST variant data cannot override session variant."""
        headers = get_navigation_headers()
        # GET to assign variant via session (no events logged)
        response = self.client.get(self.abtest_url, **headers)
        session_variant = response.context['variant']
        
        # Click - server uses session variant, ignores POST data
        ajax_headers = get_ajax_headers()
        response_click = self.client.post(
            self.click_url,
            data={},  # Server ignores any variant in POST
            **ajax_headers
        )
        
        self.assertEqual(response_click.status_code, 200)
        
        # Check both exposure and conversion use session variant
        exposure = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).first()
        conversion = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).first()
        self.assertIsNotNone(exposure)
        self.assertIsNotNone(conversion)
        self.assertEqual(exposure.variant, session_variant)
        self.assertEqual(conversion.variant, session_variant)
    
    def test_exposure_deduplication_on_second_click(self):
        """Test that second click does not create duplicate exposure."""
        headers = get_navigation_headers()
        ajax_headers = get_ajax_headers()
        
        # GET - no events
        response1 = self.client.get(self.abtest_url, **headers)
        session_id = response1.wsgi_request.session.session_key
        
        # First click - creates exposure + conversion
        self.client.post(self.click_url, data={}, **ajax_headers)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        
        # Second click - should NOT create duplicate exposure, only conversion
        self.client.post(self.click_url, data={}, **ajax_headers)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 2)
    
    def test_non_get_requests_do_not_log_exposure(self):
        """Test that HEAD/other methods do not log exposure (and GET doesn't either)."""
        headers = get_navigation_headers()
        # HEAD request
        response = self.client.head(self.abtest_url, **headers)
        self.assertEqual(response.status_code, 405)  # Method not allowed
        
        # Should have no events
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # POST to GET endpoint
        response = self.client.post(self.abtest_url, **headers)
        self.assertEqual(response.status_code, 405)
        
        # Should still have no events
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # GET request - also should not log exposure
        response = self.client.get(self.abtest_url, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ABTestEvent.objects.count(), 0, "GET should not log exposure")
    
    def test_non_post_requests_do_not_log_conversion(self):
        """Test that GET/HEAD to click endpoint do not log conversion."""
        ajax_headers = get_ajax_headers()
        # GET request to click endpoint
        response = self.client.get(self.click_url, **ajax_headers)
        self.assertEqual(response.status_code, 405)  # Method not allowed
        
        # Should have no events
        self.assertEqual(ABTestEvent.objects.count(), 0)
    
    def test_get_requests_never_log_exposure_regardless_of_headers(self):
        """Test that GET requests never log exposure, regardless of headers."""
        # Request with various header combinations - none should log exposure
        test_cases = [
            {
                'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'HTTP_SEC_FETCH_DEST': 'document',
                'HTTP_SEC_FETCH_MODE': 'navigate',
                'HTTP_SEC_FETCH_SITE': 'same-origin',
            },
            {
                'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            },
        ]
        
        for headers in test_cases:
            ABTestEvent.objects.all().delete()
            response = self.client.get(self.abtest_url, **headers)
            self.assertEqual(response.status_code, 200)
            # Should NOT have logged exposure
            self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 0)
    
    def test_50_50_split_across_many_sessions(self):
        """Test that variant assignment is roughly 50/50 across many sessions."""
        kudos_count = 0
        thanks_count = 0
        n = 200
        
        headers = get_navigation_headers()
        for _ in range(n):
            client = Client()  # New client = new session
            response = client.get(self.abtest_url, **headers)
            variant = response.context['variant']
            if variant == 'kudos':
                kudos_count += 1
            elif variant == 'thanks':
                thanks_count += 1
        
        # Both variants should appear
        self.assertGreater(kudos_count, 0, "Should see at least one 'kudos' variant")
        self.assertGreater(thanks_count, 0, "Should see at least one 'thanks' variant")
        self.assertEqual(kudos_count + thanks_count, n)
        
        # Roughly 50/50 split (allow 30-70% range to account for randomness)
        kudos_pct = (kudos_count / n) * 100
        thanks_pct = (thanks_count / n) * 100
        self.assertGreaterEqual(kudos_pct, 30, f"Kudos should be at least 30%, got {kudos_pct}%")
        self.assertLessEqual(kudos_pct, 70, f"Kudos should be at most 70%, got {kudos_pct}%")
        self.assertGreaterEqual(thanks_pct, 30, f"Thanks should be at least 30%, got {thanks_pct}%")
        self.assertLessEqual(thanks_pct, 70, f"Thanks should be at most 70%, got {thanks_pct}%")
        
        # Verify no events were logged from GET requests
        self.assertEqual(ABTestEvent.objects.count(), 0, "GET requests should not log any events")
    
    def test_variant_in_template_matches_session_variant(self):
        """Test that template button label matches session variant."""
        headers = get_navigation_headers()
        
        # Test with 'kudos'
        with patch('core.views.random.choice', return_value='kudos'):
            response = self.client.get(self.abtest_url, **headers)
            content = response.content.decode()
            # Find the AB test button specifically (id="abtest-btn")
            button_match_start = content.find('id="abtest-btn"')
            self.assertNotEqual(button_match_start, -1, "AB test button should exist")
            if button_match_start != -1:
                # Find the opening button tag
                button_tag_start = content.rfind('<button', 0, button_match_start)
                # Find the closing button tag
                button_match_end = content.find('</button>', button_match_start)
                if button_tag_start != -1 and button_match_end != -1:
                    button_html = content[button_tag_start:button_match_end]
                    self.assertIn('kudos', button_html.lower())
                    # When variant is 'kudos', button should NOT show 'thanks'
                    self.assertNotIn('thanks', button_html.lower())
        
        # Test with 'thanks'
        client2 = Client()  # New session
        with patch('core.views.random.choice', return_value='thanks'):
            response2 = client2.get(self.abtest_url, **headers)
            content2 = response2.content.decode()
            button_match_start2 = content2.find('id="abtest-btn"')
            self.assertNotEqual(button_match_start2, -1, "AB test button should exist")
            if button_match_start2 != -1:
                button_tag_start2 = content2.rfind('<button', 0, button_match_start2)
                button_match_end2 = content2.find('</button>', button_match_start2)
                if button_tag_start2 != -1 and button_match_end2 != -1:
                    button_html2 = content2[button_tag_start2:button_match_end2]
                    self.assertIn('thanks', button_html2.lower())
                    # When variant is 'thanks', button should NOT show 'kudos'
                    self.assertNotIn('kudos', button_html2.lower())
    
    def test_get_without_sec_fetch_headers_no_exposure(self):
        """Test that GET without Sec-Fetch headers does not create exposure."""
        # Request with browser UA but no Sec-Fetch headers
        response = self.client.get(
            self.abtest_url,
            HTTP_USER_AGENT='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.assertEqual(response.status_code, 200)  # Page still renders
        
        # But should NOT have logged exposure
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 0)
    
    def test_get_with_curl_ua_no_exposure(self):
        """Test that GET with curl UA does not create exposure."""
        response = self.client.get(
            self.abtest_url,
            HTTP_USER_AGENT='curl/8.6.0',
            HTTP_SEC_FETCH_DEST='document',
            HTTP_SEC_FETCH_MODE='navigate',
            HTTP_SEC_FETCH_SITE='same-origin',
        )
        self.assertEqual(response.status_code, 200)  # Page still renders
        
        # But should NOT have logged exposure (curl is detected as bot)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 0)
    
    def test_post_without_sec_fetch_headers_still_logs_conversion(self):
        """Test that POST without Sec-Fetch headers still logs conversion (clicks are always logged)."""
        headers = get_navigation_headers()
        # GET - no events
        self.client.get(self.abtest_url, **headers)
        
        # POST without Sec-Fetch headers - should still log (clicks are always logged)
        response = self.client.post(
            self.click_url,
            data={},
            HTTP_USER_AGENT='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.assertEqual(response.status_code, 200)
        
        # Should have exposure (from first click) and conversion
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
        
        # Response should indicate success
        import json
        data = json.loads(response.content)
        self.assertEqual(data.get('status'), 'ok')
    
    def test_normal_browser_flow_one_exposure_one_conversion(self):
        """Test that normal browser flow produces exactly 1 exposure + 1 conversion."""
        headers = get_navigation_headers()
        ajax_headers = get_ajax_headers()
        
        # GET - does NOT create exposure
        response1 = self.client.get(self.abtest_url, **headers)
        self.assertEqual(response1.status_code, 200)
        
        # Should have NO events from GET
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 0)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 0)
        
        # POST - creates BOTH exposure (first click) and conversion
        response2 = self.client.post(self.click_url, data={}, **ajax_headers)
        self.assertEqual(response2.status_code, 200)
        
        # Should have exactly one exposure and one conversion (both from click)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
        
        # Variants should match
        exposure = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).first()
        conversion = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).first()
        self.assertEqual(exposure.variant, conversion.variant)
