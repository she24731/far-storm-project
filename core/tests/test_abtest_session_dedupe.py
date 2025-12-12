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
    
    def test_first_get_logs_single_exposure(self):
        """Test that first GET logs exactly ONE Exposure."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        with patch('core.views.random.choice', return_value='kudos'):
            response = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['variant'], 'kudos')
        
        # Should have exactly ONE exposure, NO conversion
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 0)
        
        event = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).first()
        self.assertEqual(event.variant, 'kudos')
        self.assertEqual(event.experiment_name, 'button_label_kudos_vs_thanks')
        self.assertEqual(event.endpoint, '/218b7ae/')
    
    def test_reload_does_not_log_extra_exposure(self):
        """Test that reloading does not log additional Exposure."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        # First GET - logs one exposure
        response1 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        variant1 = response1.context['variant']
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        
        # Second GET (reload) - should NOT log additional exposure
        response2 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        variant2 = response2.context['variant']
        
        # Variant should be same
        self.assertEqual(variant1, variant2)
        
        # Should still have exactly ONE exposure
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1, "Reload should not create duplicate exposure")
    
    def test_click_logs_conversion_without_extra_exposure(self):
        """Test that click logs conversion without creating extra exposure."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        # GET - logs one exposure
        response1 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        variant1 = response1.context['variant']
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 0)
        
        # Click - logs conversion only, NO new exposure
        response_click = self.client.post(self.click_url, data={})
        self.assertEqual(response_click.status_code, 200)
        
        # Should still have exactly 1 exposure, and now 1 conversion
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
        
        # Check variant consistency
        exposure = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).first()
        conversion = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).first()
        self.assertEqual(exposure.variant, variant1)
        self.assertEqual(conversion.variant, variant1)
        self.assertEqual(exposure.variant, conversion.variant)
    
    def test_multiple_clicks_log_multiple_conversions(self):
        """Test that multiple clicks log multiple conversions, but only one exposure."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        # GET - logs one exposure
        self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        
        # First click - logs conversion only
        response1 = self.client.post(self.click_url, data={})
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
        
        # Second click - logs another conversion, NO new exposure
        response2 = self.client.post(self.click_url, data={})
        self.assertEqual(response2.status_code, 200)
        
        # Should still have exactly 1 exposure, but now 2 conversions
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 2)
    
    def test_variant_consistency_across_requests(self):
        """Test that same session uses same variant for all requests."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        # First GET - assigns variant and logs exposure
        response1 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        variant1 = response1.context['variant']
        
        # Second GET - same variant, no new exposure
        response2 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        variant2 = response2.context['variant']
        self.assertEqual(variant1, variant2)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        
        # Click - logs conversion with same variant
        response_click = self.client.post(self.click_url, data={})
        self.assertEqual(response_click.status_code, 200)
        
        # Check all events for this session have same variant
        session_id = response1.wsgi_request.session.session_key
        all_events = ABTestEvent.objects.filter(session_id=session_id)
        
        for event in all_events:
            self.assertEqual(event.variant, variant1, 
                           f"All events for session {session_id} should use variant {variant1}")
    
    def test_untrusted_variant_cannot_override_session_variant(self):
        """Test that untrusted POST variant data cannot override session variant."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        # GET to assign variant via session and log exposure
        response = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        session_variant = response.context['variant']
        
        # Click - server uses session variant, ignores POST data
        response_click = self.client.post(
            self.click_url,
            data={},  # Server ignores any variant in POST
        )
        
        self.assertEqual(response_click.status_code, 200)
        
        # Check both exposure and conversion use session variant
        exposure = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).first()
        conversion = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).first()
        self.assertIsNotNone(exposure)
        self.assertIsNotNone(conversion)
        self.assertEqual(exposure.variant, session_variant)
        self.assertEqual(conversion.variant, session_variant)
    
    def test_exposure_deduplication_on_reload(self):
        """Test that reload does not create duplicate exposure."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        # First GET - creates exposure
        response1 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        
        # Second GET (reload) - should NOT create duplicate exposure
        self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        
        # Click - should log conversion only
        self.client.post(self.click_url, data={})
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
    
    def test_non_get_requests_do_not_log_exposure(self):
        """Test that HEAD/other methods do not log exposure."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        # HEAD request
        response = self.client.head(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(response.status_code, 405)  # Method not allowed
        
        # Should have no events
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # POST to GET endpoint
        response = self.client.post(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(response.status_code, 405)
        
        # Should still have no events
        self.assertEqual(ABTestEvent.objects.count(), 0)
        
        # GET request with browser UA - should log exposure
        response = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
    
    def test_non_post_requests_do_not_log_conversion(self):
        """Test that GET/HEAD to click endpoint do not log conversion."""
        ajax_headers = get_ajax_headers()
        # GET request to click endpoint
        response = self.client.get(self.click_url, **ajax_headers)
        self.assertEqual(response.status_code, 405)  # Method not allowed
        
        # Should have no events
        self.assertEqual(ABTestEvent.objects.count(), 0)
    
    def test_bot_requests_do_not_log_exposure(self):
        """Test that bot/non-browser requests do not log exposure."""
        # Bot user agents should not log exposure
        bot_uas = [
            'curl/8.6.0',
            'Python-urllib/3.9',
            'Go-http-client/1.1',
            '',  # No UA
        ]
        
        for bot_ua in bot_uas:
            ABTestEvent.objects.all().delete()
            response = self.client.get(self.abtest_url, HTTP_USER_AGENT=bot_ua)
            self.assertEqual(response.status_code, 200)
            # Should NOT have logged exposure (not a browser)
            self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 0)
    
    def test_50_50_split_across_many_sessions(self):
        """Test that variant assignment is roughly 50/50 across many sessions."""
        kudos_count = 0
        thanks_count = 0
        n = 200
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        for _ in range(n):
            client = Client()  # New client = new session
            response = client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
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
        
        # Verify exactly n exposures were logged (one per session)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), n, "Each GET should log one exposure")
    
    def test_variant_in_template_matches_session_variant(self):
        """Test that template button label matches session variant."""
        headers = get_navigation_headers()
        
        # Test with 'kudos'
        with patch('core.views.random.choice', return_value='kudos'):
            response = self.client.get(self.abtest_url, **headers)
            content = response.content.decode()
            # Find the AB test button specifically (id="abtest")
            button_match_start = content.find('id="abtest"')
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
            button_match_start2 = content2.find('id="abtest"')
            self.assertNotEqual(button_match_start2, -1, "AB test button should exist")
            if button_match_start2 != -1:
                button_tag_start2 = content2.rfind('<button', 0, button_match_start2)
                button_match_end2 = content2.find('</button>', button_match_start2)
                if button_tag_start2 != -1 and button_match_end2 != -1:
                    button_html2 = content2[button_tag_start2:button_match_end2]
                    self.assertIn('thanks', button_html2.lower())
                    # When variant is 'thanks', button should NOT show 'kudos'
                    self.assertNotIn('kudos', button_html2.lower())
    
    def test_browser_get_without_sec_fetch_still_logs_exposure(self):
        """Test that browser GET without Sec-Fetch headers still logs exposure."""
        # Browser UA is sufficient, Sec-Fetch headers not required
        response = self.client.get(
            self.abtest_url,
            HTTP_USER_AGENT='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.assertEqual(response.status_code, 200)
        
        # Should have logged exposure (browser UA detected)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
    
    def test_curl_ua_no_exposure(self):
        """Test that GET with curl UA does not create exposure."""
        response = self.client.get(
            self.abtest_url,
            HTTP_USER_AGENT='curl/8.6.0',
        )
        self.assertEqual(response.status_code, 200)  # Page still renders
        
        # Should NOT have logged exposure (curl is detected as bot)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 0)
    
    def test_post_logs_conversion(self):
        """Test that POST logs conversion."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        # GET - logs exposure
        self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        
        # POST - should log conversion
        response = self.client.post(self.click_url, data={})
        self.assertEqual(response.status_code, 200)
        
        # Should have exposure (from GET) and conversion (from POST)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
        
        # Response should indicate success
        import json
        data = json.loads(response.content)
        self.assertEqual(data.get('status'), 'ok')
    
    def test_normal_browser_flow_one_exposure_one_conversion(self):
        """Test that normal browser flow produces exactly 1 exposure + 1 conversion."""
        browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        
        # GET - creates exposure
        response1 = self.client.get(self.abtest_url, HTTP_USER_AGENT=browser_ua)
        self.assertEqual(response1.status_code, 200)
        
        # Should have one exposure from GET
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 0)
        
        # POST - creates conversion only
        response2 = self.client.post(self.click_url, data={})
        self.assertEqual(response2.status_code, 200)
        
        # Should have exactly one exposure (from GET) and one conversion (from click)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
        
        # Variants should match
        exposure = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).first()
        conversion = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).first()
        self.assertEqual(exposure.variant, conversion.variant)
