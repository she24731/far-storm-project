"""
Tests for the abtest_report management command.
"""

from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from core.models import ABTestEvent


class ABTestReportCommandTest(TestCase):
    """Test the abtest_report management command."""
    
    def setUp(self):
        """Set up test data with both variants."""
        self.experiment_name = "button_label_kudos_vs_thanks"
        self.endpoint = "/218b7ae/"
        
        # Create test data: kudos variant
        # 50 exposures, 10 conversions (20% rate)
        for i in range(50):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant="kudos",
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint=self.endpoint,
                session_id=f"session_kudos_{i}",
            )
        for i in range(10):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant="kudos",
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint=self.endpoint,
                session_id=f"session_kudos_{i % 10}",
            )
        
        # Create test data: thanks variant
        # 60 exposures, 18 conversions (30% rate)
        for i in range(60):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant="thanks",
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint=self.endpoint,
                session_id=f"session_thanks_{i}",
            )
        for i in range(18):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant="thanks",
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint=self.endpoint,
                session_id=f"session_thanks_{i % 18}",
            )
    
    def test_report_includes_both_variants(self):
        """Test that the report includes both variants."""
        out = StringIO()
        call_command('abtest_report', stdout=out)
        output = out.getvalue()
        
        # Should contain both variants
        self.assertIn('kudos', output)
        self.assertIn('thanks', output)
        
        # Should contain exposure counts
        self.assertIn('50', output)  # kudos exposures
        self.assertIn('60', output)  # thanks exposures
        
        # Should contain conversion counts
        self.assertIn('10', output)  # kudos conversions
        self.assertIn('18', output)  # thanks conversions
    
    def test_report_shows_correct_conversion_rates(self):
        """Test that conversion rates are calculated correctly."""
        out = StringIO()
        call_command('abtest_report', stdout=out)
        output = out.getvalue()
        
        # kudos: 10/50 = 20%
        self.assertIn('20.00%', output)
        
        # thanks: 18/60 = 30%
        self.assertIn('30.00%', output)
    
    def test_report_identifies_winner(self):
        """Test that the report correctly identifies the winner."""
        out = StringIO()
        call_command('abtest_report', stdout=out)
        output = out.getvalue()
        
        # thanks should win (30% > 20%)
        self.assertIn('Winner: "thanks"', output)
        self.assertIn('30.00%', output)
        self.assertIn('20.00%', output)
    
    def test_report_shows_tie_when_rates_equal(self):
        """Test that the report shows TIE when conversion rates are equal."""
        # Clear existing data
        ABTestEvent.objects.all().delete()
        
        # Create equal conversion rates: both 25%
        # kudos: 40 exposures, 10 conversions
        for i in range(40):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant="kudos",
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint=self.endpoint,
                session_id=f"session_kudos_{i}",
            )
        for i in range(10):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant="kudos",
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint=self.endpoint,
                session_id=f"session_kudos_{i % 10}",
            )
        
        # thanks: 40 exposures, 10 conversions
        for i in range(40):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant="thanks",
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint=self.endpoint,
                session_id=f"session_thanks_{i}",
            )
        for i in range(10):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant="thanks",
                event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
                endpoint=self.endpoint,
                session_id=f"session_thanks_{i % 10}",
            )
        
        out = StringIO()
        call_command('abtest_report', stdout=out)
        output = out.getvalue()
        
        self.assertIn('TIE', output)
        self.assertIn('equal conversion rates', output)
    
    def test_report_shows_caution_for_low_exposures(self):
        """Test that the report shows caution when total exposures < 30."""
        # Clear existing data
        ABTestEvent.objects.all().delete()
        
        # Create small dataset: 10 exposures total
        for i in range(5):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant="kudos",
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint=self.endpoint,
                session_id=f"session_kudos_{i}",
            )
        for i in range(5):
            ABTestEvent.objects.create(
                experiment_name=self.experiment_name,
                variant="thanks",
                event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
                endpoint=self.endpoint,
                session_id=f"session_thanks_{i}",
            )
        
        out = StringIO()
        call_command('abtest_report', stdout=out)
        output = out.getvalue()
        
        self.assertIn('CAUTION', output)
        self.assertIn('less than 30', output)
        self.assertIn('10', output)  # total exposures
    
    def test_report_shows_success_for_sufficient_exposures(self):
        """Test that the report shows success message when exposures >= 30."""
        out = StringIO()
        call_command('abtest_report', stdout=out)
        output = out.getvalue()
        
        # Total exposures = 50 + 60 = 110, which is >= 30
        self.assertIn('sufficient for basic analysis', output)
        self.assertIn('110', output)  # total exposures
    
    def test_report_includes_timestamp(self):
        """Test that the report includes a timestamp."""
        out = StringIO()
        call_command('abtest_report', stdout=out)
        output = out.getvalue()
        
        self.assertIn('Generated:', output)
    
    def test_report_includes_total_events(self):
        """Test that the report includes total events count."""
        out = StringIO()
        call_command('abtest_report', stdout=out)
        output = out.getvalue()
        
        # Total events = 50 + 10 + 60 + 18 = 138
        self.assertIn('Total Events:', output)
        self.assertIn('138', output)
    
    def test_report_handles_zero_exposures(self):
        """Test that the report handles variants with zero exposures gracefully."""
        # Clear existing data
        ABTestEvent.objects.all().delete()
        
        # Create only conversions (no exposures) for one variant
        ABTestEvent.objects.create(
            experiment_name=self.experiment_name,
            variant="kudos",
            event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
            endpoint=self.endpoint,
            session_id="session_1",
        )
        
        # Create normal data for other variant
        ABTestEvent.objects.create(
            experiment_name=self.experiment_name,
            variant="thanks",
            event_type=ABTestEvent.EVENT_TYPE_EXPOSURE,
            endpoint=self.endpoint,
            session_id="session_2",
        )
        ABTestEvent.objects.create(
            experiment_name=self.experiment_name,
            variant="thanks",
            event_type=ABTestEvent.EVENT_TYPE_CONVERSION,
            endpoint=self.endpoint,
            session_id="session_2",
        )
        
        out = StringIO()
        call_command('abtest_report', stdout=out)
        output = out.getvalue()
        
        # Should not crash and should show N/A for kudos conversion rate
        self.assertIn('N/A', output)
        self.assertIn('kudos', output)
        self.assertIn('thanks', output)

