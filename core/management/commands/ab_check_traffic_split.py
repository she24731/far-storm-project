"""
Django management command to check A/B test traffic split and sample ratio.

Usage:
    python manage.py ab_check_traffic_split --experiment=button_label_kudos_vs_thanks
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from core.models import ABTestEvent


class Command(BaseCommand):
    help = 'Check A/B test traffic split and detect sample ratio mismatch'

    def add_arguments(self, parser):
        parser.add_argument(
            '--experiment',
            type=str,
            default='button_label_kudos_vs_thanks',
            help='Experiment name to analyze (default: button_label_kudos_vs_thanks)',
        )
        parser.add_argument(
            '--event-type',
            type=str,
            choices=['exposure', 'conversion', 'all'],
            default='exposure',
            help='Event type to analyze (default: exposure). Note: conversions were previously called "click"',
        )
        parser.add_argument(
            '--exclude-forced',
            action='store_true',
            help='Exclude forced variants (from ?force_variant parameter)',
        )

    def handle(self, *args, **options):
        experiment_name = options['experiment']
        event_type = options['event_type']
        exclude_forced = options['exclude_forced']

        self.stdout.write(self.style.SUCCESS(f'\n=== A/B Test Traffic Split Analysis ==='))
        self.stdout.write(f'Experiment: {experiment_name}')
        self.stdout.write(f'Event Type: {event_type}')
        self.stdout.write(f'Exclude Forced: {exclude_forced}\n')

        # Build query
        query = Q(experiment_name=experiment_name)
        if exclude_forced:
            query &= Q(is_forced=False)
        
        if event_type != 'all':
            query &= Q(event_type=event_type)

        # Get counts per variant
        variant_counts = (
            ABTestEvent.objects
            .filter(query)
            .values('variant')
            .annotate(count=Count('id'))
            .order_by('variant')
        )

        if not variant_counts:
            self.stdout.write(self.style.WARNING('No events found for this experiment.'))
            return

        # Calculate totals and percentages
        total = sum(item['count'] for item in variant_counts)
        variant_data = {}
        
        for item in variant_counts:
            variant = item['variant']
            count = item['count']
            percentage = (count / total * 100) if total > 0 else 0
            variant_data[variant] = {
                'count': count,
                'percentage': percentage,
            }

        # Display results
        self.stdout.write(f'Total Events: {total}\n')
        self.stdout.write('Variant Distribution:')
        self.stdout.write('-' * 50)
        
        for variant in sorted(variant_data.keys()):
            data = variant_data[variant]
            self.stdout.write(
                f"  {variant:10s}: {data['count']:6d} events ({data['percentage']:5.2f}%)"
            )
        
        self.stdout.write('-' * 50)
        self.stdout.write('')

        # Sample ratio mismatch check (expecting 50/50 split)
        if len(variant_data) == 2:
            variants = sorted(variant_data.keys())
            var_a = variants[0]
            var_b = variants[1]
            
            pct_a = variant_data[var_a]['percentage']
            pct_b = variant_data[var_b]['percentage']
            
            # Flag if any variant is < 40% or > 60% (expecting 50/50)
            threshold_low = 40.0
            threshold_high = 60.0
            
            self.stdout.write('Sample Ratio Mismatch Check:')
            self.stdout.write('-' * 50)
            
            mismatch_detected = False
            if pct_a < threshold_low or pct_a > threshold_high:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠️  {var_a}: {pct_a:.2f}% is outside expected range "
                        f"({threshold_low}% - {threshold_high}%)"
                    )
                )
                mismatch_detected = True
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓  {var_a}: {pct_a:.2f}% is within expected range"
                    )
                )
            
            if pct_b < threshold_low or pct_b > threshold_high:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠️  {var_b}: {pct_b:.2f}% is outside expected range "
                        f"({threshold_low}% - {threshold_high}%)"
                    )
                )
                mismatch_detected = True
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓  {var_b}: {pct_b:.2f}% is within expected range"
                    )
                )
            
            if not mismatch_detected:
                self.stdout.write(self.style.SUCCESS('\n✓ No sample ratio mismatch detected.'))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        '\n⚠️  Sample ratio mismatch detected! '
                        'This may indicate issues with variant assignment logic.'
                    )
                )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Expected 2 variants, found {len(variant_data)}. '
                    'Cannot perform sample ratio check.'
                )
            )

        # Additional statistics
        self.stdout.write('\nAdditional Statistics:')
        self.stdout.write('-' * 50)
        
        # Click-through rate (if analyzing exposures, show CTR)
        if event_type == 'exposure' or event_type == 'all':
            exposure_query = Q(experiment_name=experiment_name, event_type=ABTestEvent.EVENT_TYPE_EXPOSURE)
            conversion_query = Q(experiment_name=experiment_name, event_type=ABTestEvent.EVENT_TYPE_CONVERSION)
            
            if exclude_forced:
                exposure_query &= Q(is_forced=False)
                conversion_query &= Q(is_forced=False)
            
            exposure_counts = (
                ABTestEvent.objects
                .filter(exposure_query)
                .values('variant')
                .annotate(count=Count('id'))
            )
            
            conversion_counts = (
                ABTestEvent.objects
                .filter(conversion_query)
                .values('variant')
                .annotate(count=Count('id'))
            )
            
            exposure_dict = {item['variant']: item['count'] for item in exposure_counts}
            conversion_dict = {item['variant']: item['count'] for item in conversion_counts}
            
            self.stdout.write('Conversion Rates (Click-Through Rates):')
            for variant in sorted(set(list(exposure_dict.keys()) + list(conversion_dict.keys()))):
                exposures = exposure_dict.get(variant, 0)
                conversions = conversion_dict.get(variant, 0)
                ctr = (conversions / exposures * 100) if exposures > 0 else 0
                self.stdout.write(f"  {variant:10s}: {conversions}/{exposures} conversions ({ctr:.2f}% conversion rate)")

        self.stdout.write('')

