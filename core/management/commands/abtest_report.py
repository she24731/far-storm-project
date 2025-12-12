"""
Django management command to generate an A/B test summary report.

Queries ABTestEvent table and computes exposure/conversion statistics per variant.

Usage:
    python manage.py abtest_report
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone
from core.models import ABTestEvent


class Command(BaseCommand):
    help = 'Generate A/B test summary report from ABTestEvent table'

    def handle(self, *args, **options):
        experiment_name = "button_label_kudos_vs_thanks"
        endpoint = "/218b7ae/"
        
        # Query events for this experiment and endpoint
        events = ABTestEvent.objects.filter(
            experiment_name=experiment_name,
            endpoint=endpoint
        )
        
        total_events = events.count()
        
        # Get exposure and conversion counts per variant
        exposure_counts = (
            events
            .filter(event_type=ABTestEvent.EVENT_TYPE_EXPOSURE)
            .values('variant')
            .annotate(count=Count('id'))
        )
        
        conversion_counts = (
            events
            .filter(event_type=ABTestEvent.EVENT_TYPE_CONVERSION)
            .values('variant')
            .annotate(count=Count('id'))
        )
        
        # Build dictionaries for easy lookup
        exposure_dict = {item['variant']: item['count'] for item in exposure_counts}
        conversion_dict = {item['variant']: item['count'] for item in conversion_counts}
        
        # Get all variants (should be "kudos" and "thanks")
        all_variants = sorted(set(list(exposure_dict.keys()) + list(conversion_dict.keys())))
        
        # Print report header
        self.stdout.write(self.style.SUCCESS('\n=== A/B Test Summary Report ==='))
        self.stdout.write(f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M:%S %Z")}')
        self.stdout.write(f'Experiment: {experiment_name}')
        self.stdout.write(f'Endpoint: {endpoint}')
        self.stdout.write(f'Total Events: {total_events:,}')
        self.stdout.write('')
        
        if not all_variants:
            self.stdout.write(self.style.WARNING('No data found for this experiment/endpoint.'))
            return
        
        # Print table header
        self.stdout.write('-' * 70)
        self.stdout.write(f'{"Variant":<15} {"Exposures":<15} {"Conversions":<15} {"Conversion Rate":<20}')
        self.stdout.write('-' * 70)
        
        # Calculate and display stats per variant
        variant_stats = []
        total_exposures = 0
        
        for variant in sorted(all_variants):
            exposures = exposure_dict.get(variant, 0)
            conversions = conversion_dict.get(variant, 0)
            conversion_rate = (conversions / exposures * 100) if exposures > 0 else 0.0
            
            total_exposures += exposures
            variant_stats.append({
                'variant': variant,
                'exposures': exposures,
                'conversions': conversions,
                'conversion_rate': conversion_rate,
            })
            
            # Format conversion rate as percentage
            rate_str = f'{conversion_rate:.2f}%' if exposures > 0 else 'N/A'
            
            self.stdout.write(
                f'{variant:<15} {exposures:<15,} {conversions:<15,} {rate_str:<20}'
            )
        
        self.stdout.write('-' * 70)
        self.stdout.write('')
        
        # Determine winner
        if len(variant_stats) >= 2:
            # Sort by conversion rate (descending)
            sorted_stats = sorted(variant_stats, key=lambda x: x['conversion_rate'], reverse=True)
            winner = sorted_stats[0]
            runner_up = sorted_stats[1]
            
            if winner['conversion_rate'] == runner_up['conversion_rate']:
                self.stdout.write(self.style.WARNING('Result: TIE (equal conversion rates)'))
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Winner: "{winner["variant"]}" '
                        f'(conversion rate: {winner["conversion_rate"]:.2f}% vs '
                        f'{runner_up["conversion_rate"]:.2f}%)'
                    )
                )
        elif len(variant_stats) == 1:
            self.stdout.write(
                self.style.WARNING(
                    f'Only one variant found: "{variant_stats[0]["variant"]}" '
                    f'(conversion rate: {variant_stats[0]["conversion_rate"]:.2f}%)'
                )
            )
        
        self.stdout.write('')
        
        # Sample size caution
        if total_exposures < 30:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  CAUTION: Total exposures ({total_exposures}) is less than 30. '
                    'Results may not be statistically significant. Consider collecting more data.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Sample size: {total_exposures} total exposures (sufficient for basic analysis)'
                )
            )
        
        self.stdout.write('')

