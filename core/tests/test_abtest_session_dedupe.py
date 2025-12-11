"""
Tests for session-based A/B test assignment and deduplication.

Tests per-session variant assignment, exposure deduplication, and variant consistency.
"""
from django.test import TestCase, Client
from unittest.mock import patch
from core.models import ABTestEvent


class ABTestSessionAssignmentTest(TestCase):
    """Test per-session variant assignment and exposure deduplication."""
    
    def setUp(self):
        """Set up test client and clear events."""
        self.client = Client()
        self.abtest_url = '/218b7ae/'
        self.click_url = '/218b7ae/click/'
        self.browser_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ABTestEvent.objects.all().delete()
    
    def test_first_get_assigns_variant_and_logs_one_exposure(self):
        """Test that first GET assigns variant and logs exactly one exposure."""
        with patch('core.views.random.choice', return_value='kudos'):
            response = self.client.get(self.abtest_url, HTTP_USER_AGENT=self.browser_ua)
        
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
        # First GET - should log one exposure
        response1 = self.client.get(self.abtest_url, HTTP_USER_AGENT=self.browser_ua)
        variant1 = response1.context['variant']
        
        exposure_count_1 = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count()
        self.assertEqual(exposure_count_1, 1)
        
        # Second GET in same session - should NOT log another exposure
        response2 = self.client.get(self.abtest_url, HTTP_USER_AGENT=self.browser_ua)
        variant2 = response2.context['variant']
        
        # Variant should be same
        self.assertEqual(variant1, variant2)
        
        # Should still have exactly one exposure
        exposure_count_2 = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE).count()
        self.assertEqual(exposure_count_2, 1, "Second GET should not create duplicate exposure")
    
    def test_variant_consistency_across_requests(self):
        """Test that same session uses same variant for all requests."""
        # First GET
        response1 = self.client.get(self.abtest_url, HTTP_USER_AGENT=self.browser_ua)
        variant1 = response1.context['variant']
        
        # Second GET
        response2 = self.client.get(self.abtest_url, HTTP_USER_AGENT=self.browser_ua)
        variant2 = response2.context['variant']
        
        # Click
        response_click = self.client.post(
            self.click_url,
            data={},
            HTTP_USER_AGENT=self.browser_ua
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
        # First GET to assign variant via session
        response = self.client.get(self.abtest_url, HTTP_USER_AGENT=self.browser_ua)
        session_variant = response.context['variant']
        
        # Try to send different variant in POST
        wrong_variant = 'thanks' if session_variant == 'kudos' else 'kudos'
        response_click = self.client.post(
            self.click_url,
            data={'variant': wrong_variant},  # Wrong variant
            HTTP_USER_AGENT=self.browser_ua
        )
        
        self.assertEqual(response_click.status_code, 200)
        
        # Check conversion uses session variant, not POST variant
        conversion = ABTestEvent.objects.filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION).first()
        self.assertIsNotNone(conversion)
        self.assertEqual(conversion.variant, session_variant)
        self.assertNotEqual(conversion.variant, wrong_variant)
    
    def test_exposure_deduplication_with_db_check(self):
        """Test that DB check prevents duplicate exposures even if session flag fails."""
        # First GET - creates exposure
        response1 = self.client.get(self.abtest_url, HTTP_USER_AGENT=self.browser_ua)
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
        
        # Now second GET should NOT create another exposure due to DB check
        response2 = self.client.get(self.abtest_url, HTTP_USER_AGENT=self.browser_ua)
        self.assertEqual(response2.status_code, 200)
        
        # The view checks DB before creating, so it should detect existing exposure
        # and not create another
        exposures_after_second_get = ABTestEvent.objects.filter(
            experiment_name='button_label_kudos_vs_thanks',
            endpoint='/218b7ae/',
            session_id=session_id,
            event_type=ABTestEvent.EVENT_TYPE_EXPOSURE
        )
        # Should have exactly 2: original from first GET + the one we manually created
        # The second GET should NOT have created a third due to DB check
        self.assertEqual(exposures_after_second_get.count(), 2)

