"""
Tests for A/B test management commands.

Tests ab_check_traffic_split and ab_analyze_button_label commands.
"""
from django.test import TestCase
from django.core.management import call_command
from io import StringIO
from core.models import ABTestEvent


class ABTestTrafficSplitCommandTest(TestCase):
    """Test ab_check_traffic_split management command."""
    
    def setUp(self):
        """Set up test data."""
        self.experiment_name = 'button_label_kudos_vs_thanks'
        # Clear any existing events
        ABTestEvent.objects.all().delete()
    
    def test_traffic_split_balanced_no_mismatch(self):
        """Test traffic split with balanced 50/50 distribution."""
        # Create 100 exposure events for 'kudos'
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        # Create 100 exposure events for 'thanks'
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='thanks',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # Run the command
        out = StringIO()
        call_command('ab_check_traffic_split', experiment=self.experiment_name, stdout=out)
        output = out.getvalue()
        
        # Assert output contains counts for both variants
        self.assertIn('kudos', output)
        self.assertIn('thanks', output)
        self.assertIn('100', output)  # Should show 100 events for each
        
        # Assert no sample ratio mismatch warning
        self.assertNotIn('Sample ratio mismatch detected', output)
        self.assertIn('No sample ratio mismatch detected', output)
        self.assertIn('within expected range', output)
    
    def test_traffic_split_skewed_shows_mismatch(self):
        """Test traffic split with skewed distribution (180 vs 20)."""
        # Create 180 exposure events for 'kudos'
        for i in range(180):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        # Create only 20 exposure events for 'thanks'
        for i in range(20):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='thanks',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # Run the command
        out = StringIO()
        call_command('ab_check_traffic_split', experiment=self.experiment_name, stdout=out)
        output = out.getvalue()
        
        # Assert output contains counts for both variants
        self.assertIn('kudos', output)
        self.assertIn('thanks', output)
        self.assertIn('180', output)  # Should show 180 events for kudos
        self.assertIn('20', output)  # Should show 20 events for thanks
        
        # Assert sample ratio mismatch warning is present
        self.assertIn('Sample ratio mismatch detected', output)
        self.assertIn('outside expected range', output)
        self.assertIn('⚠️', output)  # Warning emoji
    
    def test_traffic_split_with_conversions(self):
        """Test traffic split command shows conversion rates."""
        # Create exposure events
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='thanks',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # Create some conversion events
        for i in range(20):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='conversion',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        for i in range(30):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='thanks',
                event_type='conversion',
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # Run the command
        out = StringIO()
        call_command('ab_check_traffic_split', experiment=self.experiment_name, stdout=out)
        output = out.getvalue()
        
        # Should show conversion rates
        self.assertIn('Conversion Rates', output)
        self.assertIn('conversion rate', output)
        self.assertIn('20/100', output)  # kudos: 20 conversions / 100 exposures
        self.assertIn('30/100', output)  # thanks: 30 conversions / 100 exposures


class ABTestAnalyzeCommandTest(TestCase):
    """Test ab_analyze_button_label management command."""
    
    def setUp(self):
        """Set up test data."""
        self.experiment_name = 'button_label_kudos_vs_thanks'
        # Clear any existing events
        ABTestEvent.objects.all().delete()
    
    def test_analyze_with_sample_data(self):
        """Test statistical analysis with sample dataset."""
        # Create 100 exposure events for 'kudos'
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        # Create 20 conversion events for 'kudos'
        for i in range(20):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='conversion',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        # Create 100 exposure events for 'thanks'
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='thanks',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # Create 30 conversion events for 'thanks'
        for i in range(30):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='thanks',
                event_type='conversion',
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # Run the command
        out = StringIO()
        call_command(
            'ab_analyze_button_label',
            experiment=self.experiment_name,
            confidence_level=0.95,
            stdout=out
        )
        output = out.getvalue()
        
        # Assert output contains hypotheses section
        self.assertIn('HYPOTHESES', output)
        self.assertIn('Null Hypothesis', output)
        self.assertIn('Alternative Hypothesis', output)
        
        # Assert output contains numerical results
        self.assertIn('NUMERICAL RESULTS', output)
        self.assertIn('Variant A ("kudos")', output)
        self.assertIn('Variant B ("thanks")', output)
        self.assertIn('Exposures (nA)', output)
        self.assertIn('Exposures (nB)', output)
        self.assertIn('Conversions (cA)', output)
        self.assertIn('Conversions (cB)', output)
        self.assertIn('Conversion Rate', output)
        
        # Assert specific values are present
        self.assertIn('100', output)  # 100 exposures for both
        self.assertIn('20', output)  # 20 conversions for kudos
        self.assertIn('30', output)  # 30 conversions for thanks
        
        # Assert statistical test results
        self.assertIn('Statistical Test Results', output)
        self.assertIn('Z-Score', output)
        self.assertIn('P-Value', output)
        self.assertIn('p-value', output.lower())  # Case insensitive check
        self.assertIn('Confidence Interval', output)
        self.assertIn('95%', output)
        
        # Assert executive summary
        self.assertIn('EXECUTIVE SUMMARY', output)
        self.assertIn('RECOMMENDATION', output)
    
    def test_analyze_with_insufficient_data(self):
        """Test that command handles insufficient data gracefully."""
        # Create only one variant's data
        for i in range(10):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        # Run the command
        out = StringIO()
        call_command(
            'ab_analyze_button_label',
            experiment=self.experiment_name,
            stdout=out
        )
        output = out.getvalue()
        
        # Should show error about insufficient data
        self.assertIn('ERROR', output)
        self.assertIn('Expected exactly 2 variants', output)
    
    def test_analyze_with_zero_exposures(self):
        """Test that command handles zero exposures gracefully."""
        # Create only conversion events (no exposures)
        for i in range(10):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='conversion',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        for i in range(10):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='thanks',
                event_type='conversion',
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # Run the command
        out = StringIO()
        call_command(
            'ab_analyze_button_label',
            experiment=self.experiment_name,
            stdout=out
        )
        output = out.getvalue()
        
        # Should show warning about insufficient data
        self.assertIn('WARNING', output)
        self.assertIn('Insufficient data', output)
        self.assertIn('0 exposures', output)
    
    def test_analyze_with_custom_confidence_level(self):
        """Test that command accepts custom confidence level."""
        # Create minimal valid dataset
        for i in range(50):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='thanks',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # Add some conversions
        for i in range(10):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='conversion',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        for i in range(15):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='thanks',
                event_type='conversion',
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # Run with custom confidence level
        out = StringIO()
        call_command(
            'ab_analyze_button_label',
            experiment=self.experiment_name,
            confidence_level=0.90,
            stdout=out
        )
        output = out.getvalue()
        
        # Should show 90% confidence level
        self.assertIn('90.0%', output)
        self.assertIn('Confidence Level', output)
    
    def test_analyze_shows_effect_size(self):
        """Test that command shows effect size calculations."""
        # Create dataset with clear difference
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        for i in range(10):  # 10% conversion rate
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='kudos',
                event_type='conversion',
                endpoint='/218b7ae/',
                session_id=f'session_kudos_{i}',
                is_forced=False,
            )
        
        for i in range(100):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='thanks',
                event_type='exposure',
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        for i in range(25):  # 25% conversion rate
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant='thanks',
                event_type='conversion',
                endpoint='/218b7ae/',
                session_id=f'session_thanks_{i}',
                is_forced=False,
            )
        
        # Run the command
        out = StringIO()
        call_command(
            'ab_analyze_button_label',
            experiment=self.experiment_name,
            stdout=out
        )
        output = out.getvalue()
        
        # Should show effect size
        self.assertIn('Effect Size', output)
        self.assertIn('Absolute Difference', output)
        self.assertIn('Relative Improvement', output)
        self.assertIn('percentage points', output)

