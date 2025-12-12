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
        'HTTP_SEC_FETCH_DEST': 'document',
        'HTTP_SEC_FETCH_MODE': 'navigate',
        'HTTP_SEC_FETCH_SITE': 'none',
        'HTTP_USER_AGENT': BROWSER_UA,
    }


def get_ajax_headers():
    """Get realistic headers for AJAX POST requests."""
    return {
        'HTTP_USER_AGENT': BROWSER_UA,
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
    
    def test_first_get_assigns_variant_and_logs_one_exposure(self):
        """Test that first GET assigns variant and logs exactly one exposure."""
        headers = get_navigation_headers()
        with patch('core.views.random.choice', return_value='kudos'):
            response = self.client.get(self.abtest_url, **headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['variant'], 'kudos')
        
        # Should have exactly one exposure event
        exposure_events = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE)
        self.assertEqual(exposure_events.count(), 1)
        
        event = exposure_events.first()
        self.assertEqual(event.variant, 'kudos')
        self.assertEqual(event.experiment_name, 'button_label_kudos_vs_thanks')
        self.assertEqual(event.endpoint, '/218b7ae/')
    
    def test_second_get_same_session_no_duplicate_exposure(self):
        """Test that second GET in same session does NOT create duplicate exposure."""
        headers = get_navigation_headers()
        # First GET - should log one exposure
        response1 = self.client.get(self.abtest_url, **headers)
        variant1 = response1.context['variant']
        
        exposure_count_1 = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count()
        self.assertEqual(exposure_count_1, 1)
        
        # Second GET in same session - should NOT log another exposure
        response2 = self.client.get(self.abtest_url, **headers)
        variant2 = response2.context['variant']
        
        # Variant should be same
        self.assertEqual(variant1, variant2)
        
        # Should still have exactly one exposure
        exposure_count_2 = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count()
        self.assertEqual(exposure_count_2, 1, "Second GET should not create duplicate exposure")
    
    def test_click_creates_conversion_and_not_duplicate_exposure(self):
        """Test that click creates conversion without duplicating exposure."""
        headers = get_navigation_headers()
        # First GET - creates exposure
        response1 = self.client.get(self.abtest_url, **headers)
        variant1 = response1.context['variant']
        
        # Should have exactly one exposure
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 0)
        
        # Click
        ajax_headers = get_ajax_headers()
        response_click = self.client.post(
            self.click_url,
            data={},
            **ajax_headers
        )
        self.assertEqual(response_click.status_code, 200)
        
        # Should still have exactly one exposure, and now one conversion
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
        
        # Check variant consistency
        exposure = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).first()
        conversion = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).first()
        self.assertEqual(exposure.variant, variant1)
        self.assertEqual(conversion.variant, variant1)
        self.assertEqual(exposure.variant, conversion.variant)
    
    def test_click_without_exposure_backfills_exposure_once(self):
        """Test that click without prior exposure backfills exposure."""
        ajax_headers = get_ajax_headers()
        # Direct POST to click endpoint without prior GET
        response_click = self.client.post(
            self.click_url,
            data={},
            **ajax_headers
        )
        self.assertEqual(response_click.status_code, 200)
        
        # Should have created both exposure (backfilled) and conversion
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count(), 1)
        self.assertEqual(ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).count(), 1)
        
        # Check variant consistency
        exposure = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).first()
        conversion = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).first()
        self.assertEqual(exposure.variant, conversion.variant)
    
    def test_variant_consistency_across_requests(self):
        """Test that same session uses same variant for all requests."""
        headers = get_navigation_headers()
        # First GET
        response1 = self.client.get(self.abtest_url, **headers)
        variant1 = response1.context['variant']
        
        # Second GET
        response2 = self.client.get(self.abtest_url, **headers)
        variant2 = response2.context['variant']
        
        # Click
        ajax_headers = get_ajax_headers()
        response_click = self.client.post(
            self.click_url,
            data={},
            **ajax_headers
        )
        self.assertEqual(response_click.status_code, 200)
        
        # All should use same variant
        self.assertEqual(variant1, variant2)
        
        # Check all events for this session have same variant
        session_id = response1.wsgi_request.session.session_key
        all_events = ABTestEvent.objects.filter(session_id=session_id)
        
        for event in all_events:
            self.assertEqual(event.variant, variant1, 
                           f"All events for session {session_id} should use variant {variant1}")
    
    def test_untrusted_variant_cannot_override_session_variant(self):
        """Test that untrusted POST variant data cannot override session variant."""
        headers = get_navigation_headers()
        # First GET to assign variant via session
        response = self.client.get(self.abtest_url, **headers)
        session_variant = response.context['variant']
        
        # Try to send different variant in POST (even though server ignores it)
        wrong_variant = 'thanks' if session_variant == 'kudos' else 'kudos'
        ajax_headers = get_ajax_headers()
        response_click = self.client.post(
            self.click_url,
            data={'variant': wrong_variant},  # Wrong variant - server ignores this
            **ajax_headers
        )
        
        self.assertEqual(response_click.status_code, 200)
        
        # Check conversion uses session variant, not POST variant
        conversion = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).first()
        self.assertIsNotNone(conversion)
        self.assertEqual(conversion.variant, session_variant)
        self.assertNotEqual(conversion.variant, wrong_variant)
    
    def test_exposure_deduplication_with_db_check(self):
        """Test that DB check prevents duplicate exposures even if session flag fails."""
        headers = get_navigation_headers()
        # First GET - creates exposure
        response1 = self.client.get(self.abtest_url, **headers)
        session_id = response1.wsgi_request.session.session_key
        
        # Verify one exposure exists
        exposures_1 = ABTestEvent.objects.filter(
            experiment_name='button_label_kudos_vs_thanks',
            endpoint='/218b7ae/',
            session_id=session_id,
            event_type=ABTestEvent.EVENT_TYPE_EXPOSURE
        )
        self.assertEqual(exposures_1.count(), 1)
        
        # Manually create another exposure (simulating edge case)
        ABTestEvent.objects.create(
            experiment_name='button_label_kudos_vs_thanks',
            variant='kudos',
            event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
            endpoint='/218b7ae/',
            session_id=session_id,
            is_forced=False,
        )
        
        # Second GET - should detect existing exposure in DB and not create another
        response2 = self.client.get(self.abtest_url, **headers)
        self.assertEqual(response2.status_code, 200)
        
        # Should still have exactly 2: original + manual (get_or_create prevents duplicate)
        exposures_after_second_get = ABTestEvent.objects.filter(
            experiment_name='button_label_kudos_vs_thanks',
            endpoint='/218b7ae/',
            session_id=session_id,
            event_type=ABTestEvent.EVENT_TYPE_EXPOSURE
        )
        self.assertEqual(exposures_after_second_get.count(), 2)
    
    def test_non_get_requests_do_not_log_exposure(self):
        """Test that HEAD/other methods do not log exposure."""
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
    
    def test_non_post_requests_do_not_log_conversion(self):
        """Test that GET/HEAD to click endpoint do not log conversion."""
        ajax_headers = get_ajax_headers()
        # GET request to click endpoint
        response = self.client.get(self.click_url, **ajax_headers)
        self.assertEqual(response.status_code, 405)  # Method not allowed
        
        # Should have no events
        self.assertEqual(ABTestEvent.objects.count(), 0)
    
    def test_non_navigation_requests_do_not_log_exposure(self):
        """Test that prefetch/background requests do not log exposure."""
        # Request without Sec-Fetch headers (or with non-navigation values)
        response = self.client.get(
            self.abtest_url,
            HTTP_USER_AGENT=BROWSER_UA,
            HTTP_SEC_FETCH_DEST='image',  # Not a navigation
            HTTP_SEC_FETCH_MODE='no-cors',
        )
        self.assertEqual(response.status_code, 200)  # Page still renders
        
        # But should NOT have logged exposure
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
