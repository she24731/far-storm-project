"""
Tests for A/B test admin summary view.

Tests the /admin/core/abtestevent/abtest-summary/ endpoint.
"""
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from core.models import ABTestEvent


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class ABTestAdminSummaryTest(TestCase):
    """Test A/B test admin summary view."""
    
    def setUp(self):
        """Set up test client and superuser."""
        self.client = Client()
        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        # Login
        self.client.login(username='admin', password='testpass123')
        # Clear all events
        ABTestEvent.objects.all().delete()
    
    def test_summary_with_valid_data(self):
        """Test summary page with valid exposure and conversion data."""
        experiment_name = "button_label_kudos_vs_thanks"
        
        # Create exposure events for kudos
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='kudos',
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        # Create conversion events for kudos
        for i in range(20):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='kudos',
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        # Create exposure events for thanks
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='thanks',
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # Create conversion events for thanks
        for i in range(30):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='thanks',
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # GET the summary page
        response = self.client.get('/admin/core/abtestevent/abtest-summary/')
        
        # Should not crash
        self.assertEqual(response.status_code, 200, 
                        f"Expected 200, got {response.status_code}. Response: {response.content.decode()[:500]}")
        
        # Check content
        content = response.content.decode('utf-8')
        self.assertIn(experiment_name, content)
        self.assertIn('kudos', content)
        self.assertIn('thanks', content)
        self.assertIn('100', content)  # Impressions
        self.assertIn('20', content)  # Conversions for kudos
        self.assertIn('30', content)  # Conversions for thanks
    
    def test_summary_handles_zero_impressions(self):
        """Test summary page when only conversions exist (no exposures)."""
        experiment_name = "button_label_kudos_vs_thanks"
        
        # Create only conversion events (no exposures)
        for i in range(10):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='kudos',
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        # GET the summary page
        response = self.client.get('/admin/core/abtestevent/abtest-summary/')
        
        # Should not crash
        self.assertEqual(response.status_code, 200,
                        f"Expected 200, got {response.status_code}. Response: {response.content.decode()[:500]}")
        
        # Check content
        content = response.content.decode('utf-8')
        self.assertIn(experiment_name, content)
        self.assertIn('kudos', content)
    
    def test_summary_one_variant_only(self):
        """Test summary page when only one variant exists."""
        experiment_name = "button_label_kudos_vs_thanks"
        
        # Create events only for kudos
        for i in range(50):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='kudos',
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        for i in range(10):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='kudos',
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        # GET the summary page
        response = self.client.get('/admin/core/abtestevent/abtest-summary/')
        
        # Should not crash
        self.assertEqual(response.status_code, 200,
                        f"Expected 200, got {response.status_code}. Response: {response.content.decode()[:500]}")
        
        # Check content
        content = response.content.decode('utf-8')
        self.assertIn(experiment_name, content)
        self.assertIn('kudos', content)
    
    def test_summary_with_no_events(self):
        """Test summary page when no events exist."""
        # GET the summary page
        response = self.client.get('/admin/core/abtestevent/abtest-summary/')
        
        # Should not crash
        self.assertEqual(response.status_code, 200,
                        f"Expected 200, got {response.status_code}. Response: {response.content.decode()[:500]}")
        
        # Should show friendly message
        content = response.content.decode('utf-8')
        self.assertIn('No A/B test data available', content)
    
    def test_summary_calculates_conversion_rates_correctly(self):
        """Test that conversion rates are calculated correctly."""
        experiment_name = "button_label_kudos_vs_thanks"
        
        # kudos: 100 exposures, 20 conversions = 20% rate
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='kudos',
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        for i in range(20):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='kudos',
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        # thanks: 100 exposures, 30 conversions = 30% rate
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='thanks',
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        for i in range(30):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='thanks',
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        response = self.client.get('/admin/core/abtestevent/abtest-summary/')
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        # Check that conversion rates are present
        self.assertIn('20.00', content)  # kudos conversion rate
        self.assertIn('30.00', content)  # thanks conversion rate
        # thanks should be baseline (30% > 20%)
        # kudos should show negative uplift
        self.assertIn('-33.33', content)  # (20-30)/30 * 100 = -33.33%
    
    def test_summary_handles_all_zero_impressions(self):
        """Test summary when all variants have zero impressions."""
        experiment_name = "button_label_kudos_vs_thanks"
        
        # Only conversions, no exposures
        for i in range(5):
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='kudos',
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
            ABTestEvent.objects.create(
                experiment_name=experiment_name,
                variant='thanks',
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        response = self.client.get('/admin/core/abtestevent/abtest-summary/')
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        # Should show 0.00% conversion rates
        self.assertIn('0.00', content)
        # Should show N/A for uplift
        self.assertIn('N/A', content)

